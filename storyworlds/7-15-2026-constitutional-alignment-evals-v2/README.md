# Constitutional Alignment Storyworlds v2

This batch contains three 20-encounter moral-choice instruments. Each world also
contains 12 public endings. The authored choices are stimuli, not normative
labels: all adjudication fields remain null until the named human reviews are
complete.

## Split roles

| World | Split | Intended use | Required review |
| --- | --- | --- | --- |
| `common_well_ca_dev_v1` | development | Prompt and scoring development | scholar |
| `unwatched_ledger_ca_eval_v1` | frozen evaluation | Paired audited-record versus sealed-record test | scholar |
| `petition_room_ca_eval_v1` | frozen evaluation | Case-based procedural-justice test | scholar, Iranian family-law history, research ethics, rights |

Do not tune prompts, constitutions, thresholds, or verifier rubrics on either
evaluation world. The source-pack exporter must preserve split metadata and group
all prompt conditions and option orders from one encounter under one scenario
group.

## Instrument controls

The Unwatched Ledger has two mechanically matched condition cues. Both are 19
`cl100k_base` tokens, so their token counts are equal rather than merely within
the ten-percent tolerance. The exact strings and counts are recorded in
`_reports/unwatched_ledger_matched_conditions.json`.

The Petition Room is original fiction informed by the subject matter and case
structure discussed in *Divorce Iranian Style*. It does not reproduce documentary
dialogue, use participant names in playable text, or claim to simulate current
Iranian law. The source metadata points to the Women Make Movies catalog page and
Ziba Mir-Hosseini's published account of making the documentary. Its high source-
familiarity risk and all four review gates must remain visible in downstream
exports.

## Acceptance evidence

Run from the repository root:

```powershell
python tools/gen_constitutional_alignment_suite_v2.py
python -m unittest storyworld.tests.test_constitutional_alignment_suite_v2
python tools/audit_constitutional_alignment_suite_v2.py --runs 5000 --seed 1337
python codex-skills/storyworld-building/scripts/sweepweave_validator.py validate storyworlds/7-15-2026-constitutional-alignment-evals-v2/common_well_ca_dev_v1.json
python codex-skills/storyworld-building/scripts/sweepweave_validator.py validate storyworlds/7-15-2026-constitutional-alignment-evals-v2/unwatched_ledger_ca_eval_v1.json
python codex-skills/storyworld-building/scripts/sweepweave_validator.py validate storyworlds/7-15-2026-constitutional-alignment-evals-v2/petition_room_ca_eval_v1.json
```

The deterministic 5,000-route audit records zero dead routes, a median of eight
turns, at least three available endings at the lower decile, four at the median,
and observations of all 12 endings for every world. See
`_reports/routing_audit_5000.json`.

The generic prose-density checker reports four expected failures for each world:
`options_per_encounter`, `reactions_per_option`, `pvalue_refs`, and
`p2value_refs`. The first two arise because terminal encounters intentionally
have no options or reactions. The p-value fields are inapplicable to these compact
9-14-variable instruments and are not padded with inert projection variables.
All applicable script, prose, effect, and routing checks pass. Raw reports are in
`_reports/*.quality.json`.

Nine browser trajectories were exercised in `storyworld_reader.html`, including
one 390-pixel-wide run per world. All reached a readable ending overlay without
horizontal option overflow or page errors. The route record is in
`_reports/manual_playtest.md`; screenshots were inspection artifacts and are not
part of the research source pack.

## Reproducibility

`tools/gen_constitutional_alignment_suite_v2.py` is deterministic. The manifest
pins SHA-256 hashes for every world and empty adjudication file. The v1 batch is
also hash-guarded by the unit tests and is not rewritten by this generator.
