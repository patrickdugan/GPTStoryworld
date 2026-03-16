from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(__file__).resolve().parents[3]
SMALL_BUILDER_SCRIPTS = REPO_ROOT / "codex-skills" / "small-storyworld-builder" / "scripts"
CONVEYOR_SCRIPTS = REPO_ROOT / "hermes-skills" / "storyworld-conveyor" / "scripts"


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def dump_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")


def append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True) + "\n")


def summarize_trm_advice(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"source_path": str(path), "parse_ok": False}
    summary: Dict[str, Any] = {"source_path": str(path), "parse_ok": True}
    for key in (
        "focus_metrics",
        "target_endings",
        "priority_fixes",
        "notes",
        "recommendations",
        "storyworld",
        "phase_guidance",
        "quality_failures",
        "recommended_overrides",
        "raw_metrics",
    ):
        if key in payload:
            summary[key] = payload[key]
    if "advice" in payload and isinstance(payload["advice"], dict):
        advice = payload["advice"]
        for key in (
            "focus_metrics",
            "target_endings",
            "priority_fixes",
            "notes",
            "recommendations",
            "phase_guidance",
            "quality_failures",
            "recommended_overrides",
            "raw_metrics",
        ):
            if key in advice and key not in summary:
                summary[key] = advice[key]
    if "payload" in payload and isinstance(payload["payload"], dict):
        nested = payload["payload"]
        for key in (
            "focus_metrics",
            "target_endings",
            "priority_fixes",
            "notes",
            "recommendations",
            "storyworld",
            "phase_guidance",
            "quality_failures",
            "recommended_overrides",
            "raw_metrics",
        ):
            if key in nested and key not in summary:
                summary[key] = nested[key]
    return summary


def build_trm_advice_from_reports(run_dir: Path, python_bin: str, config: Dict[str, Any], dry_run: bool) -> Path | None:
    mc_report = str(config.get("monte_carlo_report", "") or "").strip()
    if not mc_report:
        return None
    advice_out = run_dir / "reports" / "trm_advice.generated.json"
    if dry_run:
        return advice_out
    cmd = [
        python_bin,
        str(CONVEYOR_SCRIPTS / "build_storyworld_trm_advice.py"),
        "--mc-report",
        str(Path(mc_report).resolve()),
        "--out-advice",
        str(advice_out),
        "--storyworld-label",
        str(config.get("storyworld_label") or Path(config.get("swmd", "storyworld")).stem),
    ]
    quality_report = str(config.get("quality_report", "") or "").strip()
    if quality_report:
        cmd.extend(["--quality-report", str(Path(quality_report).resolve())])
    rc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if rc.returncode != 0:
        raise RuntimeError((rc.stderr or rc.stdout or "failed to build TRM advice").strip())
    return advice_out


def build_stage_manifest(
    run_id: str,
    stage: str,
    status: str,
    input_files: List[str],
    output_files: List[str],
    counters: Dict[str, Any],
    notes: List[str] | None = None,
) -> Dict[str, Any]:
    ts = now_iso()
    return {
        "run_id": run_id,
        "stage": stage,
        "status": status,
        "started_at": ts,
        "completed_at": ts,
        "input_files": input_files,
        "output_files": output_files,
        "counters": counters,
        "notes": notes or [],
    }


def run_command(stage_dir: Path, command: List[str]) -> int:
    stdout_path = stage_dir / "stdout.log"
    stderr_path = stage_dir / "stderr.log"
    with stdout_path.open("w", encoding="utf-8", newline="\n") as out_handle, stderr_path.open(
        "w", encoding="utf-8", newline="\n"
    ) as err_handle:
        proc = subprocess.run(command, stdout=out_handle, stderr=err_handle, text=True, check=False)
    return int(proc.returncode)


