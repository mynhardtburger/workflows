# Finding Format

You MUST produce your findings in exactly this format. The orchestrator parses this to merge findings from all verification agents.

## Finding ID Scheme

Use the prefix assigned to you in your prompt:
- Installation Workflow Verifier: `INST-001`, `INST-002`, ...
- Usage Workflow Verifier: `USAGE-001`, `USAGE-002`, ...
- Staleness Detector: `STALE-001`, `STALE-002`, ...

## Format

For each finding:

### [FINDING-ID]: [Short descriptive title]

- **Type:** inaccurate | undocumented | stale
- **Severity:** critical | major | minor
- **Category:** env-var | cli-arg | api-endpoint | config | data-model | file-path | external-dep | build-target
- **Workflow:** installation | usage
- **Doc location:** `path/to/doc.md:LINE` (exact file and line in documentation)
- **Code location:** `path/to/code.go:LINE` (if applicable — where the truth lives in code)
- **Description:** Clear statement of the discrepancy. State what the documentation says AND what the code actually does.
- **Suggestion:** Concrete recommendation for fixing the documentation.

## Severity Definitions

- **critical** — would cause user failure, security implications, or data loss (e.g., wrong auth flow, missing required env var, incorrect API endpoint)
- **major** — would cause confusion or incorrect usage, but user could recover (e.g., wrong default value, missing parameter, outdated config key)
- **minor** — cosmetic or edge-case discrepancy (e.g., slightly outdated version, renamed but equivalent key)

## Rules

- Only report findings you have HIGH confidence about. You must have a concrete code reference.
- If uncertain, list in a "## Low-Confidence Findings" section at the end, clearly marked.
- Fuzzy name matches (e.g., `MAAS_DB_HOST` vs `DB_HOST`) should be noted as "possible match" in Low-Confidence, not reported as stale.
- Do NOT report on prose quality, grammar, or style — only factual accuracy.
