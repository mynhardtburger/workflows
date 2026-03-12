# Review Queue — Execution Efficiency Rubric

This rubric evaluates how efficiently the review queue agent executed the workflow. It is triggered after the report is written and the milestone updated. The purpose is to identify inefficiencies so the workflow can be continuously improved. The output is a score out of 25 (aggregate of 5 criteria at 5 points each) and a brief explanation.

---

## Criterion 1: Data Pipeline Efficiency (1-5 points)

Did the fetch and analysis scripts run cleanly without manual intervention?

- **Score 1**: Scripts failed entirely. Agent had to rewrite or replace them from scratch.
- **Score 2**: Scripts ran but with errors (jq failures, missing fields, scope issues). Agent wrote workaround scripts to re-fetch data.
- **Score 3**: Scripts completed but with warnings (Unicode sanitization needed, some PRs had empty data). Agent handled it without major workarounds.
- **Score 4**: Scripts ran cleanly. Minor issues (e.g., one PR failed to fetch) resolved by the script's own error handling.
- **Score 5**: Both `fetch-prs.sh` and `analyze-prs.py` ran in a single call each with no errors, no workarounds, and no manual re-runs.

**Red flags**: Agent writing its own fetch/analysis Python script instead of using the provided ones. Re-running the same script multiple times. Manually fetching individual PRs.

---

## Criterion 2: Context Management (1-5 points)

Did the agent avoid flooding its context with large data?

- **Score 1**: Agent read raw PR files (50KB+) directly into its context. Multiple "output too large" truncation errors. Critical data was lost.
- **Score 2**: Agent read analysis.json when it was too large, causing truncation. Had to re-read with offset/limit workarounds.
- **Score 3**: Agent used the split file structure (analysis.json summary + per-PR files) but read more files than necessary.
- **Score 4**: Agent read only the summary and the specific per-PR files needed. Used sub-agents for review evaluation. Minor unnecessary reads.
- **Score 5**: Agent read the compact summary once, delegated review evaluation to parallel sub-agents, and only read individual analysis files for report generation. Zero truncation, zero wasted reads.

**Red flags**: "Output too large" messages. Agent reading `prs/{number}.json` directly instead of `reviews/{number}/` comment files. Reading the same file multiple times.

---

## Criterion 3: Tool Call Economy (1-5 points)

Did the agent complete the workflow in a reasonable number of tool calls?

- **Score 1**: 50+ tool calls. Extensive thrashing.
- **Score 2**: 40-49 tool calls. Significant wasted calls.
- **Score 3**: 30-39 tool calls. Some unnecessary investigation but generally on track.
- **Score 4**: 20-29 tool calls. Efficient execution with minimal waste.
- **Score 5**: Under 20 tool calls. Ran scripts, delegated review to sub-agents, synced milestone, wrote report, updated milestone description — all with no wasted steps.

**Benchmark**: The ideal workflow is approximately:
1. Read CLAUDE.md + template (2 calls)
2. Run fetch-prs.sh (1 call)
3. Run analyze-prs.py (1 call)
4. Read analysis summary + spawn parallel sub-agents for per-PR evaluation (2-4 calls)
5. Find/create milestone + sync PRs + comment on blocked (3-5 calls)
6. Write report (1 call)
7. Update milestone description (1 call)
Total: ~11-15 calls

---

## Criterion 4: Error Recovery (1-5 points)

When something went wrong, did the agent recover gracefully or spiral?

- **Score 1**: A single error caused the agent to abandon the approach entirely and start over.
- **Score 2**: Errors caused multi-step debugging sessions (5+ tool calls to diagnose and fix).
- **Score 3**: Agent encountered errors and recovered within 2-3 tool calls.
- **Score 4**: Agent encountered a minor error and recovered in 1 call.
- **Score 5**: No errors encountered, or the agent's first recovery attempt succeeded immediately.

**Red flags**: Agent writing replacement scripts when the provided one fails. Retrying the same failing command. Long debugging chains.

---

## Criterion 5: Completeness (1-5 points)

Did the agent complete ALL 9 checklist items?

- **Score 1**: Completed 4 or fewer items. Major deliverables missing.
- **Score 2**: Completed 5-6 items. Report was written but milestone was not updated, or review evaluation was skipped.
- **Score 3**: Completed 7 items. One or two steps skipped or done incorrectly.
- **Score 4**: All 9 items completed but with minor issues.
- **Score 5**: All 9 items completed correctly: fetch, analyze, sub-agent evaluation, milestone find/create, milestone sync, blocker comments, write report, update milestone, self-evaluate.

**The 9 checklist items**:
1. Run fetch-prs.sh
2. Run analyze-prs.py
3. Evaluate PRs via sub-agents
4. Find or create Review Queue milestone
5. Sync PRs to milestone
6. Comment on blocked PRs
7. Write the review queue report
8. Update milestone description
9. Self-evaluate execution
