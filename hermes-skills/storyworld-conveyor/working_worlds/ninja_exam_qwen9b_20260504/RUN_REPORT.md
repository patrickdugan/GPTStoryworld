# Ninja Exam Qwen 9B Storyworld Run

## Purpose

Build a short original hidden-village ninja exam storyworld from a Qwen3.5-9B design packet. The user requested a Naruto/Naturo-like premise; no local Naruto/Naturo storyworld source was found in the likely storyworld folders, so this run uses only broad ninja-academy genre motifs and avoids canon names, villages, clans, powers, and plot events.

## Main Artifact

- Storyworld: `ninja_exam_qwen9b_storyworld.json`
- Full SWMD export: `ninja_exam_qwen9b_storyworld.swmd.md`
- Minified SWMD export: `ninja_exam_qwen9b_storyworld.swmd.min.md`
- IFID: `SW-NINJA-EXAM-QWEN9B-20260504`
- Title: `The Silent Veil Ninja Exam`
- Shape: 22 nonterminal encounters plus 6 endings.
- Core variables: `Stealth`, `Loyalty`, `Focus`, `Mercy`, `Rivalry`, `VillageTrust`.
- Secret route: balance stealth, loyalty, focus, and mercy through `page_021_final_silence` and `page_022_under_village_route` into `page_end_silent_veil`.

## Qwen 9B Role

Qwen3.5-9B Q4 produced the design scaffold:

- title: `The Silent Veil of Kurogane`
- thesis: mastery is stealth plus moral judgment under village politics, not just combat
- variables: stillness, loyalty, focus, mercy, rivalry
- cast: Kaelen, Varek, Councilor Sora, Mira, Jiro
- trials: market stealth, poisoned feast, broken bridge, reflection pool, stolen scroll, whisper network, endless corridor, civilian-vs-asset, mirror match, final silence

The completion hit the output cap before finishing the JSON, so Codex materialized the storyworld deterministically from the usable packet rather than trusting malformed generated JSON.

Recorded Qwen timing:

- Prompt tokens: `161`
- Completion tokens: `900`
- Total tokens: `1061`
- Prompt eval: `3044.509 ms`, `52.88 tok/s`
- Generation: `183829.523 ms`, `4.90 tok/s`
- Wall time: about `187.7 s`
- Finish reason: `length`

## Validation

- SweepWeave validator: `VALID OK`
- Strict quality gate: pass
- Hard acceptance audit: pass
- Authoring verifier: pass
- Weighted authoring verifier score: `0.6875473484848484`

Key quality metrics:

- Encounters: `28`
- Options per encounter: `4.0`
- Reactions per option: `3.0`
- Effects per reaction: `5.0`
- Average encounter words: `53.18`
- Average reaction words: `31.90`
- pValue refs: `528`
- p2Value refs: `264`

## Pathing Notes

Hilbert pathing found the secret ending at depth `21`, inside the 18-30 target band.

Caveat: the route count hit the cap, so the secret is overexposed. The next improvement is to add more discriminating late gates around final silence, false orders, mercy, and under-village investigation.

The legacy Monte Carlo harness reports `Chain: 0` because of the custom generated format, but it still emitted an ending distribution with no dead ends. Treat validator, acceptance audit, and Hilbert pathing as the stronger structural authorities for this run.

## SWMD Round-Trip

After the 27B 128k probe, this run was exported to both full and minified SWMD. A conservative `swmd_patch_json.py` bridge was added to patch a valid base JSON from full SWMD encounter text/choice/reaction edits.

Round-trip smoke:

- Source JSON -> full SWMD -> patched JSON
- Patched JSON: `ninja_exam_qwen9b_storyworld.swmd_roundtrip.json`
- Patch report: `swmd_roundtrip_report.json`
- Validator: `VALID OK`

This supports the safer authoring flow: ask 27B for bounded SWMD-0 encounter blocks, patch those blocks into the existing valid JSON, then validate JSON before scoring or playtesting.
