# Trinity Storyworld Reasoning Benchmark: A Bioethics Trace Case Study

## Abstract
We present a compact Trinity-only benchmark for comparing reasoning style in storyworld play traces. The benchmark is derived from Trinity Thinking runs on a bioethics escalation storyworld and scores each pick-time reasoning trace on five heuristic dimensions: stakeholder breadth, tradeoff depth, reversibility, uncertainty, and legitimacy. We compare two prompt variants, v2 and v3, and find that v3 yields broader stakeholder framing, more explicit legitimacy language, and somewhat stronger tradeoff and uncertainty handling, while reversibility remains unchanged.

## Introduction
Reasoning benchmarks often focus on answer accuracy or external judgments. That misses a different property that matters in moral and constitutional storyworlds: the shape of the model's own deliberation. This case study treats the model's pick-time reasoning text as the object of analysis and asks a narrower question: does the reasoning itself become broader, more explicit, and more institutionally aware when the storyworld prompt is sharpened?

The data here comes from Trinity Thinking playthroughs on two versions of the same bioethics world. Both versions use the same broad moral frame, but the v3 version makes the choice structure and the legitimacy stakes more explicit.
This release does not yet include other model families or the secret-ending play environment; those are the next planned slices for the benchmark suite.

## Related Work
This benchmark sits between three common evaluation styles:

- outcome-oriented benchmarks that score the final answer or action
- judge-based evaluations that ask a separate model to grade a completion
- trace-oriented analyses that inspect the model's own reasoning text

The present case study follows the third path. It is closer to a reasoning-process audit than to a classical accuracy benchmark. That matters in storyworld settings because the output is not a single answer, but a sequence of constrained moral choices whose justification style is itself part of the object of study.

The next contrast baseline for this suite is `o3-mini` on the same prompt structure, and a useful external slice is an Arcee model run on the same task. A Codex webhook run of one of the storyworlds would add a frontier-model reference point. Those comparisons are follow-on releases rather than part of the table below.

## Benchmark Design
The benchmark scores each reasoning trace from 1 to 5 on five dimensions:

- stakeholder breadth: how many affected parties or institutions are explicitly named
- tradeoff depth: whether the trace compares concrete harms and benefits
- reversibility: whether it addresses rollback, contingency, or irreversibility
- uncertainty: whether it distinguishes facts from guesses or hedges appropriately
- legitimacy: whether it invokes public trust, oversight, accountability, or public record

The scoring is heuristic and text-based. It is designed for comparative analysis of reasoning style, not for ground-truth moral grading.

### Rubric Rules
The published scorer uses the pick-time reasoning text only. It does not consume the prompt body, the storyworld scene text, or the reaction payload. Each dimension is scored by phrase-trigger rules:

- stakeholder breadth rises when the trace names more affected parties or institutions
- tradeoff depth rises when the trace compares alternatives or uses explicit tradeoff language
- reversibility rises when the trace mentions rollback, contingency, revisiting, or undoing
- uncertainty rises when the trace acknowledges unknowns, limits, or conditional reasoning
- legitimacy rises when the trace names public trust, oversight, accountability, or the public record

The intent is not to perfectly measure moral quality. The intent is to create a stable, inspectable proxy for reasoning breadth that can be reproduced across runs.

## Data
We analyzed 69 Trinity play traces:

- v2 run: 36 traces
- v3 run: 33 traces

Each row in the published benchmark contains:

- the run label
- encounter and step identifiers
- the selected option id and text
- the extracted reasoning text
- per-dimension scores
- a short evidence payload showing which phrases triggered each dimension score

## Method
The published benchmark is built from the model's pick-time reasoning text rather than the full story prompt. This matters because the prompts are intentionally rich and would otherwise inflate the scores with storyworld scaffolding. Using the reasoning text only makes the benchmark more reflective of the model's own deliberative style.

In implementation terms, the scorer lowercases the pick-time trace text, applies a small phrase-trigger rubric for each dimension, maps trigger counts to integer scores on a 1-5 scale, and averages the five dimensions into an overall score. That makes the export deterministic and easy to reproduce, while still surfacing differences in reasoning breadth and institutional awareness.

