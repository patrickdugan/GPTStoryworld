---
name: social-forecast
description: Forecast-oriented reasoning for strategy storyworlds (Diplomacy and related coalition games). Use when you need to analyze a storyworld's coalition/defection/betrayal/death-ground dynamics, apply recursive pValue/p2Value model augmentation to Diplomacy *_p files, run fast MAS simulations, and emit a single actionable forecast report with evidence traces.
---

# Social Forecast

## Overview
Use this skill as the default shortcut when an agent is given a strategy storyworld and must quickly produce an evidence-backed social forecast.

## Quick Start
Run the single entrypoint:

```powershell
python social-forecast/scripts/social_forecast.py --storyworld C:\projects\GPTStoryworld\storyworlds\russia_to_austria_grudger_p.json
```

This produces:
- a consolidated report JSON,
- a per-step reasoning trace JSONL,
- strategy posture recommendation.

## Workflow
1. Validate the input storyworld with sweepweave_validator.py when available.
2. If file is Diplomacy *_p.json with power_* cast (or --apply-model yes), apply recursive model patches:
   - default `--write-mode copy` writes a patched copy in `outputs` and leaves the source unchanged,
   - optional `--write-mode inplace` updates the source file.
   - p2 desirability terms,
   - survival/death-ground/pressure variables,
   - Paine-style coalition tradeoff effects.
3. Build agent priors from storyworld content (reaction style mix plus character trust/threat/survival properties) before simulation.
4. Run effect-density analysis when available.
5. Run recursive MAS simulation sized to cast (clamped to 3-7 agents).
6. Emit one forecast report with recommendation.

## Core Scripts
- scripts/social_forecast.py: One-command orchestrator for forecasting a storyworld.
- scripts/apply_recursive_models_to_p_storyworlds.py: Model augmentation utility for Diplomacy *_p files.
- scripts/mas_recursive_reasoner.py: Recursive MAS engine (p, p2, manifold scan, death-ground logic).
- scripts/run_recursive_series.py: Batch 4-7 player simulation utility.

## Decision Rules
- Prefer social_forecast.py unless user explicitly requests manual, per-script control.
- For non-Diplomacy storyworlds, still run recursive simulation and report; skip model patching unless explicitly requested.
- Always report exact output file paths.
- Use `--write-mode copy` unless the user explicitly asks to mutate the source storyworld.

## References
- references/forecast_interpretation.md: How to read report fields and map them to strategy choices.
