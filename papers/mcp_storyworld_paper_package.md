# MCP Storyworld Paper Package

Date: 2026-04-17

Companion evidence memo:

- `papers/mcp_storyworld_breakthrough_evidence.md`

## Working titles

1. `Bounded-Context Storyworld Generation with MCP Packetization`
2. `Tiny Models, Large Worlds: MCP-Mediated Storyworld Synthesis Beyond Prompt Window Scale`
3. `Externalized World Memory for Storyworld Generation with Small Models`

## One-sentence claim

A small model in the 1.5B-3B range can participate in generation of large structured storyworld artifacts under a roughly 6k-token context budget when world state is externalized into MCP-accessed cards or packets and generation is split into bounded phases.

## Abstract draft

Large structured narrative artifacts are usually treated as a long-context generation problem, which makes them expensive and brittle for small local models. We describe a bounded-context storyworld generation workflow in which world state is not kept in prompt context, but externalized into indexed cards and phase-specific packets accessed through an MCP-style retrieval layer. In our local GPTStoryworld stack, this design let small models in the 1.5B-3B range operate under a context budget of roughly 6k tokens while still contributing to production of storyworld JSON artifacts much larger than the model context window. Repo evidence from March 15-16, 2026 shows the method landing as reusable code and configs, including a 6144-token port profile and same-night large storyworld artifacts in the roughly 77 KB to 116 KB range. Follow-up work on March 29-30, 2026 added a cleaner MCP/TRM smoke path and showed perfect routing accuracy on a small benchmark for tool selection over indexed storyworld data. The central result is not that a tiny model internally "held" an 80k world, but that bounded routing, retrieval, and phased generation can turn small models into practical controllers for much larger structured outputs. We outline the system design, artifact evidence, and a replication plan for controlled benchmarking against naive long-context baselines.

## Problem framing

The paper should argue against the default framing:

- baseline framing: "large storyworlds require large prompt windows"

The proposed framing:

- large storyworld generation can be decomposed into retrieval, planning, local block authoring, revision, and validation
- once those functions are separated, the model no longer needs the whole world in-context
- MCP or MCP-like tool calls become the memory control plane

## Scope of the claim

What we should claim:

- bounded-context control works
- small models can route over externalized world memory
- the overall system can emit artifacts far larger than prompt context
- the system is practical enough to run locally

What we should not claim without new evidence:

- that every final storyworld block was authored directly by the small model in one pass
- that this is universally better than larger models on quality
- that the current pipeline is already optimal for direct block authoring

## Contributions

1. A bounded-context architecture for storyworld generation using indexed cards or packets instead of full-world prompts.
2. A concrete local implementation in GPTStoryworld with reusable skill, config, and phase-pipeline assets.
3. Evidence that a roughly 6k-token budget was sufficient for the system path around large structured storyworld outputs.
4. A routing/control-plane result showing that tiny models can reliably choose retrieval actions over storyworld indices.
5. A replication plan that separates routing success, generation success, and final artifact size.

## Cross-domain extension: trivia and factual QA

Yes, this paper can be extended beyond storyworlds, and trivia or fact QA is the cleanest second domain.

The right claim is not:

- "a 2B model magically knows more trivia than it should"

The right claim is:

- a 2B model that fails a closed-book or no-retrieval benchmark can recover substantial accuracy when given a bounded MCP retrieval interface over an externalized knowledge corpus, while staying inside a small prompt budget

That turns the paper from a storyworld-specific result into a more general systems claim:

- **MCP as a memory control plane for tiny models**

Current repo-local evidence now supports that extension on a small frozen trivia slice:

- run:
  - `hermes-skills/pure-trm-trainer/runs/wiki_card_routerbench_qwen2b_4bit_full13_compact`
- result:
  - `closed_book_accuracy = 0.769`
  - `mcp_routed_accuracy = 1.0`
  - `mcp_minus_closed = 0.231`

Important caveat:

