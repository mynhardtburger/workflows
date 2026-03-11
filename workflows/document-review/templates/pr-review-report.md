## Documentation Review: {VERDICT}

<!-- VERDICT must be one of: PASS | PASS WITH SUGGESTIONS | FAIL -->

### Summary

{SUMMARY}

<!-- 1-3 sentence overview: what this PR does, whether it has user-facing
impact, and whether documentation updates are sufficient. -->

### Findings

<!-- If there are no findings, write the following line and skip to Notes: -->
<!-- "No documentation gaps identified." -->

<!-- Otherwise, repeat the following block for each finding: -->

#### {FINDING_NUMBER}. {FINDING_TITLE}

- **Severity**: {SEVERITY}
- **Category**: {CATEGORY}
- **Blast radius**: {BLAST_RADIUS}
- **Code change**: {CODE_CHANGE}
- **Expected documentation**: {EXPECTED_DOCUMENTATION}
- **What is missing**: {WHAT_IS_MISSING}
- **Suggested text**: {SUGGESTED_TEXT}

<!-- Field values:
  SEVERITY: CRITICAL | MAJOR | MINOR
  CATEGORY: Category letter and name from Phase 2 (e.g., "B -- CLI and Command Changes")
  BLAST_RADIUS: BROAD | NARROW
  CODE_CHANGE: File path and brief description of what changed
  EXPECTED_DOCUMENTATION: Which doc file should be updated, or where new docs should be added
  WHAT_IS_MISSING: Specific description of the documentation gap
  SUGGESTED_TEXT: Exact text to add or replace if confidence is high enough.
    Otherwise: "Manual review recommended -- [reason]."
-->

<!-- End of repeating finding block -->

### Notes

{NOTES}

<!-- Optional section for contextual observations that do not rise to the level
of a finding. Examples: advisory about missing foundational docs, areas not
fully assessed due to PR scale, documentation structure improvements.
Omit this section entirely if there are no notes. -->
