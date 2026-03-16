# negotiation-storyworld-env

Companion environment for `storyworld-env` focused on **static storyworld formula quality**.

This package complements turn-log manifold projection by adding:
- `audit_storyworld.py`: validates reaction logic/effects quality contracts
- `formula_manifold_projection.py`: builds fixed-dimension vectors from reaction AST/effect structures

## Install

```bash
cd C:/projects/GPTStoryworld/negotiation-storyworld-env
pip install -e .
```

## Audit Usage

```bash
python audit_storyworld.py --storyworld C:/projects/AI_Diplomacy/ai_diplomacy/storyworld_bank_focus_1915/forecast_backstab_p.json --strict
```

Checks include:
- non-constant inclination/desirability AST
- pValue and p2Value evidence in reaction logic
- dynamic (non-constant) effect value scripts
- Trust/Threat authored property depth guidance

## Projection Usage

```bash
python formula_manifold_projection.py --storyworld C:/projects/AI_Diplomacy/ai_diplomacy/storyworld_bank_focus_1915/forecast_backstab_p.json --out projection.json
```

Outputs a compact fixed-size vector suitable for downstream forecasting pipelines.
