---
name: trm-for-mcp-paper
description: Build and update the TRM for MCP paper package in GPTStoryworld, including figure regeneration, benchmark table refresh, storyworld and trivia environment-study framing, and the standalone LaTeX manuscript `papers/trm_for_mcp/trm_for_mcp_context_for_free.tex`. Use when Codex needs to revise the paper, refresh plots from local run artifacts, tighten claims against evidence, or stage the manuscript for PDF compilation.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Research, Paper, MCP, TRM, Trivia, Storyworlds]
    related_skills: [pure-trm-trainer, storyworld-conveyor-runner]
---

# TRM For MCP Paper

Use this skill when the target is the paper package, not the benchmark or training loop itself.

The paper workspace is:

- `papers/trm_for_mcp/`

The canonical manuscript is:

- `papers/trm_for_mcp/trm_for_mcp_context_for_free.tex`

## Quick Start

1. Read [artifact-map.md](./references/artifact-map.md).
2. Read [claim-guardrails.md](./references/claim-guardrails.md).
3. If the paper depends on fresh trivia numbers, use the context-constrained workflow in [context-constrained-workflow.md](./references/context-constrained-workflow.md).
4. Rebuild the generated paper assets:
   - `python hermes-skills/trm-for-mcp-paper/scripts/build_trm_for_mcp_paper.py`
5. Only then edit the manuscript.
6. Compile only if a local TeX toolchain exists.

## Workflow

1. Start from local artifacts, not paper prose.
   - Read [artifact-map.md](./references/artifact-map.md).
   - Refresh figures before editing claims if any benchmark inputs may have changed.
   - If the user is changing argument, title, abstract, or captions, also read [manuscript-playbook.md](./references/manuscript-playbook.md).
2. Rebuild generated assets.
   - Canonical command:
     - `python hermes-skills/trm-for-mcp-paper/scripts/build_trm_for_mcp_paper.py`
   - This regenerates:
     - `papers/trm_for_mcp/figures/*.png`
     - `papers/trm_for_mcp/generated/*.tex`
     - `papers/trm_for_mcp/generated/metrics_summary.json`
3. Edit the manuscript only after the generated assets are current.
   - Keep claims tied to measured outputs.
   - Separate answer accuracy from route fidelity.
   - Treat storyworld runs as an environment study unless stronger replicated evals exist.
4. Compile only if a TeX toolchain is available locally.
   - Optional command:
     - `python hermes-skills/trm-for-mcp-paper/scripts/build_trm_for_mcp_paper.py --compile`
   - If `pdflatex` is missing, do not claim the PDF was built.
5. When adding new figures or tables, update the build script first so the paper stays reproducible.
6. Keep the manuscript synchronized with the generated macros and tables.
   - If a number appears in prose and already exists in `generated/metrics_macros.tex`, prefer the macro.
   - If a figure depends on a new metric, add it to `build_assets.py` and emit it into `generated/metrics_summary.json` or a new generated `.tex` include.
7. When the user wants fresh evidence rather than prose revision, use the context-constrained wrappers in this skill first.
   - Those wrappers intentionally delegate benchmark and training execution to `pure-trm-trainer`.
   - Do not fork separate benchmark logic inside this paper skill.

## Task Modes

Use one of these modes explicitly when planning the work.

- `refresh`
  - Rebuild figures, tables, and macros from current run artifacts with minimal prose edits.
- `tighten`
  - Revise abstract, thesis, interpretation, captions, and section transitions without changing the figure set.
- `extend`
  - Add a new figure, table, appendix, section, or comparison while preserving reproducibility.
- `compile`
  - Attempt PDF compilation only after a successful asset rebuild.

## Context-Constrained Workflow

This skill includes thin scripts for the 4 GB-class workflow that the paper depends on.

Use them when the user wants to refresh evidence under the same constrained regime:

- Safe capped router training:
  - `python hermes-skills/trm-for-mcp-paper/scripts/run_context_constrained_trivia_train.py`
- Single trivia bench run:
  - `python hermes-skills/trm-for-mcp-paper/scripts/run_context_constrained_trivia_bench.py --run-id <name>`
