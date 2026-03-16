#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, obj: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def append_jsonl(path: Path, obj: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def run_storyworld_env(worlds: List[Path], out_dir: Path, checkpoint: Dict, existing_report: Path | None = None) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "quality_vector_score.json"
    log_path = out_dir / "run.log"
    if existing_report and existing_report.exists():
        if not report_path.exists():
            report_path.write_text(existing_report.read_text(encoding="utf-8"), encoding="utf-8")
        with log_path.open("a", encoding="utf-8") as log:
            log.write(f"[{utc_now()}] Reused existing storyworld-env report: {existing_report}\n")
        checkpoint["storyworld_env"] = {
            "status": "completed_reused",
            "started_at": checkpoint["storyworld_env"].get("started_at") or utc_now(),
            "finished_at": utc_now(),
            "duration_sec": 0.0,
            "report": str(report_path),
            "log": str(log_path),
            "return_code": 0,
        }
        return

    cmd = [
        "python",
        "storyworld-env/quality_vector_score.py",
        "--storyworlds",
        *[str(w) for w in worlds],
        "--runs",
        "200",
        "--out",
        str(report_path),
    ]

    start = time.time()
    with log_path.open("a", encoding="utf-8") as log:
        log.write(f"\n[{utc_now()}] START storyworld-env\n")
        log.write("CMD: " + " ".join(cmd) + "\n")
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.stdout:
            log.write(proc.stdout + "\n")
        if proc.stderr:
            log.write(proc.stderr + "\n")
        log.write(f"[{utc_now()}] END storyworld-env rc={proc.returncode}\n")

    checkpoint["storyworld_env"] = {
        "status": "completed" if proc.returncode == 0 else "failed",
        "started_at": checkpoint["storyworld_env"].get("started_at") or utc_now(),
        "finished_at": utc_now(),
        "duration_sec": round(time.time() - start, 2),
        "report": str(report_path),
        "log": str(log_path),
        "return_code": proc.returncode,
    }


