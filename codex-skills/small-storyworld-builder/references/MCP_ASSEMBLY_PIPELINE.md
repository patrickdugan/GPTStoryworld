# MCP Assembly Pipeline (Small-Model, 8k Context)

Use this as the default planner/worker contract for 1.5B-3B local models.

## Objective
Build storyworld acts through a deterministic assembly line:
1. Spool -> encounter chunk assembly
2. Numeric invariant review
3. Act completion plan
4. Holistic appraisal (full or `partial_chunked`)

## Inputs
- `global_state`
- `act_goal`
- `spool_batch` (3-5 spools)
- `neighbor_summaries`
- `invariants`
- `mc_summary`
- `manifold_summary`

## Phases
1. `plan`
- Output JSON only: `objective`, `constraints`, `risks`, `checks`.

2. `characterize`
- Output JSON only: `voices`, `tensions`, `stance_shift`, `dialogue_style`.

3. `encounter_build`
- Output one SWMD encounter block only.
- First line must be `ENC <id> turn=<span>`.
- Must include at least one `ORX` line.

4. `act_complete`
- Output JSON only: `act_status`, `continuity_risks`, `unresolved_threads`, `next_focus`.
- Include numeric before/after values when available.

5. `recharacterize`
- Same JSON contract as `characterize`, after act updates.

6. `late_stage_holistic`
- Output one refined SWMD encounter block plus compact appraisal metadata in MCP logs.
- If full context cannot fit, set holistic mode to `partial_chunked`.

## Small-Model Guardrails
- Keep context budget <= 8192 tokens equivalent.
- Keep one target encounter per call.
- Prefer <= 3 options for small-mode passes unless explicitly overridden.
- Keep effects fan-out bounded and deterministic.
- Keep narrative concise and dialogue-forward.

## Invariant Review Contract
For each evaluated option include:
- `name`
- `value_before`
- `value_after`
- `status`
- `corrections` (minimal numeric changes only)

## Parse Accounting
Track both:
- `model_parse_ok` (raw model format quality)
- `parse_ok` (post-repair pipeline validity)

Use fallback-to-target-block on malformed output to keep the assembly line moving.
