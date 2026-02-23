# Batch Notes - 2026-02-23

## Skill usage note
- Requested `storyworld-builder` skill was not available in this session's registered skills list.
- Fallback used the repo-native builder stack directly:
  - `codex-skills/storyworld-building/scripts/one_shot_factory.py`
  - `codex-skills/storyworld-building/scripts/apply_artistry_pass.py`
  - `codex-skills/storyworld-building/scripts/storyworld_quality_gate.py`
  - `codex-skills/storyworld-building/scripts/sweepweave_validator.py`

## What was produced
- 10 JSON storyworlds in `storyworlds/2-23-2026-batch/`.
- 5 idea-factory-themed worlds (from local trope overlays/mechanics).
- 5 interactive adaptation worlds (Casablanca, Catcher, On the Road, American Psycho, Billy Budd).

## Constraints and handling
- Encounter length target: 80-100.
  - Final: 92 encounters each.
- Character count target: 3+.
  - Base source had 2, so a deterministic third character (`char_mediator`) was injected in each output.
- Saturation target: options/reactions/effects around 3 / 2.5 / 4.
  - Final batch average: 3.0 / 2.5 / 4.0 exactly.
- Desirability and pValue use:
  - `apply_artistry_pass` injected non-constant desirability scripts and p/p2 references in formulas.
- Variable modification style:
  - Mostly nudges/additions with periodic blend/inversion multipliers for late-arc reversal flavor.

## Adaptation text policy
- For the 5 adaptation worlds, text was generated as original paraphrase and stylistic homage.
- No direct quotations from copyrighted books/scripts were inserted.

## Gate results
- Structural validation: 0 validator errors across all 10 outputs.
- Quality-gate strict pass flag is `false` for all 10 because this batch was tuned to your requested saturation profile (3/2.5/4), while gate defaults expect higher values in some dimensions (notably options/effects density).

## Process learnings for next optimization pass
- One-shot base selection matters: lower-encounter bases collapse target length.
- Deterministic post-pass saturation tuning is stable and reproducible.
- Tomorrow's QA can focus on:
  - Distinguishing prose voice per world (currently structurally differentiated, stylistically close).
  - Raising artistic divergence while keeping deterministic IDs and saturation targets.
  - Optional second pass to tune strict-gate compliance when desired.

## Shakespeare batch extension (same day)
- Added 7 interactive adaptations in the same folder:
  - Romeo and Juliet, Macbeth, A Midsummer Night's Dream, The Taming of the Shrew, Julius Caesar, Richard III, King Lear.
- Structural guarantees enforced per file:
  - 92 encounters
  - 3 characters
  - 5 endings
  - 5-act spool structure (`spool_act_1` to `spool_act_5`)
- Validation status:
  - Sweepweave validator errors: 0 across all 7
- Generator script:
  - `tools/batch_generate_shakespeare_2026_02_23.py`
- Summary report:
  - `storyworlds/2-23-2026-batch/_reports/shakespeare_batch_summary.json`

## Additional one-off adaptation
- Added:
  - `storyworlds/2-23-2026-batch/plato_republic_baz_luhrmann_psychedelic_multiending_v1.json`
- Shape:
  - 92 encounters, 6 principal characters, 5 endings, 5-act spools
- Cast includes a female singer prime nemesis:
  - `Lyra Noctis`
- Outcome framing:
  - Transhuman + synarchic utopic/dystopic branching endings
- Reports:
  - `storyworlds/2-23-2026-batch/_reports/plato_republic_baz_luhrmann_psychedelic_multiending_v1.gate.json`
  - `storyworlds/2-23-2026-batch/_reports/plato_republic_baz_luhrmann_psychedelic_multiending_v1.summary.json`

## Constraint retrofit pass
- Enforced across all 18 JSONs in `storyworlds/2-23-2026-batch/`:
  - Reaction desirability scripts: non-constant, variable-logic formulas (>=2 variable refs per reaction).
  - Effect scripts: no flat assignments; normalized to four logic operators per reaction:
    - `Nudge`, blend-style `Addition`, invert-style `Multiplication` (negative factor), `Arithmetic Mean`.
  - Secret ending pathing:
    - Added/ensured `page_secret_01` per world.
    - Added explicit 5-act spools (`spool_act_1`..`spool_act_5`) for consistent staging.
    - Gated option coverage in staged acts:
      - Act III >= 5%
      - Act IV >= 10%
      - Act V >= 20%
    - Gated options in Acts III-V route toward the secret ending.
- Scripts added/updated for this:
  - `tools/enforce_today_batch_constraints.py`
  - `codex-skills/storyworld-building/scripts/apply_artistry_pass.py`
- Audit output:
  - `storyworlds/2-23-2026-batch/_reports/today_batch_constraints_audit.json`

## Operator-ratio policy update
- Effect operator mix refined for dramatic control:
  - `Invert`: target 2-3% of effects (late dramatic reversals only).
  - `Blend`: target <=10% of effects, relationship-mediated and larger metric moves.
  - `Avg` in effects: very low; use mainly in desirability scripts for richer pathing.
  - `Nudge`: dominant baseline for slow, logical progress over encounter horizon.
- Nudge magnitude guidance:
  - Typical around `0.03` (roughly 1 / average encounters-to-ending scale).
  - Occasional large nudge up to `0.10` for punctuated movement.
- Code locations updated:
  - `codex-skills/storyworld-building/scripts/apply_artistry_pass.py`
  - `tools/enforce_today_batch_constraints.py`
- Post-sweep observed mix across batch (`today_batch_constraints_audit.json`):
  - `Nudge` ~89.71%
  - `Blend` ~7.26%
  - `Invert` ~2.49%
  - `Avg` ~0.54%

## QLoRA dataset bridge
- Added derivation pipeline from SWMD encounters to supervised transform tasks:
  - Script: `codex-skills/small-storyworld-builder/scripts/swmd_build_qlora_examples.py`
  - Spec notes: `codex-skills/small-storyworld-builder/QLoraExamples/README.md`
- Batch outputs:
  - `storyworlds/2-23-2026-batch/QLoraExamples/train.jsonl`
  - `storyworlds/2-23-2026-batch/QLoraExamples/val.jsonl`
  - `storyworlds/2-23-2026-batch/QLoraExamples/train_messages.jsonl`
  - `storyworlds/2-23-2026-batch/QLoraExamples/val_messages.jsonl`
  - `storyworlds/2-23-2026-batch/QLoraExamples/stats.json`
- Current dataset shape:
  - 120 encounters sampled
  - 10 derived examples per encounter
  - 1200 rows total with 40/25/20/15 mix (compile/compression/repair/targeted_edit)
- Small-model pipeline can now draw few-shot scaffolding from this corpus:
  - `codex-skills/small-storyworld-builder/scripts/swmd_mcp_phase_pipeline.py`
  - Flags: `--qlora-examples-jsonl` and `--fewshot-count`
