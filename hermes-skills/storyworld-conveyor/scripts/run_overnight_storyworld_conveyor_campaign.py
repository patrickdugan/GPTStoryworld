#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


DEFAULT_SOURCES = [
    "storyworlds/public-domain-adaptations-2026-02-23/pd_jane_eyre_multiending_v1.json",
    "storyworlds/public-domain-adaptations-2026-02-23/pd_dracula_multiending_v1.json",
    "storyworlds/3-2-2026-endingmatrix-focus3-v1/hawthorne_scarlet_letter_reputation_conscience_multiending_v1.json",
    "storyworlds/by-week/2026-W11/validated_macbeth.json",
    "storyworlds/generated/1984_benchmark/1984_n_shot.json",
    "storyworlds/factory_runs/the_diamond_job/polished_world.json",
    "storyworlds/ottoman_qadi.json",
    "storyworlds/mihna_constitutional_alignment.json",
    "storyworlds/politburo_shehada_repaired.json",
]


def slugify(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value[:96] or "storyworld"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")


def run_cmd(
    cmd: list[str],
    cwd: Path,
    log_path: Path,
    timeout: int,
    continue_on_failure: bool = True,
) -> dict[str, Any]:
    started = time.time()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8", newline="\n") as log:
        log.write("$ " + " ".join(cmd) + "\n\n")
        log.flush()
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(cwd),
                text=True,
                stdout=log,
                stderr=subprocess.STDOUT,
                timeout=timeout,
            )
            rc = proc.returncode
        except subprocess.TimeoutExpired:
            log.write(f"\nTIMEOUT after {timeout}s\n")
            rc = 124
    result = {
        "command": cmd,
        "returncode": rc,
        "seconds": round(time.time() - started, 3),
        "log": str(log_path),
    }
    if rc != 0 and not continue_on_failure:
        raise RuntimeError(f"command failed: {' '.join(cmd)} -> {rc}")
    return result


def world_metadata(path: Path) -> dict[str, Any]:
    try:
        data = read_json(path)
    except Exception as exc:
        return {"path": str(path), "load_error": f"{type(exc).__name__}: {exc}"}
    encounters = data.get("encounters") if isinstance(data.get("encounters"), list) else []
    spools = data.get("spools") if isinstance(data.get("spools"), list) else []
    characters = data.get("characters") if isinstance(data.get("characters"), list) else []
    properties = data.get("authored_properties") if isinstance(data.get("authored_properties"), list) else []
    terminal = [e for e in encounters if not e.get("options")]
    option_count = sum(len(e.get("options") or []) for e in encounters)
    reaction_count = sum(len(o.get("reactions") or []) for e in encounters for o in (e.get("options") or []))
    effect_count = sum(
        len(r.get("after_effects") or [])
        for e in encounters
        for o in (e.get("options") or [])
        for r in (o.get("reactions") or [])
    )
    return {
        "path": str(path),
        "title": data.get("title") or data.get("storyworld_title") or path.stem,
        "about": str(data.get("about_text") or "")[:1200],
        "encounters": len(encounters),
        "terminal_encounters": len(terminal),
        "spools": len(spools),
        "characters": len(characters),
        "properties": len(properties),
        "options": option_count,
        "reactions": reaction_count,
        "after_effects": effect_count,
        "avg_options_per_encounter": round(option_count / max(1, len(encounters)), 3),
        "avg_reactions_per_option": round(reaction_count / max(1, option_count), 3),
        "avg_effects_per_reaction": round(effect_count / max(1, reaction_count), 3),
    }


def make_source_card(
    repo: Path,
    source: Path,
    run_dir: Path,
    meta: dict[str, Any],
    trm_advice_path: Path | None,
    iteration_index: int,
) -> Path:
    card = run_dir / f"source_card_iteration_{iteration_index:02d}.md"
    title = meta.get("title") or source.stem
    trm_line = f"- TRM advice: `{trm_advice_path}`" if trm_advice_path else "- TRM advice: not available yet"
    output_version = max(1, iteration_index)
    card.write_text(
        f"""# Source Card: {title}

## Source

`{source.as_posix()}`

## Counts

```json
{json.dumps(meta, indent=2, ensure_ascii=True)}
```

## Available Reports

- Baseline directory: `{run_dir.as_posix()}`
{trm_line}
- General MeTTa/TRM scaffold: `hermes-skills/storyworld-conveyor/runtime_prompts/MeTTa_TRM_Storyworld_Building.md`

## Iteration Task

Iteration {iteration_index}: create or improve a derivative storyworld using the conveyor discipline.

Output target:

`{(run_dir / "derivative" / (slugify(source.stem) + f"_metta_trm_v{output_version}.json")).as_posix()}`

Requirements:

- Use the source world as a prompt/structure source, not as context to dump into the model.
- Preserve the source world's strongest structural idea, but change the premise enough to be a new benchmark candidate.
- Add or preserve multiple endings and at least one secret/synthesis route.
- Use MeTTa-style symbolic planning for variables, gates, endings, and repair targets.
- Use TRM-style repair packets: router, verifier, repair, commit/veto, curriculum row.
- Run validator and at least one quality/authoring score after creating or modifying the derivative.
- If a stage fails, write `failure.md` explaining whether the failure is model/tool-following, schema, verifier, context budget, or missing script.

## Conveyor Constraints

- Use only bounded artifacts: cards, reports, SWMD-min, encounter index.
- Do not inline a whole JSON storyworld into a prompt.
- Do not claim success unless output files exist and validation was attempted.
- Prefer terminal tools over prose.
""",
        encoding="utf-8",
        newline="\n",
    )
    return card


