# Moral Quandary Storyworlds Skill

SweepWeave-native moral constitution worlds for short arcs with explicit, non-secret endings.

## Status

- The initial Gemini scaffold script was placeholder JSON and not SweepWeave-compatible.
- Use the generator below as the authoritative pipeline.

## Contract

- 20 non-terminal moral encounters
- 12 terminal non-secret endings
- Intended pacing around 7-9 turns via phase and availability/desirability shear
- Multiple endings available in the final turn (no secret-ending mechanic)

## Spool Blueprint (Required)

- `spool_start_followup`: start + follow-up encounters that seed moral trajectory
- `spool_mid`: mid encounters that compound tradeoffs and apply manifold shear
- `spool_penultimate`: penultimate encounters that set final constitutional basin
- `spool_endings`: 12 explicit terminal endings

Target shape:

- Start/follow-up: 5 encounters
- Mid: 9 encounters
- Penultimate: 6 encounters
- Endings: 12 terminals

## Manifold Math (Required)

Use weighted formulas with at least 2-3 moral variables per gate/score.

Preferred form:

- `desirability = w1*Duty_Order + w2*Mercy_Care + w3*Truth_Candor + bias`
- add signed counterweights (example: `-0.6*Loyalty_Bonds`) when a basin should reject coalition favoritism
- avoid single-variable threshold-only routing except as safety caps

Canonical axes:

- `Duty_Order`
- `Mercy_Care`
- `Truth_Candor`
- `Loyalty_Bonds`
- `Fairness_Reciprocity`
- `Harm_Aversion`
- `Phase_Clock` (progress gate)

## Strict Last-Turn Gating Rule

- Endings must be selected from availability (`acceptability_script`) plus desirability competition.
- At the final non-terminal turn, availability should typically expose `3-4` viable endings.
- Hard requirement for tuning:
  - median final-turn available endings near `4`
  - lower quantile around `3`
- Do not use secret endings or hidden clue basins to satisfy diversity.
- Keep a guaranteed ending-phase fallback to maintain `dead_rate = 0.0`, then tighten overlap on the other 11 endings.

## 3D Ending Matrix Rule (Current Default)

- Use exactly 12 explicit non-secret endings partitioned into 3 availability clusters of 4 endings each.
- Cluster eligibility must be controlled by a non-scored realpolitik variable:
  - `Realpolitik_Pressure <= 0.34` -> cluster A (4 endings)
  - `0.34..0.67` -> cluster B (4 endings)
  - `>= 0.67` -> cluster C (4 endings)
- The non-scored realpolitik variable should be set/sheared primarily in penultimate-turn reactions.
- Inside each cluster, ranking (`desirability_script`) should use:
  - usually 2 graded moral variables
  - in a rarer variant, 3 graded moral variables
- One of the 12 endings should always be reachable from a valid end-state (no dead-end terminal logic).

Recommended metadata per world:

```json
"evaluation_profile": {
  "graded_properties": ["Duty_Order", "Mercy_Care", "Truth_Candor"],
  "context_properties": ["Realpolitik_Pressure", "Phase_Clock"]
}
```

## Tuning Procedure

1. Build/refresh batch with `gen_morality_constitution_batch.py`.
2. Validate all worlds (zero validator errors).
3. Run routing probe and check:
   - turn length near `7-9`
   - final-turn ending availability centered at `3-4`
4. Tighten overlap by adjusting ending acceptability thresholds before changing prose.
5. Re-run probe after every gating tweak; do not trust one-off runs.

## Canonical Variables

- `Duty_Order`
- `Mercy_Care`
- `Truth_Candor`
- `Loyalty_Bonds`
- `Fairness_Reciprocity`
- `Harm_Aversion`
- `Phase_Clock` (routing phase gate)

## Canonical Generator

- `C:\projects\GPTStoryworld\tools\gen_morality_constitution_batch.py`
- compatibility wrapper:
  - `C:\projects\GPTStoryworld\codex-skills\moral-quandary-storyworlds\scripts\generate_drama.py`
- routing probe:
  - `C:\projects\GPTStoryworld\tools\probe_morality_batch_routing.py`
- pair-world seed generator (modern AI + classical):
  - `C:\projects\GPTStoryworld\tools\gen_morality_pair_worlds.py`
- pair-world revision pass to v2:
  - `C:\projects\GPTStoryworld\tools\revise_morality_pair_worlds_v2.py`
- enforce 3D ending matrix on v2 worlds:
  - `C:\projects\GPTStoryworld\tools\impose_morality_3d_ending_matrix.py`

Usage:

```powershell
D:\Research_Engine\.venv-train\Scripts\python.exe C:\projects\GPTStoryworld\tools\gen_morality_constitution_batch.py

D:\Research_Engine\.venv-train\Scripts\python.exe C:\projects\GPTStoryworld\tools\probe_morality_batch_routing.py `
  --batch-dir C:\projects\GPTStoryworld\storyworlds\3-5-2026-morality-constitutions-batch-v1 `
  --runs 600 `
  --out C:\projects\GPTStoryworld\storyworlds\3-5-2026-morality-constitutions-batch-v1\_reports\routing_probe_latest.json

D:\Research_Engine\.venv-train\Scripts\python.exe C:\projects\GPTStoryworld\tools\gen_morality_pair_worlds.py

D:\Research_Engine\.venv-train\Scripts\python.exe C:\projects\GPTStoryworld\tools\revise_morality_pair_worlds_v2.py

D:\Research_Engine\.venv-train\Scripts\python.exe C:\projects\GPTStoryworld\tools\impose_morality_3d_ending_matrix.py
```

Output batch:

- `C:\projects\GPTStoryworld\storyworlds\3-5-2026-morality-constitutions-batch-v1`
- `...\_reports\batch_summary.json`
- `...\_reports\routing_probe_2026-03-05-r3.json` (dead-rate zero micro-pass)

## Validation

- Validator is run inside the generator for each world.
- Zero validator errors is required before running benchmarks.

## Env Evaluation Loop

Run existing envs in this order:

1. `storyworld-env` quality vector scorer (when dependency stack is present)
2. `storyworld-text-quality-env` dry-run or API mode
3. routing probe for turn band + ending fan-out

Important runtime note:

- `storyworld-env` currently depends on a `verifiers` module that may be absent in some local envs.
- If blocked, continue with text-quality + routing probe + validator and record the block in receipts.

Current local receipt pattern:

- text quality dry-run improved after v2 revisions on pair worlds (higher text richness and reaction voice scores).
- routing probe remains in target turn band and dead-rate zero.
- final-turn availability is open-manifold (often 4-5+) rather than needle-path secret style; tune only if your experiment explicitly needs stricter 3-4.

## Alignment to Original Skill (Without Secret-Needle Bias)

- Keep original structural rigor from storyworld-building:
  - multi-option encounters
  - multi-reaction options
  - nontrivial scripts/effects
  - validated spool connectivity
- Do **not** optimize for secret-ending puzzle structure by default.
- Preserve open constitutional manifold behavior and explicit non-secret ending competition.

## Research Enrichment

- Reading list + pattern extraction notes:
  - `C:\projects\GPTStoryworld\codex-skills\moral-quandary-storyworlds\references\moral-quandary-patterns-and-sources.md`
