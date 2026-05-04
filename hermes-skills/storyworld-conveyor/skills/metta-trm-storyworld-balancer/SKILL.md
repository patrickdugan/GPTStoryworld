---
name: metta-trm-storyworld-balancer
description: Use MeTTa-style symbolic world models and TRM balance packets to guide storyworld Monte Carlo calibration, ending reachability repair, secret-route balancing, and bounded-context small-model storyworld revision.
---

# MeTTa/TRM Storyworld Balancer

Use this skill when a storyworld needs holistic balance reasoning but the active model has limited context. The goal is to externalize global structure into compact MeTTa-style facts and TRM packets, then use those packets to guide targeted edits.

This skill is a trial control-plane skill. It does not replace validators, Monte Carlo, quality gates, or the conveyor runner. It frames those artifacts so a smaller model can reason over balancing decisions without rereading the whole world.

## Operating Rule

Artifacts outrank prose. Do not claim balance improvement unless a before/after artifact exists:

- MeTTa facts: `world_balance.metta`
- TRM packet: `trm_balance_packet.json`
- Balance brief: `balance_brief.md`
- Validator/quality/Monte Carlo outputs after any edit

## Minimal Workflow

1. Build a bounded symbolic packet:

```bash
python hermes-skills/storyworld-conveyor/skills/metta-trm-storyworld-balancer/scripts/build_metta_trm_balance_packet.py \
  --storyworld <world.json> \
  --out-dir <run_dir>/metta_trm_balance \
  --quality-report <quality_gate.json> \
  --monte-carlo-report <monte_carlo.txt>
```

2. Read only `balance_brief.md` first. Read `trm_balance_packet.json` only when choosing concrete repairs. Read `world_balance.metta` only when you need symbolic closure or route/gate inspection.

3. Choose one bounded repair objective:

- unreachable ending
- overdominant ending
- under-sampled secret route
- dead-end or zero-inbound encounter
- low pValue/desirability alignment
- weak reaction/effect diversity
- gate threshold mismatch

4. Patch the storyworld or conveyor config using normal storyworld tooling.

5. Rerun validator, Monte Carlo, quality gate, and authoring score. Compare against the original packet. If metrics are unchanged, record a no-op failure.

## Hackathon One-Command Loop

For a Hermes demo where the local 27B model is useful but not reliable as a full autonomous agent, run the deterministic loop and let Qwen provide bounded authoring notes:

```bash
python hermes-skills/storyworld-conveyor/skills/metta-trm-storyworld-balancer/scripts/run_metta_trm_qwen_author_loop.py \
  --storyworld storyworlds/by-week/2026-W11/validated_macbeth.json \
  --out-dir /tmp/hermes_hackathon_metta_qwen_macbeth \
  --mc-runs 300 \
  --qwen-base-url http://127.0.0.1:8081/v1 \
  --qwen-model Qwen3.5-27B.Q4_K_M.gguf
```

This loop:

- builds baseline validator, quality, authoring, Monte Carlo, and MeTTa/TRM packet artifacts;
- applies a deterministic TRM-side pValue/p2Value alignment repair;
- asks Qwen for bounded prose/design notes from the MeTTa/TRM repair packet;
- reruns scores on the candidate world;
- writes `run_summary.json` and `hermes_artifact_report.md`.

Use this when Hermes should launch and review a measurable loop, not when the local model should perform all tool orchestration itself.

## Hackathon Evidence Pack

For the live hackathon framing, prefer the broader demo runner. It compares whole-context pressure against MCP packet budgets, runs the MeTTa/TRM repair loop, and emits a talk-track brief plus scorecard:

```bash
python hermes-skills/storyworld-conveyor/skills/metta-trm-storyworld-balancer/scripts/run_hackathon_storyworld_demo.py \
  --storyworld storyworlds/by-week/2026-W11/validated_macbeth.json \
  --out-dir hermes-skills/storyworld-conveyor/tmp/hackathon_storyworld_demo \
  --context-tokens 32768 \
  --max-encounters 12 \
  --max-new-tokens 768 \
  --mc-runs 120 \
  --qwen-base-url http://127.0.0.1:8081/v1 \
  --qwen-model Qwen3.5-27B.Q4_K_M.gguf
```

