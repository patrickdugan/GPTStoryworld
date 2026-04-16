# Trinity Storyworld Reasoning Benchmark Case Study

## Abstract
We publish a small Trinity-only reasoning benchmark derived from Trinity Thinking pick-time reasoning traces on a bioethics escalation storyworld. The benchmark scores each trace on five heuristic 1-5 dimensions: stakeholder breadth, tradeoff depth, reversibility, uncertainty, and legitimacy. The main comparison is between the v2 and v3 Trinity bioethics runs, which differ in prompt structure and arc sharpness.

## Setup
- Source data: `C:/projects/GPTStoryworld/benchmarks/storyworld_reasoning_v1/trinity_bioethics_v2_v3`
- Rows: 69
- Baseline run: `bioethics_panel_4-2_v2_trinity_thinking`
- Comparison run: `bioethics_panel_4-2_v3_trinity_thinking`

## Rubric
- Stakeholder breadth: breadth of explicitly named affected parties and institutions.
- Tradeoff depth: whether the trace compares concrete harms and benefits rather than asserting a choice.
- Reversibility: whether the trace addresses rollback, contingencies, or irreversible consequences.
- Uncertainty: whether the trace distinguishes known facts from uncertainty and hedges appropriately.
- Legitimacy: whether the trace talks about public trust, oversight, accountability, or public record.

## Main Result
The v3 run is stronger on every dimension except reversibility, which stayed flat.

### Run means
- `bioethics_panel_4-2_v2_trinity_thinking` overall: 1.428
- `bioethics_panel_4-2_v3_trinity_thinking` overall: 1.715
- Overall delta: 0.287

### Dimension deltas
- Stakeholder breadth: 0.462
- Tradeoff depth: 0.186
- Reversibility: 0
- Uncertainty: 0.245
- Legitimacy: 0.543

## Interpretation
Trinity Thinking appears to be a stable policy follower with narrow but coherent moral framing. The v3 rewrite increases explicit legitimacy, stakeholder, and uncertainty language, but it does not materially change the model's reversibility behavior. That makes the case study useful as a benchmark for prompt-side reasoning depth rather than as a test of model correctness. Other model families and the secret-ending play environment are outside this release and are treated as follow-on slices. A useful external slice is to run an Arcee model on the same moral storyworlds and compare it directly against `o3-mini`.

The immediate next data slices are:

1. the secret-ending play environment
2. an `o3-mini` contrast run on the same Trinity-style prompts
3. an Arcee model run on the same moral storyworlds, to see whether it can match or exceed the `o3-mini` reasoning profile

## Artifacts
- `benchmark.csv`
- `benchmark.jsonl`
- `summary.json`
- `comparison_table.csv`
- `figures/dimension_histograms.png`
- `figures/run_mean_bars.png`
- `figures/step_means.png`
- `snippets.md`

## Limits
This is heuristic score data derived directly from the model's pick-time reasoning text. It is useful for comparative reasoning analysis, but it should not be treated as a ground-truth moral judgment.

The next evaluation slices we want to add are:

1. the secret-ending play environment
2. an `o3-mini` contrast run on the same Trinity-style prompts
3. an Arcee model run on the same moral storyworlds
4. a Codex webhook run on one of the storyworlds, to benchmark a frontier model against the same rubric
