# QLoraExamples (Batch 2-23-2026)

Derived supervised dataset for small-model adapter training from SWMD encounter blocks.

## Files
- `train.jsonl`: instruction/input/output rows.
- `val.jsonl`: held-out validation rows.
- `train_messages.jsonl`: chat-format training rows.
- `val_messages.jsonl`: chat-format validation rows.
- `stats.json`: generation parameters and histogram.
- `aug_train.jsonl`, `aug_val.jsonl`: hard-negative expanded corpus.
- `aug_train_messages.jsonl`, `aug_val_messages.jsonl`: chat-format expanded corpus.
- `aug_stats.json`: expansion stats.

## Current build
- Encounters sampled: `120`
- Examples per encounter: `10`
- Total rows: `1200`
- Task mix:
  - `compile`: 480 (40%)
  - `compression`: 300 (25%)
  - `repair`: 240 (20%)
  - `targeted_edit`: 180 (15%)

## Canonical output schema
- `SWMD-MICRO-0.1`
- Keep key structure stable across all outputs.

## Rebuild command
```powershell
python C:/projects/GPTStoryworld/codex-skills/small-storyworld-builder/scripts/swmd_build_qlora_examples.py `
  --swmd-glob "storyworlds/2-23-2026-batch/*.swmd.min.md" `
  --out-dir "storyworlds/2-23-2026-batch/QLoraExamples" `
  --max-total-encounters 120 `
  --examples-per-encounter 10 `
  --val-ratio 0.05
```

## Hard-negative expansion to ~2k
```powershell
python C:/projects/GPTStoryworld/codex-skills/small-storyworld-builder/scripts/swmd_expand_qlora_hard_negatives.py `
  --in-dir "storyworlds/2-23-2026-batch/QLoraExamples" `
  --target-total 2000 `
  --out-prefix "aug"
```
