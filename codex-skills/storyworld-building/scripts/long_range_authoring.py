import argparse
import json
import re
import subprocess
from pathlib import Path


def run(cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def parse_distribution(output):
    dist = []
    dead_end = None
    for line in output.splitlines():
        if "DEAD_END" in line:
            m = re.search(r"\\((\\s*[0-9.]+)%\\)", line)
            if m:
                dead_end = float(m.group(1))
        if "page_end_" in line:
            name_match = re.search(r"(page_end_[A-Za-z0-9_]+)", line)
            pct_match = re.search(r"\\((\\s*[0-9.]+)%\\)", line)
            if name_match and pct_match:
                dist.append((name_match.group(1), float(pct_match.group(1))))
    return dist, dead_end


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("storyworld", help="Path to storyworld JSON")
    parser.add_argument("--runs", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    storyworld = Path(args.storyworld)
    if not storyworld.exists():
        raise SystemExit(f"Missing storyworld: {storyworld}")

    validator = Path(__file__).resolve().parent / "sweepweave_validator.py"
    mc = Path(__file__).resolve().parent / "monte_carlo_rehearsal.py"

    run(["python", str(validator), "validate", str(storyworld)])
    mc_out = run(["python", str(mc), str(storyworld), "--runs", str(args.runs), "--seed", str(args.seed)])

    dist, dead_end = parse_distribution(mc_out.stdout)
    dist_sorted = sorted(dist, key=lambda x: -x[1])

    report = storyworld.with_name(storyworld.stem + "_long_range_authoring.md")
    lines = []
    lines.append(f"# Long-Range Authoring Report: {storyworld.name}")
    lines.append("")
    lines.append(f"Runs: {args.runs} | Seed: {args.seed}")
    lines.append("")
    lines.append("## Ending Distribution")
    for name, pct in dist_sorted:
        lines.append(f"- {name}: {pct:.1f}%")
    if dead_end is not None:
        lines.append(f"- DEAD_END: {dead_end:.1f}%")
    lines.append("")
    lines.append("## Tuning Notes")
    if dead_end is not None and dead_end >= 5.0:
        lines.append("- Dead-end rate high: widen fallback ending gate.")
    for name, pct in dist_sorted:
        if pct > 30.0:
            lines.append(f"- {name} too high: raise acceptability or lower desirability.")
        if 0.0 < pct < 1.0:
            lines.append(f"- {name} too low: lower acceptability or raise desirability.")
    if not dist_sorted:
        lines.append("- No endings parsed; check Monte Carlo output format.")
    lines.append("")
    lines.append("## Raw Monte Carlo Output")
    lines.append("```")
    lines.append(mc_out.stdout.strip())
    lines.append("```")

    report.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
