# Verify Docs Workflow

Discovers project inputs, outputs, and behaviors from source code, then verifies
documentation claims against those discoveries.

## Pipeline

1. **Reconnaissance** — Detect languages, frameworks, components; classify documentation files
2. **Discovery** — Parallel agents scan for env vars, CLI args, config schemas, API endpoints, data models, file I/O, external deps, build targets
3. **Verification** — Parallel agents cross-reference discoveries against docs for accuracy, completeness, and staleness
4. **Report** — Generate structured report at `artifacts/verify-docs/verify-docs-report.md`

## Commands

- `/verify` — Run the full verification pipeline

## Architecture

The workflow controller lives at `.claude/skills/controller/SKILL.md`.
Discovery and verification agent prompts are in `.claude/skills/controller/references/`.
Output is written to `artifacts/verify-docs/`.

## Principles

- Precision over recall — only report findings with high confidence
- Only report factual accuracy issues, not prose quality or style
- Every finding must have a concrete code reference
- Uncertain findings go in a Low-Confidence section, not the main findings
