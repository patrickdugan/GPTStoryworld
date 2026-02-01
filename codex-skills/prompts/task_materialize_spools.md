Task: Materialize SweepWeave spools using the editor’s native format.

Authoritative contract:
- sweepweave_validator.py is the contract. Never bypass it.
- The JSON must load in SweepWeave 0.1.9.

Rules:
- Spools must match the native SweepWeave object shape:
  { creation_index, creation_time, modified_time, encounters: [], id, spool_name, starts_active }
- DO NOT invent spool_type, title, or name fields.
- Encounter membership is ONLY via encounters[*].connected_spools.
- starts_active must be false for all spools except the first (lowest creation_index).

Process (MANDATORY):
1) Validate the input file:
   python sweepweave_validator.py validate "<path-to-json>"
   If invalid, stop and fix before proceeding.

2) Materialize missing spools:
   python tools/materialize_spools.py "<path-to-json>" "<tmp-output-json>"

3) Replace the original file with the tmp output.

4) Validate again:
   python sweepweave_validator.py validate "<path-to-json>"

Deliverable:
- Report number of spools materialized
- Report validator result (VALID or error list)