The score export was generated into:

- `benchmark.jsonl`
- `benchmark.csv`
- `summary.json`

The case-study assets also include:

- `figures/dimension_histograms.png`
- `figures/run_mean_bars.png`
- `figures/step_means.png`
- `snippets.md`
- `comparison_table.csv`

## Results
The v3 run is stronger on every tracked dimension except reversibility, which stays flat.

### Aggregate means
- v2 overall score: 1.428
- v3 overall score: 1.715
- delta: +0.287

### Dimension deltas
- stakeholder breadth: +0.462
- tradeoff depth: +0.186
- reversibility: +0.000
- uncertainty: +0.245
- legitimacy: +0.543

### Table 1. Run Summary
| Run | Rows | Overall | Stakeholder | Tradeoff | Reversibility | Uncertainty | Legitimacy |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| v2 | 36 | 1.428 | 2.417 | 1.056 | 1.000 | 1.028 | 1.639 |
| v3 | 33 | 1.715 | 2.879 | 1.242 | 1.000 | 1.273 | 2.182 |

### Table 2. Comparison
| Metric | Delta |
| --- | ---: |
| Overall | +0.287 |
| Stakeholder breadth | +0.462 |
| Tradeoff depth | +0.186 |
| Reversibility | +0.000 |
| Uncertainty | +0.245 |
| Legitimacy | +0.543 |

## Interpretation
Trinity Thinking appears to operate as a stable policy follower with coherent but narrow moral framing. The v3 prompt variant pushes the model to mention more stakeholders and more institutional stakes, and it slightly improves tradeoff and uncertainty language. The most visible shift is legitimacy: v3 more often refers to trust, oversight, accountability, or public record.

That said, Trinity does not suddenly become a deep pluralist deliberator. The reversibility dimension remains flat, and the model still favors conservative closure-oriented moves. The benchmark therefore measures a meaningful but bounded improvement in reasoning style rather than a wholesale change in moral strategy.

## Discussion
This case study is useful for at least three reasons:

1. It captures reasoning style directly from the model rather than from an external judge.
2. It distinguishes prompt-driven structure from model-intrinsic deliberative breadth.
3. It produces a compact, publishable artifact set with both quantitative summaries and qualitative trace examples.

For the broader research agenda, the result suggests that storyworld design can function as a controllable lens on reasoning style. Small prompt changes can materially alter what the model says it is weighing, even when the chosen actions remain conservative.

The immediate next data slices to add are:

1. the secret-ending play environment, to test whether hidden-branch topology changes reasoning breadth
2. an `o3-mini` contrast run on the same Trinity-style prompts, to compare depth-first reasoning against Trinity's narrower policy-following style
3. an Arcee model run on the same moral storyworlds, to see whether it can match or exceed the `o3-mini` reasoning profile
4. a Codex webhook run on one of the storyworlds, to benchmark a frontier model against the same rubric

## Figure Captions
- Figure 1, `dimension_histograms.png`: Overlaid histograms of the five rubric dimensions plus the overall score for v2 and v3.
- Figure 2, `run_mean_bars.png`: Side-by-side mean scores for each dimension, comparing v2 and v3.
- Figure 3, `step_means.png`: Mean overall reasoning score across the playthrough arc, showing how the two runs evolve over step index.

## Limitations
This benchmark is intentionally heuristic.

- It uses simple rubric-based scoring rather than human annotation or model-based judgment.
- It is sensitive to the wording of the storyworld prompts and to the trace format.
- It should not be interpreted as a ground-truth moral capability score.
- The current release covers only one model family and one storyworld family.

## Conclusion
The Trinity bioethics case study shows that a storyworld benchmark can surface differences in reasoning style even when the model's final action policy remains conservative. V3 is the better reasoning trace set by this rubric, mainly because it expands stakeholder and legitimacy language without changing the underlying reversibility pattern.

## Artifacts
- `benchmark.csv`
- `benchmark.jsonl`
- `summary.json`
- `comparison_table.csv`
- `results_table.md`
- `results_table.tex`
- `snippets.md`
- `figures/dimension_histograms.png`
- `figures/run_mean_bars.png`
- `figures/step_means.png`