- the routed path won on accuracy and reduced retrieved evidence size, but it still incurred extra routing-prompt overhead in this first implementation
- later partial router fine-tuning produced a checkpoint with `mcp_routed_accuracy = 0.923` against `closed_book_accuracy = 0.692`, showing that a trained tiny router can recover most of the gain even before the fine-tune is complete
- the repo now also contains a capped run path for `3.9 GiB` GPU / low CPU-placement experiments so the paper can report a real bounded-memory protocol rather than an unconstrained local anecdote
- that capped path now has a completed fine-tune plus full benchmark run with `closed_book_accuracy = 0.769` and `mcp_routed_accuracy = 1.0` on the 13-question frozen slice
- however, the same run still showed `mcp_route_accuracy = 0.308`, so the paper should separate answer correctness from route-faithfulness

Why trivia is a good second domain:

1. It is much easier to score than storyworld quality.
2. It separates retrieval success from answer-style quality.
3. It lets us show that the storyworld result was not just a domain-specific quirk.
4. It supports a simple before-and-after story:
   - 2B closed-book baseline fails
   - 2B plus naive stuffed retrieval helps somewhat
   - 2B plus MCP-routed retrieval helps more under the same context budget

What this should become experimentally:

1. A fixed tiny-model baseline with no retrieval.
2. The same tiny model with naive top-k chunk stuffing.
3. The same tiny model with MCP-routed retrieval over indexed knowledge cards.
4. Optionally, a larger-model closed-book and open-book control.

The paper only gets stronger if the context budget is held fixed across all conditions.

## Paper outline

### 1. Introduction

- Motivate the long-context bottleneck for structured world generation.
- Explain why storyworlds are a clean testbed: many interdependent entities, encounters, options, reactions, and global constraints.
- State the key thesis: externalized memory plus bounded phase prompts can substitute for large prompt windows.

### 2. System design

- Storyworld decomposition into cards, indices, and packets.
- MCP or MCP-like retrieval surface.
- Phase pipeline:
  - plan
  - characterize
  - encounter_build
  - act_complete
  - recharacterize
  - late_stage_holistic
- Separation between retrieval control and local content generation.

### 3. Historical implementation evidence

- March 15-16, 2026 breakthrough window.
- 6144-token config.
- same-night large artifact outputs.
- user feedback showing working generation rather than mere speculation.

### 4. Follow-up routing validation

- March 29-30, 2026 MCP/TRM smoke path.
- tool-routing benchmark.
- why routing accuracy matters for context economy.

### 5. Experimental plan

- replay the bounded pipeline on held-out worlds
- compare against naive context stuffing
- measure artifact scale, routing quality, and editing quality separately
- add a cross-domain factual QA or trivia benchmark with the same bounded-memory principle

### 6. Limitations and threats to validity

- ambiguous attribution between small-model authored content and system scaffolding
- generation quality still weaker than routing quality
- current evidence is a strong internal result but not yet a polished benchmark paper
- for trivia or QA, retrieval must be evaluated fairly against the right baseline; an open-book MCP system should not be compared dishonestly against a closed-book model and presented as pure parametric knowledge

### 7. Conclusion

- bounded-context generation is a viable alternative to naive long-context prompting for this class of task

## Experiment matrix

