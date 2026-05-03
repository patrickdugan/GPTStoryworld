#!/usr/bin/env bash
set -euo pipefail

repo="/home/snacksack/projects/GPTStoryworld"
run_id="qwen27b_romeo_sanaa_40enc_20260503T230325Z"
run_dir="$repo/hermes-skills/storyworld-conveyor/hermes_runs/$run_id"

cd "$repo"
/home/snacksack/.local/bin/hermes chat \
  --query "$(cat "$run_dir/prompt_chunk_02_retry.txt")" \
  --ignore-rules \
  --max-turns 1 \
  --source "hackathon-romeo-sanaa-chunk-2-retry"
