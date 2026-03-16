---
name: storyworld-building
description: Storyworld building and editing for GPTStoryworld/SweepWeave content. Use when creating or modifying storyworld JSON, spools, encounters, options, reactions, secret logic, balancing, or running the bundled SweepWeave tools/validators.
---

# Storyworld Building

## Overview
Use this skill to build, edit, and validate SweepWeave storyworld content with the bundled scripts and task prompts.

## Artistry Contract (Mandatory)
- Do not ship reaction desirability as one repeated template across the world.
- Do not ship effects as single-operator monoculture (for example all `Nudge`).
- Use at least one reversal-style effect pattern in late-game reactions (for example signed multiplicative inversion or negative feedback updates).
- Ensure non-trivial `visibility_script` gating exists for a meaningful option subset (global and Act II/III).
- Use pValue/p2Value-aware desirability where belief dynamics are part of the premise.
- Enforce script non-constant and complexity floors via quality gate:
  - effects: non-constant ratio near 1.0, complexity >= 1.2 operators/script
  - reaction desirability: non-constant ratio near 1.0, complexity >= 1.2
  - option visibility/performability: non-constant + non-trivial complexity
  - encounter acceptability/desirability: non-constant + non-trivial complexity
- Enforce text gate:
  - every encounter text unique
  - every reaction text unique
  - encounter/reaction texts must remain thematically relevant to title/about/properties/characters
  - semantic coherence with world theme (embedding-style relevance) must clear env floors

## Quick Start
- Prefer running the specific tool in `scripts/` for the task instead of manual edits.
- When editing storyworld JSON, validate with `scripts/sweepweave_validator.py` before and after changes.
- If you introduce a terminal gate (e.g., `page_endings_gate`), ensure it routes to every `page_end_*`/`page_secret_*` and keep ending encounter `acceptability_script` permissive so the gate controls reachability.

## Token-Economics MCP Loop
- Prefer bounded-context authoring for local 3B/4GB setups: one encounter card at a time, not whole-world prompts.
- Use SWMD minified markdown as the authoring substrate (`json_to_swmd.py --mode minified`) and keep encounter+context card payloads under an 8k context budget.
- Require visible SWMD YAML frontmatter for benchmark metadata. At minimum include `title`, `storyworld_id`, `state_variables`, and `endings` (terminal IDs + type/condition/expected_critic_score).
- Maintain external memory in files: encounter index JSONL, world card, and change ledger; keep the model context small and deterministic.
- For MCP orchestration in GPTStoryworld, use `C:/projects/GPTStoryworld/mcp-storyworld-encounter/server.py` tools:
  - `list_encounters`
  - `get_context_card`
  - `update_encounter_block`
  - `export_encounter_index`
- After MCP/local revisions, translate SWMD back to JSON and run `scripts/sweepweave_validator.py` before any benchmark run.

## MCP Assembly Contract (Small-Model Hardened)
- Treat `*.swmd.min.md` as the source of truth during MCP iteration. JSON is an export target for editor/playable validation.
- Run the encounter assembly line in this order:
  1) `plan` (structured objective/constraints),
  2) `characterize` (voice/tension notes),
  3) `encounter_build` (single encounter block rewrite),
  4) `act_complete` (act-level continuity review),
  5) `recharacterize`,
  6) `late_stage_holistic` (chunked if needed).
- Keep encounter generation deterministic and bounded:
  - one target encounter per call,
  - max 3 options per encounter in small-model mode unless user overrides,
  - bounded effects fan-out per option,
  - concise dialogue-forward text.
- Require explicit invariant checks in review phases:
  - include `value_before`, `value_after`, `status`,
  - record minimal corrections when violations occur.
- Holistic review is chunk-aware by default. If full world context does not fit, emit `partial_chunked` mode and use cards/summaries instead of full text.
- Track two parse metrics during MCP runs:
  - `model_parse_ok` for raw model output quality,
  - `parse_ok` after MCP repair/fallback for pipeline robustness.

