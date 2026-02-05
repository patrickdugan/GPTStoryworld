import argparse
import json
import re
import subprocess
from pathlib import Path


POLISH_THRESHOLDS = {
    "effects_per_reaction": 4.5,
    "reactions_per_option": 2.5,
    "options_per_encounter": 3.2,
    "desirability_vars_per_reaction": 1.6,
    "act2_gate_pct": 5.0,
    "act2_gate_vars": 1.2,
    "act3_gate_pct": 8.0,
    "act3_gate_vars": 1.5,
    "secret_reachability_pct": 5.0,
}


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


def collect_vars(script, out):
    if script is None:
        return
    if isinstance(script, dict):
        if script.get("pointer_type") == "Bounded Number Pointer":
            char = script.get("character")
            keyring = script.get("keyring") or []
            if char and keyring:
                out.add((char, keyring[0]))
        for v in script.values():
            collect_vars(v, out)
    elif isinstance(script, list):
        for v in script:
            collect_vars(v, out)


def count_vars(script):
    out = set()
    collect_vars(script, out)
    return len(out)


def script_has_operator(script, operator_type):
    if isinstance(script, dict):
        if script.get("operator_type") == operator_type:
            return True
        for v in script.values():
            if script_has_operator(v, operator_type):
                return True
    elif isinstance(script, list):
        for v in script:
            if script_has_operator(v, operator_type):
                return True
    return False


def is_visibility_gated(script):
    if script is True:
        return False
    if isinstance(script, dict) and script.get("pointer_type") == "Boolean Constant":
        return not bool(script.get("value", False)) if script.get("value") is not None else True
    return True


def compute_metrics(data):
    encounters = data.get("encounters", [])
    enc_by_id = {e.get("id"): e for e in encounters if e.get("id")}

    total_options = 0
    total_reactions = 0
    total_effects = 0
    desirability_vars = []

    enc_with_options = 0
    for enc in encounters:
        options = enc.get("options", []) or []
        if options:
            enc_with_options += 1
        total_options += len(options)
        for opt in options:
            reactions = opt.get("reactions", []) or []
            total_reactions += len(reactions)
            for rxn in reactions:
                effects = rxn.get("after_effects", []) or []
                total_effects += len(effects)
                desirability_vars.append(count_vars(rxn.get("desirability_script")))

    effects_per_reaction = (total_effects / total_reactions) if total_reactions else 0.0
    reactions_per_option = (total_reactions / total_options) if total_options else 0.0
    options_per_encounter = (total_options / enc_with_options) if enc_with_options else 0.0
    desirability_vars_avg = (sum(desirability_vars) / len(desirability_vars)) if desirability_vars else 0.0

    spools = data.get("spools", [])
    act2_ids = set()
    act3_ids = set()
    for sp in spools:
        name = (sp.get("spool_name") or "").lower()
        sid = (sp.get("id") or "").lower()
        ids = sp.get("encounters", []) or []
        if "act ii" in name or "act2" in sid or "act_2" in sid:
            act2_ids.update(ids)
        if "act iii" in name or "act3" in sid or "act_3" in sid:
            act3_ids.update(ids)

    def gate_stats(enc_ids):
        opts = 0
        gated = 0
        gated_vars = []
        for eid in enc_ids:
            enc = enc_by_id.get(eid)
            if not enc:
                continue
            for opt in enc.get("options", []) or []:
                opts += 1
                vis = opt.get("visibility_script", True)
                if is_visibility_gated(vis):
                    gated += 1
                    gated_vars.append(count_vars(vis))
        pct = (gated / opts * 100.0) if opts else 0.0
        avg_vars = (sum(gated_vars) / len(gated_vars)) if gated_vars else 0.0
        return pct, avg_vars, opts, gated

    act2_pct, act2_vars, act2_opts, act2_gated = gate_stats(act2_ids)
    act3_pct, act3_vars, act3_opts, act3_gated = gate_stats(act3_ids)

    secret_checks = []
    for enc in encounters:
        eid = enc.get("id", "")
        if eid.startswith("page_secret_"):
            acc = enc.get("acceptability_script")
            vars_count = count_vars(acc)
            has_distance = script_has_operator(acc, "Absolute Value")
            secret_checks.append((eid, vars_count, has_distance))

    return {
        "effects_per_reaction": effects_per_reaction,
        "reactions_per_option": reactions_per_option,
        "options_per_encounter": options_per_encounter,
        "desirability_vars_avg": desirability_vars_avg,
        "act2": (act2_pct, act2_vars, act2_opts, act2_gated),
        "act3": (act3_pct, act3_vars, act3_opts, act3_gated),
        "secret_checks": secret_checks,
    }


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
