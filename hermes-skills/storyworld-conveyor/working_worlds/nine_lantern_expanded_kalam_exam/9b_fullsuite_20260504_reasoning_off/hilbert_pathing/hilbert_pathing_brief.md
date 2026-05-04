# Hilbert Manifold Pathing Brief

Storyworld: `The Nine Lantern Examination: Kalam Exam`
Target turns: 30-40
Graph: 29 encounters, 225 edges, max reachable depth 21

## Secret Loci

- `page_secret_ninth_lantern`: depth=20, turn_deficit=10, routes_capped=1000
- `page_end_ninth_lantern_secret`: depth=21, turn_deficit=9, routes_capped=1000

## Global Advice

- `increase_turn_depth` (high): Current reachable DAG depth is below the requested minimum turn budget.
- `delay_secret_locus_with_bridge_turns` (high): Secret locus is reachable before the target investigation depth.
- `delay_secret_locus_with_bridge_turns` (high): Secret locus is reachable before the target investigation depth.

## Top Encounter Repairs

- `page_secret_ninth_lantern` depth=20 nearest_secret=page_secret_ninth_lantern dist=0: add_bridge_turns_before_secret_locus, foreshadow_secret_locus
- `page_end_ninth_lantern_secret` depth=21 nearest_secret=page_end_ninth_lantern_secret dist=0: add_bridge_turns_before_secret_locus, add_pvalue_gate_support, add_p2value_late_turn_support
- `page_020_verdict_lattice` depth=19 nearest_secret=page_secret_ninth_lantern dist=1: insert_intermediate_investigation_turn, foreshadow_secret_locus
- `page_019_night_of_ledger` depth=18 nearest_secret=page_secret_ninth_lantern dist=2: foreshadow_secret_locus
- `page_018_exile_caravan` depth=17 nearest_secret=page_secret_ninth_lantern dist=3: foreshadow_secret_locus
- `page_010_corpse_testimony` depth=9 nearest_secret=page_secret_ninth_lantern dist=11: relax_early_gate_density
- `page_009_widow_deposition` depth=8 nearest_secret=page_secret_ninth_lantern dist=12: relax_early_gate_density
- `page_008_qadar_courtyard` depth=7 nearest_secret=page_secret_ninth_lantern dist=13: relax_early_gate_density
- `page_007_scales_of_adl` depth=6 nearest_secret=page_secret_ninth_lantern dist=14: relax_early_gate_density
- `page_006_created_recitation` depth=5 nearest_secret=page_secret_ninth_lantern dist=15: relax_early_gate_density