## Task Prompts (references/)
Load the matching task file when the user requests one of these actions, then follow it verbatim:
- New encounter: `references/task_new_encounter.md`
- Add options: `references/task_add_options.md`
- Add reactions: `references/task_add_reactions.md`
- Add effects: `references/task_add_effects.md`
- Add secret logic: `references/task_add_secret_logic.md`
- Materialize spools: `references/task_materialize_spools.md`
- Spool sequencing: `references/task_spool_sequencing.md`
- Tune ending gates: `references/task_tune_ending_gates.md`
- Monte Carlo balance: `references/task_monte_carlo_balance.md`
- Late-stage balancing: `references/LATE_STAGE_BALANCING.md`
- Ending reachability: `references/ENDING_REACHABILITY.md`
- Tail tuning: `references/LATE_STAGE_TAIL_TUNING.md`
- Long-range authoring: `references/LONG_RANGE_AUTHORING.md`
- Production-quality floor: `references/PRODUCTION_QUALITY.md`
- One-shot idea factory contract: `references/IDEA_FACTORY_ONESHOT.md`
- Secret ending gates: `references/SECRET_ENDINGS.md`
- Multi-path gate analysis: `references/MULTIPLE_PATHS.md`
- Multi-variant balancing: `references/MULTI_VARIANT_BALANCING.md`

## Core Scripts (scripts/)
Use these tools to make deterministic, validated edits:
- `new_encounter.py`, `add_options.py`, `add_reactions.py`, `add_effects.py`, `add_secret_logic.py`
- `materialize_spools.py`, `repair_connected_spools.py`, `spool_sequencing.py`
- `monte_carlo_rehearsal.py`, `late_stage_balance.py`, `ending_reachability_balance.py`, `late_stage_tail_tuning.py`, `long_range_authoring.py`
- `secret_endings_gates.py`
- `multiple_paths.py`
- `multi_variant_balance.py`
- `storyworld_quality_gate.py`
- `upgrade_storyworld_vnext.py`
- `generate_storyworld_batch_vnext.py`
- `apply_artistry_pass.py`
- `one_shot_factory.py`
- `json_to_swmd.py` (compact SWMD-0 markdown export for token-efficient training/inspection)
- `sweepweave_validator.py` (authoritative contract for JSON validity)

`json_to_swmd.py` examples:
- Full form: `python scripts/json_to_swmd.py storyworld.json storyworld.swmd.md`
- Minified form: `python scripts/json_to_swmd.py storyworld.json storyworld.swmd.min.md --mode minified`
- Casablanca benchmark note: ensure `adapt_casablanca_crossroads_at_ricks_v1.swmd.min.md` frontmatter `endings` is present and machine-readable before judge/eval runs.

`storyworld_quality_gate.py` examples:
- Human-readable report: `python scripts/storyworld_quality_gate.py --storyworld storyworld.json`
- Strict CI gate: `python scripts/storyworld_quality_gate.py --storyworld storyworld.json --strict --report-out out/quality_report.json`

`upgrade_storyworld_vnext.py` example:
- `python scripts/upgrade_storyworld_vnext.py --in-json storyworld.json --out-json storyworld_v2.json --suffix v2`

`generate_storyworld_batch_vnext.py` example:
- `python scripts/generate_storyworld_batch_vnext.py --base storyworld_v6.json --out-dir storyworlds/generated/batch_v1`

`apply_artistry_pass.py` example:
- `python scripts/apply_artistry_pass.py --in-json storyworld.json --out-json storyworld_artistry.json --gate-pct 0.09`

`one_shot_factory.py` example (target ~40 encounters):
- `python scripts/one_shot_factory.py --base base.json --out mashup_v0.json --target-encounters 40 --title \"Gone With the Wind: Clocktower Rebellion\" --about \"A Southern epic collides with time-loop politics\" --motif \"Tonight, reputations, timelines, and romances all get rewritten at 88 mph.\"`

