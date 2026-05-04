# Tiny Master Control Planner Baseline

This is a first executable receipt for the master control-plane idea.

## Inputs

- Corpus: `hermes-skills/storyworld-conveyor/trm_corpus/master_control_planner_seed/`
- Train rows: `900`
- Validation rows: `99`
- Split: episode-disjoint
- Model tier encoded in corpus: `9B_Q4`
- Context budget: `8192`

## Model

The baseline is a tiny multinomial Naive Bayes next-role classifier:

```text
global_state + available_roles -> next_trm_role
```

It is intentionally lightweight. This is a smoke receipt, not the final TRM.

## Result

- Row accuracy: `13/99 = 0.1313`
- Exact episode sequence rate: `0/11 = 0.0`

The low score is useful. After removing direct role-order leakage, the current synthetic corpus does not yet contain enough adaptive signal for a real master planner. It mostly proves the data shape and training/eval loop.

## Interpretation

The existing 9-TRM seed corpus is good for role-local control. It is not yet sufficient for a master planner that chooses among roles under changing conditions.

The next data pool should append real conveyor/Hermes histories:

- skipped roles
- repeated repair roles
- context overflow recoveries
- parse failures
- no-op vetoes
- reader-harness failures
- successful secret-route repairs
- before/after verifier deltas

That is the dataset that should teach the master planner.
