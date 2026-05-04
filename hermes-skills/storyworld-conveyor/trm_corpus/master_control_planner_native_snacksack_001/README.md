# Master Planner Auto-Research Loop

This run collects real storyworld diagnostic states for the master control planner.

- Iterations: `10`
- Context budget: `32768`
- Model tier: `27B_Q4`
- Planner: `native`
- Planner agreement: `20/20 = 1.0`

Files:

- `auto_research_rows.jsonl`: trainable `state/tools -> oracle_role` rows.
- `trajectory_episodes.jsonl`: one-step episode rows compatible with the planner episode schema.
- `planner_predictions.jsonl`: selected planner proposal versus deterministic oracle, with native/model traces.
- `steps/*`: per-iteration metrics, planner state, and role artifact.

This loop intentionally does not patch storyworld files. It collects supervision for the master planner.
