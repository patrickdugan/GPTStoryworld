---
name: pure-trm-trainer
description: Build and run pure TRM controller training workflows under Hermes, including corpus assembly from TRM play logs, event logs, reasoning traces, and normalized JSONL datasets. Use when Codex needs to curate cross-environment controller data, turn logs into conductor-style training corpora, launch a Hermes-wrapped trainer, or prepare a skills-hub-ready TRM training workflow that stays separate from prose or adapter authoring.
---

# Pure TRM Trainer

Use this skill to keep TRM training narrow: controller behavior, transition choice, constraint satisfaction, verifier logic, and rebalance reasoning, not prose generation.

Start from normalized `state/tools/action` records whenever possible. If the source data is raw, convert it once into that shape before training.

## Workflow

1. Decide the target controller behavior.
   - Use TRM for topology, action selection, constraint satisfaction, rebalancing, and verifier-style reasoning.
   - Do not mix in story prose quality unless the user explicitly wants a hybrid model.
2. Arrange the corpus.
   - Read [data-arrangement.md](./references/data-arrangement.md) for source selection and split rules.
   - Read [source-patterns.md](./references/source-patterns.md) for concrete source recipes.
3. Build a normalized corpus.
   - Canonical builder:
     - `python hermes-skills/storyworld-conveyor/scripts/build_trm_training_corpus.py --config hermes-skills/storyworld-conveyor/sample_data/trm_training_corpus_spec.sample.json`
4. Launch Hermes-wrapped training.
   - Canonical runner:
     - `python hermes-skills/storyworld-conveyor/scripts/run_trm_trainer_hermes.py --config hermes-skills/storyworld-conveyor/sample_data/trm_trainer_hermes_safe.json`
5. Inspect artifacts.
   - Check `prepare_corpus/manifest.json`
   - Check `trainer_config.resolved.json`
   - Check `launch_trainer/manifest.json`
   - Check final `summary.json`

## Corpus Rules

- Prefer diverse environments over repeated near-duplicates from one environment.
- Keep train/validation splits separated by environment or run when possible, not just by row.
- Preserve source metadata in `meta` so later audits can trace bad behavior back to a world, run, or prompt family.
- Treat reasoning traces as supervision only when they encode decision-relevant state, candidate actions, or critique. Skip decorative chain-of-thought.
- Use Monte Carlo, verifier, or transition metrics to decide what the controller should improve; do not guess from surface prose.

## Hermes Runner

Use [run_trm_trainer_hermes.py](../storyworld-conveyor/scripts/run_trm_trainer_hermes.py) for the full Hermes path. It performs three stages:

- `prepare_corpus`
- `prepare_config`
- `launch_trainer`

Use [run_hrm_trainer_hermes.py](../storyworld-conveyor/scripts/run_hrm_trainer_hermes.py) only when the user already has a clean conductor dataset and does not need corpus assembly.

## Source Types

Supported directly by the corpus builder:

- `trm_play_root`
  - Expects AICOO/TRM setup output with `worlds/*/trm_traces.jsonl`
  - Converts play logs into `state/tools/action`
- `jsonl`
  - `mode=normalized`: rows already contain `state`, `tools`, `action`
  - `mode=reasoning_trace`: build `state` from selected fields and map action/tool fields explicitly

## Hard Rules

- Keep this skill pure TRM. If the user wants prose, authoring adapters, or encounter block generation, switch to another skill or a separate workflow.
- Do not claim a run succeeded unless the Hermes stage manifests say `completed`.
- Do not train on mixed-quality logs without preserving source metadata.
- Do not let validation rows come from the same environment slice used for training if the task is cross-environment generalization.
- Do not silently strip invalid rows; record counts in the corpus manifest.

## References

- Data curation guide: [data-arrangement.md](./references/data-arrangement.md)
- Source recipes: [source-patterns.md](./references/source-patterns.md)

## Example Requests

- "Use pure-trm-trainer to turn these TRM play logs into a cross-world controller dataset."
- "Build a Hermes-safe TRM training run from verifier traces and held-out validation worlds."
- "Prepare a hub-ready pure TRM workflow that learns from logs and reasoning traces without mixing in prose generation."
