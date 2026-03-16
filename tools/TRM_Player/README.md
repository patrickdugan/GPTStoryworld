# TRM_Player Harness

Structured option-selection benchmark harness (TRM-style), parallel to `tools/LLM_Player`.

Use this when you want policy-style behavior:
- input: encounter text + local story context + state snapshot + available options
- output: ranked options and chosen option (top-1 by default, top-k logged)

It supports:
- baseline Qwen 1.7B Instruct
- Claude-constitution QLoRA adapter on the same base model

## Quick Start

```powershell
python tools/TRM_Player/run_trm_player_bench.py `
  --storyworld C:\projects\GPTStoryworld\storyworlds\2-23-2026-batch\adapt_casablanca_crossroads_at_ricks_v2_1940s_textpass.json `
  --base-model-path D:\Research_Engine\Qwen_Storyworld\cache\models\Qwen3-1.7B `
  --adapter-path D:\Research_Engine\Qwen_Storyworld\adapters\claude_constitution_q_lora `
  --output-root D:\Research_Engine\Storyworld_LLM_Plays `
  --max-encounters 93 `
  --top-k 3 `
  --context-window 4
```

## Dry Run

```powershell
python tools/TRM_Player/run_trm_player_bench.py `
  --storyworld C:\projects\GPTStoryworld\storyworlds\2-23-2026-batch\adapt_casablanca_crossroads_at_ricks_v2_1940s_textpass.json `
  --base-model-path D:\dummy\qwen `
  --adapter-path D:\dummy\adapter `
  --dry-run
```

## Output Layout

- `<output_root>\<run_id>\meta\run_config.json`
- `<output_root>\<run_id>\prompts\encounter_cards.jsonl`
- `<output_root>\<run_id>\baseline_qwen_1_7b_trm\decisions.jsonl`
- `<output_root>\<run_id>\baseline_qwen_1_7b_trm\summary.json`
- `<output_root>\<run_id>\adapter_claude_constitution_qlora_trm\decisions.jsonl`
- `<output_root>\<run_id>\adapter_claude_constitution_qlora_trm\summary.json`
- `<output_root>\<run_id>\comparisons\comparison_summary.json`
- `<output_root>\<run_id>\comparisons\bench_rows.jsonl`
- `<output_root>\<run_id>\manifest.json`

## Notes

- This harness performs option scoring (policy-like), not open-ended response generation.
- State snapshot is derived from storyworld initial character property values (depth-0 authored properties).

## Secret Ending Competition (Verifier Env)

Use `run_trm_verifier_gauntlet.py` to run N secret-ending attempts with context and verifier scoring:

```powershell
python tools/TRM_Player/run_trm_verifier_gauntlet.py `
  --storyworld C:\projects\GPTStoryworld\storyworlds\2-23-2026-batch\adapt_casablanca_crossroads_at_ricks_v1.json `
  --base-model-path D:\Research_Engine\Qwen_Storyworld\cache\models\Qwen3-1.7B `
  --adapter-path D:\Research_Engine\Qwen_Storyworld\adapters\claude_constitution_q_lora `
  --secret-attempts 12 `
  --context-window 6 `
  --secret-explore-top-k 3
```

Outputs include:
- `gauntlet_manifest.json`
- `verifier_bundle/` results from `verifiers_envs/run_all_verifiers.py`
- `attempts.json` with N playthroughs for needle-in-haystack scoring.
