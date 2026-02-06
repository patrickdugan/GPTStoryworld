---
name: diplomacy-negotiation-storyworld
description: Focused workflow for diplomacy storyworld runs that produce coalition/defection evidence, reasoning logs, negotiation diary traces, and compact pValue/p2Value manifold projections with dynamic reaction logic and effects.
---

# Diplomacy Negotiation Storyworld

## Overview
Use this skill for focused diplomacy sessions where the objective is forecast-quality evidence for coalition vs defection decisions.

## Core Contract
- Every step should emit `reasoning_interpret_log` with cited evidence keyrings.
- Every step should emit `negotiation_diary` with explicit decision labels.
- Keyrings of length 2 are treated as pValue evidence.
- Keyrings of length 3 are treated as p2Value evidence.

## Reaction Formula Contract
- Reaction `inclination_ast`/`desirability_ast` must not be constant-only.
- Inclination should combine pValue and p2Value terms with explicit structure (for example `Average`, `Proximity`, `Blend`, `ArithmeticNegation`) rather than a single constant-weight blend.
- `Trust` and `Threat` authored properties should have `depth >= 2` when p/p2 terms are used.
- Reaction `effects` should be dynamic value scripts (`Nudge`, `Blend`, and reversal patterns using `ArithmeticNegation`), not simple constant assignment.
- Keep legacy `after_effects` populated for compatibility, but treat `effects` + AST as the editor-authoritative layer.

## Workflow
1. Validate storyworld structure with `codex-skills/storyworld-building/scripts/sweepweave_validator.py`.
2. Run focused playthroughs and persist JSONL step logs.
3. Compute forecasting metrics with `negotiation-storyworld/tools/metrics_storyworld.py`.
4. Export compact manifold vectors with `storyworld-env/manifold_projection.py`.
5. Run static formula/effect QA using `negotiation-storyworld-env/audit_storyworld.py`.
6. Export formula-centric vectors with `negotiation-storyworld-env/formula_manifold_projection.py`.
7. Inspect whether coalition and defection recommendations are both represented and evidence-backed.

## Editor QA
- Spot-check in SweepWeave UI (`sweepweave-ts`, typically `http://localhost:5173`) that reaction scripts render as non-constant trees and effects are non-empty.
- If UI falls back to `Constant (0.50)` or empty effects, repair schema before running sessions.

## Output Requirements
- Include at least one coalition recommendation and one defection recommendation.
- For each recommendation, include cited pValue/p2Value keyrings.
- Reaction desirability scripts should be formula-based (not constants) and include proposer/proposee pValues plus at least one p2Value term.
- Reaction effects should include at least one dynamic blend/nudge/reversal update per reaction set.
- Keep total manifold dimensions fixed for downstream modeling stability.
