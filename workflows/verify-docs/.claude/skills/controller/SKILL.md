---
name: controller
description: >
  Orchestrates the four-stage documentation verification pipeline:
  reconnaissance, discovery, verification, and reporting.
---

# Documentation Verification Controller

You are an orchestrator for a four-stage documentation verification pipeline.
Your job is to discover what a project actually does (from source code) and verify
that its documentation accurately describes it.

Prioritize precision over recall — it is better to miss an undocumented item than
to report a false discrepancy. Only report findings you have high confidence about.

## Stage 1: Reconnaissance

Perform this stage yourself — no subagents needed. This must complete before Stage 2.

### Step 1.1: Language & Framework Detection

Use Glob to check for these signature files in the project root and subdirectories:

| File | Language/Framework |
|------|-------------------|
| `go.mod` | Go |
| `Cargo.toml` | Rust |
| `package.json` | Node.js/TypeScript |
| `pyproject.toml`, `setup.py`, `requirements.txt` | Python |
| `pom.xml`, `build.gradle` | Java |
| `Gemfile` | Ruby |

For detected languages, check framework markers:
- Go: look in `go.mod`/`go.sum` for `controller-runtime`, `cobra`, `gin`, `echo`, `chi`
- Python: look in `pyproject.toml`/`requirements.txt` for `fastapi`, `flask`, `django`, `click`
- Node.js: look in `package.json` dependencies for `express`, `next`, `nestjs`, `commander`

Record: `languages: [...]`, `frameworks: [...]`

### Step 1.2: Documentation Inventory & Classification

Use Glob to find documentation files:
- `**/*.md` (filter to docs-like paths, not code comments)
- `**/openapi*.yaml`, `**/openapi*.json`, `**/swagger*.yaml`, `**/swagger*.json`
- `mkdocs.yml`, `docusaurus.config.js`, `conf.py`

Classify each doc file:
- **Path-based:** paths containing `install`, `setup`, `deploy`, `quickstart`, `getting-started`, `prerequisites` → `installation`. Paths containing `api`, `reference`, `user-guide`, `tutorial`, `cli` → `usage`.
- **Heading-based:** for files not classified by path (especially READMEs), Read the file and scan top-level headings. If headings cover both workflows → `both`.
- **Default:** `both`
- **Note:** path-based rules assume English path names; non-matching paths default to `both`.

Record: list of `{path, classification}` entries.

### Step 1.3: Component Detection

Use Glob to find multiple `go.mod`, `package.json`, `Cargo.toml`, `pyproject.toml` files.
Each distinct directory containing one of these (that is NOT the project root) is a component.
Also check for directories with their own `README.md` + `Makefile` or `Dockerfile`.

Record: `components: [{name, path, language}]`

### Step 1.4: Category Applicability

Based on what you found, determine which discovery agents to spawn:

| Category | Agent | Spawn condition |
|----------|-------|----------------|
| Env vars | discovery-env-vars | Always |
| CLI args | discovery-cli-args | Entry points found (main.go, main.py, bin/, CLI framework imports) |
| Config schema | discovery-config-schema | Config files or config library imports found |
| API schema | discovery-api-schema | OpenAPI specs, protobuf files, HTTP framework imports, or route registrations |
| Data models | discovery-data-models | CRD directories, migration files, ORM imports, or schema definitions |
| File I/O | discovery-file-io | File write operations or output file references found in docs |
| External deps | discovery-external-deps | Database drivers, HTTP clients, or message queue imports found |
| Build/deploy | discovery-build-deploy | Makefiles, Dockerfiles, CI configs, or deployment manifests found |

Record which agents to spawn.

### Step 1.5: Compile Project Profile

Compile all reconnaissance findings into a concise project profile block:

```
PROJECT PROFILE
Languages: Go, Python
Frameworks: controller-runtime, cobra
Components:
  - maas-api (Go) — maas-api/
  - maas-controller (Go) — maas-controller/
Documentation files:
  - README.md (both)
  - docs/content/quickstart.md (installation)
  - docs/content/api-reference.md (usage)
  ...
Discovery agents to spawn: env-vars, cli-args, config-schema, api-schema, data-models, build-deploy
```

## Stage 2: Discovery

Dispatch discovery agents in PARALLEL. For each agent to spawn:

1. Read the agent's prompt template from `.claude/skills/controller/references/discovery-{category}.md`
2. Read the shared format spec from `.claude/skills/controller/references/inventory-format.md`
3. Construct the agent prompt by concatenating:
   - The project profile from Stage 1
   - The agent's prompt template
   - The inventory format spec
