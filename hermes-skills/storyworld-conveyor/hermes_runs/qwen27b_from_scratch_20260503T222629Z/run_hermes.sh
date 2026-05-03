#!/usr/bin/env bash
set -o pipefail
cd "$HOME/projects/GPTStoryworld"
run_dir="hermes-skills/storyworld-conveyor/hermes_runs/qwen27b_from_scratch_20260503T222629Z"
echo "=== Hermes Qwen 27B from-scratch storyworld run ==="
echo "started_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "pwd=$(pwd)"
echo "model_status=$(curl -s --max-time 5 http://127.0.0.1:8081/v1/models || true)"
echo "prompt_file=$run_dir/prompt.txt"
echo "--- hermes invocation ---"
hermes chat --query "$(cat "$run_dir/prompt.txt")" --skills storyworld-conveyor-runner --yolo --max-turns 45 --source hackathon-qwen27b-from-scratch
rc=$?
echo "--- hermes exit rc=$rc ---"
echo "ended_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
exit $rc