def line_count(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


def main() -> int:
    parser = argparse.ArgumentParser(description="Hermes context-managed port of the small storyworld builder for 4GB VRAM setups.")
    parser.add_argument("--config", required=True, help="JSON config path.")
    parser.add_argument("--run-id", default="", help="Optional run id override.")
    parser.add_argument("--dry-run", action="store_true", help="Write manifests and commands but do not run the model stages.")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))

    run_id = str(args.run_id or config.get("run_id") or f"small_port_{int(time.time())}")
    artifact_root = ensure_dir(Path(config["artifact_root"]).resolve())
    run_dir = ensure_dir(artifact_root / run_id)
    dump_json(run_dir / "run_config.snapshot.json", config)

    python_bin = str(config.get("python_bin") or sys.executable)
    swmd_path = Path(config["swmd"]).resolve()
    model_path = str(Path(config["model_path"]).resolve())
    adapter_path = str(config.get("adapter_path", "") or "")
    trm_advice_path = Path(config.get("trm_advice_json", "")).resolve() if config.get("trm_advice_json") else None
    qlora_examples = str(Path(config["qlora_examples_jsonl"]).resolve()) if config.get("qlora_examples_jsonl") else ""

    index_stage = ensure_dir(run_dir / "build_encounter_index")
    index_dir = ensure_dir(run_dir / "indices" / "encounter_index")
    index_cmd = [
        python_bin,
        str(SMALL_BUILDER_SCRIPTS / "swmd_encounter_index.py"),
        "--swmd",
        str(swmd_path),
        "--out-dir",
        str(index_dir),
    ]
    dump_json(index_stage / "command.json", {"command": index_cmd})

    if args.dry_run:
        status = "planned"
    else:
        rc = run_command(index_stage, index_cmd)
        status = "completed" if rc == 0 else "failed"
    dump_json(
        index_stage / "manifest.json",
        build_stage_manifest(
            run_id,
            "build_encounter_index",
            status,
            [str(swmd_path)],
            [str(index_dir / "encounters.jsonl"), str(index_dir / "world_card.txt")],
            {"encounters_indexed": line_count(index_dir / "encounters.jsonl")},
        ),
    )
    dump_json(index_stage / "progress.json", {"stage": "build_encounter_index", "status": status, "updated_at": now_iso()})
    append_jsonl(index_stage / "events.jsonl", {"event": "stage_finished", "status": status, "at": now_iso()})
    if status == "failed":
        return 1

    trm_stage = ensure_dir(run_dir / "prepare_trm_packet")
    trm_packet_path = run_dir / "reports" / "trm_constraints.json"
    generated_trm_advice = build_trm_advice_from_reports(run_dir, python_bin, config, args.dry_run)
    effective_trm_advice = trm_advice_path or generated_trm_advice
    trm_payload = summarize_trm_advice(effective_trm_advice) if effective_trm_advice and effective_trm_advice.exists() else {}
    trm_payload.setdefault("profile", {})
    trm_payload["profile"].update(
        {
            "goal": "bounded_context_storyworld_revision",
            "hardware": "4GB_VRAM",
            "model_family": "Qwen_2B_class",
            "memory_mode": "encounter_packet_only",
            "cross_play_memory_mode": "summary",
        }
    )
    dump_json(trm_packet_path, trm_payload)
    dump_json(
        trm_stage / "manifest.json",
        build_stage_manifest(
            run_id,
            "prepare_trm_packet",
            "completed",
            [str(p) for p in (trm_advice_path, generated_trm_advice) if p],
            [str(trm_packet_path)],
            {"keys": len(trm_payload.keys())},
            notes=["TRM constraints summarized for MCP packet injection"],
        ),
    )
    dump_json(trm_stage / "progress.json", {"stage": "prepare_trm_packet", "status": "completed", "updated_at": now_iso()})
    append_jsonl(trm_stage / "events.jsonl", {"event": "stage_finished", "status": "completed", "at": now_iso()})

    phase_stage = ensure_dir(run_dir / "phase_pipeline")
    phase_events = run_dir / "reports" / "phase_events.jsonl"
    phase_state = run_dir / "reports" / "phase_state.json"
    phase_cmd = [
        python_bin,
        str(SMALL_BUILDER_SCRIPTS / "swmd_mcp_phase_pipeline.py"),
        "--swmd",
        str(swmd_path),
        "--backend",
        str(config.get("inference_backend", "auto")),
        "--model-path",
        model_path,
        "--max-encounters",
        str(int(config.get("max_encounters", 12))),
        "--start-index",
        str(int(config.get("start_index", 0))),
        "--neighbor-hops",
        str(int(config.get("neighbor_hops", 1))),
        "--context-budget-tokens",
        str(int(config.get("context_budget_tokens", 8192))),
        "--reserve-output-tokens",
        str(int(config.get("reserve_output_tokens", 1024))),
        "--planning-card-tokens",
        str(int(config.get("planning_card_tokens", 900))),
        "--max-new-tokens",
        str(int(config.get("max_new_tokens", 160))),
        "--temperature",
        str(float(config.get("temperature", 0.0))),
        "--out-jsonl",
        str(phase_events),
        "--state-json",
        str(phase_state),
        "--fewshot-count",
        str(int(config.get("fewshot_count", 0))),
        "--external-constraints-json",
        str(trm_packet_path),
    ]
    phases = str(config.get("phases", "")).strip()
    if phases:
        phase_cmd.extend(["--phases", phases])
    if adapter_path:
        phase_cmd.extend(["--adapter-path", adapter_path])
    if qlora_examples:
        phase_cmd.extend(["--qlora-examples-jsonl", qlora_examples])
    if bool(config.get("repair_build_output", False)):
        phase_cmd.append("--repair-build-output")
    if bool(config.get("apply", False)):
        phase_cmd.append("--apply")
    dump_json(phase_stage / "command.json", {"command": phase_cmd})

    if args.dry_run:
        phase_status = "planned"
    else:
        rc = run_command(phase_stage, phase_cmd)
        phase_status = "completed" if rc == 0 else "failed"
    dump_json(
        phase_stage / "manifest.json",
        build_stage_manifest(
            run_id,
            "phase_pipeline",
            phase_status,
            [str(swmd_path), str(trm_packet_path)],
            [str(phase_events), str(phase_state)],
            {"rows": line_count(phase_events)},
            notes=["4GB-friendly bounded-context phase loop"],
        ),
    )
    dump_json(phase_stage / "progress.json", {"stage": "phase_pipeline", "status": phase_status, "updated_at": now_iso()})
    append_jsonl(phase_stage / "events.jsonl", {"event": "stage_finished", "status": phase_status, "at": now_iso()})
    if phase_status == "failed":
        return 1

    summary = {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "swmd": str(swmd_path),
        "phase_events": str(phase_events),
        "phase_state": str(phase_state),
        "trm_constraints": str(trm_packet_path),
        "status": "planned" if args.dry_run else "completed",
    }
    dump_json(run_dir / "summary.json", summary)
    print(str(run_dir))
    print(str(run_dir / "summary.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
