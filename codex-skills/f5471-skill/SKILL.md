---
name: f5471-skill
description: Deterministic Form 5471 workpaper pipeline for German UG entities using prior-year carryforward, fixed filer rules, tie-outs, and PDF fill-map emission.
---

# Form 5471 deterministic pipeline

Use this skill when preparing Form 5471 workpapers for a foreign corporation where inputs are known and must be handled mechanically (no legal conclusions, no exploratory reasoning).

## What this skill does

- Extracts prior-year and current-year values from PDFs into normalized JSON.
- Applies deterministic filer/schedule rules from config and user inputs.
- Builds schedule stubs and E&P rollforward outputs.
- Validates hard tie-outs.
- Emits a PDF fill-map JSON for browser or desktop automation.

## Required inputs

- `inputs_5471.json` (single source of truth, human-controlled facts)
- prior-year 5471 PDF
- current-year financials PDF

## Run sequence

1. `python tooling/parse_pdfs.py --inputs inputs_5471.json --outdir outputs`
2. `python tooling/compute_5471.py --inputs inputs_5471.json --parsed outputs/parsed --outdir outputs`
3. `python tooling/validate.py --inputs inputs_5471.json --computed outputs/computed_outputs.json --out outputs/validation.json`
4. `python tooling/emit_fill_map.py --computed outputs/computed_outputs.json --validation outputs/validation.json --out outputs/fill_map_5471_<tax_year>.json`

## Guarantees

- No guessed FX rates, filer categories, or required schedules.
- Values come from `inputs_5471.json`, extracted records, or explicit defaults in config.
- All unresolved assumptions are surfaced as warnings or open items.

## Limits

- This skill creates workpapers and fill maps, not legal filing conclusions.
- If source PDFs are image-only scans, extraction quality depends on text availability.

