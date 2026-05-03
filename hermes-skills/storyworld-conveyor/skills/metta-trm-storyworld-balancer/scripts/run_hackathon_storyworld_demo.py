#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[5]
THIS_DIR = Path(__file__).resolve().parent
CONVEYOR_SCRIPTS = REPO_ROOT / "hermes-skills" / "storyworld-conveyor" / "scripts"
DEFAULT_STORYWORLD = REPO_ROOT / "storyworlds" / "by-week" / "2026-W11" / "validated_macbeth.json"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")


def run_cmd(cmd: list[str], cwd: Path, log_path: Path, timeout: int = 900) -> dict[str, Any]:
    started = time.time()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("$ " + " ".join(cmd) + "\n\n")
        handle.flush()
        try:
            proc = subprocess.run(cmd, cwd=str(cwd), text=True, stdout=handle, stderr=subprocess.STDOUT, timeout=timeout)
            rc = int(proc.returncode)
        except subprocess.TimeoutExpired:
            handle.write(f"\nTIMEOUT after {timeout}s\n")
            rc = 124
    return {"command": cmd, "returncode": rc, "seconds": round(time.time() - started, 3), "log": str(log_path)}


def token_estimate(text: str) -> int:
    # Conservative enough for budget deltas without depending on a tokenizer.
    return max(1, len(text.encode("utf-8")) // 4)


def script_text(value: Any) -> str:
    if isinstance(value, dict):
        raw = value.get("value")
        if isinstance(raw, str):
            return raw
        return " ".join(script_text(v) for v in value.values())
    if isinstance(value, list):
        return " ".join(script_text(v) for v in value)
    if isinstance(value, str):
        return value
    return ""


def storyworld_profile(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    profile: dict[str, Any] = {
        "path": str(path),
        "bytes": path.stat().st_size,
        "whole_context_token_estimate": token_estimate(text),
    }
    if path.suffix.lower() != ".json":
        return profile
    data = read_json(path)
    encounters = data.get("encounters", []) if isinstance(data.get("encounters"), list) else []
    options = 0
    reactions = 0
    terminal = 0
    sample_titles: list[str] = []
    for encounter in encounters:
        opts = encounter.get("options", []) if isinstance(encounter, dict) else []
        if not opts:
            terminal += 1
        options += len(opts) if isinstance(opts, list) else 0
        if isinstance(opts, list):
            for option in opts:
                rxns = option.get("reactions", []) if isinstance(option, dict) else []
                reactions += len(rxns) if isinstance(rxns, list) else 0
        if len(sample_titles) < 5 and isinstance(encounter, dict):
            title = script_text(encounter.get("title_text") or encounter.get("title") or encounter.get("text_script"))
            sample_titles.append(title[:120])
    profile.update(
        {
            "title": data.get("storyworld_title") or data.get("title") or path.stem,
            "encounters": len(encounters),
            "terminal_encounters": terminal,
            "options": options,
            "reactions": reactions,
            "sample_encounter_titles": sample_titles,
        }
    )
    return profile


def probe_openai_endpoint(base_url: str, timeout: int) -> dict[str, Any]:
    if not base_url:
        return {"ok": False, "skipped": True}
    url = base_url.rstrip("/") + "/models"
    req = urllib.request.Request(url, headers={"Authorization": "Bearer dummy"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8", errors="replace"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}", "url": url}
    models = payload.get("data", []) if isinstance(payload, dict) else []
    return {"ok": True, "url": url, "models": [m.get("id") for m in models[:10] if isinstance(m, dict)]}


def prepare_mcp_preflight(
    *,
    storyworld: Path,
    out_dir: Path,
    python_bin: str,
    context_tokens: int,
    max_encounters: int,
    neighbor_hops: int,
    max_new_tokens: int,
    max_input_output_ratio: float,
    timeout: int,
) -> dict[str, Any]:
    config_path = out_dir / "mcp_config.json"
    logs = out_dir / "logs"
    run_id = out_dir.name + "_mcp"
    prep_cmd = [
        python_bin,
        str(CONVEYOR_SCRIPTS / "prepare_mcp_conveyor_config.py"),
        "--storyworld",
        str(storyworld),
        "--out-config",
        str(config_path),
        "--artifact-root",
        str(out_dir / "context_port_runs"),
        "--run-id",
        run_id,
        "--context-budget-tokens",
        str(context_tokens),
        "--reserve-output-tokens",
        "1024",
        "--planning-card-tokens",
        "900",
        "--max-new-tokens",
        str(max_new_tokens),
        "--max-input-output-ratio",
        str(max_input_output_ratio),
        "--max-encounters",
        str(max_encounters),
        "--neighbor-hops",
        str(neighbor_hops),
    ]
    prep = run_cmd(prep_cmd, REPO_ROOT, logs / "prepare_mcp_config.log", timeout=timeout)
    result: dict[str, Any] = {"prepare": prep, "config": str(config_path)}
    if prep["returncode"] != 0 or not config_path.exists():
        result["status"] = "failed_prepare"
        return result

    port_cmd = [
        python_bin,
        str(CONVEYOR_SCRIPTS / "run_small_model_storyworld_port.py"),
        "--config",
        str(config_path),
        "--preflight-only",
    ]
    port = run_cmd(port_cmd, REPO_ROOT, logs / "mcp_budget_preflight.log", timeout=timeout)
    config = read_json(config_path)
    run_dir = Path(config["artifact_root"]) / config["run_id"]
    budget_path = run_dir / "mcp_budget_preflight" / "budget_report.json"
    rows_path = run_dir / "mcp_budget_preflight" / "budget_rows.jsonl"
    result.update({"preflight": port, "run_dir": str(run_dir), "budget_report": str(budget_path), "budget_rows": str(rows_path)})
    if budget_path.exists():
        budget = read_json(budget_path)
        result["status"] = budget.get("status", "unknown")
        result["budget"] = budget
        return result
    if port["returncode"] != 0:
        result["status"] = "failed_preflight"
        return result
    result["status"] = "missing_budget_report"
    return result


def run_metta_loop(
    *,
    storyworld: Path,
    out_dir: Path,
    python_bin: str,
    mc_runs: int,
    qwen_base_url: str,
    qwen_model: str,
    qwen_timeout: int,
    skip_qwen: bool,
    timeout: int,
) -> dict[str, Any]:
    cmd = [
        python_bin,
        str(THIS_DIR / "run_metta_trm_qwen_author_loop.py"),
        "--storyworld",
        str(storyworld),
        "--out-dir",
        str(out_dir),
        "--python-bin",
        python_bin,
        "--mc-runs",
        str(mc_runs),
        "--timeout",
        str(timeout),
        "--qwen-base-url",
        qwen_base_url,
        "--qwen-model",
        qwen_model,
        "--qwen-timeout",
        str(qwen_timeout),
    ]
    if skip_qwen:
        cmd.append("--skip-qwen")
    command = run_cmd(cmd, REPO_ROOT, out_dir / "logs" / "metta_trm_loop.log", timeout=max(timeout * 5, 1200))
    summary_path = out_dir / "run_summary.json"
    result: dict[str, Any] = {"command": command, "run_summary": str(summary_path)}
    if command["returncode"] != 0 or not summary_path.exists():
        result["status"] = "failed"
        return result
    result["status"] = "completed"
    result["summary"] = read_json(summary_path)
    return result


def write_scorecard(path: Path, source_profile: dict[str, Any], mcp: dict[str, Any], metta: dict[str, Any]) -> None:
    rows: list[dict[str, Any]] = [
        {
            "lane": "whole_context_naive",
            "metric": "estimated_input_tokens",
            "value": source_profile.get("whole_context_token_estimate"),
            "note": "Approximate full JSON prompt cost before instructions and examples.",
        },
        {
            "lane": "mcp_packet",
            "metric": "preflight_status",
            "value": mcp.get("status"),
            "note": "completed means the packet policy is safe to hand to the model.",
        },
        {
            "lane": "mcp_packet",
            "metric": "worst_prompt_tokens",
            "value": (mcp.get("budget") or {}).get("worst_prompt_tokens"),
            "note": "Largest bounded packet in MCP preflight.",
        },
        {
            "lane": "mcp_packet",
            "metric": "overflow_count",
            "value": (mcp.get("budget") or {}).get("overflow_count"),
            "note": "Must stay at zero for a clean live demo.",
        },
    ]
    summary = metta.get("summary") or {}
    baseline = summary.get("baseline") or {}
    candidate = summary.get("candidate") or {}
    delta = summary.get("score_delta") or {}
    rows.extend(
        [
            {
                "lane": "metta_trm_repair",
                "metric": "baseline_authoring_score",
                "value": baseline.get("weighted_authoring_verifier_score"),
                "note": "Before symbolic/TRM-guided repair.",
            },
            {
                "lane": "metta_trm_repair",
                "metric": "candidate_authoring_score",
                "value": candidate.get("weighted_authoring_verifier_score"),
                "note": "After deterministic MeTTa/TRM repair.",
            },
            {
                "lane": "metta_trm_repair",
                "metric": "authoring_score_delta",
                "value": delta.get("weighted_authoring_verifier_score"),
                "note": "Main benchmark lift for the demo.",
            },
            {
                "lane": "metta_trm_repair",
                "metric": "baseline_quality_failures",
                "value": ";".join(str(x) for x in baseline.get("quality_failures", [])),
                "note": "Typed verifier-visible defects before repair.",
            },
            {
                "lane": "metta_trm_repair",
                "metric": "candidate_quality_failures",
                "value": ";".join(str(x) for x in candidate.get("quality_failures", [])),
                "note": "Remaining typed defects after repair.",
            },
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["lane", "metric", "value", "note"])
        writer.writeheader()
        writer.writerows(rows)


def write_hermes_prompt(path: Path, storyworld: Path, demo_dir: Path, qwen_base_url: str, qwen_model: str) -> None:
    path.write_text(
        "Use terminal tools now. Do not narrate intended actions without making tool calls.\n"
        "Use only these skills: storyworld-conveyor-runner, metta-trm-storyworld-balancer.\n"
        "Goal: demonstrate that 27B becomes useful for piecemeal storyworld building when MCP packets, MeTTa facts, "
        "TRM repair targets, and deterministic validators constrain the loop.\n\n"
        "Run this command from the GPTStoryworld repo root:\n\n"
        f"python hermes-skills/storyworld-conveyor/skills/metta-trm-storyworld-balancer/scripts/run_hackathon_storyworld_demo.py "
        f"--storyworld {storyworld.as_posix()} "
        f"--out-dir {demo_dir.as_posix()} "
        "--context-tokens 32768 --max-encounters 12 --mc-runs 120 "
        f"--qwen-base-url {qwen_base_url} --qwen-model {qwen_model}\n\n"
        "After it finishes, inspect demo_brief.md, demo_scorecard.csv, demo_summary.json, and the run manifests. "
        "Report only artifact paths, counts, scores, and failures. If the model endpoint is down, rerun with --skip-qwen "
        "and preserve the endpoint failure as evidence that the deterministic control plane still produces receipts.\n",
        encoding="utf-8",
        newline="\n",
    )


def write_brief(path: Path, payload: dict[str, Any]) -> None:
    profile = payload["source_profile"]
    mcp = payload["mcp_preflight"]
    metta = payload["metta_trm_loop"]
    budget = mcp.get("budget") or {}
    summary = metta.get("summary") or {}
    baseline = summary.get("baseline") or {}
    candidate = summary.get("candidate") or {}
    delta = summary.get("score_delta") or {}
    whole_tokens = profile.get("whole_context_token_estimate")
    packet_tokens = budget.get("worst_prompt_tokens")
    compression = ""
    if isinstance(whole_tokens, (int, float)) and isinstance(packet_tokens, (int, float)) and packet_tokens:
        compression = f" ({whole_tokens / packet_tokens:.1f}x smaller than whole-context JSON)"

    lines = [
        "# Hermes Hackathon Storyworld Demo Brief",
        "",
        "## Claim",
        "",
        "A 27B local model is not reliable enough to be the whole storyworld-building agent. The demo claim is narrower and stronger: Hermes skills make the model viable as a bounded authoring/reasoning component inside an MCP, MeTTa, TRM, and verifier-controlled loop.",
        "",
        "## Evidence Lanes",
        "",
        f"- Source storyworld: `{profile.get('path')}`",
        f"- Encounters/options/reactions: {profile.get('encounters')} / {profile.get('options')} / {profile.get('reactions')}",
        f"- Whole-context JSON estimate: {whole_tokens} tokens",
        f"- MCP preflight status: {mcp.get('status')}",
        f"- MCP worst packet estimate: {packet_tokens} tokens{compression}",
        f"- MCP overflow count: {budget.get('overflow_count')}",
        f"- Baseline authoring score: {baseline.get('weighted_authoring_verifier_score')}",
        f"- Candidate authoring score: {candidate.get('weighted_authoring_verifier_score')}",
        f"- Score delta: {delta.get('weighted_authoring_verifier_score')}",
        f"- Baseline failures: {baseline.get('quality_failures')}",
        f"- Candidate failures: {candidate.get('quality_failures')}",
        "",
        "## Demo Interpretation",
        "",
        "This should be presented as benchmark transcendence by architecture, not as evidence that Qwen 27B is secretly strong. The model contributes local prose and option-level inference; MCP constrains context, MeTTa gives a compact world model, TRM packets pick repair targets and commit/veto criteria, and validators prevent compliance theater.",
        "",
        "## Live Talk Track",
        "",
        "1. Show naive whole-context cost and failure mode: broad storyworld authoring burns context and tends to narrate intentions.",
        "2. Show MCP preflight: the same world is sliced into bounded packets with hard overflow checks.",
        "3. Show MeTTa/TRM packet: failures become typed repair targets instead of vague quality complaints.",
        "4. Show before/after score: the scaffold moves measured authoring quality even when the 27B model is mediocre.",
        "5. State the actual research thesis: compact open models become useful when skills act as control planes over tools, memory, verifiers, and repair curricula.",
        "",
        "## Artifacts",
        "",
        f"- Summary JSON: `{payload.get('summary_path')}`",
        f"- Scorecard CSV: `{payload.get('scorecard_path')}`",
        f"- Hermes prompt: `{payload.get('hermes_prompt_path')}`",
        f"- MCP run dir: `{mcp.get('run_dir')}`",
        f"- MeTTa/TRM run summary: `{metta.get('run_summary')}`",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a hackathon evidence pack for MCP + MeTTa/TRM storyworld authoring.")
    parser.add_argument("--storyworld", default=str(DEFAULT_STORYWORLD))
    parser.add_argument("--out-dir", default=str(REPO_ROOT / "hermes-skills" / "storyworld-conveyor" / "tmp" / "hackathon_storyworld_demo"))
    parser.add_argument("--python-bin", default=sys.executable)
    parser.add_argument("--context-tokens", type=int, default=32768)
    parser.add_argument("--max-encounters", type=int, default=12)
    parser.add_argument("--neighbor-hops", type=int, default=1)
    parser.add_argument("--max-new-tokens", type=int, default=768)
    parser.add_argument("--max-input-output-ratio", type=float, default=24.0)
    parser.add_argument("--mc-runs", type=int, default=120)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--qwen-base-url", default="http://127.0.0.1:8081/v1")
    parser.add_argument("--qwen-model", default="Qwen3.5-27B.Q4_K_M.gguf")
    parser.add_argument("--qwen-timeout", type=int, default=90)
    parser.add_argument("--skip-qwen", action="store_true")
    parser.add_argument("--fresh", action="store_true", help="Delete the output dir before running.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    storyworld = Path(args.storyworld).resolve()
    if not storyworld.exists():
        raise FileNotFoundError(str(storyworld))
    out_dir = Path(args.out_dir).resolve()
    if args.fresh and out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    endpoint = probe_openai_endpoint(args.qwen_base_url, args.qwen_timeout)
    profile = storyworld_profile(storyworld)
    mcp = prepare_mcp_preflight(
        storyworld=storyworld,
        out_dir=out_dir / "mcp_preflight",
        python_bin=args.python_bin,
        context_tokens=args.context_tokens,
        max_encounters=args.max_encounters,
        neighbor_hops=args.neighbor_hops,
        max_new_tokens=args.max_new_tokens,
        max_input_output_ratio=args.max_input_output_ratio,
        timeout=args.timeout,
    )
    metta = run_metta_loop(
        storyworld=storyworld,
        out_dir=out_dir / "metta_trm_loop",
        python_bin=args.python_bin,
        mc_runs=args.mc_runs,
        qwen_base_url=args.qwen_base_url,
        qwen_model=args.qwen_model,
        qwen_timeout=args.qwen_timeout,
        skip_qwen=args.skip_qwen,
        timeout=args.timeout,
    )

    scorecard_path = out_dir / "demo_scorecard.csv"
    summary_path = out_dir / "demo_summary.json"
    brief_path = out_dir / "demo_brief.md"
    hermes_prompt_path = out_dir / "hermes_live_prompt.txt"

    write_scorecard(scorecard_path, profile, mcp, metta)
    write_hermes_prompt(hermes_prompt_path, storyworld, out_dir, args.qwen_base_url, args.qwen_model)
    payload = {
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source_profile": profile,
        "qwen_endpoint": endpoint,
        "mcp_preflight": mcp,
        "metta_trm_loop": metta,
        "summary_path": str(summary_path),
        "scorecard_path": str(scorecard_path),
        "brief_path": str(brief_path),
        "hermes_prompt_path": str(hermes_prompt_path),
    }
    write_json(summary_path, payload)
    write_brief(brief_path, payload)
    print(str(brief_path))
    print(str(scorecard_path))
    print(str(summary_path))
    return 0 if mcp.get("status") == "completed" and metta.get("status") == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