- Base-vs-adapter benchmark matrix:
  - `python hermes-skills/trm-for-mcp-paper/scripts/run_context_constrained_benchmark_matrix.py`
- Storyworld environment-study refresh:
  - `python hermes-skills/trm-for-mcp-paper/scripts/run_context_constrained_storyworld_env.py --run-id <name>`
- Full evidence refresh:
  - `python hermes-skills/trm-for-mcp-paper/scripts/refresh_trm_for_mcp_evidence.py`
- Release bundle packaging:
  - `python hermes-skills/trm-for-mcp-paper/scripts/package_trm_for_mcp_release.py`
  - Add `--no-zip` only if you want the directory bundle without the archive.

These are wrappers over:

- `hermes-skills/pure-trm-trainer/scripts/run_wiki_card_router_train_capped.ps1`
- `hermes-skills/pure-trm-trainer/scripts/run_trm_bench.py`
- `hermes-skills/pure-trm-trainer/references/wiki-card-router-training-spec.safe.json`
- `hermes-skills/pure-trm-trainer/references/wiki-card-routerbench-spec.json`
- `hermes-skills/storyworld-conveyor/scripts/run_small_model_storyworld_port.py`
- `hermes-skills/storyworld-conveyor/sample_data/qwen2b_4gb_context_port.json`

Read [context-constrained-workflow.md](./references/context-constrained-workflow.md) before editing those paths.

## Section Playbook

- `Abstract`
  - State the operational claim.
  - Name both studies.
  - Report the strongest bounded result and one caveat.
- `Thesis`
  - Distinguish “externalized memory” from “model knowledge.”
- `Experimental Setting`
  - Pin the hardware and context constraints.
  - Separate storyworld environment-study framing from trivia benchmark framing.
- `Trivia Environment Study`
  - Report closed-book, stuffed, MCP answer accuracy, and route accuracy separately.
  - Keep answer-quality claims tied to the frozen slice.
- `Storyworld Environment Study`
  - Frame artifact-size, prompt-token, latency, and fallback behavior as systems evidence.
  - Do not imply the storyworld plots are a fully comparable QA benchmark.
- `Interpretation`
  - Explain why answer gains and route-faithfulness can diverge.
- `Next Work`
  - Prefer concrete benchmark or routing-abstraction extensions over generic future-work prose.

Read [manuscript-playbook.md](./references/manuscript-playbook.md) for detailed guidance and preferred wording patterns.

## Figure And Table Policy

- Every figure must be generated from checked-in code.
- Every benchmark table must trace back to local JSON or JSONL artifacts named in [artifact-map.md](./references/artifact-map.md).
- Histogram bins do not need to stay fixed across revisions, but the underlying source files must.
- If a figure becomes interpretively ambiguous, add a caption caveat rather than silently dropping the ambiguity.
- Prefer one strong figure over multiple weak, redundant plots.

## Claim Governance

Use [claim-guardrails.md](./references/claim-guardrails.md) before changing the title, abstract, interpretation, or conclusion.

Short version:

- Allowed:
  - MCP improves a tiny model relative to its own no-retrieval baseline under the measured budget.
  - Storyworld MCP packetization supports outputs larger than the active prompt window.
  - The frozen trivia slice demonstrates answer-quality gains under bounded retrieval.
- Not allowed:
  - “The 2B model knows the full world.”
  - “TRM learned a faithful routing policy” when route accuracy is low.
  - “Context is literally free.”

## Scope

This skill covers:

- the paper title and manuscript structure
- figure regeneration from local run artifacts
- benchmark summary tables
- storyworld output-size and phase-event plots
- trivia benchmark plots and score tables
- conservative interpretation of MCP vs. TRM claims

This skill does not cover:

- launching new training runs
- changing the benchmark harness
- editing storyworld generation code unless the paper depends on it

For those, switch to:

- `pure-trm-trainer`
- `storyworld-conveyor-runner`

## Canonical Commands

- Rebuild paper assets:
  - `python hermes-skills/trm-for-mcp-paper/scripts/build_trm_for_mcp_paper.py`
