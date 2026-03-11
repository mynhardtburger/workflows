#!/usr/bin/env bash
#
# fetch-pr.sh — Fetch all data for a single PR into structured JSON files.
#
# Usage:
#   ./scripts/fetch-pr.sh --repo owner/repo --pr 123 [--output-dir artifacts/pr-fixer/123]
#
# Requirements:
#   - gh CLI installed and authenticated
#   - jq installed
#   - python3 installed
#

set -euo pipefail

REPO=""
PR_NUM=""
OUTPUT_DIR=""
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --repo)
            REPO="$2"
            shift 2
            ;;
        --pr)
            PR_NUM="$2"
            shift 2
            ;;
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 --repo owner/repo --pr 123 [--output-dir artifacts/pr-fixer/123]"
            exit 0
            ;;
        *)
            echo "Unknown argument: $1" >&2
            exit 1
            ;;
    esac
done

if [[ -z "$REPO" || -z "$PR_NUM" ]]; then
    echo "Error: --repo and --pr are required" >&2
    exit 1
fi

if [[ -z "$OUTPUT_DIR" ]]; then
    OUTPUT_DIR="artifacts/pr-fixer/${PR_NUM}"
fi

for cmd in gh jq python3; do
    if ! command -v "$cmd" &>/dev/null; then
        echo "Error: ${cmd} is not installed." >&2
        exit 1
    fi
done

if ! gh auth status &>/dev/null; then
    echo "Error: gh CLI is not authenticated." >&2
    exit 1
fi

OWNER="${REPO%%/*}"
REPO_NAME="${REPO##*/}"

mkdir -p "${OUTPUT_DIR}"
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

echo "Fetching PR #${PR_NUM} from ${REPO}..." >&2

# -- Fetch PR metadata, reviews, review comments, and diff in parallel --
DETAIL_FIELDS="number,title,author,createdAt,updatedAt,labels,isDraft,baseRefName,headRefName,headRefOid,url,state,additions,deletions,changedFiles,mergeable,body,reviewDecision,statusCheckRollup,comments,assignees,milestone,files,isCrossRepository,headRepositoryOwner"

echo "  Fetching PR data (parallel)..." >&2

gh pr view "$PR_NUM" --repo "$REPO" --json "$DETAIL_FIELDS" \
    2>/dev/null > "${OUTPUT_DIR}/pr.json" &
PID_PR=$!

gh api "repos/${OWNER}/${REPO_NAME}/pulls/${PR_NUM}/reviews" \
    --paginate 2>/dev/null > "${TMPDIR}/reviews.json" &
PID_REVIEWS=$!

gh api "repos/${OWNER}/${REPO_NAME}/pulls/${PR_NUM}/comments" \
    --paginate 2>/dev/null > "${TMPDIR}/review_comments.json" &
PID_RC=$!

gh api "repos/${OWNER}/${REPO_NAME}/pulls/${PR_NUM}/files" \
    --paginate 2>/dev/null \
    | jq '[.[] | {filename, status, additions, deletions, patch}]' \
    > "${OUTPUT_DIR}/diff.json" &
PID_DIFF=$!

# Wait for all parallel fetches, handling failures
wait "$PID_PR" 2>/dev/null || echo '{}' > "${OUTPUT_DIR}/pr.json"
wait "$PID_REVIEWS" 2>/dev/null || echo '[]' > "${TMPDIR}/reviews.json"
wait "$PID_RC" 2>/dev/null || echo '[]' > "${TMPDIR}/review_comments.json"
wait "$PID_DIFF" 2>/dev/null || echo '[]' > "${OUTPUT_DIR}/diff.json"

# -- Fetch check runs (depends on PR metadata for HEAD_SHA) --
echo "  Fetching CI status..." >&2
HEAD_SHA=$(jq -r '.headRefOid // empty' "${OUTPUT_DIR}/pr.json" 2>/dev/null || true)

echo '[]' > "${OUTPUT_DIR}/ci.json"
if [[ -n "$HEAD_SHA" ]]; then
    gh api "repos/${OWNER}/${REPO_NAME}/commits/${HEAD_SHA}/check-runs" \
        --paginate 2>/dev/null \
        | jq '.check_runs // []' > "${OUTPUT_DIR}/ci.json" 2>/dev/null || echo '[]' > "${OUTPUT_DIR}/ci.json"
fi

# -- Build unified comment stream using shared script --
echo "  Building unified comment stream..." >&2
python3 "${SCRIPT_DIR}/merge-comments.py" \
    --pr-json "${OUTPUT_DIR}/pr.json" \
    --reviews "${TMPDIR}/reviews.json" \
    --review-comments "${TMPDIR}/review_comments.json" \
    --output "${OUTPUT_DIR}/comments.json"

# -- Generate per-file diffs and index (for large diffs) --
echo "  Splitting diff into per-file diffs..." >&2
mkdir -p "${OUTPUT_DIR}/diffs"
jq -r '.[] | "\(.status)\t\(.additions)\t\(.deletions)\t\(.filename)"' \
    "${OUTPUT_DIR}/diff.json" 2>/dev/null > "${OUTPUT_DIR}/diff-index.txt" || true

# Write each file's diff as a separate JSON file (filename sanitized to path-safe name)
python3 -c "
import json, os, re
with open('${OUTPUT_DIR}/diff.json') as f:
    files = json.load(f)
for df in files:
    fname = df.get('filename', 'unknown')
    safe = re.sub(r'[^a-zA-Z0-9._-]', '_', fname)
    with open(os.path.join('${OUTPUT_DIR}/diffs', safe + '.json'), 'w') as out:
        json.dump(df, out, indent=2)
" 2>/dev/null || true

# -- Summary --
COMMENT_COUNT=$(jq 'length' "${OUTPUT_DIR}/comments.json" 2>/dev/null || echo "0")
DIFF_COUNT=$(jq 'length' "${OUTPUT_DIR}/diff.json" 2>/dev/null || echo "0")
CI_COUNT=$(jq 'length' "${OUTPUT_DIR}/ci.json" 2>/dev/null || echo "0")
MERGEABLE=$(jq -r '.mergeable // "unknown"' "${OUTPUT_DIR}/pr.json" 2>/dev/null || echo "unknown")

echo ""
echo "Fetch complete for PR #${PR_NUM}:"
echo "  Mergeable: ${MERGEABLE}"
echo "  Comments:  ${COMMENT_COUNT} (unified stream + per-comment files)"
echo "  Diff files: ${DIFF_COUNT} (index: diff-index.txt)"
echo "  CI checks: ${CI_COUNT}"
echo "  Output:    ${OUTPUT_DIR}/"
