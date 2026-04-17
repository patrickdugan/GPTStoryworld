from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the paper's context-constrained trivia benchmark matrix.")
    parser.add_argument("--base-run-id", default="wiki_card_routerbench_qwen2b_base_refresh", help="Run id for the base no-adapter benchmark.")
    parser.add_argument("--adapter-run-id", default="wiki_card_routerbench_qwen2b_safe_refresh", help="Run id for the safe-adapter benchmark.")
    parser.add_argument("--max-questions", type=int, default=13, help="Question cap for each run.")
    parser.add_argument("--gpu-max-memory-mib", type=int, default=3900, help="Per-GPU placement cap.")
    parser.add_argument("--cpu-max-memory-mib", type=int, default=256, help="CPU placement cap.")
    parser.add_argument("--dry-run", action="store_true", help="Resolve both runs without launching.")
    return parser.parse_args()


def call_wrapper(script: Path, extra_args: list[str], cwd: Path) -> int:
    cmd = [sys.executable, str(script)] + extra_args
    return int(subprocess.call(cmd, cwd=str(cwd)))


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[3]
    wrapper = repo_root / "hermes-skills" / "trm-for-mcp-paper" / "scripts" / "run_context_constrained_trivia_bench.py"

    common = [
        "--max-questions",
        str(args.max_questions),
        "--gpu-max-memory-mib",
        str(args.gpu_max_memory_mib),
        "--cpu-max-memory-mib",
        str(args.cpu_max_memory_mib),
    ]
    if args.dry_run:
        common.append("--dry-run")

    rc = call_wrapper(
        wrapper,
        ["--run-id", args.base_run_id, "--no-adapter"] + common,
        repo_root,
    )
    if rc != 0:
        return rc
    return call_wrapper(
        wrapper,
        ["--run-id", args.adapter_run_id] + common,
        repo_root,
    )


if __name__ == "__main__":
    raise SystemExit(main())
