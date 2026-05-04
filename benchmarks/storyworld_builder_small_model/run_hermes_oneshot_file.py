#!/usr/bin/env python3
"""Run Hermes one-shot from a prompt file and save the transcript."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Hermes chat --query with prompt loaded from a file.")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--skills", default="")
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--model", default="")
    args = parser.parse_args()

    prompt = Path(args.prompt).read_text(encoding="utf-8")
    cmd = ["hermes", "chat", "--yolo", "--quiet", "--query", prompt]
    if args.skills:
        cmd[2:2] = ["--skills", args.skills]
    if args.model:
        cmd[2:2] = ["--model", args.model]
    proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=args.timeout)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(proc.stdout, encoding="utf-8", newline="\n")
    print(str(out))
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
