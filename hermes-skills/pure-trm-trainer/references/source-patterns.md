# Source Patterns

## TRM Play Root

Use this for AICOO or Storyworld TRM setup outputs with `worlds/*/trm_traces.jsonl`.

Example source entry:

```json
{
  "name": "storyworld-trm-play",
  "type": "trm_play_root",
  "path": "D:/Research_Engine/runs/storyworld_trm_setup/storyworld-trm-setup-sample"
}
```

This is the cleanest source for controller training because candidate actions and picks are already present.

## Normalized JSONL

Use this when another tool already emitted `state/tools/action`.

Example source entry:

```json
{
  "name": "normalized-controller-rows",
  "type": "jsonl",
  "path": "D:/Research_Engine/datasets/controller_rows.jsonl",
  "mode": "normalized"
}
```

## Reasoning Trace JSONL

Use this for logs that contain structured decisions but are not yet normalized.

Example source entry:

```json
{
  "name": "oracle-reasoning",
  "type": "jsonl",
  "path": "C:/projects/GPTStoryworld/results/20260205_170220/codex_oracle_reasoning.jsonl",
  "mode": "reasoning_trace",
  "state_fields": ["question", "state", "world_state", "observation"],
  "tools_field": "candidate_tools",
  "tools_default": ["WAIT"],
  "action_field": "chosen_action",
  "action_default": "WAIT",
  "meta_fields": ["run_id", "episode", "turn"]
}
```

Use this only when the fields are stable enough to map into a controller row.

## Skill And Log Analysis

If the user wants to mine skills, logs, or traces:

- identify the decision boundary first
- extract only the fields that affect action choice or verification
- convert them into normalized rows
- keep the original source path in `meta`

Good examples:

- verifier reject/accept decisions
- rebalance packets paired with before/after action choices
- reasoning traces with explicit candidate actions and a chosen action

Weak examples:

- long markdown notes without action labels
- chat transcripts with no stable action field
- outputs where the "decision" is just a paragraph

## Hermes Run

After the corpus spec is ready:

```powershell
python hermes-skills/storyworld-conveyor/scripts/run_trm_trainer_hermes.py `
  --config hermes-skills/storyworld-conveyor/sample_data/trm_trainer_hermes_safe.json
```

Use `--dry-run` first when the user is still curating data paths or trainer overrides.
