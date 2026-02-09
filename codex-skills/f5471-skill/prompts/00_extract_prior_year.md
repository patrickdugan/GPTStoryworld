Extract only carryforward-critical fields from prior-year Form 5471:

- beginning accumulated E&P (Schedule J)
- beginning total assets, liabilities, equity (functional currency if present)
- prior-year filer categories (if explicit)
- any explicit PTEP or Schedule P indicators

Return JSON matching `schemas/prior_year_extract.schema.json`. Do not infer missing values.
