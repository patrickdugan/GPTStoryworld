# Native Reasoning Schema Paper

This folder contains a short paper draft for the native master-control schema result in the MeTTa/TRM storyworld conveyor.

## Core Claim

A learned tiny master planner failed on fresh storyworld diagnostic rows because it lacked a reliable control-plane floor. A compact native reasoning schema, expressed as MeTTa-style diagnostic-to-role rules and wired into the auto-research loop as a teacher policy, routed the same rows with perfect agreement on the current slice.

## Current Evidence

- Run: `hermes-skills/storyworld-conveyor/trm_corpus/master_control_planner_native_schema_local_001/`
- Planner: `native`
- Rows: `16`
- Storyworlds: `validated_macbeth.json`, `hermes_qwen27b_packet_storyworld.json`
- Native agreement: `16/16 = 1.0`
- Shadow model route counts: `commit_veto_controller = 12`, `gate_secret_route_designer = 4`
- Shadow model agreement on this slice: `0/16`

## Build

From this directory, if a LaTeX distribution is available:

```powershell
pdflatex native_reasoning_schema_for_trm_control_planes.tex
pdflatex native_reasoning_schema_for_trm_control_planes.tex
```

The paper intentionally keeps citations local and artifact-based for now. Add external literature citations only when preparing a public version.
