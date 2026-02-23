# QLoraExamples

This folder defines the canonical derived-example format for small-model QLoRA training.

## Objective
Turn SWMD encounters into repeated transformation tasks so adapters learn stable compilation behavior, not prose style drift.

## Canonical Schema
- Output schema for compile/repair/edit tasks: `SWMD-MICRO-0.1`
- Keep keys stable and ordered:
  - `schema`
  - `world_id`
  - `encounter_id`
  - `turn_span`
  - `agents`
  - `state_vars`
  - `norms`
  - `actions`
  - `transitions`
  - `source_block`

## Task Mix (v1 default)
- `compile`: 40%
- `compression`: 25%
- `repair`: 20%
- `targeted_edit`: 15%

## Build Command
```powershell
python C:/projects/GPTStoryworld/codex-skills/small-storyworld-builder/scripts/swmd_build_qlora_examples.py `
  --swmd-glob "storyworlds/2-23-2026-batch/**/*.swmd.min.md" `
  --out-dir "storyworlds/2-23-2026-batch/QLoraExamples" `
  --max-total-encounters 120 `
  --examples-per-encounter 10 `
  --val-ratio 0.05
```

## Outputs
- `train.jsonl`, `val.jsonl`: instruction/input/output rows.
- `train_messages.jsonl`, `val_messages.jsonl`: chat-style rows for SFT pipelines.
- `stats.json`: counts and task histogram.

## Integration
`swmd_mcp_phase_pipeline.py` can consume `train.jsonl` for few-shot scaffolding:
- `--qlora-examples-jsonl <.../train.jsonl>`
- `--fewshot-count 1` (or `2` if budget permits)

For expanded hard-negative training sets:
- Build with `swmd_expand_qlora_hard_negatives.py` to produce `aug_train.jsonl`/`aug_val.jsonl`.
- Prefer `aug_train.jsonl` in low-context adapter runs where MCP offloads world-scale context.
