#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "usage: $0 CHUNK_NUMBER" >&2
  exit 2
fi

chunk="$1"
repo="/home/snacksack/projects/GPTStoryworld"
run_id="qwen27b_romeo_sanaa_40enc_20260503T230325Z"
run_dir="$repo/hermes-skills/storyworld-conveyor/hermes_runs/$run_id"
prompt="$run_dir/prompt_chunk_$(printf '%02d' "$chunk").txt"

cd "$repo"
/home/snacksack/.local/bin/hermes chat \
  --query "$(cat "$prompt")" \
  --ignore-rules \
  --max-turns 1 \
  --source "hackathon-romeo-sanaa-chunk-$chunk"
