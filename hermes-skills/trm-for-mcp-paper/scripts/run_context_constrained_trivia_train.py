from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch the safe capped trivia router training workflow through pure-trm-trainer.")
    parser.add_argument("--spec-path", default="", help="Optional override for the pure-trm-trainer safe spec.")
    parser.add_argument("--python-path", default="D:\\Research_Engine\\.venv-train\\Scripts\\python.exe", help="Python interpreter used by the PowerShell launcher.")
    parser.add_argument("--ram-limit-mb", type=int, default=2048, help="Windows Job Object RAM cap for the trainer process.")
    parser.add_argument("--cpu-limit-pct", type=int, default=25, help="Windows Job Object CPU cap percent.")
    parser.add_argument("--io-limit-mbs", type=int, default=20, help="Approximate output IO throughput cap in MB/s.")
    parser.add_argument("--poll-seconds", type=int, default=5, help="Polling interval for telemetry.")
    parser.add_argument("--dry-run", action="store_true", help="Resolve the plan without launching training.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[3]
    pure_trm_root = repo_root / "hermes-skills" / "pure-trm-trainer"
    launcher = pure_trm_root / "scripts" / "run_wiki_card_router_train_capped.ps1"
    spec_path = (
        Path(args.spec_path).expanduser().resolve()
        if args.spec_path
        else (pure_trm_root / "references" / "wiki-card-router-training-spec.safe.json").resolve()
    )

    cmd = [
        "powershell",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(launcher),
        "-SpecPath",
        str(spec_path),
        "-PythonPath",
        args.python_path,
        "-RamLimitMB",
        str(args.ram_limit_mb),
        "-CpuLimitPct",
        str(args.cpu_limit_pct),
        "-IoLimitMBs",
        str(args.io_limit_mbs),
        "-PollSeconds",
        str(args.poll_seconds),
    ]
    if args.dry_run:
        cmd.append("-DryRun")
    return int(subprocess.call(cmd, cwd=str(repo_root)))


if __name__ == "__main__":
    raise SystemExit(main())
