from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch one context-constrained trivia bench run through pure-trm-trainer.")
    parser.add_argument("--run-id", required=True, help="Run id for the benchmark output directory.")
    parser.add_argument("--model-path", default="", help="Optional override for the model path.")
    parser.add_argument("--adapter-path", default="", help="Optional adapter path. Defaults to the safe adapter if present.")
    parser.add_argument("--no-adapter", action="store_true", help="Disable adapter loading even if a default adapter exists.")
    parser.add_argument("--backend", default="hf", help="Backend forwarded to pure-trm-trainer.")
    parser.add_argument("--max-questions", type=int, default=13, help="Question cap for the frozen slice.")
    parser.add_argument("--gpu-max-memory-mib", type=int, default=3900, help="Per-GPU placement cap.")
    parser.add_argument("--cpu-max-memory-mib", type=int, default=256, help="CPU placement cap.")
    parser.add_argument("--no-4bit", action="store_true", help="Disable 4-bit loading.")
    parser.add_argument("--dry-run", action="store_true", help="Resolve the bench config without launching.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[3]
    pure_trm_root = repo_root / "hermes-skills" / "pure-trm-trainer"
    safe_spec = load_json(pure_trm_root / "references" / "wiki-card-router-training-spec.safe.json")
    default_model = str(safe_spec.get("model") or "").strip()
    default_adapter = str(Path(safe_spec["output_dir"]).resolve() / "adapter")

    model_path = args.model_path or default_model
    adapter_path = ""
    if not args.no_adapter:
        adapter_path = args.adapter_path or default_adapter

    cmd = [
        sys.executable,
        str(pure_trm_root / "scripts" / "run_trm_bench.py"),
        "--bench",
        "wiki-card-routerbench",
        "--run-id",
        args.run_id,
        "--model-path",
        model_path,
        "--backend",
        args.backend,
        "--max-questions",
        str(args.max_questions),
        "--gpu-max-memory-mib",
        str(args.gpu_max_memory_mib),
        "--cpu-max-memory-mib",
        str(args.cpu_max_memory_mib),
    ]
    if adapter_path:
        cmd += ["--adapter-path", adapter_path]
    if args.dry_run:
        cmd.append("--dry-run")
    if args.no_4bit:
        cmd.append("--no-4bit")
    else:
        cmd.append("--load-in-4bit")
    return int(subprocess.call(cmd, cwd=str(repo_root)))


if __name__ == "__main__":
    raise SystemExit(main())