def hermes_prompt(
    source_card: Path,
    iteration_dir: Path,
    source: Path,
    iteration_index: int,
    previous_dir: Path | None,
) -> str:
    previous_text = ""
    if previous_dir is not None:
        previous_text = f"""
Read the previous iteration directory before editing:
{previous_dir.as_posix()}

Compare against its `hermes_artifact_report.md`, `failure.md`, validator outputs, and derivative JSON if present.
Your job is not to restart from scratch; repair or improve the best available derivative unless it is unusable.
"""
    return f"""Use only the storyworld-conveyor-runner skill.
Use terminal tools. Do not narrate intended actions without tool calls.

Read this source card:
{source_card.as_posix()}

Read this general scaffold:
hermes-skills/storyworld-conveyor/runtime_prompts/MeTTa_TRM_Storyworld_Building.md
{previous_text}

Task:
Iteration {iteration_index}: create or improve one derivative storyworld based on the source world `{source.as_posix()}` and the source card, using the conveyor discipline. Write artifacts under `{iteration_dir.as_posix()}`. If direct full generation is too large, create a seed derivative and a concrete repair plan with verifier outputs. Run validator and quality/authoring checks where possible. Record all commands and outcomes in `{(iteration_dir / 'hermes_artifact_report.md').as_posix()}`.

Hard rule:
If you cannot complete the derivative, create `{(iteration_dir / 'failure.md').as_posix()}` with a precise failure class and the next bounded command to run.
"""


