#!/usr/bin/env bash
set -euo pipefail

# Real-filesystem write guard for Hermes sessions.
# Usage:
#   tools/hermes_write_guard.sh pre
#   tools/hermes_write_guard.sh post /mnt/c/.../file.json

ROOT="/mnt/c/projects/GPTStoryworld/storyworlds/by-week/2026-W11"
MODE="${1:-}"
FILE="${2:-}"

if [[ -z "$MODE" ]]; then
  echo "usage: $0 <pre|post> [file]" >&2
  exit 2
fi

if [[ ! -d "$ROOT" ]]; then
  echo "ERROR: root missing: $ROOT" >&2
  exit 10
fi

case "$MODE" in
  pre)
    pwd
    ls -ld "$ROOT"
    ;;
  post)
    if [[ -z "$FILE" ]]; then
      echo "ERROR: post mode requires file path" >&2
      exit 3
    fi
    case "$FILE" in
      "$ROOT"/*) ;;
      *)
        echo "ERROR: file outside allowed root: $FILE" >&2
        exit 11
        ;;
    esac
    pwd
    ls -l "$FILE"
    wc -c "$FILE"
    ;;
  *)
    echo "ERROR: unknown mode: $MODE (expected pre|post)" >&2
    exit 4
    ;;
esac

