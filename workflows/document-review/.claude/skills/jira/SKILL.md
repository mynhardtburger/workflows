---
name: jira
description: Create a Jira epic from the documentation review report with child bugs and tasks for each finding.
---

# Jira Skill

You are creating Jira issues from the documentation review report. Each finding
becomes a child issue under a parent epic so the team can track remediation.

## Prerequisites

- `artifacts/report.md` must exist (run `/report` first)
- The `mcp-atlassian` MCP integration must be active
- A Jira project key must be provided as an argument or via the `JIRA_PROJECT`
  environment variable

## Inputs

Gather these values before creating any issues. Arguments passed to the `/jira`
command take precedence over environment variables.

| Parameter | Argument | Env Var | Required |
|-----------|----------|---------|----------|
| Project key | first positional arg | `JIRA_PROJECT` | Yes |
| Component | `component=<name>` | `JIRA_COMPONENT` | No |
| Labels | `labels=<a,b,c>` | `JIRA_LABELS` | No |
| Fix version | `fixversion=<name>` | `JIRA_FIX_VERSION` | No |
| Team | `team=<name>` | `JIRA_TEAM` | No |

If the project key is missing from both the argument and environment, stop and
ask the user to provide it.

## Process

### Step 1: Read the Report

Read `artifacts/report.md`. Extract:

- **Header metadata**: date, repository, commit SHA, instruction
- **Summary table**: dimension x severity counts and ratings
- **All findings**: each finding under its severity heading (Critical, High,
  Medium, Low)

For each finding, capture:

- **ID**: the severity-prefixed number (C1, H1, M1, L1, etc.)
- **Title**: the heading text after the ID
- **Dimension**: the quality dimension (Accuracy, Completeness, etc.)
- **File**: the file path and line reference
- **Source**: which phase detected it (review, verify)
- **Issue**: description of what is wrong
- **Evidence**: quoted text or output demonstrating the problem
- **Fix**: the suggested correction (if present)

### Step 2: Resolve Jira Metadata

1. Check arguments first, then fall back to environment variables
2. Parse comma-separated labels into a list
3. If no project key is available, stop and ask the user
4. Confirm the plan with the user before creating issues:
   - Project key
   - Number of findings to file
   - Any optional fields that will be set

### Step 3: Create the Epic

Use `mcp__mcp-atlassian__jira_create_issue` to create an Epic:

- **Project**: the resolved project key
- **Issue type**: `Epic`
- **Summary**: `Documentation Review: <repository>` (use the repository from
  the report header; if unavailable use the project directory name)
- **Description**: Build the description from the report metadata and summary
  table. Include:
  - Date of the review
  - Repository and commit SHA
  - The full dimension x severity summary table
  - Total finding counts by severity
- **Labels**: merge `doc-review` with any user-provided labels
- **Component**: set if provided
- **Fix version**: set if provided

Record the created epic key (e.g., `PROJ-123`).

### Step 4: Create Child Issues

For each finding in the report, create a child issue under the epic.

#### Classify as Bug or Task

Decide per-finding based on the issue content:

- **Bug** — the finding impacts external users or customers. Examples:
  - Incorrect instructions that would cause users to fail
  - Missing steps that block user workflows
  - Broken commands or wrong API references users would encounter
  - Misleading descriptions of user-facing behavior
  - Dead links in user-facing documentation

- **Task** — the finding impacts developers or is a maintenance/housekeeping
  item. Examples:
  - Internal inconsistencies between developer docs
  - Structural or organizational improvements
  - Stale references in contributor-facing documentation
  - Style or formatting issues
  - Missing code comments or developer-facing docs

#### Map Severity to Priority

| Report Severity | Jira Priority |
|----------------|---------------|
| Critical | Highest |
| High | High |
| Medium | Medium |
| Low | Low |

#### Build the Issue

Use `mcp__mcp-atlassian__jira_create_issue` for each finding:

- **Project**: the resolved project key
- **Issue type**: `Bug` or `Task` (per classification above)
- **Parent**: the epic key from Step 3
- **Summary**: `<ID>. <title>` (e.g., `C1. Incorrect CLI flag in quickstart`)
- **Priority**: mapped from severity (see table above)
- **Description**: structured as follows:

```
## Issue

<issue text from the finding>

## Why This Is a Problem

<reasoning about why this matters, synthesized from the dimension, evidence,
and context — explain the impact on users or developers>

**Evidence:**
<quoted evidence from the finding>

**Affected file:** <file path and line>
**Quality dimension:** <dimension>
**Detected by:** <source phase(s)>

## Expected Outcome

<what needs to be true when this is resolved — derived from the Fix field if
present, otherwise describe the desired end state based on the issue>
```

- **Labels**: merge the severity in lowercase (e.g., `critical`, `high`),
  the dimension in lowercase with hyphens (e.g., `accuracy`, `completeness`),
  `doc-review`, and any user-provided labels
- **Component**: set if provided
- **Fix version**: set if provided

### Step 5: Report Results

After all issues are created, present a summary to the user:

```
## Jira Issues Created

**Epic:** <EPIC-KEY> — Documentation Review: <repository>

| ID | Type | Key | Summary | Priority |
|----|------|-----|---------|----------|
| C1 | Bug  | PROJ-124 | Incorrect CLI flag in quickstart | Highest |
| H1 | Task | PROJ-125 | Inconsistent config key names | High |
| ... | ... | ... | ... | ... |

**Total:** N issues (X bugs, Y tasks) under <EPIC-KEY>
```

## Error Handling

- If `mcp__mcp-atlassian__jira_create_issue` fails for a specific finding,
  log the error, continue with remaining findings, and report failures at
  the end
- If the epic creation fails, stop and report the error — do not attempt to
  create child issues without a parent epic
- If the MCP tool is not available, inform the user that the `mcp-atlassian`
  integration must be active and stop

## Output

This skill does not write to `artifacts/`. Its output is the set of Jira
issues created via the MCP integration.

## When This Phase Is Done

Report the summary table to the user and re-read the controller
(`.claude/skills/controller/SKILL.md`) for next-step guidance.
