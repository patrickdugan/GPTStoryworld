# Master Control Planner Curriculum

## Thesis

The 9-TRM mesh can be trained upward from role-local control into a master control planner. The LLM is not the planner. The LLM is a bounded proposal source that is called by the planner through typed trajectories.

The master planner learns to answer:

- Which trajectory should be run next?
- Which TRM role owns the decision?
- What is the smallest MCP packet needed?
- Should the LLM be asked for prose, options, reactions, clues, rationale, or nothing?
- Which verifier signal decides commit, retry, shrink-context, or veto?

This is the control-plane architecture for making 9B/27B useful in storyworld construction without asking them to behave like autonomous 70B+ agents.

## Existing Corpus

The current seed pack already contains:

- `trajectory_library.jsonl`: full trajectory rows with role, state, LLM contract, metrics, and labels.
- `trm_control_rows.jsonl`: compact `state/tools/action/meta` rows for role-local control models.
- `sft_messages.jsonl`: chat-shaped distillation rows for a small LLM or Hermes skill policy.
- `world_control_facts.metta`: symbolic facts for trajectory routing and closure checks.
- `train.jsonl` / `val.jsonl`: split for supervised control-policy training.

Current scale:

- Rows: `1000`
- Estimated tokens: `284129`
- Roles: `9`

## Planner Episode Shape

A master-planner episode should group several role-local trajectory rows into one conveyor decision sequence.

```json
{
  "episode_id": "episode_000123",
  "world_id": "macbeth_factory_run_04",
  "model_tier": "9B_Q4",
  "context_budget_tokens": 8192,
  "objective": "repair_secret_route_reachability",
  "initial_metrics": {
    "validator_errors": 0,
    "authoring_score": 0.71,
    "secret_reachability": 0.01,
    "ending_entropy": 1.12
  },
  "steps": [
    {
      "role_id": "mcp_context_router",
      "state_ref": "row_id",
      "chosen_action": "SELECT_MCP_PACKET",
      "llm_call_type": "none",
      "accepted": true
    },
    {
      "role_id": "gate_secret_route_designer",
      "state_ref": "row_id",
      "chosen_action": "ASK_LLM_CLUE_LINES",
      "llm_call_type": "clue_lines",
      "accepted": true
    },
    {
      "role_id": "commit_veto_controller",
      "state_ref": "row_id",
      "chosen_action": "COMMIT_PATCH",
      "llm_call_type": "none",
      "accepted": true
    }
  ],
  "final_metrics": {
    "validator_errors": 0,
    "authoring_score": 0.74,
    "secret_reachability": 0.08,
    "ending_entropy": 1.42
  },
  "episode_label": {
    "success": true,
    "best_next_role": "stop",
    "failure_class": "none",
    "reward": 0.81
  }
}
```

## Training Targets

Train role-local TRMs first:

- `role_id -> chosen_action`
- `(state, tools) -> chosen_action`
- `(failure_mode, metrics_before) -> repair_target`
- `(metrics_before, metrics_after) -> commit_or_veto`

Then train the master planner:

- `(global_state, metric_defect, budget) -> next_role`
- `(global_state, next_role) -> context_packet_spec`
- `(global_state, next_role) -> llm_call_type`
- `(trajectory_history, validator_delta) -> continue_or_stop`
- `(episode_history, metrics_delta) -> reward`

## Why 9B Becomes Plausible

9B should not be asked to create a full storyworld in one pass. It can plausibly supply local material when all of these are fixed outside the model:

- target encounter ID
- nearby context card
- current variables and desired deltas
- option/reaction slot count
- stable consequence IDs
- forbidden global rewrites
- output shape
- verifier target

The TRM mesh owns the hard control problem. The 9B model supplies narrow imaginative samples.

## 9B Factory Mode

Use 9B only in these trajectory calls:

- `ASK_LLM_BOUNDED_DRAFT`: one encounter paragraph or rewrite.
- `ASK_LLM_OPTION_SET`: 3-5 option candidates with intended variable deltas.
- `ASK_LLM_REACTION_TEXT`: local reaction text under fixed outcome slots.
- `ASK_LLM_CLUE_LINES`: foreshadowing lines for a known secret/synthesis gate.
- `ASK_LLM_RATIONALE`: short explanation of theme or character pressure.

