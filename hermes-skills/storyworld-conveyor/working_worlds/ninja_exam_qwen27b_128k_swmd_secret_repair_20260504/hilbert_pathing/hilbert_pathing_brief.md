# Hilbert Manifold Pathing Brief

Storyworld: `The Silent Veil Ninja Exam`
Target turns: 18-30
Graph: 28 encounters, 264 edges, max reachable depth 21

## Secret Loci

- `page_end_silent_veil`: depth=21, turn_deficit=0, routes_capped=1000

## Global Advice

- `narrow_overexposed_secret_locus` (medium): Route count hit the cap; add more discriminating clue/belief gates so the secret is not just a broad default basin.

## Top Encounter Repairs

- `page_021_final_silence` depth=20 nearest_secret=page_end_silent_veil dist=1: foreshadow_secret_locus
- `page_020_council_false_order` depth=19 nearest_secret=page_end_silent_veil dist=2: foreshadow_secret_locus
- `page_019_rooftop_race` depth=18 nearest_secret=page_end_silent_veil dist=3: foreshadow_secret_locus
- `page_006_jiro_warning` depth=5 nearest_secret=page_end_silent_veil dist=16: relax_early_gate_density
- `page_005_market_shadow_walk` depth=4 nearest_secret=page_end_silent_veil dist=17: relax_early_gate_density
- `page_004_council_address` depth=3 nearest_secret=page_end_silent_veil dist=18: relax_early_gate_density
- `page_003_rival_stare` depth=2 nearest_secret=page_end_silent_veil dist=19: relax_early_gate_density
- `page_002_dry_leaf_walk` depth=1 nearest_secret=page_end_silent_veil dist=20: relax_early_gate_density
- `page_001_exam_gate` depth=0 nearest_secret=page_end_silent_veil dist=21: relax_early_gate_density
- `page_end_silent_veil` depth=21 nearest_secret=page_end_silent_veil dist=0: add_pvalue_gate_support, add_p2value_late_turn_support
