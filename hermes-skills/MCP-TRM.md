Yes — that is a very good TRM use case.

What you want is not “a TRM that knows everything in the corpus,” but a tiny routing model that learns how to convert a task state into a compact retrieval action. That can cut token cost hard, because the big model stops doing expensive “search by reading.”

The key reframing is:

Do not train the TRM to answer from the index. Train it to choose what to fetch from the index.

That means the TRM’s output should be things like:

which namespace to query
which entity / subgraph / doc family is relevant
which hop comes next
what compression level is needed
whether enough evidence has already been retrieved
whether to escalate to the main LLM

So the architecture becomes:

User/query → TRM router → index actions → tiny retrieved bundle → LLM reasoning

instead of:

User/query → LLM reads giant context blob

That is where the efficiency comes from.

Best version of the idea

Train a TRM to emit a structured action like:

{
  "intent": "retrieve",
  "sources": ["storyworld_lore", "character_state"],
  "entity_ids": ["casablanca_rick", "ilsa"],
  "query_type": "relationship_state",
  "top_k": 3,
  "compression": "summary_atoms",
  "confidence": 0.87,
  "escalate": false
}

Or even more compactly:

{
  "route_id": 41,
  "keys": [183, 992, 44],
  "depth": 2
}

where route_id maps to a retrieval template outside the model.

That is important: push as much syntax and lookup machinery out of the model as possible.

Why this is a strong TRM task

TRMs are a better fit for this than broad freeform generation because index lookup is:

low-bandwidth
structured
recurrent
easy to supervise
cheap to evaluate
often decomposable into deterministic substeps

It is much easier to make a small model good at:

“find the right shard / entity / node / tool”
than at:
“read 50k tokens and reason globally”

So you get a leverage effect: a weak model can still be very good at pointing.

What to train on

You want training examples of the form:

state → retrieval decision

not just question → answer.

For each example, store:

user query
current world/task state
available indexes/tools
gold retrieval targets
optional multi-hop chain
success/failure label
final answer quality after retrieval

A single training row might look like:

{
  "input": {
    "task": "What promise did Rick implicitly break in the prior scene?",
    "world": "casablanca",
    "turn_context": {
      "scene_id": 18,
      "active_characters": ["rick", "renault", "ilsa"],
      "recent_events": ["exit_letters", "bar_argument"]
    }
  },
  "target": {
    "source": "scene_memory",
    "keys": ["scene_14_recap", "rick_ilsa_commitment_arc"],
    "hop_plan": ["recent_event_lookup", "relationship_arc_lookup"],
    "compression": "evidence_snippets"
  }
}
Three training regimes that make sense
1. Supervised routing

Use traces from your current harness or from a stronger model.

Generate labels like:

correct collection
correct entity ids
correct retrieval depth
correct stop/escalate decision

This is the easiest place to start.

2. Distilled search policy

Let a stronger model perform multi-step retrieval over your corpus, then distill its action choices into the TRM.

So you are not distilling the final prose answer — you are distilling the search behavior.

3. Outcome-based reinforcement / bandit tuning

Reward the TRM when:

retrieval was small
answer stayed correct
fewer tokens were consumed
latency stayed low

Penalty when:

it retrieved irrelevant chunks
it missed crucial evidence
it over-escalated
it caused expensive fallback

This is probably the best late-stage tuning objective:
accuracy per token, not just accuracy.

What the index should look like

If you want “tremendous context efficiency,” the index must be designed for TRM use.

The index should expose small symbolic handles, not giant text blobs.

Good primitives:

entity ids
scene ids
arc ids
relation edges
event hashes
constitutional feature tags
summary atoms
contradiction flags
latent topic tags
temporal adjacency links

For storyworlds, I would strongly consider a layered index:

Layer 0: symbolic routing layer

Tiny records:

world
scene
character
object
arc
relationship
active goals
unresolved tensions
Layer 1: compressed semantic layer

Short summaries / atoms:

1–3 sentence event summaries
relationship deltas
belief-state updates
secret-ending progress markers
Layer 2: raw evidence layer

Actual logs, dialogue, transcripts, scene text

The TRM should mostly operate over Layers 0 and 1, and only rarely trigger Layer 2.

The really important trick

Train the TRM to output pointers, not text.

Bad:

“Rick probably feels betrayed because…”

