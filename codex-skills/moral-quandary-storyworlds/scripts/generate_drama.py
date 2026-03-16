#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Compatibility wrapper for morality batch generation."
    )
    ap.add_argument(
        "--python-exe",
        default=r"D:\Research_Engine\.venv-train\Scripts\python.exe",
        help="Python executable used to run the canonical generator.",
    )
    args = ap.parse_args()

    # Resolve GPTStoryworld repo root from this skill path.
    repo_root = Path(__file__).resolve().parents[3]
    generator = repo_root / "tools" / "gen_morality_constitution_batch.py"
    if not generator.exists():
        raise SystemExit(f"Missing canonical generator: {generator}")

    cmd = [str(args.python_exe), str(generator)]
    proc = subprocess.run(cmd, check=False)
    return int(proc.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
