# Constitutional Rubric Verifier Env

Purpose: score a single storyworld play trace against a constitutional rubric with weighted priority variables so schema overlays stay clean.

## Inputs
- `trace`: ordered list of play events with fields like `action`, `state_delta`, `outcome`.
- `rubric`: weighted dimensions and hard constraints.

## Output
JSON with:
- `total_score`
- `dimension_scores`
- `hard_violations`
- `constitutional_pass`

## Usage
```powershell
python src/constitutional_rubric_env.py --trace examples/sample_trace.json --rubric config/rubric_schema.json
```
