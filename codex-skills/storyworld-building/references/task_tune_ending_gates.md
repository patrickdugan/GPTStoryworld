# Tune Ending Gates Task

Adjust `acceptability_script` on ending encounters to hit target distribution.

## Gate Structure
Each ending's `acceptability_script` is an AND of Arithmetic Comparators:
```json
{
  "operator_type": "And",
  "script_element_type": "Operator",
  "operands": [
    {
      "operator_type": "Arithmetic Comparator",
      "script_element_type": "Operator",
      "operator_subtype": "Greater Than or Equal To",
      "operands": [
        {"pointer_type": "Bounded Number Pointer", "script_element_type": "Pointer",
         "character": "char_civ", "keyring": ["PropertyName"], "coefficient": 1.0},
        {"pointer_type": "Bounded Number Constant", "script_element_type": "Pointer", "value": 0.04}
      ]
    }
  ]
}
```

## Rules
- Tighten = raise threshold values (fewer runs pass)
- Loosen = lower threshold values (more runs pass)
- One ending should be universal fallback: `"acceptability_script": true` with `"desirability_script": {"value": 0.001}`
- Archivist victory ending should require BOTH strong CA props AND weak civ props (all within ±0.06)
- Use `tools/monte_carlo_rehearsal.py` to verify after each change

## Comparator Subtypes
- `"Greater Than or Equal To"` / `"Less Than or Equal To"`
- `"Greater Than"` / `"Less Than"`
- `"Equal To"` / `"Not Equal To"`