| ID | Question | Setup | Primary metrics | Existing evidence | Status |
|---|---|---|---|---|---|
| E1 | Can a tiny model operate under a ~6k budget in this workflow? | Replay `qwen2b_4gb_context_port.json` and `qwen2b_4gb_context_port_posttrain.json` | prompt budget, phase completion, wall time, memory | 6144-token configs and March 15-16 session evidence | Partial |
| E2 | Can the system emit a final artifact much larger than prompt context? | Reproduce a March 15-16 style world build | final JSON bytes, encounter count, options/reactions/effects counts | 76,821 / 115,080 / 116,343 byte artifacts on 2026-03-16 | Partial |
| E3 | Does MCP routing reduce required context while preserving task relevance? | Run MCP/TRM smoke benchmark | tool accuracy, route correctness, retrieved token count, compression ratio | `mcp_trm_smoke_qwen35_2b` with `tool_accuracy: 1.0` | Strong |
| E4 | Is bounded phased generation better than naive long-prompt generation on small models? | Compare packetized pipeline against one-shot long prompt baseline | completion rate, schema validity, quality score, token cost | not yet run cleanly | Missing |
| E5 | Which phases need the model, and which can be deterministic? | Ablate generation phases | parse validity, artifact quality, latency | later runs suggest routing/planning stronger than direct block authoring | Partial |
| E6 | How much of the gain comes from retrieval vs prompt discipline? | hold model fixed, vary retrieval availability | prompt size, quality, failure rate | conceptual only | Missing |
| E7 | Can the same bounded-memory idea transfer from storyworlds to factual QA? | 2B model on trivia or open-book QA with no retrieval vs stuffed retrieval vs MCP routing | exact match, F1, route accuracy, retrieved tokens, latency | full frozen-slice routerbench now exists with uncapped and capped runs | Partial |
| E8 | Can a tiny model with MCP beat its own no-retrieval baseline under a fixed small context budget? | fixed 2B model, fixed token budget, held-out benchmark corpus | accuracy delta, token efficiency, evidence sufficiency | `0.769 -> 1.0` on the compact base run, `0.692 -> 0.923` on checkpoint-10 | Partial |

## Table draft for the paper

| Condition | Model | Context budget | Retrieval mode | Output scale | Notes |
|---|---|---:|---|---:|---|
| Bounded pipeline | 2B-class | 6144 | MCP cards / indexed packets | 76 KB to 116 KB artifact range observed | strongest historical evidence |
| MCP/TRM smoke | Qwen 3.5 2B | compact routing prompt | tool call over local index | small benchmark bundle | `tool_accuracy: 1.0` |
| Naive long-context baseline | 2B-class | as large as possible | none | to be measured | required for final paper |
| Larger-model control | 7B-9B class | matched or larger | optional MCP | to be measured | useful but not required for first note |
| Trivia MCP extension | 2B-class | fixed small budget | MCP lookups over knowledge cards | benchmark accuracy | best cross-domain validation |
| Trivia MCP extension, capped | 2B-class | fixed small budget, `3900 MiB` GPU cap | MCP lookups over knowledge cards | benchmark accuracy under bounded device memory | methods-strengthening path |

## Figure plan

### Figure 1. System overview

Show:

- storyworld index
- MCP retrieval layer
- bounded phase packets
- small model
- structured artifact output

Purpose:

- establish that the model is not carrying the full world in prompt context

### Figure 2. Prompt budget vs artifact size

Show:

- 6144-token context budget
- final artifact sizes around 76 KB / 115 KB / 116 KB

Purpose:

- visually communicate the asymmetry between local prompt budget and final output scale

### Figure 3. Phase pipeline diagram

Show:

- plan
- characterize
- encounter_build
- act_complete
- recharacterize
- late_stage_holistic

Purpose:

- explain decomposition as the core systems trick

### Figure 4. MCP routing benchmark

Show:

- example query
- tool decision
- retrieved card
- compression ratio
- `tool_accuracy`

Purpose:

- make the routing/control-plane result legible

### Figure 5. Failure mode split

Show:

- routing success
- phase completion
- parse-valid block authoring

Purpose:

- clarify that routing/control can already work even where direct authoring still lags

### Figure 6. Baseline comparison

Show:

- naive long prompt vs bounded MCP pipeline
- token cost
- completion rate
- schema validity

Purpose:

- this is the figure that turns internal evidence into a publishable experiment story

### Figure 7. Cross-domain transfer

Show:

- same memory-control architecture
- storyworld generation on one side
- factual QA or trivia on the other
- same bounded-context principle

Purpose:

- show that the contribution is architectural, not storyworld-specific

## Claims, evidence, and caveats table

