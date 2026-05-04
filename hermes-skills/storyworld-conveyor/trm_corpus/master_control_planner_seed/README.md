# Master Control Planner Seed Corpus

Episode-level curriculum derived from the 9-TRM encounter trajectory library.

- Episodes: `111`
- Master control rows: `999`
- Model tier: `9B_Q4`
- Context budget: `8192` tokens
- Average reward: `0.3067`
- Success rate: `0.045`

Files:

- `trajectory_episodes.jsonl`: episode-level planner rows.
- `master_control_rows.jsonl`: per-step `global_state/tools -> next_role` rows.
- `train.jsonl` / `val.jsonl`: row views derived from an episode-disjoint split.
- `episode_train.jsonl` / `episode_val.jsonl`: episode split for sequence-level evaluation.
- `sample_episode.json`: one readable episode.
- `manifest.json`: corpus receipt.

This is still synthetic bootstrapping data. Because the seed episodes follow the nine-role conveyor order, a tiny baseline is a smoke receipt, not a generalization proof. The next lift comes from appending real Hermes/conveyor histories with skipped, repeated, and failed role transitions.
