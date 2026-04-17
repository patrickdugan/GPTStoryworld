from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch the bounded storyworld environment-study runner through storyworld-conveyor.")
    parser.add_argument("--config", default="", help="Optional override for the small-model context-port config.")
    parser.add_argument("--run-id", default="", help="Optional run id override.")
    parser.add_argument("--dry-run", action="store_true", help="Write manifests and commands without running model stages.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[3]
    conveyor_root = repo_root / "hermes-skills" / "storyworld-conveyor"
    script = conveyor_root / "scripts" / "run_small_model_storyworld_port.py"
    config = (
        Path(args.config).expanduser().resolve()
        if args.config
        else (conveyor_root / "sample_data" / "qwen2b_4gb_context_port.json").resolve()
    )

    cmd = [
        sys.executable,
        str(script),
        "--config",
        str(config),
    ]
    if args.run_id:
        cmd += ["--run-id", args.run_id]
    if args.dry_run:
        cmd += ["--dry-run"]
    return int(subprocess.call(cmd, cwd=str(repo_root)))


if __name__ == "__main__":
    raise SystemExit(main())
