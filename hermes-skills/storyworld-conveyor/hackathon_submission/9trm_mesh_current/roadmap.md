# Hermes Creativity Hackathon Roadmap: 9-TRM Mesh For Storyworld Encounter Assembly

## Demo Thesis

The deliverable is not "27B suddenly becomes a strong autonomous storyworld author." The deliverable is that Hermes skills can make smaller models useful inside a complex creative-engineering workflow by decomposing storyworld construction into a MeTTa + MCP + TRM control mesh.

The LLM supplies bounded local inputs: scene text, option candidates, reaction phrasing, clue lines, and ambiguity resolution. The TRMs own routing, context choice, schema mechanics, verifier repair, and commit/veto.

## Current Evidence Already In Repo

- Demo evidence runner: `0ac5f7c6 Add hackathon storyworld demo evidence runner`.
- 9-TRM trajectory library: `0baaad79 Add 9 TRM encounter assembly trajectory library`.
- Seed corpus: `hermes-skills/storyworld-conveyor/trm_corpus/encounter_assembly_9trm_seed/`.
- Corpus scale: 1000 trajectories, 900/100 train/val split, about 284k estimated tokens.
- Control views: full trajectory rows, normalized `state/tools/action/meta` rows, chat/SFT rows, MeTTa control facts.
- Safe training manifest: `train_manifest.json` says training is not yet launched and requires caps.

## Current Status Update

- Tiny per-role control baseline trained: `hermes-skills/storyworld-conveyor/trm_runs/encounter_assembly_9trm_tiny_mesh/`.
- Held-out action accuracy: 96/100 = 0.96.
- Submission pack built: `hermes-skills/storyworld-conveyor/hackathon_submission/9trm_mesh_current/`.
- Scope note: this is a trained tiny control-policy mesh, not a full neural TRM/QLoRA run.

## Nine TRMs To Show

- `mcp_context_router`: selects the smallest packet.
- `world_state_summarizer`: builds the state card from MeTTa facts and ledger deltas.
- `llm_prompt_composer`: asks the LLM only for the missing bounded component.
- `option_manifold_planner`: gets or selects option archetypes.
- `reaction_dynamics_mapper`: maps options to success/mixed/failure reactions.
- `effect_script_synthesizer`: turns narrative intent into effects, pValues, and p2Values.
- `gate_secret_route_designer`: designs clue and threshold logic.
- `validator_repair_critic`: turns verifier failures into typed repair targets.
- `commit_veto_controller`: commits, retries, shrinks context, or reroutes.

## Tonight Minimum Deliverable

1. Train a tiny control-policy baseline from `trm_control_rows.jsonl`.
2. Emit a model/eval receipt with per-role action accuracy and confusion counts.
3. Run the hackathon evidence command on the Macbeth demo world.
4. Produce a final bundle folder with README, corpus manifest, training receipt, demo brief, scorecard, and a short talk-track.

This is enough to honestly say: "We trained small control models on a 9-TRM mesh curriculum and used that mesh to constrain local LLM storyworld assembly."

Do not claim full neural TRMs or QLoRA success unless the corresponding run artifacts exist.

## Timeboxed Plan

### 0-20 minutes: Freeze Submission Story

- Use the phrase "trained small control models" if tonight's run is a tiny classifier or lightweight baseline.
- Use "TRM training curriculum" for the 284k-token corpus.
- Reserve "neural TRM trained" for a real capped trainer run with checkpoints.

### 20-70 minutes: Tiny Mesh Training Receipt

Target output:

- `trm_runs/encounter_assembly_9trm_tiny_mesh/model_summary.json`
- `trm_runs/encounter_assembly_9trm_tiny_mesh/eval.json`
- `trm_runs/encounter_assembly_9trm_tiny_mesh/predictions.jsonl`
- `trm_runs/encounter_assembly_9trm_tiny_mesh/events.jsonl`

Required metrics:

- Overall action accuracy.
- Per-role accuracy.
- Confusion counts for `COMMIT_PATCH`, `VETO_AND_RETRY`, `SHRINK_CONTEXT`, and LLM-request actions.
- Example predictions for at least one encounter assembly path.

Safety:

- Keep run under the manifest caps: 2048 MB RAM, 50 percent CPU, 50 MB/s IO.
- If no hard-cap path is available, run only a dry-run trainer receipt and do not call it trained.

### 70-130 minutes: Mesh Demo Run

Run:

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

If the endpoint is down:

```bash
python hermes-skills/storyworld-conveyor/skills/metta-trm-storyworld-balancer/scripts/run_hackathon_storyworld_demo.py \
  --storyworld storyworlds/by-week/2026-W11/validated_macbeth.json \
  --out-dir hermes-skills/storyworld-conveyor/tmp/hackathon_storyworld_demo \
  --context-tokens 32768 \
  --max-encounters 12 \
  --max-new-tokens 768 \
  --mc-runs 120 \
  --skip-qwen
```

Minimum metrics to show:

- Whole-context token estimate.
- MCP worst packet estimate and overflow count.
- Before/after authoring score.
- Baseline and candidate failure classes.
- Path to MeTTa/TRM packet artifacts.

### 130-190 minutes: Submit Bundle

Create:

- `hackathon_submission/README.md`
- `hackathon_submission/demo_brief.md`
- `hackathon_submission/architecture.md`
- `hackathon_submission/evidence_manifest.json`
- `hackathon_submission/sample_trajectory.json`
- `hackathon_submission/sample_prediction.json`

Suggested title:

`Hermes 9-TRM Creative Skill Mesh: Making 27B Viable For Bounded Storyworld Assembly`

### 190-240 minutes: Rehearsal

Talk track:

1. A whole storyworld is too much context and too much control burden for a 27B OSS model.
2. MCP turns the world into encounter packets.
3. MeTTa turns the global design into compact symbolic control facts.
4. Nine tiny TRM/control models decide how to work the LLM.
5. Validators and commit/veto prevent compliance theater.
6. Result: smaller models participate in a complex creative-engineering skill, rather than pretending to be the whole engineer.

## Claims Matrix

Safe to claim now:

- A 9-TRM encounter assembly curriculum exists.
- It has 1000 trajectories and about 284k estimated tokens.
- It includes normalized control rows and chat/SFT rows.
- It decomposes LLM use into bounded local requests.

Safe after tiny training receipt:

- Small trained control models can route actions inside the mesh on held-out rows.
- Per-role control policies can be evaluated independently.

Unsafe unless separately evidenced:

- The 27B model autonomously builds high-quality 80-encounter worlds.
- Neural TRMs outperform larger LLMs on storyworld construction.
- The trained mesh generalizes beyond the synthetic seed corpus.

## Best Hackathon Framing

"I am not trying to make the small model smarter by wishing harder. I am reducing the creative task into a mesh of small learned control policies, symbolic state, memory packets, and validators. The LLM becomes a local imagination component. The skill is the architecture."
