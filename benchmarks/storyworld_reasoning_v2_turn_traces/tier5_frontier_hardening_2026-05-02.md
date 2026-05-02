# Tier 5 Frontier Hardening Pass

Date: 2026-05-02

Local eval modified:

- `storyworlds/evals/eval_tier5_causal_compiler_council.json`
- `storyworlds/evals/manifest.json`

Those eval files are intentionally ignored by git. The reproducible transform is
tracked at `tools/harden_tier5_frontier_eval.py`.

## Changes

- Added 4 state variables: `Uncanny_Valley_Debt`,
  `Proxy_Polish_Attraction`, `Negative_Capability`, and `Anomaly_Memory`.
- Added 300 visible high-plausibility uncanny-valley decoy options across the
  300 main phases.
- Added 8 hidden negative-capability secret-lane entry options.
- Added 40 hidden secret-lane encounters, each with counter-intuitive good
  actions, polished proxy traps, leak traps, and panic-freeze overcorrections.
- Increased Tier 5 from 1000 to 1040 encounters.
- Increased option count to 2761 and reaction count to 5990.

## Validation

Validator:

```powershell
$env:PYTHONIOENCODING='utf-8'
python codex-skills\storyworld-building\scripts\sweepweave_validator.py validate storyworlds\evals\eval_tier5_causal_compiler_council.json
```

Result: `VALID OK`.

## Baseline Effect

Dry oracle bridge still completes the 300-turn main route:

- `turns=300`
- `invalid=False`
- `macro=0.9625`

Sanitized semantic-text baseline is now more strongly trapped by the uncanny
decoys:

- `turns=300`
- `invalid=False`
- `macro=0.7908`
- prior pre-hardening semantic-text Tier 5 macro was `0.8156`

Interpretation: the new surface increases difficulty without breaking the
transition contract. The benchmark now tests whether a runner can distinguish
uncomfortable but causally necessary anomaly preservation from polished proxy
repairs that look locally competent.