def baseline_source(repo: Path, source: Path, run_root: Path, args: argparse.Namespace, idx: int) -> dict[str, Any]:
    rel_slug = slugify(source.with_suffix("").as_posix())
    run_dir = run_root / f"{idx:02d}_{rel_slug}"
    reports = run_dir / "reports"
    worlds = run_dir / "worlds"
    indices = run_dir / "indices"
    logs = run_dir / "logs"
    worlds.mkdir(parents=True, exist_ok=True)
    copied_source = worlds / source.name
    if not copied_source.exists():
        shutil.copy2(source, copied_source)

    meta = world_metadata(source)
    write_json(reports / "metadata.json", meta)

    commands: list[dict[str, Any]] = []
    story_scripts = repo / "codex-skills" / "storyworld-building" / "scripts"
    conveyor_scripts = repo / "hermes-skills" / "storyworld-conveyor" / "scripts"
    small_scripts = repo / "codex-skills" / "small-storyworld-builder" / "scripts"

    commands.append(run_cmd(
        [args.python_bin, str(story_scripts / "sweepweave_validator.py"), "validate", str(source)],
        repo,
        logs / "validator.log",
        timeout=args.command_timeout,
    ))

    quality_report = reports / "quality_gate.json"
    if (story_scripts / "storyworld_quality_gate.py").exists():
        commands.append(run_cmd(
            [
                args.python_bin,
                str(story_scripts / "storyworld_quality_gate.py"),
                "--storyworld",
                str(source),
                "--strict",
                "--report-out",
                str(quality_report),
            ],
            repo,
            logs / "quality_gate.log",
            timeout=args.command_timeout,
        ))

    authoring_report = reports / "authoring_score.json"
    if (conveyor_scripts / "score_storyworld_authoring.py").exists():
        commands.append(run_cmd(
            [
                args.python_bin,
                str(conveyor_scripts / "score_storyworld_authoring.py"),
                "--storyworld",
                str(source),
                "--repo-root",
                str(repo),
                "--out-json",
                str(authoring_report),
            ],
            repo,
            logs / "authoring_score.log",
            timeout=args.command_timeout,
        ))

    mc_report = reports / "monte_carlo.txt"
    if (story_scripts / "monte_carlo_rehearsal.py").exists():
        commands.append(run_cmd(
            [
                args.python_bin,
                str(story_scripts / "monte_carlo_rehearsal.py"),
                str(source),
                "--runs",
                str(args.mc_runs),
                "--seed",
                "17",
            ],
            repo,
            mc_report,
            timeout=args.command_timeout,
        ))

    swmd = worlds / f"{source.stem}.swmd.min.md"
    if (story_scripts / "json_to_swmd.py").exists():
        commands.append(run_cmd(
            [args.python_bin, str(story_scripts / "json_to_swmd.py"), str(source), str(swmd), "--mode", "minified"],
            repo,
            logs / "json_to_swmd.log",
            timeout=args.command_timeout,
        ))

    index_dir = indices / "encounter_index"
    if swmd.exists() and (small_scripts / "swmd_encounter_index.py").exists():
        commands.append(run_cmd(
            [args.python_bin, str(small_scripts / "swmd_encounter_index.py"), "--swmd", str(swmd), "--out-dir", str(index_dir)],
            repo,
            logs / "encounter_index.log",
            timeout=args.command_timeout,
        ))

    mcp_config = reports / "mcp_config.json"
    if (conveyor_scripts / "prepare_mcp_conveyor_config.py").exists():
        commands.append(run_cmd(
            [
                args.python_bin,
                str(conveyor_scripts / "prepare_mcp_conveyor_config.py"),
                "--storyworld",
                str(swmd if swmd.exists() else source),
                "--out-config",
                str(mcp_config),
                "--max-encounters",
                "12",
            ],
            repo,
            logs / "prepare_mcp_config.log",
            timeout=args.command_timeout,
        ))
    if mcp_config.exists() and (conveyor_scripts / "run_small_model_storyworld_port.py").exists():
        commands.append(run_cmd(
            [
                args.python_bin,
                str(conveyor_scripts / "run_small_model_storyworld_port.py"),
                "--config",
                str(mcp_config),
                "--preflight-only",
            ],
            repo,
            logs / "mcp_preflight.log",
            timeout=args.command_timeout,
        ))

    trm_advice = reports / "trm_rebalance_advice.json"
    if mc_report.exists() and (conveyor_scripts / "build_storyworld_trm_advice.py").exists():
        cmd = [
            args.python_bin,
            str(conveyor_scripts / "build_storyworld_trm_advice.py"),
            "--mc-report",
            str(mc_report),
            "--out-advice",
            str(trm_advice),
            "--storyworld-label",
            str(meta.get("title") or source.stem),
        ]
        if quality_report.exists():
            cmd.extend(["--quality-report", str(quality_report)])
        commands.append(run_cmd(cmd, repo, logs / "trm_advice.log", timeout=args.command_timeout))

    source_card = make_source_card(repo, source, run_dir, meta, trm_advice if trm_advice.exists() else None, 1)
    write_json(reports / "baseline_commands.json", commands)

    return {
        "source": str(source),
        "run_dir": str(run_dir),
        "metadata": meta,
        "source_card": str(source_card),
        "quality_report": str(quality_report) if quality_report.exists() else None,
        "authoring_report": str(authoring_report) if authoring_report.exists() else None,
        "monte_carlo_report": str(mc_report) if mc_report.exists() else None,
        "trm_advice": str(trm_advice) if trm_advice.exists() else None,
        "commands": commands,
    }


