# Capability-State Metric

Date: 2026-05-02

Path-prefix scoring is useful for checking whether a run found the intended
route, but it is too brittle as a sole benchmark metric. A different route can
preserve the objective, while a locally high-scoring route can lose the latent
state needed for a secret ending.

This metric scores the run without comparing it to `oracle_path`.

## Metric Components

- `local_decision_quality`: mean option-quality score from the eval contract.
- `commitment_coverage`: whether the run accumulated the commitments required by
  the world categories, such as evidence, memory, constraint, recovery, planning,
  deception-checking, coordination, and frontier hardening commitments.
- `anti_commitment_debt`: accumulated anti-commitments, contradictions, and proxy
  polish debt.
- `decoy_susceptibility`: fraction of choices that hit known decoy surfaces such
  as uncanny-valley polish, proxy repair, secret leakage, or panic-freeze traps.
- `hazard_avoidance`: inverse of decoy and high-risk choice rate.
- `secret_gate_readiness`: route-independent estimate of whether the run has the
  state needed for a high-value or secret ending.
- `capability_composite`: weighted blend of quality, coverage, hazard avoidance,
  secret-readiness, and non-oracle consistency.

## Dry Semantic Baseline Snapshot

| Tier | Old composite | Capability composite | Quality | Coverage | Anti-debt | Decoy rate | Secret readiness |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| T1 | 0.9176 | 0.8698 | 0.8410 | 0.8333 | 0.3333 | 0.0000 | 0.8411 |
| T2 | 0.9612 | 0.9342 | 0.9369 | 0.8000 | 0.0000 | 0.0000 | 1.0000 |
| T3 | 0.9006 | 0.8580 | 0.7905 | 0.8571 | 0.4286 | 0.0000 | 0.7934 |
| T4 | 0.9209 | 0.8306 | 0.7967 | 0.6667 | 0.2222 | 0.0000 | 0.8846 |
| T5 hardened | 0.7908 | 0.6299 | 0.5570 | 0.7000 | 1.0000 | 0.3333 | 0.4180 |

The useful result is T5 hardened: the old composite remains moderately high
because the run keeps making legal locally plausible choices, but the
capability-state metric catches the actual failure mode: high anti-commitment
debt, repeated decoy hits, and weak secret-gate readiness.

## Tool

Tracked scorer:

```powershell
python tools\storyworld_capability_score.py --run <run.jsonl>
```

The private eval manifest remains in `storyworlds/evals/manifest.json`, so the
tool expects that local ignored eval pack to be present.
