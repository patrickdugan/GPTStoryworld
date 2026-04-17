from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def call(script: Path, extra_args: list[str], cwd: Path) -> int:
    cmd = [sys.executable, str(script)] + extra_args
    return int(subprocess.call(cmd, cwd=str(cwd)))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Refresh context-constrained evidence for the TRM for MCP paper and rebuild the paper assets.")
    parser.add_argument("--storyworld-run-id", default="storyworld_env_refresh", help="Run id for the bounded storyworld environment study.")
    parser.add_argument("--base-run-id", default="wiki_card_routerbench_qwen2b_base_refresh", help="Run id for the base no-adapter trivia benchmark.")
    parser.add_argument("--adapter-run-id", default="wiki_card_routerbench_qwen2b_safe_refresh", help="Run id for the safe-adapter trivia benchmark.")
    parser.add_argument("--skip-trivia", action="store_true", help="Skip the trivia benchmark refresh.")
    parser.add_argument("--skip-storyworld", action="store_true", help="Skip the storyworld environment-study refresh.")
    parser.add_argument("--skip-paper", action="store_true", help="Skip rebuilding the paper assets.")
    parser.add_argument("--dry-run", action="store_true", help="Resolve each stage without launching model work.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[3]
    skill_root = repo_root / "hermes-skills" / "trm-for-mcp-paper" / "scripts"

    if not args.skip_storyworld:
        rc = call(
            skill_root / "run_context_constrained_storyworld_env.py",
            ["--run-id", args.storyworld_run_id] + (["--dry-run"] if args.dry_run else []),
            repo_root,
        )
        if rc != 0:
            return rc

    if not args.skip_trivia:
        rc = call(
            skill_root / "run_context_constrained_benchmark_matrix.py",
            [
                "--base-run-id",
                args.base_run_id,
                "--adapter-run-id",
                args.adapter_run_id,
            ]
            + (["--dry-run"] if args.dry_run else []),
            repo_root,
        )
        if rc != 0:
            return rc

    if not args.skip_paper:
        rc = call(
            skill_root / "build_trm_for_mcp_paper.py",
            [],
            repo_root,
        )
        if rc != 0:
            return rc

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
