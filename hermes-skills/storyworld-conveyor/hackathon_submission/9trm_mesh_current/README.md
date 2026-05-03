# Hermes 9-TRM Creative Skill Mesh Submission Pack

## One-Sentence Claim

Hermes skills can make smaller models useful for complex creative-engineering work by decomposing storyworld encounter assembly into MCP memory, MeTTa symbolic state, nine trained control policies, bounded LLM calls, and verifier-backed commit/veto.

## Evidence

- Trajectory rows: 1000
- Estimated corpus tokens: 284129
- Tiny control training accuracy: 0.96
- Tiny control eval rows: 100
- Whole-context estimate: 705087
- MCP worst packet tokens: 13556
- MCP overflow count: 0
- Storyworld authoring score delta: 0.1123595505617977

## Honest Scope

The trained model receipt here is a tiny per-role control-policy baseline, not a full neural TRM or QLoRA run. The important demo is the architecture: small trained control policies decide how to work the LLM inside the skill mesh.

## Talk Track

1. A 27B OSS model is too weak and too context-constrained to be the whole storyworld engineer.
2. The Hermes skill mesh decomposes the job into nine control roles.
3. MCP bounds context, MeTTa gives compact symbolic state, and validators create typed repair targets.
4. A tiny trained mesh chooses bounded LLM/tool actions with held-out receipts.
5. The result is a viable path for compact models in complex infused skills.