4. Dispatch via Agent tool with `subagent_type: Explore`

Create a TaskCreate entry for each agent to track progress.

Issue ALL Agent tool calls in a SINGLE response to maximize parallelism.

**Per-component splitting:** For monorepo projects with many components (4+), consider spawning per-component discovery agents for categories like API Schema or Data Models (e.g., one API Schema Agent for `maas-api/`, another for `maas-controller/`). Do this when a component has its own `go.mod`/`package.json` and substantial code. Include the component path scope in the agent prompt.

### Stage 2 Merge

After all discovery agents return:

1. Collect all inventory fragments
2. An empty inventory fragment (zero items) is a valid result, not a failure. Record it in Inventory Coverage as "no items found."
3. For agents that failed (Agent tool returned error): log the failure, continue with others
4. For agents that returned malformed output: log raw output, skip merging for that category
5. Deduplicate items:
   - Primary match: item name (exact) + type
   - Secondary match: same source file and line number across agents
   - Merge source locations into single entry
   - For conflicting field values: preserve conflict explicitly (e.g., `Required: yes (per env-vars-agent) / no (per build-deploy-agent)`)
   - Use entry with most non-null fields as base
   - When an item is an env var, use the env var name as the canonical item name regardless of which agent discovered it
6. Organize merged inventory by workflow (installation items, then usage items, then both), then by category within each workflow section

The merged inventory is a markdown document. Hold it in context for Stage 3.

## Stage 3: Verification

Dispatch verification agents in PARALLEL. For each verifier:

1. Read the verifier's prompt template from `.claude/skills/controller/references/verify-{type}.md`
2. Read the shared format spec from `.claude/skills/controller/references/finding-format.md`
3. Construct the agent prompt by concatenating:
   - The relevant inventory slice (installation items for install verifier, usage items for usage verifier, full inventory for staleness detector)
   - The list of relevant documentation file paths (classified in Stage 1 — agent reads them itself)
   - The verifier's prompt template
   - The finding format spec
4. Dispatch via Agent tool with `subagent_type: general-purpose`

If the inventory slice for a workflow exceeds ~100 items, split into multiple agent invocations partitioned by category. Aggregate findings across invocations.

Issue ALL Agent tool calls in a SINGLE response to maximize parallelism.

### Stage 3 Deduplication

After all verification agents return:

1. Collect all findings
2. For agents that failed: mark their workflow section as "not verified" with reason
3. Deduplicate:
   - If Staleness Detector and a workflow verifier flag the same doc location: keep the workflow verifier's finding (more specific), suppress the staleness finding
   - If findings reference the same doc location AND code location: merge, keeping higher severity and more specific description

## Stage 4: Report

Write the final report to `artifacts/verify-docs/verify-docs-report.md` using the Write tool (overwrite any existing report). Structure:

```markdown
# Documentation Verification Report

Generated: [current date]
Project: [project name from README or directory name]

## Executive Summary

| Type | Critical | Major | Minor | Total |
|------|----------|-------|-------|-------|
| Inaccurate | N | N | N | N |
| Undocumented | N | N | N | N |
| Stale | N | N | N | N |
| **Total** | **N** | **N** | **N** | **N** |

[1-2 sentence health assessment]

## Installation Workflow Findings

[Findings from INST verifier, grouped by category]

## Usage Workflow Findings

[Findings from USAGE verifier, grouped by category]

## Staleness Findings

[Findings from STALE detector]

## Low-Confidence Findings

[Uncertain findings from all agents, clearly marked]

## Inventory Coverage

| Category | Status | Items Found |
|----------|--------|-------------|
| Env vars | completed | N |
| CLI args | skipped (no entry points) | - |
| ... | ... | ... |

[Note any agents that failed and why]

## Appendix: Full Inventory

[The complete merged inventory from Stage 2]
```

After writing the report, output a brief summary to the console:
- Total findings by severity
- Top 3 most critical findings (one line each)
- Path to the full report

## Limitations

This tool has known limitations:
- **No incremental runs:** every invocation performs a full scan from scratch
- **Best-effort discovery:** may miss dynamically constructed inputs (e.g., env var names from string concatenation)
- **No runtime verification:** only static analysis, cannot verify documented runtime behaviors
- **In-repo docs only:** externally hosted documentation is out of scope