Good:

relationship_arc_lookup(rick, ilsa, prewar_commitments)
scene_memory(scene_14)
event_delta(exit_letters)

Every token the TRM emits in natural language is efficiency you are leaking.

One TRM or many?

Start with one TRM.

Train one narrow retrieval controller that does:

source selection
key prediction
stop/escalate

Then split later only if needed:

TRM-R: retrieval routing
TRM-C: compression choice
TRM-J: judge for “enough evidence?”

But I would not begin with a swarm. The first win is proving that one tiny router can reduce context materially.

Metrics that actually matter

Do not just measure answer accuracy.

Track:

retrieval precision@k
retrieval recall@k
average tokens retrieved
average tokens sent to the main LLM
escalation rate
answer accuracy
answer accuracy per 1k tokens
latency
“catastrophic miss” rate

The killer metric is something like:

quality-adjusted answer accuracy / total inference tokens

That tells you whether the TRM is genuinely buying efficiency.

Training data sources you already likely have

You probably already have good seed data from:

storyworld trajectories
secret-ending grading traces
failed runs where the model “forgot” relevant lore
harness logs from deterministic tasks
TRM/LLM disagreements
existing MCP / tool traces
offline judge rationales that mention missing evidence

Those can be converted into routing supervision.

Very plausible failure modes

The main ones:

1. Overfitting to lexical shortcuts

TRM memorizes word-to-index patterns and fails when the same need is phrased differently.

Fix: paraphrase heavily and vary task framing.

2. Over-retrieval

TRM retrieves too much “just in case.”

Fix: explicit token-budget penalty.

3. Under-retrieval

TRM acts overconfident and starves the LLM.

Fix: train stop/escalate separately and add miss penalties.

4. Index drift

If your summaries / entity graphs are stale, the TRM learns bad routing.

Fix: make index refresh deterministic and versioned.

5. Hidden dependency on large-model cleanup

System “works” only because the big LLM repairs bad retrieval.

Fix: evaluate retrieval quality directly before answer generation.

The strongest near-term design

I would do this:

Phase 1

Build a deterministic retrieval API with fixed actions:

get_entity(id)
get_scene(id)
get_arc(id)
get_recent_events(char_id)
search_relation(a,b)
get_secret_progress(world_state)
fetch_evidence(keys, budget)
Phase 2

Generate oracle traces using a strong model or hand-authored policies.

Phase 3

Train a small TRM to map from compact task state to those API calls.

Phase 4

Measure savings against your current “stuff context and hope” baseline.

Phase 5

Only then add multi-hop planning or hierarchical TRMs.

Even better: retrieval sketches

One especially powerful idea is to have the TRM emit a retrieval sketch rather than exact chunks:

{
  "need": "character motive",
  "scope": "recent+arc",
  "entities": ["rick", "ilsa"],
  "time_window": "last_5_scenes",
  "budget": 400
}

Then a deterministic executor resolves that into actual chunk ids.

This is often easier to train than direct chunk-id prediction, and more robust to reindexing.

Bottom line

Yes, this is one of the best uses for TRMs.

Not as miniature general reasoners, but as learned retrieval controllers that replace expensive token-based search with cheap structured lookup.

The winning recipe is:

tiny TRM
pointer outputs
layered index
deterministic executor
optimize for accuracy per token
keep natural language generation out of the router

If you want, I can turn this into a concrete training spec for your setup: dataset schema, loss targets, model size guess, and a minimal retrieval-TRM pipeline you could drop into Tesseract or GPTStoryworld.

do
Thought for a couple of seconds

Here’s a concrete spec for a retrieval-TRM tuned for index lookup and context compression in your Tesseract / GPTStoryworld stack.

1. Objective

Train a small model to do:

route a query/task state to the right index slice
predict the minimal retrieval plan
decide whether retrieved evidence is sufficient
escalate to larger reasoning only when needed

The TRM should not answer the user’s question in prose. It should emit a compact retrieval action or retrieval sketch.

Core optimization target:

maximize downstream task quality while minimizing retrieved tokens

2. System architecture

Use a 4-stage flow:

A. Task state encoder

Input bundle:

user/query text
world ID / environment ID
current scene / episode / turn
active entities
recent event atoms
current objective
optional prior failed retrieval attempts
B. Retrieval TRM

Outputs a structured action:

