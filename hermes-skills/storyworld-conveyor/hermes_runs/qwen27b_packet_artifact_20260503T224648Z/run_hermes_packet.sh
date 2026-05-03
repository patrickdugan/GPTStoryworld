#!/usr/bin/env bash
set -euo pipefail

repo="/home/snacksack/projects/GPTStoryworld"
run_id="qwen27b_packet_artifact_20260503T224648Z"
run_dir="$repo/hermes-skills/storyworld-conveyor/hermes_runs/$run_id"

cd "$repo"
/home/snacksack/.local/bin/hermes chat \
  --query "$(cat "$run_dir/prompt.txt")" \
  --ignore-rules \
  --max-turns 1 \
  --source hackathon-qwen27b-packet
