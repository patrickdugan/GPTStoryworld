import argparse
import json
import re
import subprocess
from pathlib import Path

from polish_metrics import POLISH_THRESHOLDS, compute_metrics


def run(cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def parse_distribution(output):
    dist = []
    dead_end = None
    for line in output.splitlines():
        if "DEAD_END" in line or "Dead-end rate" in line:
            m = re.search(r"\((\s*[0-9.]+)%\)", line)
            if m:
                dead_end = float(m.group(1))
        if "page_end_" in line:
            name_match = re.search(r"(page_end_[A-Za-z0-9_]+)", line)
            pct_match = re.search(r"\((\s*[0-9.]+)%\)", line)
            if name_match and pct_match:
                dist.append((name_match.group(1), float(pct_match.group(1))))
    return dist, dead_end


def parse_secret_reachability(output):
    secrets = {}
    in_section = False
    for line in output.splitlines():
        if line.strip().startswith("--- Secret Reachability"):
            in_section = True
            continue
        if in_section:
            if line.strip().startswith("---"):
                break
            m = re.search(r"(page_secret_[A-Za-z0-9_]+).*\((\s*[0-9.]+)%\)", line)
            if m:
                secrets[m.group(1)] = float(m.group(2))
    return secrets


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
    secrets_pct = parse_secret_reachability(mc_out.stdout)
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
    for sid, pct in secrets_pct.items():
        if pct < POLISH_THRESHOLDS["secret_reachability_pct"]:
            lines.append(f"- {sid} secret reachability below {POLISH_THRESHOLDS['secret_reachability_pct']:.1f}%: raise acceptability or visibility gating.")
    lines.append("")
    lines.append("## Structural Metrics")
    metrics = compute_metrics(json.loads(storyworld.read_text(encoding="utf-8")))
    lines.append(f"- Effects per reaction: {metrics['effects_per_reaction']:.2f}")
    lines.append(f"- Reactions per option: {metrics['reactions_per_option']:.2f}")
    lines.append(f"- Options per encounter: {metrics['options_per_encounter']:.2f}")
    lines.append(f"- Vars per reaction desirability: {metrics['desirability_vars_avg']:.2f}")
    act2_pct, act2_vars, act2_opts, act2_gated = metrics["act2"]
    act3_pct, act3_vars, act3_opts, act3_gated = metrics["act3"]
    lines.append(f"- Act II visibility gating: {act2_pct:.1f}% (avg vars {act2_vars:.2f}, gated {act2_gated}/{act2_opts})")
    lines.append(f"- Act III visibility gating: {act3_pct:.1f}% (avg vars {act3_vars:.2f}, gated {act3_gated}/{act3_opts})")
    if metrics["secret_checks"]:
        for eid, vars_count, has_distance in metrics["secret_checks"]:
            distance_note = "metric distance ok" if has_distance and vars_count >= 2 else "needs 2-var metric distance gate"
            lines.append(f"- Secret gate {eid}: vars={vars_count}, {distance_note}")
    else:
        lines.append("- Secret gate check: no secret encounters found")
    lines.append("")
    lines.append("## Threshold Checks")
    def check(val, target, label, op="ge"):
        ok = val >= target if op == "ge" else val <= target
        status = "OK" if ok else "LOW"
        lines.append(f"- {label}: {val:.2f} (target {target}) -> {status}")

    check(metrics["effects_per_reaction"], POLISH_THRESHOLDS["effects_per_reaction"], "Effects per reaction")
    check(metrics["reactions_per_option"], POLISH_THRESHOLDS["reactions_per_option"], "Reactions per option")
    check(metrics["options_per_encounter"], POLISH_THRESHOLDS["options_per_encounter"], "Options per encounter")
    check(metrics["desirability_vars_avg"], POLISH_THRESHOLDS["desirability_vars_per_reaction"], "Vars per reaction desirability")
    check(act2_pct, POLISH_THRESHOLDS["act2_gate_pct"], "Act II gated %")
    check(act2_vars, POLISH_THRESHOLDS["act2_gate_vars"], "Act II gated vars")
    check(act3_pct, POLISH_THRESHOLDS["act3_gate_pct"], "Act III gated %")
    check(act3_vars, POLISH_THRESHOLDS["act3_gate_vars"], "Act III gated vars")

    lines.append("")
    lines.append("## Raw Monte Carlo Output")
    lines.append("```")
    lines.append(mc_out.stdout.strip())
    lines.append("```")

    report.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
