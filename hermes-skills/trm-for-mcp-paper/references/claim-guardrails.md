# TRM For MCP Claim Guardrails

Use this reference before changing claims, framing, or conclusions.

## Safe Core Claim

A tiny model with a hard memory and context budget can materially improve task performance when MCP externalizes world state and a routing policy selects relevant evidence at answer time.

## Strong But Defensible Claims

- MCP acts as an external memory control plane for tiny models.
- Under the measured bounded setup, the 2B trivia model outperforms its own closed-book baseline when using MCP-routed retrieval.
- Storyworld MCP packetization supports phased generation over outputs much larger than the active prompt window.
- Answer correctness can improve even when explicit route-faithfulness remains weak.

## Claims That Need Extra Caution

- “TRM learned routing.”
  Use only when paired with the measured route metric and its limitations.
- “Context for free.”
  Clarify that the free part is effective accessible state relative to active prompt budget, not literal zero-cost retrieval.
- “Generalization.”
  Use only with a clear statement of what held-out condition or cross-environment split is meant.

## Claims To Avoid

- The 2B model inherently knows the benchmark answers.
- The router faithfully learned the intended policy when route accuracy is low.
- The storyworld pipeline proves universal long-context reasoning.
- The measured frozen slice is equivalent to a broad trivia benchmark.
- Storyworld output size alone proves coherent authorship quality.

## Caveat Patterns

Use one when needed:

- “The answer metric improved even though route fidelity remained limited.”
- “This is a bounded environment study rather than a universal benchmark result.”
- “The output-scale result shows externalized state handling, not unrestricted long-context reasoning.”
- “The current evidence supports capability gain under this budget, not a full routing-policy imitation claim.”
