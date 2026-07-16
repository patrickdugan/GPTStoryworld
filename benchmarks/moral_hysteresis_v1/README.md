# Moral Hysteresis

**Moral Hysteresis: How Language Models Revise Blame After a Narrative Twist**

This benchmark measures how internal representations change as successive
sentences revise apparent blame, intent, consent, harm, responsibility, deserved
punishment, forgiveness, and trust. It is a sentence-trajectory instrument, not a
Sweepweave choice world and not a source of normative training labels.

## Current status

| Component | Status |
| --- | --- |
| 15 matched story families, 60 bilingual trajectories | built and validated |
| English draft | built |
| Simplified Chinese translation | built, native-speaker review required |
| 2,880 human rating units | scaffolded, empty |
| Reference Transformers activation harvester | built, no model capture committed |
| Distributed Kimi K2 Thinking capture | external infrastructure required |
| Raw geometry and cross-lingual CKA analysis | built |
| Moral-dimension probes | built, blocked until ratings and reliability pass |
| Dataset license | unresolved; owner decision required before publication |

The checked dataset has five moral-revision mechanisms. Each mechanism has one
independent family in the train, validation, and held-out test split. Every family
has a `reveal_late` path and a `known_early` control containing the exact same six
sentences in a different order and ending with the same summary. Both languages
share event IDs and sentence order within each trajectory.

## Why this extends story geometry

Goodfire's [Meandering on Manifolds](https://www.goodfire.ai/research/stories-in-space)
harvests the last-token activation after each sentence and studies the resulting
trajectory. This benchmark uses that extraction point for moral belief revision
and adds a last-four-token mean robustness capture for language-specific
sentence-final tokenization.

The primary frontier target is a pinned local checkpoint of Kimi K2 Thinking.
Moonshot's [official model card](https://huggingface.co/moonshotai/Kimi-K2-Thinking)
describes a one-trillion-parameter MoE with 61 layers and recommends distributed
inference engines. Goodfire's
[frontier-scale infrastructure account](https://www.goodfire.ai/blog/interpretability-infra-at-frontier-scale)
describes a patched inference server used to harvest Kimi K2 Thinking activations.
The reference script here is suitable only when the selected checkpoint can
return `hidden_states`; an API completion is not internal access.

## Reproduce the checked artifacts

```powershell
python benchmarks/moral_hysteresis_v1/scripts/build_dataset.py
python benchmarks/moral_hysteresis_v1/scripts/validate_dataset.py
python benchmarks/moral_hysteresis_v1/scripts/harvest_activations.py `
  --output-dir artifacts/moral_hysteresis_plan `
  --dry-run
```

Reference capture for a locally loadable, revision-pinned checkpoint:

```powershell
python benchmarks/moral_hysteresis_v1/scripts/harvest_activations.py `
  --model-id <local-path-or-model-id> `
  --revision <immutable-revision> `
  --output-dir artifacts/moral_hysteresis_capture
```

Analyze a conforming capture:

```powershell
python benchmarks/moral_hysteresis_v1/scripts/analyze_activations.py `
  --capture-dir artifacts/moral_hysteresis_capture `
  --output artifacts/moral_hysteresis_analysis.json
```

With the checked empty rating template, the analyzer emits raw geometry and blocks
semantic probes. It permits moral-dimension probes only when every unit has at
least three valid annotators and interval Krippendorff alpha is at least 0.80 for
all eight dimensions. Publication additionally requires named native-speaker and
research-ethics review records.

This repository currently has no root license. The dataset manifest therefore
records `license_status: needs_owner_decision`, and the analyzer treats license
resolution as a publication gate.

See `PROTOCOL.md` for estimands and `CAPTURE_CONTRACT.md` for a distributed
Kimi/Silico handoff.
