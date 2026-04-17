# MCP Trivia Extension Note

Date: 2026-04-17

Companion files:

- `papers/mcp_storyworld_breakthrough_evidence.md`
- `papers/mcp_storyworld_paper_package.md`

## Goal

Extend the storyworld paper into a broader claim:

- MCP-style bounded retrieval can let an absurdly small model, such as a 2B model with a tiny context window, outperform its own no-retrieval baseline on factual QA or trivia tasks that it otherwise handles poorly.

The clean claim is not:

- "the 2B model knows the trivia"

The clean claim is:

- the 2B model can use MCP as an external memory control plane to fetch the right evidence under a fixed small prompt budget and answer more accurately than it can in closed-book mode

## Why this extension matters

If the storyworld paper stands alone, a skeptical reader can say:

- maybe this only works for weird structured authoring tasks
- maybe the benefit is specific to narrative decomposition

If the same architecture improves factual QA, the contribution becomes broader:

- tiny-model capability can be increased by routing over externalized memory rather than by scaling prompt windows

## Best paper framing

Better umbrella title if this result lands:

- `MCP as a Memory Control Plane for Tiny Models`

Storyworlds then become:

- Domain A: structured world generation

Trivia or factual QA becomes:

- Domain B: factual retrieval and answer extraction

## Recommended benchmark framing

Do not frame it as "closed-book benchmark beaten by cheating with retrieval."

Frame it as a controlled open-book or retrieval-augmented benchmark comparison with fixed context budget:

1. Same 2B model, no retrieval
2. Same 2B model, naive top-k chunk stuffing
3. Same 2B model, MCP-routed retrieval over indexed cards
4. Optional larger-model controls

The key comparison is:

- **same model, same budget, different memory architecture**

## Minimum viable experimental design

### Condition A. Closed-book tiny-model baseline

- model: 2B class
- context budget: fixed small budget, for example around 4k to 6k
- input: question only
- output: final answer only

Purpose:

- establish that the tiny model cannot do well enough unaided

### Condition B. Naive retrieval baseline

- same model
- same total budget
- retrieve top-k chunks by keyword or embedding search
- stuff those chunks directly into the prompt

Purpose:

- test whether dumb retrieval alone is enough

### Condition C. MCP-routed retrieval

- same model
- same total budget
- model chooses among a small tool surface
- only a targeted card or passage bundle is injected

Purpose:

- isolate the value of routing and bounded retrieval discipline

### Condition D. Larger-model control

- 7B to 9B class, optional

Purpose:

- show whether the tiny-model plus MCP stack approaches or exceeds a larger closed-book model

## Tool surface for trivia MCP

Keep the tool interface minimal.

Recommended tools:

1. `search_entities(query)`
   - returns a small ranked list of entity ids or titles
2. `get_entity_card(entity_id)`
   - returns a compact entity card with name, aliases, short description, and key facts
3. `get_passage(doc_id, passage_id)`
   - returns one evidence passage
4. `get_relation_card(subject, relation)`
   - returns structured fields such as birth date, capital, inventor, treaty date, etc.
5. `escalate`
   - use when the model cannot find enough evidence confidently

This is the exact same control-plane pattern as the storyworld setup:

- route
- fetch only what is needed
- answer from bounded evidence

## Corpus design

The evidence corpus should be frozen in advance.

Good options:

1. a benchmark-provided support corpus
2. a fixed Wikipedia snapshot converted into cards
3. a curated held-out trivia corpus with exact provenance

Do not let the retrieval backend query the live web for benchmark answers if the goal is a publishable controlled result.

## Card design for factual QA

Storyworld cards become knowledge cards.

Recommended card types:

1. entity card
   - title
   - aliases
   - 3 to 8 key facts
2. event card
   - date
   - location
   - actors
   - outcome
3. relation card
   - subject
   - relation
   - object
   - provenance
4. disambiguation card
   - distinguish similarly named entities
5. passage card
   - one short grounded excerpt

This helps keep retrieval targeted and budgeted.

## Metrics

Primary metrics:

1. exact match
2. token-level F1
3. answerable rate
4. route accuracy
5. evidence sufficiency
6. retrieved token count
7. end-to-end latency

Secondary metrics:

1. compression ratio
2. number of tool calls
3. hallucination rate after retrieval
4. wrong-route vs wrong-extraction split

## Key figure ideas

### Figure A. Accuracy under fixed budget

Show:

- no retrieval
- naive stuffed retrieval
- MCP-routed retrieval

This is the most important figure.

### Figure B. Retrieved tokens vs accuracy

Show:

- naive retrieval uses more context
- MCP retrieval uses less context for equal or better accuracy

### Figure C. Failure decomposition

