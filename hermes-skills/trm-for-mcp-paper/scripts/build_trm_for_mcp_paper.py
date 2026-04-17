from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def main() -> int:
    parser = argparse.ArgumentParser(description="Rebuild the TRM for MCP paper assets and optionally compile the manuscript.")
    parser.add_argument("--compile", action="store_true", help="Also run pdflatex if available.")
    args = parser.parse_args()

    root = repo_root()
    paper_dir = root / "papers" / "trm_for_mcp"
    build_script = paper_dir / "build_assets.py"
    tex_file = paper_dir / "trm_for_mcp_context_for_free.tex"

    subprocess.run([sys.executable, str(build_script)], check=True, cwd=str(root))

    if not args.compile:
        return 0

    pdflatex = shutil.which("pdflatex")
    if not pdflatex:
        print("pdflatex not found; assets rebuilt but PDF not compiled.", file=sys.stderr)
        return 1

    subprocess.run(
        [pdflatex, "-interaction=nonstopmode", "-halt-on-error", tex_file.name],
        check=True,
        cwd=str(paper_dir),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
