import argparse
import json
import math
import subprocess
from pathlib import Path


def run_mc(storyworld: Path, runs: int, seed: int):
    mc = Path(__file__).resolve().parent / "monte_carlo_rehearsal.py"
    proc = subprocess.run(
        ["python", str(mc), str(storyworld), "--runs", str(runs), "--seed", str(seed)],
        capture_output=True,
        text=True,
        check=True,
    )
    return proc.stdout


def parse_distribution(output: str):
    counts = {}
    total = 0
    for line in output.splitlines():
        if "page_end_" in line or "DEAD_END" in line:
            parts = line.split()
            if not parts:
                continue
            name = parts[0]
            for token in parts:
                if token.isdigit():
                    count = int(token)
                    counts[name] = count
                    total += count
                    break
    return counts, total


def entropy(counts, total):
    if total <= 0:
        return 0.0, 0.0
    h = 0.0
    for c in counts.values():
        if c <= 0:
            continue
        p = c / total
        h -= p * math.log(p + 1e-12, 2)
    eff = 2 ** h if h > 0 else 0.0
    return h, eff


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("storyworld")
    parser.add_argument("--runs", type=int, default=5000)
    parser.add_argument("--seeds", type=str, default="42,43,44")
    args = parser.parse_args()

    storyworld = Path(args.storyworld)
    seeds = [int(s.strip()) for s in args.seeds.split(",") if s.strip()]

    print(f"Storyworld: {storyworld}")
    for seed in seeds:
        out = run_mc(storyworld, args.runs, seed)
        counts, total = parse_distribution(out)
        h, eff = entropy(counts, total)
        max_share = max(counts.values()) / total if total else 0.0
        min_share = min(counts.values()) / total if total else 0.0
        print(f"Seed {seed}: total={total} max={max_share:.3f} min={min_share:.3f} entropy={h:.2f} eff={eff:.2f}")
        for name, count in sorted(counts.items(), key=lambda x: -x[1])[:6]:
            print(f"  {name}: {count} ({(count/total)*100:.1f}%)")


if __name__ == "__main__":
    main()
