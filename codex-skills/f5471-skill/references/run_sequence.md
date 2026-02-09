# Run sequence

1. Copy `inputs_5471.example.json` to `inputs_5471.json` and set file paths + facts.
2. Run parse:
   - `python tooling/parse_pdfs.py --inputs inputs_5471.json --outdir outputs`
3. Run compute:
   - `python tooling/compute_5471.py --inputs inputs_5471.json --parsed outputs/parsed --outdir outputs`
4. Run validation:
   - `python tooling/validate.py --inputs inputs_5471.json --computed outputs/computed_outputs.json --out outputs/validation.json`
5. Emit fill-map:
   - `python tooling/emit_fill_map.py --computed outputs/computed_outputs.json --validation outputs/validation.json --out outputs/fill_map_5471_<tax_year>.json`

Outputs:
- `outputs/parsed/prior_year_extract.json`
- `outputs/parsed/current_year_extract.json`
- `outputs/computed_outputs.json`
- `outputs/validation.json`
- `outputs/fill_map_5471_<tax_year>.json`

