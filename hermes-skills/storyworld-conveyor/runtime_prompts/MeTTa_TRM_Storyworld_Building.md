# MeTTa/TRM Scaffold for General Storyworld Building

## Use

This is a compact control-plane scaffold for building and improving storyworlds without dumping whole JSON worlds into a model context. Use it as a planning and repair grammar alongside the storyworld conveyor.

## Core Claim

Treat a storyworld as a typed causal graph:

- encounters expose choices
- choices produce reactions
- reactions modify variables
- variables gate later encounters/options/endings
- endings should be reachable through multiple legible routes
- secret endings should require cross-variable synthesis, not just hidden flags

The LLM writes and interprets prose. The conveyor/verifiers score structure. TRM-like packets should route attention to concrete repair targets. MeTTa-like atoms should keep the plan modular and auditable.

## MeTTa-Style Atoms

Use these as a symbolic planning layer, not necessarily as executable MeTTa.

```lisp
(: Encounter Type)
(: Option Type)
(: Reaction Type)
(: Variable Type)
(: Ending Type)
(: Character Type)
(: Motif Type)
(: Gate Type)
(: Metric Type)

(has-option Encounter Option)
(has-reaction Option Reaction)
(changes Reaction Variable Delta)
(gates Gate Encounter)
(gates Gate Option)
(routes-to Reaction Encounter)
(routes-to Reaction Ending)
(owned-by Variable Character)
(perceived-by Variable Character)
(motif-supports Motif Ending)
(failure Metric Evidence)
(repair-target Metric Encounter)
(repair-action Repair Target)
```

## Research MCP World Model

For domain-heavy storyworlds, do not treat RAG as a flat pile of excerpts. Build a compact research world model first:

```lisp
(: ResearchWorldModel Type)
(: ResearchSource Type)
(: ResearchTerm Type)
(: ResearchQueryNest Type)
(: ResearchCard Type)

(research-world-model research_mcp_world_model_v1)
(research-source-node Source)
(research-source-path Source Path)
(research-term TermId "term text")
(research-term-role TermId "seed|associated")
(research-term-depth TermId Depth)
(cooccurs-with TermA TermB Score)
(research-query-nest Nest)
(query-nest-term Nest TermId)
(query-nest-query Nest QueryText)
(research-card CardId)
(research-card-term CardId TermId)
```

The intended RAG loop is bird-nest expansion:

1. Start from seed terms in the authoring brief and current storyworld.
2. Mine configured source files for co-occurring associated terms.
3. Expand associated terms one or more depths into query nests.
4. Select bounded research cards from source chunks with the strongest topic/world overlap.
5. Inject only the cards, term summaries, source paths, and MeTTa facts into MCP packets.
6. Use the nests to decide what to retrieve next; do not let the model invent scholarship to fill gaps.

This makes research stimulus a reusable world-model class: topic terms become graph nodes, sources become evidence nodes, query nests become retrieval actions, and storyworld authoring packets consume only bounded evidence.

## TRM Packet Types

1. Router TRM

Routes the next operation to one of:

- validate
- score
- inspect-card
- repair-gate
- repair-effects
- repair-ending-reachability
- repair-secret-route
- polish-prose
- export-index
- stop-as-noop

2. Verifier TRM

Reads current reports and says whether the artifact is allowed to advance.

Hard blockers:

- structural validator failure
- missing terminal route
- dead-end rate above zero unless explicitly tolerated
- missing output artifact
- quality report absent after claim of scoring

3. Repair TRM

Maps a concrete failure to a bounded edit.

Examples:

- `dead_end_rate > 0` -> add continuation reaction from bottleneck encounter
- `secret route absent` -> add gated option with two prerequisite variables
- `effect_operator_dominance` -> replace repeated `Nudge` with Blend/Clamp/WeightedSum where schema permits
- `pvalue_alignment low` -> rewrite desirability to reference actor and witness perception variables

4. Commit/Veto TRM

Commits an edit only if:

- target metric is plausible
- edit scope is local
- validator can be run after edit
- no unrelated files are touched

5. Curriculum TRM

Records the row for future training:

```json
{
  "world": "...",
  "metric_before": {},
  "failure": "...",
  "repair_plan": "...",
  "edit_scope": ["..."],
  "metric_after": {},
  "commit": true
}
```

## General Build Loop

1. Baseline

Run validator, quality gate, authoring score, Monte Carlo, SWMD export, and encounter index.

2. Symbolize

Make a small source card:

- title/about
- cast
- variables
- spools
- ending map
- current failures
- 3-6 repair targets

3. Route

Choose one bounded operation from the Router TRM list.

4. Edit

Modify only the local artifacts required by the chosen operation.

5. Verify

Run the same metrics again.

6. Compare

Write before/after JSON and a short delta brief.

7. Iterate

Do not start another generation loop unless the previous loop changed either files or metrics.

## Prompt Contract for Hermes

When calling Hermes on local Qwen, use one skill:

`storyworld-conveyor-runner`

Keep prompt shape:

```text
Use only the storyworld-conveyor-runner skill.
Use terminal tools; do not narrate future actions without tool calls.
Read <source_card.md>.
Read <MeTTa_TRM_Storyworld_Building.md>.
Run the bounded conveyor operation requested below.
Write all outputs under <run_dir>.
If a tool or stage fails, record the failure in <run_dir>/failure.md and stop cleanly.
```

## Success Metrics

A successful iteration must produce at least one of:

- better `weighted_authoring_verifier_score`
- fewer strict quality failures
- lower dead-end rate
- more balanced ending distribution
- reachable secret route where absent before
- valid SWMD and encounter index where absent before
- clear failure diagnosis showing why the conveyor could not follow the task

No-op detection:

If files and metrics are unchanged, call the iteration a no-op failure.
