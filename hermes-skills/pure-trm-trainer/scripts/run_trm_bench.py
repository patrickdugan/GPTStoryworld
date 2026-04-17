#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Dict


BENCHES: Dict[str, Dict[str, Path]] = {
    "routerbench": {
        "spec": Path(__file__).resolve().parents[1] / "references" / "routerbench-spec.json",
        "runner": Path(__file__).resolve().parents[1] / "scripts" / "run_trm_routerbench.py",
    },
    "primehub-envs": {
        "spec": Path(__file__).resolve().parents[1] / "references" / "primehub-envs-bench.json",
        "runner": Path(__file__).resolve().parents[1] / "scripts" / "run_trm_routerbench.py",
    },
    "primehub-baseline": {
        "spec": Path(__file__).resolve().parents[1] / "references" / "primehub-baseline-bench.json",
        "runner": Path(__file__).resolve().parents[1] / "scripts" / "run_trm_routerbench.py",
    },
    "wiki-card-routerbench": {
        "spec": Path(__file__).resolve().parents[1] / "references" / "wiki-card-routerbench-spec.json",
        "runner": Path(__file__).resolve().parents[1] / "scripts" / "run_wiki_card_routerbench.py",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a named TRM bench from the pure-trm-trainer skill.")
    parser.add_argument("--bench", required=True, choices=sorted(BENCHES.keys()), help="Named bench to launch.")
    parser.add_argument("--run-id", default="", help="Optional run id override.")
    parser.add_argument("--dry-run", action="store_true", help="Resolve the bench config and print the path without launching.")
    parser.add_argument("--template-root", default="", help="Optional trainer template root override.")
    parser.add_argument("--corpus-spec", default="", help="Optional corpus spec override.")
    parser.add_argument("--benchmark-root", default="", help="Optional benchmark root override for fixed benchmark runners.")
    parser.add_argument("--output-root", default="", help="Optional output root override.")
    parser.add_argument("--model-path", default="", help="Optional local model path for fixed benchmark runners.")
    parser.add_argument("--adapter-path", default="", help="Optional adapter path for fixed benchmark runners.")
    parser.add_argument("--backend", default="", help="Optional backend override for fixed benchmark runners.")
    parser.add_argument("--max-questions", default="", help="Optional question cap for fixed benchmark runners.")
    parser.add_argument("--load-in-4bit", action="store_true", help="Force 4-bit loading on fixed benchmark runners.")
    parser.add_argument("--no-4bit", action="store_true", help="Disable 4-bit loading on fixed benchmark runners.")
    parser.add_argument("--gpu-max-memory-mib", default="", help="Optional per-GPU max memory cap for fixed benchmark runners.")
    parser.add_argument("--cpu-max-memory-mib", default="", help="Optional CPU placement memory cap for fixed benchmark runners.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    skill_root = Path(__file__).resolve().parents[1]
    bench = BENCHES[args.bench]
    spec_path = bench["spec"]
    runner = bench["runner"]
    cmd = [
        sys.executable,
        str(runner),
        "--config",
        str(spec_path),
    ]
    if args.run_id:
        cmd += ["--run-id", args.run_id]
    if args.dry_run:
        cmd += ["--dry-run"]
    if runner.name == "run_trm_routerbench.py":
        if args.template_root:
            cmd += ["--template-root", args.template_root]
        if args.corpus_spec:
            cmd += ["--corpus-spec", args.corpus_spec]
    if runner.name == "run_wiki_card_routerbench.py":
        if args.benchmark_root:
            cmd += ["--benchmark-root", args.benchmark_root]
        if args.output_root:
            cmd += ["--output-root", args.output_root]
        if args.model_path:
            cmd += ["--model-path", args.model_path]
        if args.adapter_path:
            cmd += ["--adapter-path", args.adapter_path]
        if args.backend:
            cmd += ["--backend", args.backend]
        if args.max_questions:
            cmd += ["--max-questions", args.max_questions]
        if args.gpu_max_memory_mib:
            cmd += ["--gpu-max-memory-mib", args.gpu_max_memory_mib]
        if args.cpu_max_memory_mib:
            cmd += ["--cpu-max-memory-mib", args.cpu_max_memory_mib]
        if args.load_in_4bit:
            cmd += ["--load-in-4bit"]
        if args.no_4bit:
            cmd += ["--no-4bit"]
    return int(subprocess.call(cmd, cwd=str(skill_root)))


if __name__ == "__main__":
    raise SystemExit(main())
