# AGENTS.md

## Purpose
GPTStoryworld is the authoring/conversion side of the storyworld stack.
Primary outputs are SweepWeave JSON and token-efficient SWMD markdown (`SWMD-0`, `SWMD-0-MIN`) used by TRM training/eval tooling.

## Repo Role In The Split
- `GPTStoryworld`:
  - Author/edit storyworld JSON.
  - Export JSON -> SWMD (`codex-skills/storyworld-building/scripts/json_to_swmd.py`).
  - Keep human-facing reader tools.
- `StoryworldTRM/TRMStoryworld`:
  - Build controller datasets.
  - Run TRM eval/rollout harness and benchmarks.

## Canonical Workflow
1. Author or tune storyworld JSON in `storyworlds/`.
2. Export SWMD:
   - Full: `python codex-skills/storyworld-building/scripts/json_to_swmd.py in.json out.swmd.md`
   - Minified: `python codex-skills/storyworld-building/scripts/json_to_swmd.py in.json out.swmd.min.md --mode minified`
3. Feed SWMD-min into TRM dataset/eval tools in `TRMStoryworld`.
4. Keep IDs stable (`enc_*`, `opt_*`, `rxn_*`) for deterministic round-trip and hashing.

## Security And Git Hygiene (Mandatory)
- Never commit secrets in logs, prompts, model specs, or artifacts.
- Before commit, scan for key-like tokens:
  - `sk-...`, `sk-proj-...`, `Bearer ...`, `OPENAI_API_KEY=...`
- If found in logs/artifacts, redact in-place before staging:
  - Replace token with `REDACTED` (preserve surrounding log context).
- Do not commit generated run logs/artifacts unless explicitly requested.

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
- `storyworlds/diplomacy/*.json`
- `storyworld_reader.html`
- `storyworld_reader_swmd.html` (experimental)