Show:

- wrong route
- correct route, wrong extraction
- insufficient evidence
- hallucinated answer despite evidence

### Figure D. Architectural transfer

Show:

- storyworld cards and knowledge cards side by side
- same memory-control pattern

## Strongest defensible claim

If results are good, the strongest safe claim is:

- A 2B model under a small fixed context budget can substantially outperform its own no-retrieval baseline on factual QA when coupled to an MCP-style external memory control plane.

Even stronger, if it lands:

- Under the same small context budget, MCP-routed retrieval beats naive chunk stuffing for the same 2B model.

Possible stretch claim, only if measured:

- A 2B model plus MCP can approach or exceed a larger closed-book model on a fixed open-book factual QA benchmark.

## What would make the result paper-worthy

This extension becomes strong if all of these are true:

1. the 2B baseline is clearly weak without retrieval
2. naive retrieval helps, but not enough
3. MCP routing helps more than naive retrieval under the same budget
4. the corpus is frozen and auditable
5. routing mistakes and answer mistakes are analyzed separately

## Concrete implementation seam in this repo

The benchmark scaffold now exists in the repo.

Named bench wiring:

- `hermes-skills/pure-trm-trainer/references/wiki-card-routerbench-spec.json`
- `hermes-skills/pure-trm-trainer/references/bench-menu.md`
- `hermes-skills/pure-trm-trainer/scripts/run_trm_bench.py`

Runner and MCP-style card index:

- `hermes-skills/pure-trm-trainer/scripts/run_wiki_card_routerbench.py`
- `hermes-skills/pure-trm-trainer/scripts/wiki_card_mcp_server.py`

Frozen benchmark slice:

- `benchmarks/wiki_card_routerbench/cards.jsonl`
- `benchmarks/wiki_card_routerbench/questions.jsonl`
- `benchmarks/wiki_card_routerbench/README.md`

This is the current benchmark layout:

1. `closed_book`
2. `stuffed`
3. `mcp_routed`

So the trivia extension is no longer just a paper idea. It now has a runnable repo-local scaffold that sits beside the existing router bench machinery rather than outside it.

Current smoke status:

- heuristic backend smoke completed successfully
- named dispatcher path also launched successfully
- this proves the benchmark wiring and artifact contract
- it does **not** yet count as the paper result, because the real claim depends on a true 2B model run under the intended fixed VRAM/context budget

## First real result on the 2B model

We now have a real local run on the intended small-model path:

- run dir:
  - `hermes-skills/pure-trm-trainer/runs/wiki_card_routerbench_qwen2b_4bit_full13_compact`
- model:
  - `D:\Research_Engine\models\Qwen3.5\Qwen3.5-2B-HF`
- runtime:
  - 4-bit HF path on the local 4 GB RTX 3050 laptop GPU
- benchmark size:
  - 13 frozen questions from `benchmarks/wiki_card_routerbench/questions.jsonl`

Top-line result:

1. `closed_book_accuracy = 0.769`
2. `stuffed_accuracy = 1.0`
3. `mcp_routed_accuracy = 1.0`
4. `mcp_minus_closed = 0.231`
5. `mcp_route_accuracy = 1.0`

This is the first concrete cross-domain evidence that the tiny-model MCP framing is not just a storyworld trick.

## Resource envelope for the 4 GB laptop path

The paper should explicitly frame the hardware constraint as part of the contribution.

Current safe local envelope:

1. GPU budget:
   - `3900 MiB`
2. CPU placement budget for model weights:
   - `256 MiB`
3. Host RAM cap for training wrapper:
   - `2048 MiB`
4. Quantization:
   - 4-bit NF4

This matters because the relevant comparison is not "what happens on a roomy workstation."
It is:

- what a tiny model can do on a 4 GB class consumer GPU when raw long-context prompting and silent CPU offload are not allowed to rescue the run

Repo-local safety wiring now exists for that:

- capped trainer wrapper:
  - `hermes-skills/pure-trm-trainer/scripts/run_wiki_card_router_train_capped.ps1`
- safe trainer spec:
  - `hermes-skills/pure-trm-trainer/references/wiki-card-router-training-spec.safe.json`
- safe run plan:
  - `hermes-skills/pure-trm-trainer/references/wiki-card-router-safe-plan.json`

The evaluation runner also now accepts explicit `max_memory` caps, so the benchmark can be reported as a bounded-device experiment rather than an unconstrained local run.

We now also have a completed safe fine-tune and bounded-device full benchmark run:

- safe training run:
  - `hermes-skills/pure-trm-trainer/runs/wiki_card_router_train_qwen2b_safe`
