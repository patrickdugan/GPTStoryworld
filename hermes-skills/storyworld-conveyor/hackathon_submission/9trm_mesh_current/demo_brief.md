# Hermes Hackathon Storyworld Demo Brief

## Claim

A 27B local model is not reliable enough to be the whole storyworld-building agent. The demo claim is narrower and stronger: Hermes skills make the model viable as a bounded authoring/reasoning component inside an MCP, MeTTa, TRM, and verifier-controlled loop.

## Evidence Lanes

- Source storyworld: `C:\projects\GPTStoryworld\storyworlds\by-week\2026-W11\validated_macbeth.json`
- Encounters/options/reactions: 16 / 58 / 178
- Whole-context JSON estimate: 705087 tokens
- MCP preflight status: completed
- MCP worst packet estimate: 13556 tokens (52.0x smaller than whole-context JSON)
- MCP overflow count: 0
- Baseline authoring score: 0.607636946452147
- Candidate authoring score: 0.7199964970139447
- Score delta: 0.1123595505617977
- Baseline failures: ['p2value_refs', 'validator_errors']
- Candidate failures: ['validator_errors']

## Demo Interpretation

This should be presented as benchmark transcendence by architecture, not as evidence that Qwen 27B is secretly strong. The model contributes local prose and option-level inference; MCP constrains context, MeTTa gives a compact world model, TRM packets pick repair targets and commit/veto criteria, and validators prevent compliance theater.

## Live Talk Track

1. Show naive whole-context cost and failure mode: broad storyworld authoring burns context and tends to narrate intentions.
2. Show MCP preflight: the same world is sliced into bounded packets with hard overflow checks.
3. Show MeTTa/TRM packet: failures become typed repair targets instead of vague quality complaints.
4. Show before/after score: the scaffold moves measured authoring quality even when the 27B model is mediocre.
5. State the actual research thesis: compact open models become useful when skills act as control planes over tools, memory, verifiers, and repair curricula.

## Artifacts

- Summary JSON: `C:\projects\GPTStoryworld\hermes-skills\storyworld-conveyor\tmp\hackathon_storyworld_demo\demo_summary.json`
- Scorecard CSV: `C:\projects\GPTStoryworld\hermes-skills\storyworld-conveyor\tmp\hackathon_storyworld_demo\demo_scorecard.csv`
- Hermes prompt: `C:\projects\GPTStoryworld\hermes-skills\storyworld-conveyor\tmp\hackathon_storyworld_demo\hermes_live_prompt.txt`
- MCP run dir: `C:\projects\GPTStoryworld\hermes-skills\storyworld-conveyor\tmp\hackathon_storyworld_demo\mcp_preflight\context_port_runs\mcp_preflight_mcp`
- MeTTa/TRM run summary: `C:\projects\GPTStoryworld\hermes-skills\storyworld-conveyor\tmp\hackathon_storyworld_demo\metta_trm_loop\run_summary.json`
