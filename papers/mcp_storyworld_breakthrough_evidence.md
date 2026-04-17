# MCP-Bounded Storyworld Breakthrough Evidence Memo

Date: 2026-04-17

## Question

Did we already demonstrate that a tiny model with a roughly 6k token context budget could use MCP-style bounded retrieval / packetization to produce a much larger storyworld JSON artifact?

## Short answer

Yes. The strongest evidence is a cluster of work on **March 15-16, 2026**, followed by a clearer scaling and routing validation pass on **March 29-30, 2026**.

The most paper-worthy claim is not merely "small model made JSON." It is:

> A small model in the 1.5B-3B class, operating under a bounded context budget of about 6k tokens, can participate in a phased MCP-mediated storyworld generation workflow that emits structured storyworld artifacts far larger than its prompt window, because the world state is externalized into indexed cards / packets rather than loaded into prompt context.

## Chronology

### 1. Breakthrough window: March 15-16, 2026

Primary session:

- `codex-chat-sessions/sessions/2026/03/15/rollout-2026-03-15T16-50-56-019cf30d-3b1c-7d71-af33-1ac57203098b.jsonl`

Most important evidence from that window:

1. The bounded-context configuration was made concrete in:
   - `hermes-skills/storyworld-conveyor/sample_data/qwen2b_4gb_context_port.json`
   - `hermes-skills/storyworld-conveyor/sample_data/qwen2b_4gb_context_port_posttrain.json`
2. Those configs explicitly set:
   - `context_budget_tokens: 6144`
   - `reserve_output_tokens: 768`
   - `planning_card_tokens: 700`
   - `max_new_tokens: 96`
3. The small-model/MCP approach was formalized in:
   - `codex-skills/small-storyworld-builder/SKILL.md`
4. That skill states the method directly:
   - small local models in the 1.5B-3B range
   - MCP bounded-context cards
   - no full-world prompt loading

### 2. Immediate user feedback showing it was already working

Repo-local session history shows that by **2026-03-16 01:46:18 -03:00** the discussion had already moved from "can it work?" to quality tuning:

- `the skill works ok with GLM5 producing a storyworld however needs per encounter avg. option/reaction/effect guidelines to be tighter it produced just one option per encounter`

Then at **2026-03-16 01:47:22 -03:00**:

- `it included the options but the visibility filters were too tight should have a guideline that increases visibility/accessability filters for only some small % of options later in the storyworld`

Source:

- `codex-chat-sessions/history.jsonl`

This is important evidence. It suggests the breakthrough had already happened. The conversation was no longer about first-principles feasibility, but about tuning encounter richness and visibility gating after a generated storyworld already existed.

### 3. Same-night artifact evidence for large outputs

Three storyworld JSON files were modified on **2026-03-16 01:11:33 AM**:

- `storyworlds/france_to_germany_machiavellian_p.json` - 76,821 bytes
- `storyworlds/hive_to_glam_machiavellian.json` - 115,080 bytes
- `storyworlds/shadow_to_bio_grudger.json` - 116,343 bytes

Interpretation:

- The first artifact is very close to the remembered "80k JSON" claim.
- The latter two exceed it.
- This does not prove every byte was authored in one pass by the tiny model, but it does strongly support the claim that the bounded pipeline was already producing large structured storyworld outputs well beyond the model's direct context window.

### 4. Commit evidence that the method landed in code at the same time

Relevant commits:

- `bb01af628794e5e632413ed27ba673840c58b2a0` - 2026-03-16 00:04:26 -0300
  - added `swmd_mcp_phase_pipeline.py`
  - added `swmd_mcp_iterate_8k.py`
  - added `qwen2b_4gb_context_port*.json`
  - added the `storyworld-conveyor` package and related tooling
- `802d667c9bec5d418ffa75259104fbd931c382e4` - 2026-03-16 00:11:56 -0300
  - added `codex-skills/small-storyworld-builder/SKILL.md`

Interpretation:

- The method was not just discussed informally.
- It was codified into reusable skills, configs, and pipeline scripts on the same night as the artifact and user-feedback evidence.

## Follow-up window: March 29-30, 2026

Primary session:

- `codex-chat-sessions/sessions/2026/03/29/rollout-2026-03-29T20-49-32-019d3c00-b55c-75e1-a60c-3dcfe06ea8c4.jsonl`

This looks like the second-stage maturation pass rather than the original breakthrough.

Important evidence:

1. The user explicitly asked for a scalability probe with a small model:
   - `let's have the Qwen 2B make a really simple storyworld conceptually but with a lot of encounters to test how scalable this is`
2. The repo added a concrete MCP/TRM smoke path:
   - `hermes-skills/storyworld-conveyor/scripts/run_storyworld_mcp_trm_smoke.py`
3. The smoke outputs reported a clean routing result:
   - run id: `mcp_trm_smoke_qwen35_2b`
   - status: `completed`
   - model: `Qwen3.5-2B-HF`
   - `tool_accuracy: 1.0`
   - `route_correct: 3`
   - `route_incorrect: 0`
4. A later handoff described a large abstract-letter world target and reported:
   - target around 80 encounters
   - realized 84 encounters

Interpretation:

- March 29-30 is best understood as the "make it legible, benchmarkable, and reproducible" phase.
- March 15-16 remains the more likely origin point for the actual breakthrough.

## Why this may deserve a paper

This work has the shape of a publishable systems/result note because it combines:

1. A concrete constraint:
   - roughly 6k-token budget on a tiny local model
2. A mechanism:
   - MCP-style retrieval / packetization / phased generation
3. A meaningful outcome:
   - storyworld artifacts materially larger than the prompt window
4. A practical demonstration:
   - local runs, configs, generated artifacts, and later route-accuracy metrics

The paper claim should be framed as **context externalization and control-plane routing**, not as "the small model internally held an 80k world in context."

## Clean paper framing

Working title idea:

- `Bounded-Context Storyworld Generation: MCP Packetization Lets Tiny Models Emit Large Structured Worlds`

Core claim:

- A tiny model can act as a planner/router/phase actor over indexed world cards and bounded packets, allowing the overall system to synthesize large structured storyworld outputs without loading the whole world into prompt context.

What to emphasize:

1. Context-budget discipline
2. Externalized world memory
3. Structured intermediate packets
4. Phased generation instead of monolithic prompting
5. Observable artifact size and route accuracy

## What still needs replication before writing the paper in earnest

1. Re-run the March 15-16 path on a held-out storyworld with preserved configs.
2. Measure exact token budgets per phase instead of relying only on config ceilings.
3. Record end-to-end artifact statistics:
   - bytes
   - encounter count
   - options/reactions/effects counts
4. Compare against a naive long-prompt baseline.
5. Separate "system produced large JSON" from "small model directly authored every final block."

## Best evidence register

- Breakthrough session:
  - `codex-chat-sessions/sessions/2026/03/15/rollout-2026-03-15T16-50-56-019cf30d-3b1c-7d71-af33-1ac57203098b.jsonl`
- Follow-up scaling session:
  - `codex-chat-sessions/sessions/2026/03/29/rollout-2026-03-29T20-49-32-019d3c00-b55c-75e1-a60c-3dcfe06ea8c4.jsonl`
- Session history confirmations:
  - `codex-chat-sessions/history.jsonl`
- Small-model skill:
  - `codex-skills/small-storyworld-builder/SKILL.md`
- 6k-budget configs:
  - `hermes-skills/storyworld-conveyor/sample_data/qwen2b_4gb_context_port.json`
  - `hermes-skills/storyworld-conveyor/sample_data/qwen2b_4gb_context_port_posttrain.json`
- Large output artifacts:
  - `storyworlds/france_to_germany_machiavellian_p.json`
  - `storyworlds/hive_to_glam_machiavellian.json`
  - `storyworlds/shadow_to_bio_grudger.json`
- Follow-up MCP/TRM smoke output root:
  - `hermes-skills/storyworld-conveyor/context_port_runs/mcp_trm_smoke_qwen35_2b`

## Bottom line

If the question is "did the breakthrough happen?", the answer is **yes, probably on March 15-16, 2026**.

If the question is "what is the paper-worthy contribution?", the answer is:

- **bounded-context MCP storyworld generation with tiny models**

If the question is "what is the next step?", it is:

- turn this memo into a paper outline plus a replication checklist and figure plan.