Do not use 9B for:

- whole-world planning
- schema mechanics
- acceptance testing
- commit decisions
- self-certification
- unbounded lore expansion

## Data Pool Expansion

The seed corpus is synthetic and useful for bootstrapping. The high-value next data comes from real conveyor histories:

- Hermes prompt packets and raw model outputs.
- Parse failures and repaired outputs.
- Validator, Monte Carlo, quality-vector, and reader-harness deltas.
- Human/Codex commit decisions.
- Context-budget failures.
- No-op repair loops.
- Successful secret-route repairs.

The first tiny master-planner baseline makes this concrete:

- Corpus: `hermes-skills/storyworld-conveyor/trm_corpus/master_control_planner_seed/`
- Run: `hermes-skills/storyworld-conveyor/trm_runs/master_control_planner_tiny/`
- Episode-disjoint validation: `13/99 = 0.1313` next-role accuracy after removing direct role-order leakage.

Interpretation: role-local TRMs are already easy to train from the seed rows, but the master planner needs real adaptive histories with skipped roles, repeated repair loops, and failed LLM calls. The synthetic rows define the format; real conveyor traces teach the policy.

The first local auto-research loop produced:

- Run: `hermes-skills/storyworld-conveyor/trm_corpus/master_control_planner_auto_research_local_001/`
- Rows: `16`
- Tiny planner agreement before augmentation: `0/16`
- Objectives discovered: `fit_context_budget`, `repair_reader_semantics`, `diversify_effect_scripts`
- Augmented run: `hermes-skills/storyworld-conveyor/trm_runs/master_control_planner_augmented_local_001/`
- Held-out auto accuracy after augmentation: `2/3`

Interpretation: a small amount of real diagnostic supervision corrected context-routing and reader-semantics routing, but did not yet fix effect-script routing for Nudge monoculture.

The fix is to stop treating the weak learner as the control-plane floor. Add a native symbolic teacher schema first:

- Schema: `hermes-skills/storyworld-conveyor/skills/metta-trm-storyworld-balancer/references/native_master_control_schema.md`
- MeTTa-style atoms: `hermes-skills/storyworld-conveyor/skills/metta-trm-storyworld-balancer/references/native_master_control_schema.metta`
- Native run: `hermes-skills/storyworld-conveyor/trm_corpus/master_control_planner_native_schema_local_001/`
- Native planner agreement: `16/16 = 1.0`

Interpretation: the native reasoning schema supplies the fast, correct first move. The TRMs should train against this teacher policy plus real repair outcomes, then learn exceptions where the native rules are too rigid.

Each real run should append:

- `trajectory_episode.jsonl`: episode-level planner rows.
- `llm_calls.jsonl`: bounded LLM request/response rows.
- `verifier_deltas.jsonl`: before/after metrics.
- `commit_veto.jsonl`: accepted/rejected patches with reason.

## Reward Model

Use a mixed reward instead of one scalar benchmark:

```text
reward =
  0.25 * validator_pass_delta
+ 0.20 * authoring_score_delta
+ 0.15 * ending_entropy_delta
+ 0.15 * target_route_reachability_delta
+ 0.10 * text_quality_delta
+ 0.10 * context_efficiency
+ 0.05 * repair_cost_penalty_inverse
```

Hard caps:

- Any structural validator failure caps reward at `0.20`.
- Any no-op commit caps reward at `0.30`.
- Any context overflow caps reward at `0.40`.
- Any unparseable LLM output caps the LLM-call step reward at `0.10`.

## Demo Claim

Safe claim:

> We are training small control models to decide how a Hermes skill should use a bounded LLM inside a MeTTa/MCP/verifier storyworld factory. The resulting architecture makes 9B/27B models useful as local proposal engines rather than pretending they can own the whole creative-engineering stack.

Unsafe claim until additional evidence exists:

> A 9B model autonomously builds high-quality long storyworlds.