| Claim | Evidence now | What is still needed |
|---|---|---|
| Tiny models can use bounded MCP packetization for storyworld work | skill docs, configs, sessions, commits | clean rerun and formal measurement |
| The system can emit artifacts larger than prompt context | March 16 large JSON artifacts | explicit rerun with tracked provenance |
| Tiny models can route to the right storyworld memory shards | March 29-30 smoke with perfect route score on the small benchmark | larger held-out routing set |
| Small models can directly author every final storyworld block reliably | weak | do not claim yet |
| Tiny models can use the same MCP control pattern to recover factual QA accuracy | plausible, but not yet measured | run the trivia extension and report fixed-budget gains |
| Tiny models can recover factual QA gains under an explicit 4 GB-class device envelope | capped runner, completed safe fine-tune, and full capped benchmark now exist | improve route-faithfulness and expand beyond the 13-question slice |

## Minimal replication checklist

1. Preserve a copy of the exact configs:
   - `hermes-skills/storyworld-conveyor/sample_data/qwen2b_4gb_context_port.json`
   - `hermes-skills/storyworld-conveyor/sample_data/qwen2b_4gb_context_port_posttrain.json`
2. Preserve the exact historical artifacts:
   - `storyworlds/france_to_germany_machiavellian_p.json`
   - `storyworlds/hive_to_glam_machiavellian.json`
   - `storyworlds/shadow_to_bio_grudger.json`
3. Export the two key sessions:
   - `019cf30d-3b1c-7d71-af33-1ac57203098b`
   - `019d3c00-b55c-75e1-a60c-3dcfe06ea8c4`
4. Re-run one held-out bounded build with logging for:
   - per-phase prompt size
   - retrieved packet size
   - wall time
   - memory use
   - schema validity
   - final artifact bytes
5. Run a naive no-retrieval baseline on the same world.
6. Build one compact benchmark table and one system diagram.
7. Re-run the trivia benchmark with the explicit capped launcher and record the memory envelope in the final table.

## Recommended paper strategy

Best first paper:

- a short systems/result note

Why:

- the historical evidence is strong
- the replication story is plausible
- the routing result is already legible
- direct authoring quality likely still needs a cleaner benchmark before claiming too much

Best stronger version of the paper:

- storyworld result plus one cross-domain retrieval benchmark

Why:

- it upgrades the contribution from "interesting domain trick" to "general bounded-memory architecture"
- trivia or QA makes scoring simple and defensible
- it highlights that MCP is functioning as an external memory control plane, not just a storyworld convenience layer

Best second paper, later:

- a fuller benchmark paper on storyworld generation under bounded memory with ablations across model size, retrieval policy, and phase decomposition

## Writing order

1. Write the system/design section first.
2. Write the March 15-16 evidence section second.
3. Add the March 29-30 routing validation third.
4. Run the naive baseline comparison.
5. Only then finalize the abstract and title.

## Artifact index

- Evidence memo:
  - `papers/mcp_storyworld_breakthrough_evidence.md`
- Trivia extension note:
  - `papers/mcp_trivia_extension.md`
- Breakthrough session:
  - `codex-chat-sessions/sessions/2026/03/15/rollout-2026-03-15T16-50-56-019cf30d-3b1c-7d71-af33-1ac57203098b.jsonl`
- Follow-up session:
  - `codex-chat-sessions/sessions/2026/03/29/rollout-2026-03-29T20-49-32-019d3c00-b55c-75e1-a60c-3dcfe06ea8c4.jsonl`
- Small-model skill:
  - `codex-skills/small-storyworld-builder/SKILL.md`
- Bounded-context configs:
  - `hermes-skills/storyworld-conveyor/sample_data/qwen2b_4gb_context_port.json`
  - `hermes-skills/storyworld-conveyor/sample_data/qwen2b_4gb_context_port_posttrain.json`
- Large artifacts:
  - `storyworlds/france_to_germany_machiavellian_p.json`
  - `storyworlds/hive_to_glam_machiavellian.json`
  - `storyworlds/shadow_to_bio_grudger.json`
- Routing smoke output root:
  - `hermes-skills/storyworld-conveyor/context_port_runs/mcp_trm_smoke_qwen35_2b`
- Trivia capped runner:
  - `hermes-skills/pure-trm-trainer/scripts/run_wiki_card_router_train_capped.ps1`
- Trivia safe training spec:
  - `hermes-skills/pure-trm-trainer/references/wiki-card-router-training-spec.safe.json`
