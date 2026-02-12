# AGENTS.md

## Purpose
GPTStoryworld is the authoring/conversion side of the storyworld stack.
Primary outputs are SweepWeave JSON and token-efficient SWMD markdown (`SWMD-0`, `SWMD-0-MIN`) used by TRM training/eval tooling.

## Repo Role In The Split
- `GPTStoryworld`:
  - Author/edit storyworld JSON.
  - Export JSON -> SWMD (`codex-skills/storyworld-building/scripts/json_to_swmd.py`).
  - Provide quality gates and automated polish loops (scripts + envs).
  - Keep human-facing reader tools.
- `StoryworldTRM/TRMStoryworld`:
  - Build controller datasets.
  - Run TRM eval/rollout harness and benchmarks.

## Active Harness Surface (Most Used)
- Storyworld authoring + gates (skill scripts):
  - `codex-skills/storyworld-building/scripts/sweepweave_validator.py`
  - `codex-skills/storyworld-building/scripts/storyworld_quality_gate.py`
  - `codex-skills/storyworld-building/scripts/apply_artistry_pass.py`
  - `codex-skills/storyworld-building/scripts/one_shot_factory.py`
  - `codex-skills/storyworld-building/scripts/json_to_swmd.py`
- Benchmark-style scoring:
  - `storyworld-env/quality_vector_score.py`
  - `storyworld-env/__init__.py` (benchmark metrics + pass/fail targets)
  - `storyworld-env/pathing_lab/` (experimental pathing probes; optional)
- Text judge loop (LLM-as-judge):
  - `storyworld-text-quality-env/evaluate_text_quality.py`
  - `storyworld-text-quality-env/iterate_text_quality_loop.py`

## Canonical Workflow
1. Author or tune storyworld JSON:
   - Canonical storage: `storyworlds/by-week/YYYY-Www/*.json`
   - Diplomacy worlds: `storyworlds/diplomacy/` (already bucketed)
2. Validate structure:
   - `python codex-skills/storyworld-building/scripts/sweepweave_validator.py validate <world.json>`
3. Enforce artistry/scripts/pathing gates:
   - `python codex-skills/storyworld-building/scripts/apply_artistry_pass.py --in-json <in.json> --out-json <out.json> --gate-pct 0.10`
   - `python codex-skills/storyworld-building/scripts/storyworld_quality_gate.py --storyworld <world.json> --strict --report-out <report.json>`
4. Run text judge + iterative rewrite loop to reach a threshold:
   - Judge: `python storyworld-text-quality-env/evaluate_text_quality.py --storyworld <world.json> --out <judge.json> --judge-model gpt-4.1-mini`
   - Loop: `python storyworld-text-quality-env/iterate_text_quality_loop.py --in-json <in.json> --out-json <out.json> --threshold 0.8 --max-iters 3 --judge-model gpt-4.1-mini --writer-model gpt-4.1-mini --work-dir <workdir>`
   - Note: `gpt-5-mini` may return non-parseable JSON in this harness; `gpt-4.1-mini` is the reliable default for now.
5. Score with multi-dimensional env benchmark (ranking + targets):
   - `python storyworld-env/quality_vector_score.py --storyworlds <a.json> <b.json> ... --runs 200 --out <rank.json>`
6. Export SWMD:
   - Full: `python codex-skills/storyworld-building/scripts/json_to_swmd.py in.json out.swmd.md`
   - Minified: `python codex-skills/storyworld-building/scripts/json_to_swmd.py in.json out.swmd.min.md --mode minified`
7. Feed SWMD-min into TRM dataset/eval tools in `TRMStoryworld`.
8. Keep IDs stable (`enc_*`, `opt_*`, `rxn_*`) for deterministic round-trip and hashing.

## Security And Git Hygiene (Mandatory)
- Never commit secrets in logs, prompts, model specs, or artifacts.
- Before commit, scan for key-like tokens:
  - `sk-...`, `sk-proj-...`, `Bearer ...`, `OPENAI_API_KEY=...`
- If found in logs/artifacts, redact in-place before staging:
  - Replace token with `REDACTED` (preserve surrounding log context).
- Do not commit generated run logs/artifacts unless explicitly requested.
  - Default locations for generated artifacts: `logs/` and `storyworlds/sweeps/`.
  - Sweep intermediates can get large; if C: is tight, offload intermediates to `D:` and keep only summaries.

## Determinism Requirements
- Normalize newlines to LF for any hashed/canonical artifact.
- Deterministic ordering:
  - Encounters/options/reactions sorted by stable IDs.
- Hashing:
  - Keep `swmd_hash` based on normalized bytes only.
  - Avoid embedding machine-local absolute paths in hashed payloads.

## UI Tooling Rule
- `storyworld_reader.html` is the human reference reader.
- Do not overwrite it for experimental controller features.
- Experimental variants must use a new file (for example `storyworld_reader_swmd.html`).

## Editing Guidance
- Keep changes minimal and composable.
- Prefer adding scripts under `tools/` or `codex-skills/.../scripts/`.
- Avoid broad refactors of core runtime unless needed for determinism or compatibility.

## Key Files
- `codex-skills/storyworld-building/scripts/json_to_swmd.py`
- `codex-skills/storyworld-building/scripts/storyworld_quality_gate.py`
- `storyworld-text-quality-env/iterate_text_quality_loop.py`
- `storyworld-env/quality_vector_score.py`
- `storyworlds/diplomacy/*`
- `storyworlds/by-week/*`
- `storyworlds/sweeps/*`
- `storyworld_reader.html`
- `storyworld_reader_swmd.html` (experimental)
