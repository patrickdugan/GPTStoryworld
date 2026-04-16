# Storyworld Reasoning Benchmark v1

This folder publishes a small Trinity-oriented benchmark for moral-reasoning style.
Current release scope:
- Trinity-only reasoning traces on the bioethics escalation storyworld
- no secret-ending play env data yet
- no other model families included in the published benchmark table yet

Primary dataset:
- [Trinity bioethics v2 vs v3 export](./trinity_bioethics_v2_v3/README.md)
- [Case study paper](./trinity_bioethics_v2_v3/paper.md)
- [Paper draft](./trinity_bioethics_v2_v3/paper_draft.md)
- [Representative snippets](./trinity_bioethics_v2_v3/snippets.md)
- [Comparison table](./trinity_bioethics_v2_v3/comparison_table.csv)

What it measures:
- stakeholder breadth
- tradeoff depth
- reversibility
- uncertainty
- legitimacy

Important note:
- These are heuristic 1-5 rubric scores derived directly from Trinity pick-time reasoning text.
- They are intended for comparing reasoning style across runs, not for judging correctness.
- The published plots live under `trinity_bioethics_v2_v3/figures/`.

Suggested use:
- compare models on the same storyworld and prompt structure
- use the benchmark as a vendor-neutral reasoning eval for Arcee or other frontier models against `o3-mini`
- inspect the per-trace `reasoning_evidence` field for examples
- use `summary.json` for run-level comparison and `benchmark.csv` for tabular analysis
- use `paper.md` and the figures as the starting point for a case-study writeup
- use `paper_draft.md` if you want a more conventional paper structure
- add the secret-ending play env, an `o3-mini` contrast run, an Arcee model run, and a Codex webhook frontier-model run as follow-on benchmark slices
