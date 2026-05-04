# Snacksack Small-Model Builder Results - 2026-05-04

Remote host: `snacksack-MS-7D32`

Working tree: `/home/snacksack/projects/GPTStoryworld`

Live endpoint during this run:

- `http://127.0.0.1:8081/v1`
- `Qwen3.5-27B.Q4_K_M.gguf`
- `n_ctx=32768`
- GPU memory snapshot before teacher calls: `19183 MiB used`, `4919 MiB free` on a 24 GiB card.

No 9B or 3B endpoint was live. The 27B run should be treated as a bounded teacher-data run, not as a small-model result.

## Native Schema Receipt

Run:

- `hermes-skills/storyworld-conveyor/trm_corpus/master_control_planner_native_snacksack_001/run_summary.json`

Result:

- Planner: `native`
- Worlds: `5`
- Iterations: `10`
- Oracle rows: `20`
- Planner agreement: `20/20 = 1.0`
- Context budget: `32768`
- Objective families: `fit_context_budget`, `repair_reader_semantics`, `diversify_effect_scripts`, `repair_schema_connectivity`

This expanded the previous native-schema receipt from a 16-row local slice to a 20-row Snacksack slice with an additional schema-connectivity objective family.

## Score Lift From Native Receipt

Baseline Snacksack scorecard:

- `benchmarks/storyworld_builder_small_model/runs/snacksack_score_001/scorecard.md` on Snacksack

Native-receipt scorecard copied locally:

- `benchmarks/storyworld_builder_small_model/runs/snacksack_score_native_001/scorecard.md`

Observed score changes after adding the native receipt to the manifest:

| Run | Before | After native receipt | Delta |
|---|---:|---:|---:|
| `snacksack_romeo_juliet_spooltight` | `0.8127` | `0.9287` | `+0.1160` |
| `snacksack_scarlet_letter_focus5` | `0.8127` | `0.9287` | `+0.1160` |
| `snacksack_macbeth_validated` | `0.8612` | `0.9112` | `+0.0500` |
| `snacksack_politburo_shehada` | `0.7642` | `0.8802` | `+0.1160` |
| `snacksack_first_and_last_men` | `0.7473` | `0.8633` | `+0.1160` |

Interpretation: the largest immediate benchmark lift is not prose generation. It is making native control-plane evidence explicit: MCP readiness plus native schema agreement.

## 27B Teacher Campaign

Strict bounded teacher campaign:

- `benchmarks/storyworld_builder_small_model/runs/snacksack_campaign_native_27b_teacher_strict_001/campaign_summary.md`
- `benchmarks/storyworld_builder_small_model/runs/snacksack_campaign_native_27b_teacher_strict_001/model_plan_extraction_summary.json`

Result:

- Jobs: `5`
- Model calls: `5`
- Extractable model plans: `5/5`
- Schema-key-valid plans: `5/5`
- JSON-only contract pass: `0/5`

The teacher produced usable plans, but still emitted analysis text before the JSON. The extractor records this as contract noncompliance while preserving the plan as teacher data.

## Materialized Prose Candidate Lift

Strict materialized candidates:

- `benchmarks/storyworld_builder_small_model/runs/snacksack_materialized_27b_teacher_native_score_001/scorecard.md`

Observed deltas:

| Run | Native score | Materialized prose candidate | Delta |
|---|---:|---:|---:|
| `snacksack_macbeth_validated` | `0.9112` | `0.9131` | `+0.0019` |
| `snacksack_politburo_shehada` | `0.8802` | `0.8807` | `+0.0005` |
| `snacksack_first_and_last_men` | `0.8633` | `0.8635` | `+0.0002` |

Wide materialized candidates:

- `benchmarks/storyworld_builder_small_model/runs/snacksack_materialized_27b_teacher_wide_native_score_001/scorecard.md`

Observed deltas:

| Run | Native score | Wide prose candidate | Delta |
|---|---:|---:|---:|
| `snacksack_macbeth_validated` | `0.9112` | `0.9112` | `+0.0000` |
| `snacksack_politburo_shehada` | `0.8802` | `0.8808` | `+0.0006` |
| `snacksack_first_and_last_men` | `0.8633` | `0.8655` | `+0.0022` |

Interpretation: bounded prose rewrites are useful teacher data but do not move the current score much unless we apply many more local rewrites or improve the scorer/materializer target. The native routing/control-plane receipt produces the main measurable lift tonight.

## Next Experiment

Run a real 9B/3B endpoint after freeing VRAM or restarting with the 9B model, then reuse the same campaign packets:

```bash
python3 benchmarks/storyworld_builder_small_model/run_small_model_builder_campaign.py \
  --scorecard benchmarks/storyworld_builder_small_model/runs/snacksack_score_native_001/scorecard.json \
  --out-dir benchmarks/storyworld_builder_small_model/runs/snacksack_campaign_native_9b_001 \
  --max-jobs 5 \
  --max-cards 10 \
  --packet-token-budget 5200 \
  --call-model \
  --base-url http://127.0.0.1:8084/v1 \
  --model Qwen_Qwen3.5-9B-Q4_K_M.gguf \
  --timeout 300 \
  --max-response-tokens 3600
```

Do not start 9B while 27B is resident unless the 27B process is intentionally stopped first.