Use `--skip-qwen` when the local endpoint is down. That still produces the deterministic evidence pack and makes the demo claim clear: the architecture turns model weakness into bounded local authoring, not autonomous whole-world planning.

The key outputs are:

- `demo_brief.md`
- `demo_scorecard.csv`
- `demo_summary.json`
- `hermes_live_prompt.txt`
- MCP budget manifests under `mcp_preflight/`
- before/after repair receipts under `metta_trm_loop/`

## 9-TRM Encounter Assembly Trajectory Library

When the goal is to train control-plane TRMs that know how to work with an LLM inside the MCP + MeTTa + skill flow, generate the trajectory library:

```bash
python hermes-skills/storyworld-conveyor/skills/metta-trm-storyworld-balancer/scripts/build_encounter_trajectory_library.py \
  --out-dir hermes-skills/storyworld-conveyor/trm_corpus/encounter_assembly_9trm_seed \
  --trajectory-count 1000 \
  --target-tokens 100000 \
  --seed 23
```

This emits:

- `trajectory_library.jsonl`: full structured trajectories.
- `trm_control_rows.jsonl`: normalized `state/tools/action/meta` rows for router/control TRMs.
- `sft_messages.jsonl`: chat-shaped rows for distillation or prompt policy tuning.
- `world_control_facts.metta`: compact symbolic control facts.
- `train.jsonl` / `val.jsonl`: train/validation split.
- `train_manifest.json`: hard-cap training handoff; do not launch training outside a cap wrapper.

The nine TRM roles are documented in `references/encounter_assembly_9trm.md`.

## Master Control Planner Episodes

After the role-local trajectory library exists, build episode-level rows for a master planner that learns which TRM role to invoke next:

```bash
python hermes-skills/storyworld-conveyor/skills/metta-trm-storyworld-balancer/scripts/build_master_planner_episodes.py \
  --trajectory-library hermes-skills/storyworld-conveyor/trm_corpus/encounter_assembly_9trm_seed/trajectory_library.jsonl \
  --out-dir hermes-skills/storyworld-conveyor/trm_corpus/master_control_planner_seed \
  --context-budget-tokens 8192
```

This emits:

- `trajectory_episodes.jsonl`: multi-step planner episodes.
- `master_control_rows.jsonl`: `global_state/tools -> next_role` rows.
- `train.jsonl` / `val.jsonl`: row views derived from an episode-disjoint split.
- `episode_train.jsonl` / `episode_val.jsonl`: sequence-level split.
- `manifest.json`: corpus receipt.

Train a tiny baseline receipt:

```bash
python hermes-skills/storyworld-conveyor/skills/metta-trm-storyworld-balancer/scripts/train_master_planner_baseline.py \
  --train hermes-skills/storyworld-conveyor/trm_corpus/master_control_planner_seed/train.jsonl \
  --val hermes-skills/storyworld-conveyor/trm_corpus/master_control_planner_seed/val.jsonl \
  --out-dir hermes-skills/storyworld-conveyor/trm_runs/master_control_planner_tiny
```

This is still a control-policy baseline, not a full neural TRM. Use it as a fast receipt before launching heavier capped training.

## Auto-Research Loop

Use the auto-research loop to collect real storyworld diagnostic states for master-planner training. This loop does not patch storyworld files. It compares the tiny planner's proposed next role against a deterministic oracle derived from context budget, schema/connectivity, reader semantics, secret-route, option, reaction, and effect diagnostics:

```bash
python hermes-skills/storyworld-conveyor/skills/metta-trm-storyworld-balancer/scripts/run_master_planner_auto_research_loop.py \
  --out-dir hermes-skills/storyworld-conveyor/trm_corpus/master_control_planner_auto_research_local_001 \
  --iterations 8 \
  --context-budget-tokens 8192 \
  --planner model
```

This emits:

