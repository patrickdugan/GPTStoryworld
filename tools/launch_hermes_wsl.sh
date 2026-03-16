#!/usr/bin/env bash
set -euo pipefail

KEYFILE=/mnt/c/Users/patri/OneDrive/Desktop/Hermes.txt
if [[ ! -f "$KEYFILE" ]]; then
  KEYFILE=/mnt/c/Users/patri/OneDrive/Desktop/hermes.txt
fi
if [[ -f "$KEYFILE" ]]; then
  API_KEY="$(tr -d '\r\n' < "$KEYFILE")"
  if [[ -n "$API_KEY" ]]; then
    hermes config set OPENROUTER_API_KEY "$API_KEY" >/dev/null
  fi
fi

cd /mnt/c/projects/GPTStoryworld/storyworlds/by-week
/mnt/c/projects/GPTStoryworld/tools/hermes_write_guard.sh pre
/mnt/c/projects/GPTStoryworld/tools/hermes_storyworld_oracle.sh pre
exec hermes chat
