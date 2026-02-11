"""
Late-stage balancing helper for special endings.

Usage:
  python late_stage_balance.py storyworld.json \
    --ending-id page_end_layla \
    --prop-a pClinical_Ethics --prop-b pCommunity_Trust \
    --accept-threshold 0.015 --weight 1.2 --bias 0.01 \
    --runs 5000 --seed 42 --apply

Notes:
- Applies acceptability/desirability to the target ending.
- Runs Monte Carlo using monte_carlo_rehearsal.py logic and prints distribution.
"""
import argparse
import json
import os
import sys
import importlib.util

from polish_metrics import POLISH_THRESHOLDS, compute_metrics


def load_mc_module():
    here = os.path.dirname(os.path.abspath(__file__))
    mc_path = os.path.join(here, "monte_carlo_rehearsal.py")
    spec = importlib.util.spec_from_file_location("monte_carlo_rehearsal", mc_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod




def bn_ptr(char, prop):
    return {
        "pointer_type": "Bounded Number Pointer",
        "script_element_type": "Pointer",
        "character": char,
        "keyring": [prop],
        "coefficient": 1.0,
    }


def bn_const(val):
    return {
        "pointer_type": "Bounded Number Constant",
        "script_element_type": "Pointer",
        "value": val,
    }


def add(*ops):
    return {
        "operator_type": "Addition",
        "script_element_type": "Operator",
        "operands": list(ops),
    }


def mul(a, b):
    return {
        "operator_type": "Multiplication",
        "script_element_type": "Operator",
        "operands": [a, b],
    }


def cmp_gte(char, prop, val):
    return {
        "operator_type": "Arithmetic Comparator",
        "operator_subtype": "Greater Than or Equal To",
        "script_element_type": "Operator",
        "operands": [bn_ptr(char, prop), bn_const(val)],
    }


def or_gate(*ops):
    return {
        "operator_type": "Or",
        "script_element_type": "Operator",
        "operands": list(ops),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("storyworld")
    ap.add_argument("--ending-id", default="page_end_layla")
    ap.add_argument("--prop-a", default="pClinical_Ethics")
    ap.add_argument("--prop-b", default="pCommunity_Trust")
    ap.add_argument("--accept-threshold", type=float, default=0.015)
    ap.add_argument("--weight", type=float, default=1.2)
    ap.add_argument("--bias", type=float, default=0.01)
    ap.add_argument("--runs", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--target-min", type=float, default=None)
    ap.add_argument("--target-max", type=float, default=None)
    args = ap.parse_args()

    with open(args.storyworld, "r", encoding="utf-8") as f:
        data = json.load(f)

    enc_by_id = {e["id"]: e for e in data.get("encounters", [])}
    end = enc_by_id.get(args.ending_id)
    if not end:
        print(f"Ending not found: {args.ending_id}")
        sys.exit(1)

    if args.apply:
        end["acceptability_script"] = or_gate(
            cmp_gte("char_player", args.prop_a, args.accept_threshold),
            cmp_gte("char_player", args.prop_b, args.accept_threshold),
        )
        end["desirability_script"] = add(
            mul(bn_ptr("char_player", args.prop_a), bn_const(args.weight)),
            mul(bn_ptr("char_player", args.prop_b), bn_const(args.weight)),
            bn_const(args.bias),
        )
        with open(args.storyworld, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("Applied ending tuning.")

    mc = load_mc_module()
    report = mc.run_monte_carlo(data, num_runs=args.runs, seed=args.seed)
    total = report["num_runs"]
    count = report["ending_counts"].get(args.ending_id, 0)
    pct = (count / total) * 100.0 if total else 0.0

    print("\nEnding distribution:")
    for k, v in report["ending_counts"].most_common():
        print(f"  {k:30s} {v:6d} ({(v/total)*100:5.1f}%)")
    print(f"\n{args.ending_id} share: {pct:.2f}%")

    metrics = compute_metrics(data)
    act2_pct, act2_vars, act2_opts, act2_gated = metrics["act2"]
    act3_pct, act3_vars, act3_opts, act3_gated = metrics["act3"]

    print("\nStructural Metrics")
    print(f"- Effects per reaction: {metrics['effects_per_reaction']:.2f}")
    print(f"- Reactions per option: {metrics['reactions_per_option']:.2f}")
    print(f"- Options per encounter: {metrics['options_per_encounter']:.2f}")
    print(f"- Vars per reaction desirability: {metrics['desirability_vars_avg']:.2f}")
    print(f"- Act II visibility gating: {act2_pct:.1f}% (avg vars {act2_vars:.2f}, gated {act2_gated}/{act2_opts})")
    print(f"- Act III visibility gating: {act3_pct:.1f}% (avg vars {act3_vars:.2f}, gated {act3_gated}/{act3_opts})")

    if metrics["secret_checks"]:
        for eid, vars_count, has_distance in metrics["secret_checks"]:
            distance_note = "metric distance ok" if has_distance and vars_count >= 2 else "needs 2-var metric distance gate"
            print(f"- Secret gate {eid}: vars={vars_count}, {distance_note}")
    else:
        print("- Secret gate check: no secret encounters found")

    print("\nThreshold Checks")
    def check(val, target, label, op="ge"):
        ok = val >= target if op == "ge" else val <= target
        status = "OK" if ok else "LOW"
        print(f"- {label}: {val:.2f} (target {target}) -> {status}")

    check(metrics["effects_per_reaction"], POLISH_THRESHOLDS["effects_per_reaction"], "Effects per reaction")
    check(metrics["reactions_per_option"], POLISH_THRESHOLDS["reactions_per_option"], "Reactions per option")
    check(metrics["options_per_encounter"], POLISH_THRESHOLDS["options_per_encounter"], "Options per encounter")
    check(metrics["desirability_vars_avg"], POLISH_THRESHOLDS["desirability_vars_per_reaction"], "Vars per reaction desirability")
    check(act2_pct, POLISH_THRESHOLDS["act2_gate_pct"], "Act II gated %")
    check(act2_vars, POLISH_THRESHOLDS["act2_gate_vars"], "Act II gated vars")
    check(act3_pct, POLISH_THRESHOLDS["act3_gate_pct"], "Act III gated %")
    check(act3_vars, POLISH_THRESHOLDS["act3_gate_vars"], "Act III gated vars")

    secret_hits = []
    for gate, count in report["ending_counts"].items():
        if gate.startswith("page_secret_"):
            secret_hits.append((gate, count / total * 100.0))
    for gate, pct in secret_hits:
        status = "OK" if pct >= POLISH_THRESHOLDS["secret_reachability_pct"] else "LOW"
        print(f"- Secret reachability {gate}: {pct:.1f}% (target {POLISH_THRESHOLDS['secret_reachability_pct']}) -> {status}")

    if args.target_min is not None and args.target_max is not None:
        ok = (pct >= args.target_min) and (pct <= args.target_max)
        status = "OK" if ok else "OUT_OF_RANGE"
        print(f"Target [{args.target_min}, {args.target_max}] -> {status}")


if __name__ == "__main__":
    main()
