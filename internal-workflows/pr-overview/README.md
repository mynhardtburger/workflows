# Review Queue Workflow

Evaluates all open PRs in a GitHub repository and generates a prioritized review queue — an ordered list of what needs human attention, ranked by type and urgency.

## Prerequisites

- [GitHub CLI (`gh`)](https://cli.github.com/) installed and authenticated
- `jq` installed

## Quick Start

```bash
# 1. Fetch PR data
./scripts/fetch-prs.sh --repo owner/repo

# 2. Run the agent to analyze and generate the queue
#    (via Ambient Code Platform or Claude Code)
```

The agent reads the fetched data, evaluates each PR via sub-agents, and writes a report to `artifacts/pr-review/review-queue-{date}.md`.

## Directory Structure

```text
pr-overview/
├── .ambient/
│   ├── ambient.json           # Workflow config
│   └── rubric.md              # Self-evaluation rubric
├── CLAUDE.md                  # Agent behavioral instructions
├── scripts/
│   ├── fetch-prs.sh           # Data fetching script (all open PRs)
│   ├── analyze-prs.py         # Blocker analysis and type classification
│   └── test-merge-order.sh    # Local merge dry-run test
├── templates/
│   ├── review-queue.md        # Output template
│   └── merge-meeting.md       # Legacy template (deprecated)
├── artifacts/
│   └── pr-review/             # Generated reports and raw data
└── README.md
```

## How It Works

1. **Fetch** — `fetch-prs.sh` pulls all open PR data from the GitHub API
2. **Analyze** — `analyze-prs.py` runs mechanical checks (CI, conflicts, Jira, staleness) and classifies PRs by type
3. **Sub-agent evaluation** — each PR's full comment stream is read by a sub-agent that understands review arcs, stale comments, and nuanced feedback
4. **Merge test** — `test-merge-order.sh` does a local dry-run merge of clean PRs in sequence
5. **Report** — generates a prioritized queue and updates the GitHub milestone

## PR Type Classification

PRs are classified by type based on labels, branch name, title, and diff shape:

| Type | Examples |
|------|----------|
| `bug-fix` | `fix/`, `bugfix/` branches, `bug` label, `fix:` title prefix |
| `feature` | `feat/` branches, `enhancement` label, `feat:` title prefix |
| `refactor` | `refactor/` branches, `cleanup` label |
| `chore` | CI/config changes, `chore:` prefix, `deps` label |
| `docs` | Markdown-only changes, `docs/` branches |

## Queue Ranking

PRs are ranked by what needs human attention first:

1. Bug fixes before features before refactors
2. Fewer blockers rank higher
3. Smaller PRs rank higher (faster to review)
4. Priority labels (`critical`, `hotfix`) boost rank
5. Draft PRs sort to the bottom

## Review Readiness Criteria

A PR is **ready for review** when:
- CI passes (all checks green or neutral)
- Not a draft
- No merge conflicts
- No unresolved substantive review feedback
- Not stale (updated within 30 days)

## Related Workflows

- **PR Fixer** (`internal-workflows/pr-fixer`) — fixes individual PRs flagged by the review queue (rebase, address feedback, run tests)
