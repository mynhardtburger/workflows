#!/usr/bin/env bash
# Usage: ./check-write-access.sh OWNER/REPO
set -euo pipefail

repo="${1:?Usage: $0 OWNER/REPO}"
perm=$(gh api "repos/${repo}/collaborators/$(gh api user -q .login)/permission" -q .permission 2>/dev/null) || {
  echo "No — no write access to ${repo}"
  exit 1
}

case "$perm" in
  admin|write) echo "Yes — permission: $perm"; exit 0 ;;
  *)           echo "No — permission: $perm";  exit 1 ;;
esac
