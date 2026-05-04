# 27B Hermes Skill Storyworld Quality Verifier Results

Date: 2026-05-04

Scope: scored 27B/Hermes-skill storyworld artifacts with the local storyworld quality gate, authoring verifier, and available verifier-env summaries.

## Summary

| Artifact | Strict quality gate | Authoring verifier | Other verifier signal | Main failure / ceiling |
| --- | ---: | ---: | ---: | --- |
| `romeo_sanaa_qwen27b_40enc` | pass | 0.8711 | quality vector 0.7679, pathing conceptuality 0.6735, text dry-run 0.7298 | Quality-vector env reports benchmark fail from pathing/ending-balance degeneracy despite balanced direct Monte Carlo. |
| `nine_lantern_expanded_kalam_exam` | pass | 0.8664 | 29 encounters, 100% gated options, 1350 pValue refs, 675 p2Value refs | Effect diversity still shallow; repeated Nudge/Addition pattern. |
| `hermes_qwen27b_packet_storyworld` | pass | 0.8589 | 18 encounters, 100% gated options, 720 pValue refs, 360 p2Value refs | Effect diversity still shallow; repeated Nudge/Addition pattern. |
| `murder_mystery_compare_20260504_001/27b_hermes_skill` | validator pass; builder score 0.7819 | 0.6068 fail | blueprint contract score 0.9907 | Authoring verifier fails pValue desirability alignment; materialized world is structurally valid but weaker as a semantic storyworld. |

## Interpretation

The 27B skill path is strong enough to produce validator-valid and strict-quality-gate-passing storyworlds when the conveyor, packetization, and deterministic repair pipeline own the control-plane work. The best scored artifacts cluster around 0.86-0.87 on the weighted authoring verifier, above the 0.65 local pass threshold.

The ceiling is not JSON validity or basic branching. The remaining bottleneck is richer game-design semantics: more diverse effect operators, better pValue/p2Value use in all generated branches, and pathing metrics that distinguish real secret-route design from mechanically reachable gates.

The murder-mystery comparison is the caution case. It scored well on blueprint contract quality before materialization and passed the structural builder scorecard, but the authoring verifier penalized missing pValue desirability alignment. That means the 27B can follow the high-level skill, but the TRM/MCP retrieval curriculum needs to make pValue/p2Value semantic alignment a first-class card/row in the flow.

## Receipts

- `hermes-skills/storyworld-conveyor/working_worlds/romeo_sanaa_qwen27b_40enc/recheck_authoring_score.json`
- `hermes-skills/storyworld-conveyor/working_worlds/nine_lantern_expanded_kalam_exam/recheck_authoring_score.json`
- `hermes-skills/storyworld-conveyor/working_worlds/hermes_qwen27b_packet_storyworld/recheck_authoring_score.json`
- `benchmarks/storyworld_builder_small_model/runs/murder_mystery_compare_20260504_001/27b_hermes_skill/recheck_authoring_score.json`
- `benchmarks/storyworld_builder_small_model/runs/murder_mystery_compare_20260504_001/comparison_summary.json`
