# Context-Constrained Workflow

Use this reference when the paper needs fresh evidence from the same 4 GB-class setup rather than only prose updates.

## Goal

Keep all benchmark and training execution anchored to the existing `pure-trm-trainer` stack while preserving the same bounded-memory story the paper argues:

- 2B-class model
- 4-bit loading
- small active context budget
- explicit GPU and CPU placement caps
- no ad hoc long-context stuffing beyond the measured workflow

## Canonical Dependencies

Training source of truth:

- `hermes-skills/pure-trm-trainer/scripts/run_wiki_card_router_train_capped.ps1`
- `hermes-skills/pure-trm-trainer/references/wiki-card-router-training-spec.safe.json`

Benchmark source of truth:

- `hermes-skills/pure-trm-trainer/scripts/run_trm_bench.py`
- `hermes-skills/pure-trm-trainer/references/wiki-card-routerbench-spec.json`

Storyworld environment-study source of truth:

- `hermes-skills/storyworld-conveyor/sample_data/qwen2b_4gb_context_port.json`
- `hermes-skills/storyworld-conveyor/context_port_runs/`

## Intended Order

1. Train or reuse a safe capped adapter.
2. Run the frozen trivia slice with the same bounded caps.
3. If needed, refresh storyworld environment-study artifacts separately.
4. Rebuild the paper figures and tables from local outputs.
5. Package a release bundle once the manuscript and generated assets are in sync.

## Wrapper Scripts In This Skill

- `scripts/run_context_constrained_trivia_train.py`
  - thin wrapper over the capped PowerShell trainer launcher in `pure-trm-trainer`
- `scripts/run_context_constrained_trivia_bench.py`
  - thin wrapper over `pure-trm-trainer/scripts/run_trm_bench.py --bench wiki-card-routerbench`
- `scripts/run_context_constrained_benchmark_matrix.py`
  - convenience runner for the paper's base-vs-adapter trivia comparison
- `scripts/run_context_constrained_storyworld_env.py`
  - thin wrapper over `storyworld-conveyor/scripts/run_small_model_storyworld_port.py`
- `scripts/refresh_trm_for_mcp_evidence.py`
  - orchestrates the storyworld wrapper, the trivia matrix wrapper, and then the paper asset rebuild
- `scripts/package_trm_for_mcp_release.py`
  - packages the manuscript, generated assets, and a source-run manifest into a release directory and zip archive

## Release Packaging

Use this after the evidence refresh path, not before it.

Canonical command:

- `python hermes-skills/trm-for-mcp-paper/scripts/package_trm_for_mcp_release.py`

Behavior:

- rebuilds paper assets unless `--skip-rebuild` is passed
- creates `papers/trm_for_mcp/releases/<bundle-name>/`
- writes `release_manifest.json` with exact source runs and git revision
- creates `<bundle-name>.zip` by default
- supports `--no-zip` when only the directory bundle is wanted

The manifest is the provenance record for the paper package. Do not ship a release bundle without it.

## Hard Rules

- Do not create separate training specs in the paper skill unless the paper requires a genuinely new measured condition.
- Do not bypass the capped trainer path for the claimed 4 GB workflow.
- Do not bypass the bounded storyworld port path for the storyworld environment study.
- Do not hardcode benchmark outcomes into the manuscript.
- Do not mix storyworld environment-study artifacts and trivia scorecards as if they came from one unified benchmark harness.
- Do not package a release bundle from stale generated assets unless the user explicitly asks for that tradeoff.
