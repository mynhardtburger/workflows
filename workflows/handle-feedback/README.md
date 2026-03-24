# Handle PR Feedback

Autonomously monitors documentation review pull requests for reviewer
comments, evaluates each piece of feedback, and either implements
beneficial suggestions or explains why a suggestion was declined.

## How It Works

1. Discovers open PRs with the `acp:document-review` label
2. Fetches all comments and filters to authorized reviewers (write access)
3. Skips already-processed comments (tracked via reactions)
4. Evaluates each comment for actionable suggestions
5. Implements beneficial suggestions as new commits on the PR branch
6. Declines non-beneficial suggestions with a brief explanation
7. Writes a summary to `artifacts/feedback-log.md`

## Commands

- `/handle-feedback` — Process all labeled PRs
- `/handle-feedback <pr-url>` — Process a single PR

## Prerequisites

- `gh` CLI authenticated with write access to the target repository
- PRs must have the `acp:document-review` label

## Output

- `artifacts/feedback-log.md` — Summary of all processed comments
- Commits pushed to PR branches (for implemented suggestions)
- Replies posted on PRs (for declined suggestions)
- Reactions added to processed comments

## Integration

This workflow is designed to run standalone — typically via a cron job or
on-demand after the document-review workflow creates PRs. It does not
require prior workflow context.