- `auto_research_rows.jsonl`: trainable `state/tools -> oracle_role` rows.
- `trajectory_episodes.jsonl`: one-step episode rows.
- `planner_predictions.jsonl`: planner proposal vs deterministic oracle.
- `steps/*`: metrics, planner state, and role artifact for each iteration.

For the native symbolic teacher policy, use:

```bash
python hermes-skills/storyworld-conveyor/skills/metta-trm-storyworld-balancer/scripts/run_master_planner_auto_research_loop.py \
  --out-dir hermes-skills/storyworld-conveyor/trm_corpus/master_control_planner_native_schema_local_001 \
  --iterations 8 \
  --context-budget-tokens 8192 \
  --planner native
```

Native schema references:

- `references/native_master_control_schema.md`
- `references/native_master_control_schema.metta`

## MeTTa Modeling Contract

Use MeTTa as a compact structural model, not as decorative syntax. The generated atoms should support questions like:

- Which endings are terminal?
- Which encounters have too few incoming routes?
- Which options carry secret tags or gate predicates?
- Which reactions move the variables that gates depend on?
- Which variables are overused, unused, or missing pValue mirrors?
- Which endings are likely under-reachable based on topology and Monte Carlo?

Core atom families:

```metta
(Storyworld <title>)
(Encounter <encounter_id>)
(Terminal <encounter_id>)
(Option <encounter_id> <option_id>)
(Consequence <encounter_id> <option_id> <target_encounter_id>)
(Reaction <encounter_id> <option_id> <reaction_index>)
(Effect <encounter_id> <option_id> <reaction_index> <property_id> <operator> <delta>)
(GateRef <encounter_id> <option_id> <property_id>)
(SecretCandidate <encounter_id> <option_id> <reason>)
(ReachabilityIssue <encounter_id> <issue>)
(BalanceSignal <signal_name> <value>)
(RepairTarget <target_id> <repair_type> <priority>)
```

See `references/metta_balance_atoms.md` for the fuller atom vocabulary and repair patterns.

## TRM Packet Contract

Each TRM packet must separate four roles:

- `router`: chooses which balance defect to inspect next.
- `verifier`: predicts whether an edit will improve the declared metric.
- `repair`: proposes the smallest schema-valid edit family.
- `commit_veto`: accepts only if validator plus metric deltas support the change.

Required packet fields:

```json
{
  "storyworld": "...",
  "observations": [],
  "balance_signals": {},
  "repair_targets": [],
  "trm_roles": {
    "router": [],
    "verifier": [],
    "repair": [],
    "commit_veto": []
  }
}
```

## Monte Carlo Calibration Use

When Monte Carlo shows poor ending distribution:

- Do not globally increase randomness first.
- Identify which gate/effect variables control the missing or dominant endings.
- Use MeTTa facts to find earlier options that can legitimately move those variables.
- Add or rebalance effects upstream, then rerun Monte Carlo.
- Prefer small threshold/effect adjustments over adding unforeshadowed secret shortcuts.

## Small-Context Discipline

For local 3B/9B or 4-bit runs:

- Never paste a full 80+ encounter world into the model.
- Use `balance_brief.md` as the default context.
- Use per-encounter MCP cards for the edit target and nearest neighbors.
- Use `world_balance.metta` for symbolic closure and routing, not full prose summarization.
- Keep each repair objective single-metric unless the packet explicitly shows a coupled defect.

## Failure Classes

Write `failure.md` if any of these occur:

- `no_storyworld_json`: no schema-shaped JSON was produced.
- `no_metric_delta`: edits did not change Monte Carlo or quality metrics.
- `unsupported_schema`: the target world uses a schema variant not understood by the script.
- `context_overflow`: the packet is still too large for the intended model.
- `tool_following_failure`: Hermes/model narrated instead of producing artifacts.

## Validation

This skill may propose repair targets, but it never certifies them. Final certification still requires the normal storyworld workflow:

- `sweepweave_validator.py`
- `storyworld_quality_gate.py`
- `monte_carlo_rehearsal.py`
- `audit_storyworld_acceptance.py`
- `score_storyworld_authoring.py`