{
  "op": "retrieve",
  "source": "relationship_arc",
  "entities": ["rick", "ilsa"],
  "time_scope": "recent_plus_background",
  "budget": 320,
  "top_k": 4,
  "compression": "summary_atoms",
  "stop_after": false,
  "confidence": 0.83
}

or a more abstract sketch:

{
  "need_type": "motive_explanation",
  "target_scope": "character_pair",
  "keys": ["rick", "ilsa"],
  "temporal_window": "last_5_scenes_plus_origin_arc",
  "budget_class": "small"
}
C. Deterministic retrieval executor

Maps the TRM output to your index:

symbolic layer lookup
summary atom fetch
evidence bundle assembly
token budget enforcement
optional rerank
D. Main model / downstream judge

Consumes only the retrieved bundle, not the full corpus.

3. Index design

This matters as much as the model.

You want a three-layer index.

Layer 0: symbolic handles

Very small records:

world_id
scene_id
character_id
relationship_id
arc_id
event_id
goal_id
secret_gate_id
constitution_tag
constraint_tag

Example:

{
  "character_id": "rick",
  "active_scene": "scene_18",
  "goal_ids": ["protect_ilsa", "maintain_detachment"],
  "relationship_ids": ["rick_ilsa_prewar", "rick_renault_alliance"]
}
Layer 1: summary atoms

Short compressed facts.

Example:

{
  "atom_id": "rick_ilsa_arc_03",
  "type": "relationship_delta",
  "text": "Rick still feels betrayed by Ilsa's departure in Paris, but masks it with cynicism.",
  "scene_refs": ["scene_04", "scene_11", "scene_18"]
}
Layer 2: raw evidence

Dialogue, transcripts, logs, world notes.

TRM should usually access Layer 0 and Layer 1. Layer 2 should be rarer and more expensive.

4. What to train on

Your dataset should be state → retrieval policy, not question → answer.

Each row should contain:

{
  "input": {
    "query": "...",
    "world_id": "casablanca",
    "scene_id": "scene_18",
    "active_entities": ["rick", "ilsa", "renault"],
    "recent_atoms": ["atom_992", "atom_441", "atom_118"],
    "objective": "explain current tension"
  },
  "target": {
    "source": "relationship_arc",
    "entity_ids": ["rick", "ilsa"],
    "top_k": 3,
    "compression": "summary_atoms",
    "budget": 320,
    "need_raw_evidence": false,
    "stop_after": false
  },
  "metadata": {
    "gold_keys": ["arc_rick_ilsa", "scene_14_recap", "betrayal_memory_cluster"],
    "downstream_success": 1,
    "retrieved_token_count": 241
  }
}
5. Label schema

I would split training targets into multiple heads or fields.

Head 1: source selection

Which index/table/tool to hit?

Classes might be:

scene_memory
character_state
relationship_arc
goal_graph
event_history
secret_progress
constitution_constraints
raw_evidence
Head 2: key prediction

Predict entity IDs / arc IDs / scene IDs / tag IDs.

Could be:

classification over frequent IDs
pointer into candidate set
contrastive scoring over candidates
Head 3: retrieval shape

Predict:

top_k
budget_class
compression_type
time_window
Head 4: stop / escalate

Binary:

enough evidence already
need more retrieval
escalate to larger reasoner
Head 5: confidence

Optional calibration head.

6. Best training regime

Use a staged approach.

Phase 1: oracle trace generation

Build oracle trajectories from:

your current harness
hand-authored lookup policies
a stronger LLM acting as planner
retrospective traces from successful runs

For each task, collect:

all available candidate index entries
oracle retrieval plan
downstream answer quality
total tokens consumed

For the oracle, force the stronger model to produce structured actions, not prose.

Example prompt pattern for oracle generation:

Given the task state and available index schema, output the minimal retrieval plan needed to answer well.
Prefer summary atoms over raw evidence.
Use raw evidence only if summary atoms are insufficient.
Respect a strict token budget.
Return JSON only.
Phase 2: supervised imitation

Train TRM to imitate the oracle action.

Loss:

cross-entropy for source choice
cross-entropy or ranking loss for keys
classification/regression for budget/top_k
BCE for stop/escalate
Phase 3: offline reranking / DPO-style preference

For the same input, compare two retrieval plans:

one more efficient and equally good
one bloated or insufficient

Train preference for:

higher downstream score
fewer tokens
fewer irrelevant fetches
Phase 4: bandit / outcome optimization

Reward signal:

reward = answer_quality
         - λ1 * retrieved_tokens
         - λ2 * irrelevant_tokens
         - λ3 * unnecessary_escalation
         - λ4 * latency

This is where you get the real efficiency behavior.

7. Data generation strategy for your setup

You already have good data sources.

Source A: storyworld runs

From GPTStoryworld:

questions
scene states
secret-ending tasks
moral tradeoff tasks
character consistency tasks

Convert successful runs into retrieval supervision.

Source B: failed runs

Very valuable.
Especially cases where the main model:

forgot prior commitments
missed a relationship arc
ignored scene history
hallucinated motives

These become examples where the gold retrieval should have included missing evidence.

Source C: evaluator rationales

If your judge says “answer ignored prior betrayal arc,” that can label the needed retrieval source.

Source D: deterministic env tasks

BashArena / ControlArena-style tasks can teach structured lookup policy even outside storyworlds.

That helps generalize the TRM as a generic retrieval controller.

8. Input representation

Do not dump too much raw text into the TRM.

Use compact structured inputs.

A good serialized form:

{
  "task_type": "motive_explanation",
  "query": "Why is Rick distancing himself from Ilsa here?",
  "world_id": "casablanca",
  "scene_id": "scene_18",
  "active_entities": ["rick", "ilsa"],
  "recent_event_ids": ["ev_18_01", "ev_18_02"],
  "recent_atom_ids": ["a_441", "a_992"],
  "objective_tag": "character_explanation",
  "candidate_sources": [
    "scene_memory",
    "relationship_arc",
    "character_state",
    "raw_evidence"
  ]
}

For a tiny model, the less freeform text the better.

You can also pre-normalize task types:

motive_explanation
relationship_status
constraint_check
secret_progress
event_recall
goal_prediction
moral_tradeoff_eval

That should help a lot.

9. Output representation

I would strongly prefer a small controlled JSON vocabulary.

Example schema:

{
  "source": "relationship_arc",
  "primary_keys": ["rick", "ilsa"],
  "secondary_keys": [],
  "time_scope": "recent_plus_origin",
  "compression": "summary_atoms",
  "budget_class": "s",
  "top_k": 3,
  "raw_evidence": false,
  "decision": "retrieve_then_answer"
}

or even a token-cheaper codebook:

{
  "s": 2,
  "k1": 41,
  "k2": 88,
  "t": 3,
  "c": 1,
  "b": 0,
  "r": 0,
  "d": 1
}

where codebook lookup happens outside the model.

That second form is uglier for debugging but probably great later.

10. Model size

For your purposes, I’d start with:

0.5B–1.5B class if you want fully flexible structured prediction
sub-500M could work if inputs are heavily normalized and action space is constrained

Realistically:

Qwen 0.5B / 0.8B / 1.5B style range is a good starting point
if the action space is very constrained, even smaller could work

You do not need a “reasoning model” in the normal sense.
You need:

high precision structured routing
good calibration
low latency

This is closer to a policy model than a chat model.

11. Candidate training losses

Use a multitask loss:

L_total =
  α * L_source
+ β * L_key
+ γ * L_budget
+ δ * L_compression
+ ε * L_stop
+ ζ * L_confidence

Where:

L_source: source classification CE
L_key: candidate ranking or pointer CE
L_budget: class CE or regression
L_compression: CE
L_stop: BCE
L_confidence: MSE or calibration loss

If you do pairwise retrieval-plan preference training:

L_pref = -log σ(score(plan_good) - score(plan_bad))

And define plan_good based on answer quality per token.

12. Evaluation suite

You need evaluation at both retrieval level and downstream level.

Retrieval metrics
source accuracy
key hit@k
retrieval precision@k
retrieval recall@k
over-retrieval rate
under-retrieval rate
average retrieved tokens
raw-evidence invocation rate
Downstream metrics
answer correctness
character consistency
secret-ending progress accuracy
moral-rubric faithfulness
contradiction rate
Efficiency metrics
total tokens sent to main LLM
average latency
escalation rate
quality per 1k tokens
catastrophic miss rate

Most important dashboard:

answer_quality / total_tokens_used

and