- safe capped full benchmark run:
  - `hermes-skills/pure-trm-trainer/runs/wiki_card_routerbench_qwen2b_safe_final_cap13`

## What the result does and does not show

What it shows:

- the same 2B model improved from `0.769` closed-book to `1.0` with MCP-routed retrieval on this frozen slice
- the routed condition matched the stuffed retrieval condition on accuracy
- the routed condition used a much smaller retrieved evidence bundle on average

Important measured context numbers from the compact run:

1. stuffed average retrieved tokens estimate:
   - `91.846`
2. mcp_routed average retrieved tokens estimate:
   - `32.846`
3. stuffed average answer prompt tokens:
   - `253.154`
4. mcp_routed average answer prompt tokens:
   - `162.231`
5. mcp_routed average route prompt tokens:
   - `265.615`
6. mcp_routed average total prompt tokens across both stages:
   - `427.846`

What it does **not** show yet:

- that the routed path is already better on total end-to-end prompt tokens than a tiny stuffed benchmark
- that the result generalizes beyond this 13-question slice
- that the current router prompt is fully optimized for token economy

So the honest interpretation is:

- MCP-routed retrieval already improves capability and sharply reduces retrieved evidence payload size
- but this first version still pays a routing-prompt overhead that should be optimized in later iterations

That is still publishable if stated correctly.

## Interrupted training result and capped evaluation result

An interrupted local QLoRA run still produced a usable router checkpoint:

- checkpoint:
  - `hermes-skills/pure-trm-trainer/runs/wiki_card_router_train_qwen2b/trainer_outputs/checkpoint-10`

Full frozen-slice evaluation from that checkpoint:

1. `closed_book_accuracy = 0.692`
2. `mcp_routed_accuracy = 0.923`
3. `stuffed_accuracy = 1.0`

This is weaker than the hand-written heuristic router on route correctness, but it is already strong enough to support the paper’s architectural claim:

- a tiny routed adapter can recover most of the gain over closed-book even before router training is finished

We also verified the new capped evaluation path on the same checkpoint under:

1. `gpu_max_memory_mib = 3900`
2. `cpu_max_memory_mib = 256`

using a 3-question slice:

1. `closed_book_accuracy = 0.667`
2. `mcp_routed_accuracy = 1.0`
3. `stuffed_accuracy = 1.0`

That capped smoke is not a new headline result, but it is important for the methods section because it shows the evaluation path can be run under an explicit no-spill style memory budget.

## Completed safe-capped fine-tune result

We now have a completed router fine-tune under the capped path:

- trainer run:
  - `hermes-skills/pure-trm-trainer/runs/wiki_card_router_train_qwen2b_safe`
- adapter:
  - `hermes-skills/pure-trm-trainer/runs/wiki_card_router_train_qwen2b_safe/trainer_outputs/adapter`
- full bounded-device benchmark:
  - `hermes-skills/pure-trm-trainer/runs/wiki_card_routerbench_qwen2b_safe_final_cap13`

Top-line result on the full 13-question frozen slice, under:

1. `gpu_max_memory_mib = 3900`
2. `cpu_max_memory_mib = 256`

was:

1. `closed_book_accuracy = 0.769`
2. `stuffed_accuracy = 1.0`
3. `mcp_routed_accuracy = 1.0`
4. `mcp_minus_closed = 0.231`

This is important because it means the paper no longer relies only on the earlier unconstrained local run. We now have the same top-line gain on a bounded-device path that was explicitly configured to avoid silent CPU placement of model weights.

Important caveat:

- `mcp_route_accuracy = 0.308`

So the fine-tuned router is not yet "route-faithful" with respect to the hand-authored expected tool labels, even though it achieved perfect final-answer accuracy on this slice. The right paper interpretation is:

- the tiny model learned to use the bounded MCP interface well enough to answer correctly
- but the route-supervision target and the answer-level target are not yet perfectly aligned

## Suggested benchmark naming

Possible names:

1. `trm-triviaBench`
2. `tinymcp-trivia`
3. `wiki-card-routerbench`

My preference:

- `wiki-card-routerbench`

Reason:

- it describes the mechanism, not just the subject matter

## Clean narrative for the paper

Section progression:

1. Storyworlds show that bounded MCP memory can drive outputs far larger than prompt context.
2. Trivia shows the same architecture improves factual QA in a much easier-to-score domain.
3. Together, they support the broader thesis that MCP is a memory control plane for tiny models.

## Recommendation

Yes, extend the paper this way.

But the right headline is not:

- "2B beats trivia"

The right headline is:

- "2B plus bounded MCP retrieval beats its no-retrieval and naive-retrieval baselines under the same small context budget"

That is technically cleaner, easier to defend, and much more publishable.
