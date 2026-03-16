#!/usr/bin/env bash
set -euo pipefail

# Oracle for Hermes storyworld work:
# - confirms real WSL<->Windows mount path
# - validates SweepWeave JSON
# - optionally runs strict quality gate
#
# Usage:
#   tools/hermes_storyworld_oracle.sh pre
#   tools/hermes_storyworld_oracle.sh validate /mnt/c/.../world.json
#   tools/hermes_storyworld_oracle.sh gate /mnt/c/.../world.json /mnt/c/.../report.json

ROOT="/mnt/c/projects/GPTStoryworld"
BYWEEK="$ROOT/storyworlds/by-week"
VALIDATOR="$ROOT/codex-skills/storyworld-building/scripts/sweepweave_validator.py"
QUALITY_GATE="$ROOT/codex-skills/storyworld-building/scripts/storyworld_quality_gate.py"
PYTHON_BIN="${PYTHON_BIN:-python3}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_BIN="python"
fi

cmd="${1:-}"
json_path="${2:-}"
report_path="${3:-}"

case "$cmd" in
  pre)
    pwd
    ls -ld "$ROOT" "$BYWEEK"
    ls -l "$VALIDATOR" "$QUALITY_GATE"
    ;;
  validate)
    [[ -n "$json_path" ]] || { echo "ERROR: missing json path" >&2; exit 2; }
    [[ -f "$json_path" ]] || { echo "ERROR: file not found: $json_path" >&2; exit 3; }
    "$PYTHON_BIN" "$VALIDATOR" validate "$json_path"
    ;;
  gate)
    [[ -n "$json_path" && -n "$report_path" ]] || { echo "ERROR: need json and report path" >&2; exit 4; }
    [[ -f "$json_path" ]] || { echo "ERROR: file not found: $json_path" >&2; exit 5; }
    "$PYTHON_BIN" "$QUALITY_GATE" --storyworld "$json_path" --strict --report-out "$report_path"
    ;;
  *)
    echo "usage: $0 <pre|validate|gate> [json] [report]" >&2
    exit 1
    ;;
esac
