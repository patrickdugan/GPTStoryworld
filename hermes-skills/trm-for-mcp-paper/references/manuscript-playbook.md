# TRM For MCP Manuscript Playbook

Use this reference when editing the paper text itself rather than just rebuilding plots.

## Section Intent

### Abstract

Target shape:

1. Problem: tiny models have hard context and memory limits.
2. Mechanism: MCP externalizes state; TRM can help control retrieval.
3. Evidence: storyworld environment study plus trivia benchmark.
4. Caveat: route faithfulness still lags.

Preferred pattern:

- sentence 1: operational setup
- sentence 2: mechanism and claim
- sentence 3: storyworld result
- sentence 4: trivia result
- sentence 5: caveat

### Title

`TRM for MCP: Context for Free` is rhetorically strong but should be handled carefully in surrounding prose.

Use nearby text to clarify:

- “for free” means externalized context under a fixed active prompt budget
- not free compute
- not free routing tokens
- not universal model knowledge

### Trivia Section

Must include:

- the fixed model family
- the fixed frozen slice size
- closed-book baseline
- stuffed baseline
- MCP-routed result
- route-faithfulness caveat

Good caption pattern:

- first clause: what is plotted
- second clause: what the main effect is
- third clause: what the reader should not overinterpret

### Storyworld Section

Treat this as a systems and environment study.

Strong evidence types:

- artifact size
- bounded prompt usage
- phase latency
- fallback rates
- routing smoke accuracy

Avoid:

- framing it as a standard benchmark score unless one actually exists
- implying each final file is a one-shot direct completion

### Interpretation

Keep this section explicit about the distinction between:

- final answer correctness
- route selection correctness
- bounded-context usability

The paper gets stronger when it openly admits the router-policy gap.

## Figure Selection Heuristics

Use figures that answer one of these questions:

- Does MCP help a tiny model on a real measured task?
- Does MCP reduce evidence burden relative to stuffing?
- Does the storyworld pipeline stay inside bounded context while producing large artifacts?
- Where does fallback happen in the storyworld loop?

Cut figures that merely restate the same claim with weaker signal.

## Preferred Language

Use:

- “bounded retrieval”
- “externalized state”
- “active prompt window”
- “frozen trivia slice”
- “route faithfulness”
- “environment study”

Avoid:

- “infinite context”
- “the model memorized the world”
- “free knowledge”
- “solved routing”
- “full generalization”

## Revision Order

1. rebuild figures and tables
2. scan macros and generated summaries
3. patch abstract and captions
4. patch interpretation and conclusion
5. only then change title or section structure if still necessary
