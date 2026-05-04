# Master Planner Auto-Research Loop

This run collects real storyworld diagnostic states for the master control planner.

- Iterations: `8`
- Context budget: `8192`
- Model tier: `9B_Q4`
- Planner agreement: `0/16 = 0.0`

Files:

- `auto_research_rows.jsonl`: trainable `state/tools -> oracle_role` rows.
- `trajectory_episodes.jsonl`: one-step episode rows compatible with the planner episode schema.
- `planner_predictions.jsonl`: tiny planner proposal versus deterministic oracle.
- `steps/*`: per-iteration metrics, planner state, and role artifact.

This loop intentionally does not patch storyworld files. It collects supervision for the master planner.