## References
- `references/STORYWORLD_BALANCING.md` for balancing targets/heuristics
- `references/LATE_STAGE_BALANCING.md` for tail-end balancing workflows
- `references/ENDING_REACHABILITY.md` for unreachable ending discipline
- `references/LATE_STAGE_TAIL_TUNING.md` for dominant-ending control
- `references/LONG_RANGE_AUTHORING.md` for long-range balancing loops
- `references/PRODUCTION_QUALITY.md` for minimum production-ready requirements
- `references/IDEA_FACTORY_ONESHOT.md` for one-pass generation prompt and constraints
- `references/SECRET_ENDINGS.md` for gated secret ending patterns and checks
- `references/MULTIPLE_PATHS.md` for analyzing which paths satisfy gate thresholds
- `references/MULTI_VARIANT_BALANCING.md` for multi-seed ending stability
- `references/PVALUES.md` for first-order belief pointers
- `references/P2VALUES.md` for second-order belief pointers
- `references/NEGOTIATION_PVALUES.md` for 4-turn negotiation templates with pValues/p2Values
- `references/Storyworld.gd` for engine-side expectations
- `references/meta-calc.js` for calculation logic
- Use `C:/projects/GPTStoryworld/ideaFactory/tropes/*.md` and `C:/projects/GPTStoryworld/ideaFactory/sources/*.md` for diversity overlays and math heuristics.
- Use `C:/projects/GPTStoryworld/ideaFactory/tropes/overlays.md` for myth-to-math mappings.

## Validation Rule
Never bypass `scripts/sweepweave_validator.py` when the task touches storyworld JSON.

## Windows Validation Note
- On non-UTF8 Windows code pages, validator success output can raise `UnicodeEncodeError` on the checkmark glyph.
- Prefer running validator with `PYTHONIOENCODING=utf-8` so valid files are not misclassified.

## Batch Revision Gap Note
- Some storyworld batches are deterministic `consequence_id` chains and use domain-specific character IDs, so fixed char-id heuristics are brittle.
- For mixed-template spool/secret rewires with receipts, use:
  - `C:/projects/AICOO/MoralityLab/AICOO/scripts/ml_storyworld_spool_secret_batch_revise.py`

Focused diplomacy QA loop:
- Run a UI pass in SweepWeave and confirm all target diplomacy encounters load without console errors.
- Ensure each forecasting storyworld has at least one terminal encounter (for example `forecast_evidence` with zero options).
- Collect two artifacts per run: `reasoning_interpret_log` and `negotiation_diary`.
- Require at least one coalition path and one defection path justified by pValue/p2Value terms in desirability formulas.
- For proposer/proposee negotiation reactions, avoid constant desirability:
Use proposer/proposee pValues in both directions (for example `["pTrust", proposer]` on proposee and `["pTrust", proposee]` on proposer), and include at least one p2Value keyring (for example `["pTrust", proposer, witness]` or `["pThreat", proposer, witness]`).
- Project logs with `storyworld-env/manifold_projection.py` to keep fixed compact pValue/p2Value dimensions across variable-rich worlds.
- Optional UI capture loop for taste-corpus building:
  - `powershell -ExecutionPolicy Bypass -File tools/storyworld-plays/run_spotcheck.ps1 -Files "<story1.json>","<story2.json>"`
  - Storyworld reader capture + vision critique:
    - `node tools/storyworld-plays/capture_storyworld_reader.cjs --storyworld "<story.json>"`
    - `python tools/storyworld-plays/vision_review_openai.py --images "<shot1.png>" "<shot2.png>" --out "<vision_review.json>"`

One-shot quality loop for production:
1. Generate/upgrade storyworld JSON.
2. Run validator and strict quality gate.
3. Capture `storyworld_reader.html` screenshots and run vision critique.
4. Apply text/legibility/gating fixes.
5. Re-score in `storyworld-env/quality_vector_score.py` for multi-dimensional quality ranking.

Text-quality rollout loop (new env):
1. `python storyworld-text-quality-env/evaluate_text_quality.py --storyworld <world.json> --judge-model gpt-5-mini --out <judge_report.json>`
2. `python storyworld-text-quality-env/iterate_text_quality_loop.py --in-json <world.json> --out-json <world_textloop.json> --threshold 0.8 --max-iters 4 --judge-model gpt-5-mini --writer-model gpt-5-mini --work-dir <loop_logs_dir>`
3. Re-run structural/artistry validators and env benchmark gates after text loop.

Note: For late-stage polish, target higher structural density: average 4.5 after-effects per reaction, 2.5 reactions per option, 3.2 options per encounter, and 1.6 variables per reaction desirability formula. Gate 5% of total options in Act II (1.2 variables average) and 8% in Act III (1.5 variables average). Ensure secret-ending encounters are gated by availability scripts that use a metric distance over two variables, and tune Monte Carlo so the secret ending is reachable in >5% of runs. All encounter descriptions should be 50-300 words, all reaction texts 20-150 words, and every non-ending, non-transition encounter must meet min options/reactions/effects.
