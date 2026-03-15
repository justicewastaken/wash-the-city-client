#!/bin/bash
set -euo pipefail

cd /root/.openclaw/workspace

# Ensure remote exists with token
if ! git remote | grep -q '^origin$'; then
  TOKEN=$(jq -r .github_token .github-token.json 2>/dev/null || echo "")
  if [ -n "$TOKEN" ]; then
    git remote add origin "https://x-access-token:${TOKEN}@github.com/justicewastaken/openclaw-backup.git"
  fi
fi

# Add all changes (respecting .gitignore)
git add -A

# Commit only if there are changes
if ! git diff-index --quiet HEAD --; then
  COMMIT_MSG="OpenClaw backup: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  git commit -m "$COMMIT_MSG"
  git push origin master
  echo "[$(date -u)] Backup committed and pushed"
else
  echo "[$(date -u)] No changes to backup"
fi