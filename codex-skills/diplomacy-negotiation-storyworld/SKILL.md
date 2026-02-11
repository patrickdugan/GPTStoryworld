---
name: diplomacy-negotiation-storyworld
description: Focused workflow for diplomacy storyworld runs that produce coalition/defection evidence, reasoning logs, negotiation diary traces, and compact pValue/p2Value manifold projections.
---

# Diplomacy Negotiation Storyworld

## Overview
Use this skill for focused diplomacy sessions where the objective is forecast-quality evidence for coalition vs defection decisions.

## Core Contract
- Every step should emit `reasoning_interpret_log` with cited evidence keyrings.
- Every step should emit `negotiation_diary` with explicit decision labels.
- Keyrings of length 2 are treated as pValue evidence.
- Keyrings of length 3 are treated as p2Value evidence.

## Workflow
1. Validate storyworld structure with `codex-skills/storyworld-building/scripts/sweepweave_validator.py`.
2. Run focused playthroughs and persist JSONL step logs.
3. Compute forecasting metrics with `negotiation-storyworld/tools/metrics_storyworld.py`.
4. Export compact manifold vectors with `storyworld-env/manifold_projection.py`.
5. Inspect whether coalition and defection recommendations are both represented and evidence-backed.

## Output Requirements
- Include at least one coalition recommendation and one defection recommendation.
- For each recommendation, include cited pValue/p2Value keyrings.
- Keep total manifold dimensions fixed for downstream modeling stability.