- Rebuild and try to compile:
  - `python hermes-skills/trm-for-mcp-paper/scripts/build_trm_for_mcp_paper.py --compile`
- Rebuild assets directly from the paper workspace:
  - `python papers/trm_for_mcp/build_assets.py`
- Launch the safe capped trivia trainer through `pure-trm-trainer`:
  - `python hermes-skills/trm-for-mcp-paper/scripts/run_context_constrained_trivia_train.py`
- Launch one bounded trivia bench through `pure-trm-trainer`:
  - `python hermes-skills/trm-for-mcp-paper/scripts/run_context_constrained_trivia_bench.py --run-id wiki_card_routerbench_qwen2b_safe_refresh`
- Launch the paper's base-vs-adapter benchmark matrix:
  - `python hermes-skills/trm-for-mcp-paper/scripts/run_context_constrained_benchmark_matrix.py`
- Launch the bounded storyworld environment study:
  - `python hermes-skills/trm-for-mcp-paper/scripts/run_context_constrained_storyworld_env.py --run-id storyworld_env_refresh`
- Refresh bounded trivia, bounded storyworld, and then rebuild the paper assets:
  - `python hermes-skills/trm-for-mcp-paper/scripts/refresh_trm_for_mcp_evidence.py`
- Package a paper release bundle with a source-run manifest:
  - `python hermes-skills/trm-for-mcp-paper/scripts/package_trm_for_mcp_release.py`

## Hard Rules

- Do not cite numbers from stale markdown notes when generated JSON artifacts exist.
- Do not merge route accuracy into answer accuracy.
- Do not claim route-faithful learning when the measured route metric is low.
- Do not describe storyworld outputs as direct small-model single-pass prompt completions when the pipeline used MCP packetization and phased generation.
- Do not add hand-made figures that cannot be regenerated from repo-local code.

## Canonical Files

- Manuscript:
  - `papers/trm_for_mcp/trm_for_mcp_context_for_free.tex`
- Figure/table builder:
  - `papers/trm_for_mcp/build_assets.py`
- Hermes wrapper:
  - `hermes-skills/trm-for-mcp-paper/scripts/build_trm_for_mcp_paper.py`
- Context-constrained training wrapper:
  - `hermes-skills/trm-for-mcp-paper/scripts/run_context_constrained_trivia_train.py`
- Context-constrained bench wrapper:
  - `hermes-skills/trm-for-mcp-paper/scripts/run_context_constrained_trivia_bench.py`
- Context-constrained matrix wrapper:
  - `hermes-skills/trm-for-mcp-paper/scripts/run_context_constrained_benchmark_matrix.py`
- Storyworld environment wrapper:
  - `hermes-skills/trm-for-mcp-paper/scripts/run_context_constrained_storyworld_env.py`
- Full evidence refresh wrapper:
  - `hermes-skills/trm-for-mcp-paper/scripts/refresh_trm_for_mcp_evidence.py`
- Release bundle wrapper:
  - `hermes-skills/trm-for-mcp-paper/scripts/package_trm_for_mcp_release.py`
- Generated outputs:
  - `papers/trm_for_mcp/figures/`
  - `papers/trm_for_mcp/generated/`
- Skill UI metadata:
  - `hermes-skills/trm-for-mcp-paper/agents/openai.yaml`

## References

- Artifact source map: [artifact-map.md](./references/artifact-map.md)
- Manuscript playbook: [manuscript-playbook.md](./references/manuscript-playbook.md)
- Claim guardrails: [claim-guardrails.md](./references/claim-guardrails.md)
- Context-constrained workflow: [context-constrained-workflow.md](./references/context-constrained-workflow.md)

## Example Requests

- "Use trm-for-mcp-paper to refresh the figures and tighten the abstract."
- "Rebuild the TRM for MCP paper package and compile the PDF if TeX is installed."
- "Update the trivia section with the newest scorecard and keep the claims conservative."
- "Use trm-for-mcp-paper in extend mode to add a figure for route-faithfulness vs answer accuracy."