def run_text_env(
    worlds: List[Path],
    out_dir: Path,
    checkpoint: Dict,
    api_key_file: str,
    max_encounters: int,
    max_reactions: int,
    models: List[str],
    deadline_ts: float,
    max_retries: int,
    retry_sleep: int,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    progress_jsonl = out_dir / "progress.jsonl"
    summary_path = out_dir / "summary.json"

    if "models" not in checkpoint["text_env"]:
        checkpoint["text_env"]["models"] = {}

    total = len(worlds)

    for model in models:
        model_key = model.replace(".", "_")
        model_dir = out_dir / model_key
        model_dir.mkdir(parents=True, exist_ok=True)

        state = checkpoint["text_env"]["models"].setdefault(
            model,
            {
                "status": "running",
                "started_at": utc_now(),
                "completed": 0,
                "failed": 0,
                "remaining": total,
                "last_world": None,
                "reports_dir": str(model_dir),
            },
        )

        # resume support: skip worlds with existing report file
        completed_names = {p.name.replace('.judge.json', '') for p in model_dir.glob('*.judge.json')}

        for idx, world in enumerate(worlds, 1):
            if time.time() > deadline_ts:
                state["status"] = "paused_deadline"
                state["remaining"] = total - state["completed"] - state["failed"]
                write_json(summary_path, checkpoint)
                return

            stem = world.stem
            if stem in completed_names:
                continue

            out_report = model_dir / f"{stem}.judge.json"
            log_file = model_dir / f"{stem}.log.txt"
            cmd = [
                "python",
                "storyworld-text-quality-env/evaluate_text_quality.py",
                "--storyworld",
                str(world),
                "--out",
                str(out_report),
                "--judge-model",
                model,
                "--api-key-file",
                api_key_file,
                "--max-encounters",
                str(max_encounters),
                "--max-reactions",
                str(max_reactions),
            ]

            ok = False
            err_tail = ""
            for attempt in range(1, max_retries + 1):
                run = subprocess.run(cmd, capture_output=True, text=True)
                log_file.write_text(
                    (run.stdout or "") + "\n" + (run.stderr or ""),
                    encoding="utf-8",
                )
                if run.returncode == 0:
                    ok = True
                    break
                comb = ((run.stdout or "") + "\n" + (run.stderr or ""))
                err_tail = comb[-2000:]
                retryable_429 = (
                    ("HTTP 429" in comb or "rate_limit_exceeded" in comb)
                    and "insufficient_quota" not in comb
                )
                if retryable_429:
                    time.sleep(retry_sleep)
                    continue
                break

            state["last_world"] = world.name
            if ok:
                state["completed"] += 1
                event = {
                    "ts": utc_now(),
                    "env": "text_env",
                    "model": model,
                    "world": world.name,
                    "status": "ok",
                    "report": str(out_report),
                    "log": str(log_file),
                }
            else:
                state["failed"] += 1
                event = {
                    "ts": utc_now(),
                    "env": "text_env",
                    "model": model,
                    "world": world.name,
                    "status": "failed",
                    "report": str(out_report),
                    "log": str(log_file),
                    "error_tail": err_tail,
                }

            state["remaining"] = total - state["completed"] - state["failed"]
            checkpoint["updated_at"] = utc_now()
            append_jsonl(progress_jsonl, event)
            write_json(summary_path, checkpoint)

        state["status"] = "completed"
        state["finished_at"] = utc_now()
        checkpoint["updated_at"] = utc_now()
        write_json(summary_path, checkpoint)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-dir", required=True)
    ap.add_argument("--public-dir", required=True)
    ap.add_argument("--api-key-file", required=True)
    ap.add_argument("--deadline-minutes", type=int, default=35)
    ap.add_argument("--max-encounters", type=int, default=24)
    ap.add_argument("--max-reactions", type=int, default=72)
    ap.add_argument("--max-retries", type=int, default=5)
    ap.add_argument("--retry-sleep", type=int, default=30)
    ap.add_argument("--models", nargs="+", default=["gpt-4.1-mini", "gpt-5-mini"])
    ap.add_argument("--reuse-storyworld-report", default="storyworlds/2-23-2026-batch/_reports/today_batch_quality_vector_score.json")
    args = ap.parse_args()

    batch = Path(args.batch_dir)
    public = Path(args.public_dir)
    reports_root = batch / "_reports" / "live_env_runs"
    sw_out = reports_root / "storyworld_env"
    text_out = reports_root / "text_env"

    worlds = sorted(batch.glob("*.json")) + sorted(public.glob("pd_*_multiending_v1.json"))

    checkpoint = {
        "started_at": utc_now(),
        "updated_at": utc_now(),
        "deadline_minutes": args.deadline_minutes,
        "world_count": len(worlds),
        "worlds": [str(w) for w in worlds],
        "storyworld_env": {"status": "running", "started_at": utc_now()},
        "text_env": {"status": "running", "started_at": utc_now(), "models": {}},
    }

    checkpoint_file = reports_root / "checkpoint_summary.json"
    write_json(checkpoint_file, checkpoint)

    existing_report = Path(args.reuse_storyworld_report) if args.reuse_storyworld_report else None
    run_storyworld_env(worlds, sw_out, checkpoint, existing_report=existing_report)
    checkpoint["updated_at"] = utc_now()
    write_json(checkpoint_file, checkpoint)

    deadline_ts = time.time() + args.deadline_minutes * 60
    run_text_env(
        worlds=worlds,
        out_dir=text_out,
        checkpoint=checkpoint,
        api_key_file=args.api_key_file,
        max_encounters=args.max_encounters,
        max_reactions=args.max_reactions,
        models=args.models,
        deadline_ts=deadline_ts,
        max_retries=args.max_retries,
        retry_sleep=args.retry_sleep,
    )

    checkpoint["text_env"]["status"] = "completed_or_paused"
    checkpoint["finished_at"] = utc_now()
    checkpoint["updated_at"] = utc_now()
    write_json(checkpoint_file, checkpoint)

    print(str(checkpoint_file))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
