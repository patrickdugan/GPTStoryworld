# LLM_Player Harness

Local benchmark harness for storyworld encounter prompts.

Primary use case:
- Baseline: Qwen 1.7B Instruct
- Adapter: Claude-constitution themed QLoRA (PEFT adapter on top of same base)

The harness:
- Reads encounter text from a storyworld JSON
- Builds one prompt per encounter
- Runs each prompt through baseline and adapter conditions
- Logs per-encounter outputs and run summaries
- Exports all artifacts to subfolders under:
  `D:\Research_Engine\Storyworld_LLM_Plays`

## Quick Start

```powershell
python tools/LLM_Player/run_llm_player_bench.py `
  --storyworld C:\projects\GPTStoryworld\storyworlds\2-23-2026-batch\adapt_casablanca_crossroads_at_ricks_v2_1940s_textpass.json `
  --base-model-path D:\Research_Engine\Qwen_Storyworld\cache\models\Qwen3-1.7B `
  --adapter-path D:\Research_Engine\Qwen_Storyworld\adapters\claude_constitution_q_lora `
  --output-root D:\Research_Engine\Storyworld_LLM_Plays `
  --max-encounters 60 `
  --max-new-tokens 180 `
  --temperature 0.2 `
  --top-p 0.9
```

For small local models, the safer defaults are now:
- `--selection-mode generate_pick`
- `--first-click-mode generate_pick`
- `--cross-play-memory-mode summary`

Avoid `score_all` plus `full_diary` on long playthroughs unless you explicitly want the extra latency.

## Dry Run (No Model Load)

```powershell
python tools/LLM_Player/run_llm_player_bench.py `
  --storyworld C:\projects\GPTStoryworld\storyworlds\2-23-2026-batch\adapt_casablanca_crossroads_at_ricks_v2_1940s_textpass.json `
  --base-model-path D:\dummy\qwen `
  --adapter-path D:\dummy\adapter `
  --dry-run
```

## Output Layout

For each run, the harness writes:

- `<output_root>\<run_id>\meta\run_config.json`
- `<output_root>\<run_id>\prompts\encounter_prompts.jsonl`
- `<output_root>\<run_id>\baseline_qwen_1_7b\generations.jsonl`
- `<output_root>\<run_id>\baseline_qwen_1_7b\summary.json`
- `<output_root>\<run_id>\adapter_claude_constitution_qlora\generations.jsonl`
- `<output_root>\<run_id>\adapter_claude_constitution_qlora\summary.json`
- `<output_root>\<run_id>\comparisons\comparison_summary.json`
- `<output_root>\<run_id>\comparisons\bench_rows.jsonl` (TRM-ready side-by-side rows)
- `<output_root>\<run_id>\manifest.json`

## Dependencies

- `transformers`
- `torch`
- `peft` (only required when `--adapter-path` is used)
