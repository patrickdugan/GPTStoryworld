# Verifier Matrix Summary

## Subjective
- `overall_demo_artifact_10`: 7.6
- `game_design_scaffold_10`: 8.4
- `reader_playability_current_harness_10`: 6.8
- `reader_playability_with_abs_operator_10`: 8.1
- `literary_polish_10`: 6.7
- `evaluation_value_10`: 8.0

## Native Storyworld Checks
- SweepWeave validator: pass
- Strict quality gate: pass
- Weighted authoring score: 0.8711
- Direct Monte Carlo: 8/8 endings reached; secret ending share 0.103

## Reader Harness Playtest
- Current reader: secret hits 0/15; secret-witness policy ended at `page_end_administrative_truce`.
- Reader with `Absolute Value` semantics: secret hits 1/15; secret-witness policy reached `page_end_social_machinery_witness_secret`.
- Finding: the authored design reaches the secret route, but the live reader lacks one operator used by the gate.

## Verifier Environments
- Negotiation audit: ok=True; reaction coverage nonconstant/p1/p2/dynamic all 1.0/1.0/1.0/1.0.
- Text-quality dry run: overall 0.7298; strongest on reaction voice and choice-consequence clarity, weakest on mechanics/characterization relevance.
- Quality-vector env: composite 0.7679, pathing conceptuality 0.6735, benchmark_pass=False.
- Quality-vector caveat: this env reports degenerate ending-balance/pathing metrics for this schema, while direct Monte Carlo reports balanced reachability across all eight endings.
- Derived reader-verifier bundle: constitutional 0.8987, needle solved=True, constrained dual 0.9392.
