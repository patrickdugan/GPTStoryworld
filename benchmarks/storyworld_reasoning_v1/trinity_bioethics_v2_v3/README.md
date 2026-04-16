# Storyworld Reasoning Benchmark v1

This benchmark is a rubric-based export of moral-reasoning traces from the storyworld playthroughs.
It scores each trace on five 1-5 dimensions:

- stakeholder breadth
- tradeoff depth
- reversibility
- uncertainty
- legitimacy

The dataset is derived from Trinity Thinking traces and is intended for model comparison on moral reasoning style, not for judging correctness.

## Included Runs
- `bioethics_panel_4-2_v2_trinity_thinking`: 36 rows, overall mean 1.428
- `bioethics_panel_4-2_v3_trinity_thinking`: 33 rows, overall mean 1.715

## Comparison
- Baseline: `bioethics_panel_4-2_v2_trinity_thinking`
- Comparison: `bioethics_panel_4-2_v3_trinity_thinking`
- Overall delta: `+0.287`
- Stakeholder breadth delta: `+0.462`
- Tradeoff depth delta: `+0.186`
- Reversibility delta: `+0.000`
- Uncertainty delta: `+0.245`
- Legitimacy delta: `+0.543`

## Files
- `benchmark.jsonl`: one row per trace
- `benchmark.csv`: flat tabular export
- `summary.json`: aggregated run statistics
