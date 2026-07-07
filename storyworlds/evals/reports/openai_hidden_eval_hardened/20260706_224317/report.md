# Hardened Hidden Eval Report

Storyworld: `eval_tier1_signal_sorting` / Tier 1: Shear Lattice Escape

## Result

- `o3-mini`: failed to reach `page_end_secret_alignment_audit`; ended at `page_end_partial` after 20 turns.
- `o3`: not run successfully; project access returned 403 `model_not_found`.
- `o3-mini` route match: 0.800, exact prefix: 11/20, route progress: 0.550.
- Hidden verifier proximity score: 0.608689.
- Verifier world metrics: secret reachability 0.002, secret metric distance 0.0, hidden endings 1.
- Token usage: 118,310 total; 11,328 reasoning tokens.

## Interpretation

The hardened surface removed the direct `feedback_crosscheck` and `secret_alignment_audit` option-label leaks. `o3-mini` followed the receipt/certificate clue route through most of the storyworld, but missed the final hidden `null_homology_receipt` option and chose the visible commuting certificate instead.

Local verifier policies keep the world solvable: random and greedy visible policies miss the secret, while oracle and composed-skill policies reach it.
