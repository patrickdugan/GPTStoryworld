# The Ninth Lantern of Bukhara: Hermes 27B Packet-to-Playable Storyworld Demo

## Abstract
This note documents a hackathon-scale storyworld authoring pipeline in which Hermes running Qwen 27B authors a compact design packet, while a deterministic MeTTa/TRM-inspired control plane materializes that packet into a validated SweepWeave storyworld. The experiment fixes the prior failure mode: instead of asking the model to explore the repository and then emit a large artifact through tools, the model produces bounded creative/game-design content and the scaffold handles schema, pValue/p2Value effects, routing, endings, and validation.

## Method
The run separates the work into three layers: Hermes/Qwen 27B supplies scenes, choices, endings, and secret-route motifs; the materializer maps those choices into a fixed lattice of variables, option profiles, p/p2 belief references, and reaction/effect templates; the validators score structural validity, quality, authoring completeness, and Monte Carlo ending reachability. This is the practical demo version of the larger MeTTa+TRM storyworld-builder thesis: the LLM remains the prose and imagination module, while the scaffold performs control-plane work that smaller local models handle poorly.

## Result
The materialized artifact contains 10 playable non-terminal encounters, 8 endings, 40 options, 120 reactions, and 600 bounded-number effects. Validator pass: True. Quality gate pass: True with failures=[]. Authoring score: 0.858900462962963.

## Demo Claim
This is not a claim that 27B alone can reliably build a full robust storyworld. The useful claim is narrower and stronger for the hackathon: with a skill/MCP/TRM-style scaffold, a 27B local model can contribute viable creative design packets to a schema-heavy interactive artifact that would otherwise collapse under context, tool-use, or validator constraints.

## Artifacts
- Hermes transcript: `hermes-skills/storyworld-conveyor/hermes_runs/qwen27b_packet_artifact_20260503T224648Z/transcript.clean.txt`
- Hermes packet: `hermes-skills\storyworld-conveyor\hermes_runs\qwen27b_packet_artifact_20260503T224648Z\hermes_packet.json`
- Playable storyworld JSON: `C:\projects\GPTStoryworld\hermes-skills\storyworld-conveyor\working_worlds\hermes_qwen27b_packet_storyworld\hermes_qwen27b_packet_storyworld.json`
- Run summary: `C:\projects\GPTStoryworld\hermes-skills\storyworld-conveyor\working_worlds\hermes_qwen27b_packet_storyworld\run_summary.json`
