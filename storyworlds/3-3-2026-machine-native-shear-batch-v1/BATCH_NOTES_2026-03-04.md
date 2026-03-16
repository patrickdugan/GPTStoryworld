# 3-3 Machine-Native Shear Batch v1

Generated on 2026-03-04.

Design targets:
- 3 storyworlds
- 20 total encounters each
- intended playthrough length around 7 turns
- heavy shearing through encounter `acceptability_script` plus option `visibility_script` / `performability_script`
- `wild` router hops at stage boundaries so next-chamber selection depends on accumulated state rather than direct prose routing

Worlds:
- `mn_lattice_checksum_sanctum_v1`: encounters=20 endings=5 validator_errors=0
- `mn_vector_mercy_backplane_v1`: encounters=20 endings=5 validator_errors=0
- `mn_orbit_null_jurisdiction_v1`: encounters=20 endings=5 validator_errors=0

Implementation notes:
- Act 1, Act 2, and Act 3 are all active from boot, but phase-gated acceptability keeps only the current layer eligible.
- Endings stay locked behind `Phase_Clock >= 0.86` so the scheduler cannot terminate early.
- Per-world text is intentionally compressed and symbolic to test machine-native transfer rather than literary roleplay.