catastrophic_miss_rate under fixed token budget
13. Baselines

Compare against these:

Baseline A: naive long context

Stuff recent logs + lore summaries + query into main model

Baseline B: embedding retrieval

Standard semantic retrieval + top-k chunks

Baseline C: rules-only retrieval

Hand-authored routing logic:

if motive question → relationship_arc first
if continuity question → scene_memory first
Baseline D: strong-LLM planner

Expensive planner that emits retrieval action

Your TRM should ideally beat B and C on efficiency, and approach D at much lower cost.

14. Minimal MVP

I’d start with just 5 sources:

scene_memory
character_state
relationship_arc
event_history
secret_progress

And just these action fields:

source
entity_ids
time_scope
compression
budget_class
stop_or_escalate

That is enough to prove the concept.

15. Concrete pipeline for Tesseract

A plausible folder layout:

tesseract/
  retrieval_trm/
    data/
      train.jsonl
      valid.jsonl
      test.jsonl
      schemas/
        action_schema.json
        index_schema.json
    indexing/
      build_symbolic_index.py
      build_summary_atoms.py
      build_raw_evidence_refs.py
    oracle/
      generate_oracle_traces.py
      score_trace_efficiency.py
    training/
      train_supervised.py
      train_preference.py
      eval_retrieval.py
    runtime/
      trm_router.py
      retrieval_executor.py
      budget_manager.py
      stop_judge.py
    reports/
      retrieval_metrics.md
      efficiency_curves.csv

Runtime flow:

storyworld task enters Tesseract
compact task-state serializer runs
TRM emits retrieval action
retrieval executor fetches atom bundle
if confidence low or evidence insufficient, second TRM step or escalate
main LLM answers from compact bundle only
16. Example training sample
{
  "input": {
    "task_type": "relationship_status",
    "query": "What tension is unresolved between Rick and Ilsa here?",
    "world_id": "casablanca",
    "scene_id": "scene_18",
    "active_entities": ["rick", "ilsa"],
    "recent_atom_ids": ["a_201", "a_441", "a_992"],
    "recent_event_ids": ["e_18_1", "e_18_2"],
    "objective_tag": "character_consistency"
  },
  "target": {
    "source": "relationship_arc",
    "entity_ids": ["rick", "ilsa"],
    "time_scope": "recent_plus_origin",
    "compression": "summary_atoms",
    "budget_class": "small",
    "top_k": 3,
    "raw_evidence": false,
    "decision": "retrieve_then_answer"
  },
  "candidates": {
    "sources": [
      "scene_memory",
      "character_state",
      "relationship_arc",
      "event_history",
      "raw_evidence"
    ]
  },
  "metrics": {
    "gold_answer_score": 0.93,
    "retrieved_tokens": 214,
    "baseline_tokens": 3411
  }
}
17. Best first experiment

The first clean experiment should be narrow.

Task

Character motive / relationship continuity in one or two storyworlds only.

Worlds

Pick:

one dense literary world
one simpler world
Goal

Show that TRM-routed retrieval:

reduces context by 5x–15x
preserves or improves answer quality
lowers catastrophic continuity misses

This is enough for a real result.

18. Strong extensions later

Once the base works, extend to:

A. hierarchical retrieval

TRM-1 picks source
TRM-2 picks exact keys or compression scheme

B. retrieval memory

Store successful retrieval patterns as reusable route templates

C. adaptive budgeter

Small budget by default, expand only if uncertainty stays high

D. constitution-aware retrieval

Retrieve only evidence relevant to moral or alignment constraints when doing constitutional eval

E. adversarial robustness

Train against misleading recent-context lure where the truly relevant fact is older or structural

19. My recommendation for your exact stack

For your research style, I would do:

one retrieval TRM
one deterministic executor
summary-atom index first
supervised imitation from oracle traces first
evaluate on secret-ending / continuity / motive tasks
only later split into multiple TRMs

This is the shortest path to demonstrating that TRMs can function as context-economy control planes rather than just mini-reasoners.

20. The punchy thesis

The thesis of the experiment is:

A tiny model does not need to reason over the whole world if it can learn to point precisely into a world model that has already been compressed into structured indices.

That is probably the cleanest “TRM for efficiency” story you can test.
## Concrete Implementation In This Repo

The executable pieces now live in `storyworld-conveyor/scripts/`:

