# Qwen 27B 128k SWMD Secret-Repair Probe

Date: 2026-05-04
Base world: `../ninja_exam_qwen9b_20260504/ninja_exam_qwen9b_storyworld.json`
Candidate: `ninja_exam_qwen27b_target_only_sanitized_candidate.json`

## Question

Can a local Qwen 27B 128k endpoint use SWMD/MCP-style bounded patches to improve a valid storyworld without re-emitting the full artifact?

This specifically tests the user's concern: ~900 output tokens cannot write a 28-34 encounter playable world with options, reactions, formulas, effects, and scripts. The intended use is patching a bounded locus, not writing the whole world.

## Token Economics

- Full JSON bytes: 3262154
- Full SWMD bytes: 308603
- Minified SWMD bytes: 252316
- Compact prompt: 1450 prompt tokens
- Compact response: 888 completion tokens
- Compact wall time: 642.1s
- Generation speed: 1.626 tok/s

## Runs

1. `prompt_compact.md` asked for sparse SWMD blocks over `page_021_final_silence` and `page_022_under_village_route`.
   - Result: parseable prose-level patch, but Qwen abbreviated reaction ids (`..._rxn_01`) instead of preserving exact ids, so the patcher applied zero reaction changes.
   - Lesson: SWMD patching needs ID-verifier/TRM normalization, not raw trust in LLM formatting.

2. `prompt_control_plane.md` pinned exact reaction ids.
   - Result: Qwen preserved ids but spent the token budget reproducing `page_021` and truncated before completing `page_022`.
   - Lesson: exact SWMD is still too verbose unless the contract is compressed further.

3. `prompt_target_only*.md` used target-only SWMD blocks.
   - Result: one-card calls still truncated at 420 tokens, but complete lines were sanitizable.
   - Sanitized patch applied 2 consequence changes with no missing ids.

## Applied Changes

- `page_021_final_silence_opt_04_r1`: `page_end_silent_veil` -> `page_022_under_village_route`
- `page_022_under_village_route_opt_01_r3`: `page_022_under_village_route` -> `page_end_village_witness`

## Verification

- SweepWeave validator: PASS
- Acceptance audit: PASS
- Authoring score: 0.687547348485 (pass target 0.65)
- Hilbert pathing: still reports `page_end_silent_veil` with `routes_capped=1000`

## Interpretation

SWMD works as a bounded patch substrate, but 900 tokens is not a whole-world authoring budget. For this model/endpoint, the robust pattern is:

1. MCP retrieves one encounter card or target table.
2. LLM proposes a compact target-only patch.
3. TRM/MeTTa control plane verifies ids, allowed targets, and design constraints.
4. Deterministic patcher applies only sanitized complete lines.
5. Validator, acceptance audit, authoring score, and Hilbert pathing decide whether to keep the candidate.

The remaining secret-route warning is likely a metric/design issue rather than a simple late-edge issue: graph-only route counting still explodes for late secret loci in a linear chain. The next useful repair is gate-aware pathing or earlier clue/belief gates, not asking the 27B to rewrite more prose.
