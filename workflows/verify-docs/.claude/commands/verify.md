# /verify - Run Documentation Verification Pipeline

## Purpose

Run the full four-stage documentation verification pipeline: reconnaissance,
discovery, verification, and reporting. Discovers what the project actually does
from source code and verifies that documentation accurately describes it.

## Process

1. Read the controller skill at `.claude/skills/controller/SKILL.md`
2. Execute all four stages in sequence:
   - **Stage 1: Reconnaissance** — Detect languages, frameworks, components, classify docs
   - **Stage 2: Discovery** — Dispatch parallel agents to scan source code
   - **Stage 3: Verification** — Dispatch parallel agents to cross-reference docs vs. code
   - **Stage 4: Report** — Generate structured report with findings

## Output

- `artifacts/verify-docs/verify-docs-report.md` — Full verification report with findings by severity
