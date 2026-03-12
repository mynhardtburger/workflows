# PR Fixer Workflow

Fixes a single pull request: rebases to resolve conflicts, evaluates and addresses reviewer feedback, runs lints and tests, and pushes clean commits.

## Prerequisites

- [GitHub CLI (`gh`)](https://cli.github.com/) installed and authenticated
- `jq` installed
- The target repo cloned locally

## Quick Start

```bash
# 1. Fetch all data for the PR
./scripts/fetch-pr.sh --repo owner/repo --pr 123

# 2. Run the agent to fix the PR
#    (via Ambient Code Platform or Claude Code)
```

The agent reads the fetched data, checks out the PR branch, and works through: rebase, reviewer feedback, lints, tests, and push.

## Directory Structure

```text
pr-fixer/
├── .ambient/
│   └── ambient.json          # Workflow config
├── CLAUDE.md                 # Agent behavioral instructions
├── scripts/
│   └── fetch-pr.sh           # Single-PR data fetcher
├── artifacts/
│   └── pr-fixer/{number}/    # Fetched data and fix report
└── README.md
```

## Fetch Script

```bash
./scripts/fetch-pr.sh --repo owner/repo --pr 123 [--output-dir artifacts/pr-fixer/123]
```

**Output:**

- `pr.json` — PR metadata (title, body, labels, branch, mergeable status)
- `comments.json` — unified chronological stream of all reviews, inline comments, and discussion
- `diff.json` — changed files with patches
- `ci.json` — check run results

## Fix Process

1. **Rebase** — resolve merge conflicts onto the base branch
2. **Review feedback** — read all comments, fix valid issues, respond to invalid concerns
3. **Lint & test** — run the project's lint and test commands
4. **Push** — force-push with lease after user confirmation

## Relationship to Review Queue

The Review Queue workflow (`internal-workflows/pr-overview`) identifies which PRs need attention. The PR Fixer can be run on individual PRs flagged by the review queue — especially those with merge conflicts or reviewer feedback that needs addressing.
