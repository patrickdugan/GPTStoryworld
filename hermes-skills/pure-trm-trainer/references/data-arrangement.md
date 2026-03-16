# Data Arrangement

## Goal

Arrange training data so the controller generalizes across environments, not just across repeated rows from one environment.

## Canonical Row Shape

Normalize every row into:

```json
{
  "state": "{\"encounter_id\":\"page_01\",\"turn\":2}",
  "tools": ["opt_a", "opt_b", "WAIT"],
  "action": "opt_b",
  "meta": {
    "source_name": "storyworld-trm-play",
    "world_id": "003_macbeth",
    "episode": 4,
    "turn": 2
  }
}
```

Rules:

- Keep `state` compact and decision-relevant.
- Keep `tools` limited to the candidate actions the controller really had.
- Keep `action` as the chosen tool or action id.
- Keep `meta` rich enough for later audits.

## What To Include

- TRM play traces:
  - best source for action selection and transition control
- Monte Carlo summaries:
  - good for rebalance targets and controller priorities
- verifier logs:
  - good for failure labels, rejected actions, and secret-ending reachability tasks
- reasoning traces:
  - use only when they expose decision state, candidate options, critiques, or repair logic
- skill-run logs:
  - useful when they contain structured actions and outcomes rather than loose prose

## What To Exclude

- free-form prose that does not map to a decision
- duplicated rows from repeated retries unless retry behavior is the target
- machine-local paths inside hashed or canonical payloads
- mixed train/validation rows from the same environment slice when generalization matters

## Split Strategy

Prefer these validation strategies, in order:

1. Hold out whole environments.
2. Hold out whole runs within an environment family.
3. Hold out episodes only when the environment count is too small.

Do not rely on random row splits alone for cross-environment claims.

## Weighting Guidance

- upweight rare but important failures:
  - invalid transitions
  - dead-end recoveries
  - special ending hits
  - constraint repairs
- downweight bulk easy rows if they dominate one environment
- keep a manifest of source counts before and after dedupe

## Reasoning Trace Guidance

Use reasoning traces when they help the controller choose or reject actions.

Good fields:

- observation
- condensed world state
- candidate actions
- chosen action
- verifier critique
- repair rationale

Bad fields:

- decorative self-talk
- repeated narration of known facts
- long chain-of-thought not tied to a decision

## Multi-Env Generalization

When combining datasets from multiple environments:

- preserve a `source_name` and `world_id`
- keep action ids stable within each environment family
- standardize the `state` schema where possible
- avoid teaching the model to depend on one environment's local naming quirks

If envs use different action namespaces, keep the raw ids in `tools/action` and add normalized tags only in `meta`.
