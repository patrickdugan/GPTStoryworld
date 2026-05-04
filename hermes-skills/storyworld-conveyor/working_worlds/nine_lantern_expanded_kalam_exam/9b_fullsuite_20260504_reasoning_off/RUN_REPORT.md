# Qwen 9B Full-Suite Kalam Run

## Runtime

- Host: snacksack via local SSH tunnel to `http://127.0.0.1:8082/v1`
- Model: `Qwen3.5-9B.Q4_K_M.gguf`
- Server fix: relaunched llama.cpp with `--reasoning off --reasoning-budget 0`; the default thinking template produced empty visible content and timeouts.
- Source world: `../nine_lantern_expanded_kalam_exam.json`

## Full-Suite Artifacts

- Hilbert pathing packet: `hilbert_pathing/hilbert_pathing_packet.json`
- Hilbert brief: `hilbert_pathing/hilbert_pathing_brief.md`
- Operation packets: `operation_packets.hilbert.jsonl`
- MCP config: `mcp_config_9b_fullsuite.json`
- MCP preflight report: `context_port_runs/kalam_9b_fullsuite_reasoning_off/mcp_budget_preflight/budget_report.json`
- Successful 9B author loop: `metta_loop_isolated_mc20_promptfix/run_summary.json`
- 9B bounded suggestions: `metta_loop_isolated_mc20_promptfix/qwen_authoring_suggestions.json`

## Results

- Whole-context JSON estimate: 771,634 tokens.
- MCP worst packet: 5,646 tokens with 0 overflow under an 8,192 token context budget.
- Hilbert depth finding: graph has 29 encounters, 225 edges, max reachable depth 21; the secret loci at depths 20-21 are short of the 30-40 turn target.
- Deterministic p2 patch touched 80 reactions and increased p2 refs from 675 to 755, but did not change the weighted authoring score.
- Baseline authoring score: 0.8664348659003831.
- Candidate authoring score: 0.8664348659003831.
- Quality gate: pass before and after.

## Interpretation

The 9B model can produce useful bounded local design notes once the prompt is storyworld-specific and reasoning is disabled. It generated Kalam-relevant route-depth notes, foreshadowing lines, secret-route clues, and effect-variety notes.

This does not yet prove 9B can execute the full repair. The current loop records the 9B suggestions and applies deterministic p2 support; it does not yet materialize bridge encounters, reroute the unreachable ending, or commit/veto schema edits from the 9B output. The next experiment should train or script a controller that converts these bounded suggestions into typed operation packets and verifier-gated patches.