- `storyworld_mcp_server.py`
  - Loads an encounter index from disk.
  - Exposes MCP tools for `get_encounter_card`, `query_lore_index`, `update_state`, `evaluate_secret_ending`, and `advance_scene`.
  - Runs as a real MCP server or as a reusable lookup library.
- `run_storyworld_mcp_trm_smoke.py`
  - Loads Qwen 3.5 2B plus an optional LoRA adapter.
  - Prompts the router to emit one JSON tool call.
  - Executes the selected MCP lookup locally and records the result bundle.
- `run_storyworld_mcp_trm_smoke.ps1`
  - Windows wrapper for the same smoke path.

Default Windows smoke command:

```powershell
powershell -ExecutionPolicy Bypass -File .\storyworld-conveyor\scripts\run_storyworld_mcp_trm_smoke.ps1
```

Default paths:

- model: `D:\Research_Engine\models\Qwen3.5\Qwen3.5-2B-HF`
- adapter: `D:\Research_Engine\storyworld_qlora\adapters\qwen35-2b-usual-suspects-local-r2-checkpoint13`
- index root: `C:\projects\GPTStoryworld\hermes-skills\storyworld-conveyor\factory_runs\the_usual_suspects_qwen35_2b_run\indices\encounter_index`
- outputs: `C:\projects\GPTStoryworld\hermes-skills\storyworld-conveyor\context_port_runs\<run_id>\`

Smoke outputs:

- `index_summary.json`
- `queries.json`
- `generations.jsonl`
- `scorecard.jsonl`
- `summary.json`

Acceptance criteria:

- The router should choose `get_encounter_card` for direct encounter-id queries.
- The router should choose `query_lore_index` for world-rule and lore queries.
- The retrieved output should be materially smaller than the full index corpus.
- The summary should report `route_correct` counts and `tool_accuracy`.

Target flow:

1. TRM emits a compact tool call.
2. MCP executes the lookup against the local index.
3. Qwen 3.5 2B sees only the retrieved card or excerpt.
4. The logs show the routing decision, the lookup result, and the compression ratio.

## Turn-Family Routing Matrix

This is the small-storyworld / Hermes assembly-line version of the same contract:

- The small-storyworld-style bounded loop keeps each turn tied to one stage artifact.
- The Hermes runner style keeps the whole flow artifact-first, resumable, and countable.
- The TRM should learn the mapping from turn family to smallest valid lookup, not to prose output.

| Prompt family | Hermes stage | TRM tool | MCP namespace | Retrieved evidence |
| --- | --- | --- | --- | --- |
| Build out an encounter | `encounter_build` | `get_encounter_card` | `encounters` | Local card, option labels, consequences, turn span |
| Follow up on a scene | `characterize` | `get_encounter_card` | `encounters` | Adjacent route context for the named encounter |
| Review world rules | `plan` | `query_lore_index` | `world_card` | World card excerpt and structural constraints |
| Review Monte Carlo for a rebalance target | `characterize` | `query_lore_index` | `monte_carlo` | Ending distribution, dead-end rate, secret reachability |
| Review quality gate failures for pathing | `act_complete` | `query_lore_index` | `quality_gate` | Options/reactions/effects failures and structural pressure |
| Revise formulas for pathing and ending rebalance | `recharacterize` | `query_lore_index` | `rebalance_advice` | Bias, weight, target min/max, and other rebalance knobs |

Recommended training corpus builder:

```powershell
python .\storyworld-conveyor\scripts\build_storyworld_turn_router_corpus.py `
  --index-root C:\projects\GPTStoryworld\hermes-skills\storyworld-conveyor\factory_runs\the_usual_suspects_qwen35_2b_run\indices\encounter_index `
  --out C:\projects\GPTStoryworld\hermes-skills\storyworld-conveyor\context_port_runs\turn_router_corpus.jsonl
```

That corpus is intended to train the TRM on the exact stage split used by the Hermes-facing storyworld skills:

- [storyworld-conveyor-runner](C:/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/skills/storyworld-conveyor-runner/SKILL.md)
- [comprehensive-storyworld-building](C:/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/skills/comprehensive-storyworld-building/SKILL.md)
- [storyworld-3090-builder](C:/projects/GPTStoryworld/hermes-skills/storyworld-3090-builder/SKILL.md)
