# Document Review Workflow

Systematic workflow for reviewing a project's documentation — assessing quality, completeness, accuracy, and consistency, then generating actionable findings and fixes.

## Features

- Auto-discovers all documentation files across the project
- Evaluates docs against 7 quality dimensions
- Classifies findings by severity for prioritized action
- Cross-references documentation claims against source code
- Runs review and verify in parallel as sub-agents for speed
- Generates inline fix suggestions grouped by file
- Supports a speedrun mode for one-shot review

## Directory Structure

```text
workflows/document-review/
├── .ambient/
│   └── ambient.json              # Workflow configuration
├── .claude/
│   ├── commands/
│   │   ├── scan.md               # Discover and catalog docs
│   │   ├── review.md             # Quality review
│   │   ├── verify.md             # Code cross-referencing
│   │   ├── report.md             # Consolidated report
│   │   ├── fix.md                # Fix suggestions
│   │   └── speedrun.md           # Full pipeline
│   └── skills/
│       ├── controller/SKILL.md   # Phase orchestration
│       ├── scan/SKILL.md         # Document discovery
│       ├── review/SKILL.md       # Quality evaluation
│       ├── verify/SKILL.md       # Source code verification
│       ├── report/SKILL.md       # Report generation
│       └── fix/SKILL.md          # Fix suggestion generation
├── templates/                    # Output format templates
│   ├── inventory.md
│   ├── findings-review.md
│   ├── findings-verify.md
│   ├── report.md
│   └── fixes.md
├── CLAUDE.md                     # Behavioral context
└── README.md                     # This file
```

## Commands

| Command | Purpose |
|---------|---------|
| `/scan` | Discover and catalog all documentation in the project |
| `/review` | Deep quality review against 7 dimensions |
| `/verify` | Cross-reference docs against source code (optional) |
| `/report` | Consolidate all findings into a deduplicated report |
| `/fix` | Generate inline fix suggestions (optional) |
| `/speedrun` | Run scan → review + verify → report in one shot |

## Workflow Phases

```text
scan ──┬──> review (sub-agent) ──┬──> report ──> fix
       └──> verify (sub-agent) ──┘
```

Review and verify are independent after scan — they run in parallel as sub-agents, each writing to its own findings file.

### 1. Scan

Discovers all documentation files using glob patterns. Catalogs each file by path, format, topic, audience, and whether it contains executable instructions. Produces an inventory.

### 2. Review

Deep-reads each document evaluating 7 quality dimensions: accuracy, completeness, consistency, clarity, currency, structure, and examples. Identifies target audience per document and assesses audience-appropriateness. Classifies findings by severity.

### 3. Verify (Optional)

Cross-references documentation claims against actual source code. Checks CLI flags, API endpoints, configuration options, default values, and behavior descriptions. Flags undocumented features found in code.

### 4. Report

Consolidates all findings from review and verify into a single deduplicated report. Findings are grouped by severity (Critical → Low) with a dimension × severity summary table. Reads from whichever findings files exist.

### 5. Fix (Optional)

Generates inline fix suggestions for each finding. Quotes problematic text, provides replacement, and explains rationale. Groups suggestions into pull request units with automatable classification and self-contained context for reliable text matching.

### 6. Speedrun

Runs scan → review + verify (parallel) → report in one shot, pausing only for critical decisions.

## Quality Dimensions

| Dimension | What It Checks |
|-----------|---------------|
| Accuracy | Do docs match reality? |
| Completeness | Are there gaps or missing docs? |
| Consistency | Do docs agree with each other? |
| Clarity | Is language clear for the audience? |
| Currency | Dead links, deprecated refs? |
| Structure | Logical organization? |
| Examples | Code samples present and correct? |

## Finding Severities

| Severity | Definition |
|----------|-----------|
| Critical | Incorrect information, broken commands, or missing steps that block users |
| High | Significant gaps, contradictions, or outdated content |
| Medium | Issues that cause confusion but have workarounds |
| Low | Minor improvements to clarity, structure, or presentation |

## Output Artifacts

Output files are written to `artifacts/`:

| File | Content |
|------|---------|
| `artifacts/inventory.md` | Documentation file catalog |
| `artifacts/findings-review.md` | Detailed findings by document |
| `artifacts/findings-verify.md` | Code verification findings |
| `artifacts/report.md` | Consolidated findings report |
| `artifacts/fixes.md` | Inline fix suggestions with PR grouping |

## Quick Start

1. Point the workflow at a project repository
2. Run `/scan` to discover documentation (or `/speedrun` for the full pipeline)
3. Run `/review` for quality analysis
4. Optionally run `/verify` to check docs against code
5. Run `/report` to consolidate all findings
6. Optionally run `/fix` for concrete fix suggestions