def run_hermes(repo: Path, row: dict[str, Any], args: argparse.Namespace, iteration_index: int) -> dict[str, Any]:
    run_dir = Path(row["run_dir"])
    source = Path(row["source"])
    iteration_dir = run_dir / f"iteration_{iteration_index:02d}"
    iteration_dir.mkdir(parents=True, exist_ok=True)
    previous_dir = run_dir / f"iteration_{iteration_index - 1:02d}" if iteration_index > 1 else None
    trm_advice = Path(row["trm_advice"]) if row.get("trm_advice") else None
    source_card = make_source_card(repo, source, run_dir, row.get("metadata", {}), trm_advice, iteration_index)
    prompt_path = iteration_dir / "hermes_prompt.txt"
    prompt = hermes_prompt(source_card, iteration_dir, source, iteration_index, previous_dir)
    prompt_path.write_text(prompt, encoding="utf-8", newline="\n")
    log_path = iteration_dir / "logs" / "hermes_oneshot.log"
    env = os.environ.copy()
    env["PATH"] = f"{Path.home() / '.hermes/bin'}:{Path.home() / '.local/bin'}:" + env.get("PATH", "")
    env["HERMES_ACCEPT_HOOKS"] = "1"
    cmd = [
        "hermes",
        "--yolo",
        "--accept-hooks",
        "-s",
        "storyworld-conveyor-runner",
        "-z",
        prompt,
    ]
    started = time.time()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8", newline="\n") as log:
        log.write("$ " + " ".join(cmd[:5]) + " <prompt>\n\n")
        log.flush()
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(repo),
                env=env,
                text=True,
                stdout=log,
                stderr=subprocess.STDOUT,
                timeout=args.hermes_timeout,
            )
            rc = proc.returncode
        except subprocess.TimeoutExpired:
            log.write(f"\nHERMES_TIMEOUT after {args.hermes_timeout}s\n")
            rc = 124
    report_path = iteration_dir / "hermes_artifact_report.md"
    failure_path = iteration_dir / "failure.md"
    derivative_jsons = sorted(str(path) for path in iteration_dir.rglob("*.json"))
    artifact_success = report_path.exists() or failure_path.exists() or bool(derivative_jsons)
    if not artifact_success:
        failure_path.write_text(
            "failure_class: no_artifacts\n"
            "detail: Hermes process exited without creating a derivative JSON, "
            "hermes_artifact_report.md, or failure.md.\n"
            f"returncode: {rc}\n"
            f"log: {log_path.as_posix()}\n"
            "next_bounded_command: rerun without --ignore-rules and require a file artifact gate.\n",
            encoding="utf-8",
            newline="\n",
        )
    return {
        "iteration": iteration_index,
        "returncode": rc,
        "seconds": round(time.time() - started, 3),
        "iteration_dir": str(iteration_dir),
        "prompt": str(prompt_path),
        "log": str(log_path),
        "artifact_success": artifact_success,
        "report": str(report_path) if report_path.exists() else None,
        "failure": str(failure_path) if failure_path.exists() else None,
        "derivative_jsons": derivative_jsons,
    }


def summarize(run_root: Path, rows: list[dict[str, Any]]) -> None:
    lines = ["# Overnight Storyworld Conveyor Campaign", ""]
    for row in rows:
        meta = row.get("metadata", {})
        lines.append(f"## {meta.get('title') or Path(row['source']).name}")
        lines.append("")
        lines.append(f"- Source: `{row['source']}`")
        lines.append(f"- Run dir: `{row['run_dir']}`")
        lines.append(f"- Encounters: {meta.get('encounters')} | endings/terminal: {meta.get('terminal_encounters')} | options: {meta.get('options')}")
        lines.append(f"- Quality report: `{row.get('quality_report')}`")
        lines.append(f"- Authoring report: `{row.get('authoring_report')}`")
        lines.append(f"- TRM advice: `{row.get('trm_advice')}`")
        if row.get("hermes_iterations"):
            for hermes_row in row["hermes_iterations"]:
                lines.append(
                    f"- Hermes iteration {hermes_row['iteration']}: "
                    f"rc={hermes_row['returncode']} artifact_success={hermes_row.get('artifact_success')} "
                    f"dir=`{hermes_row['iteration_dir']}` "
                    f"log=`{hermes_row['log']}`"
                )
        lines.append("")
    (run_root / "SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    write_json(run_root / "summary.json", rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run an overnight storyworld conveyor benchmark/improvement campaign.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--run-root", default="")
    parser.add_argument("--python-bin", default="python3")
    parser.add_argument("--source", action="append", default=[])
    parser.add_argument("--max-sources", type=int, default=5)
    parser.add_argument("--mc-runs", type=int, default=300)
    parser.add_argument("--command-timeout", type=int, default=600)
    parser.add_argument("--hermes-timeout", type=int, default=2700)
    parser.add_argument("--iterations", type=int, default=1)
    parser.add_argument("--skip-hermes", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo = Path(args.repo_root).resolve()
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    run_root = Path(args.run_root) if args.run_root else repo / "hermes-skills" / "storyworld-conveyor" / "overnight_runs" / f"campaign_{stamp}"
    run_root.mkdir(parents=True, exist_ok=True)

    sources = [Path(s) for s in (args.source or DEFAULT_SOURCES)]
    resolved: list[Path] = []
    for source in sources:
        path = source if source.is_absolute() else repo / source
        if path.exists():
            resolved.append(path)
        if len(resolved) >= args.max_sources:
            break
    if not resolved:
        raise SystemExit("No source storyworlds found.")

    rows: list[dict[str, Any]] = []
    for idx, source in enumerate(resolved, 1):
        row = baseline_source(repo, source, run_root, args, idx)
        rows.append(row)
        summarize(run_root, rows)
        if not args.skip_hermes:
            row["hermes_iterations"] = []
            for iteration_index in range(1, max(1, args.iterations) + 1):
                row["hermes_iterations"].append(run_hermes(repo, row, args, iteration_index))
                summarize(run_root, rows)

    summarize(run_root, rows)
    print(run_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
