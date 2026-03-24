# Verify Docs

Discovers what a project actually does by scanning its source code, then verifies that documentation accurately describes it. Produces a structured report of inaccuracies, undocumented features, and stale references.

## How It Works

The workflow runs a four-stage pipeline:

### Stage 1: Reconnaissance

Detects languages, frameworks, and components in the project. Classifies documentation files as installation-related, usage-related, or both. Determines which discovery agents to spawn.

### Stage 2: Discovery

Dispatches up to 8 parallel agents to scan source code:

| Agent | What it finds |
|-------|---------------|
| Env vars | Environment variables read, set, or referenced |
| CLI args | Command-line flags, arguments, and subcommands |
| Config schema | Configuration file schemas and config-loading mechanisms |
| API schema | API endpoints, request/response schemas, auth requirements |
| Data models | CRDs, database schemas, ORM models, GraphQL schemas |
| File I/O | Files the project reads from or writes to |
| External deps | External services and systems connected at runtime |
| Build/deploy | Build targets, CI/CD pipelines, deployment configs |

Agents are spawned conditionally based on what reconnaissance detects.

### Stage 3: Verification

Dispatches 3 parallel verification agents:

| Agent | What it checks |
|-------|----------------|
| Installation verifier | Accuracy and completeness of install/setup/deploy docs |
| Usage verifier | Accuracy and completeness of API/CLI/config/behavior docs |
| Staleness detector | References to things that no longer exist in the codebase |

### Stage 4: Report

Generates a structured report with findings grouped by severity (critical, major, minor) and type (inaccurate, undocumented, stale).

## Usage

```text
/verify
```

## Output

- `artifacts/verify-docs/verify-docs-report.md` — Full verification report

## Limitations

- **No incremental runs:** every invocation performs a full scan from scratch
- **Best-effort discovery:** may miss dynamically constructed inputs (e.g., env var names from string concatenation)
- **No runtime verification:** only static analysis, cannot verify documented runtime behaviors
- **In-repo docs only:** externally hosted documentation is out of scope
