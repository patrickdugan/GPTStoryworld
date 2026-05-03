# 9-TRM Encounter Assembly Trajectory Library

This pack trains control-plane TRMs for a Hermes storyworld skill flow. The LLM is treated as a bounded component that supplies local prose, option candidates, clue lines, or rationale. The TRMs decide what to ask for, what context to fetch, how to translate prose into mechanics, and when to commit or veto.

## Nine TRMs

- `mcp_context_router`: Select the smallest context packet the LLM needs for one encounter edit.
- `world_state_summarizer`: Compress MeTTa facts, ledger deltas, character beliefs, and threshold pressure into a state card.
- `llm_prompt_composer`: Turn the state card into a strict bounded authoring request.
- `option_manifold_planner`: Choose option archetypes that expose genuine tradeoffs and variable deltas.
- `reaction_dynamics_mapper`: Map each option to success, mixed, and failure reactions with character-specific consequences.
- `effect_script_synthesizer`: Convert narrative intent into effect operators, pValues, p2Values, and non-zero constants.
- `gate_secret_route_designer`: Design visibility, performability, clue, and threshold logic for secret or synthesis paths.
- `validator_repair_critic`: Classify validator, quality, Monte Carlo, and authoring-score defects into typed repair targets.
- `commit_veto_controller`: Accept, retry, reroute, or shrink context based on measured deltas and parse stability.

## Files

- `trajectory_library.jsonl`: full structured rows.
- `trm_control_rows.jsonl`: normalized `state/tools/action/meta` rows for router/control training.
- `sft_messages.jsonl`: chat-shaped rows for distilling the control policy through an LLM if needed.
- `world_control_facts.metta`: compact symbolic control facts.
- `train.jsonl` and `val.jsonl`: shuffled control-row split.
- `role_action_matrix.csv`: coverage by role and chosen action.
- `train_manifest.json`: safe training handoff with caps and checkpoint cadence.

Rows: 1000

Estimated tokens: 284129
