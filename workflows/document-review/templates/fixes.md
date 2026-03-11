# Documentation Fix Suggestions

**Project:** [name]
**Generated:** [date]
**Total suggestions:** N

## Summary

| Severity | Suggestions |
|----------|-------------|
| Error | N |
| Gap | N |
| Inconsistency | N |
| Stale | N |
| Improvement | N |

## Fixes by File

### [path/to/document.md]

#### Fix 1: [brief description]

**Severity:** Error | **Finding:** [reference to finding]
**Location:** Section "[heading]", line N

**Current text:**

> The `--port` flag sets the listening port (default: 3000).

**Suggested replacement:**

> The `--listen-port` flag sets the listening port (default: 8080).

**Rationale:** The flag was renamed from `--port` to `--listen-port` in v2.0.
The default was also changed from 3000 to 8080. See `src/cli.py:45`.

---

#### Fix 2: [brief description]

...

### [path/to/another-doc.md]

...

## New Content Needed

### [path/to/file-or-new-file.md] — [topic]

**Finding:** [reference to Gap finding]
**Location:** Suggested new section in [file], after "[heading]"

**Draft outline:**

```markdown
## [New Section Title]

[Paragraph explaining the concept]

### [Subsection]

[Details needed — requires input from maintainers on intended behavior]
```

**What's needed to complete:** [List of information needed]

## Needs Human Input

These findings require knowledge the reviewer does not have:

- **[Finding reference]** — [Why human input is needed]
- ...
