# /handle-feedback

Read `.claude/skills/handle-feedback/SKILL.md` and execute it.

This workflow discovers PRs by querying GitHub for the `acp:document-review`
label and operates without prior workflow context.

Optionally accepts a single PR link (e.g.,
`/handle-feedback https://github.com/org/repo/pull/42`) to process only
that PR instead of all labeled PRs.

$ARGUMENTS
