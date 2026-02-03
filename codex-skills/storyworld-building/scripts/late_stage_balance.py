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

    if args.target_min is not None and args.target_max is not None:
        ok = (pct >= args.target_min) and (pct <= args.target_max)
        status = "OK" if ok else "OUT_OF_RANGE"
        print(f"Target [{args.target_min}, {args.target_max}] -> {status}")


if __name__ == "__main__":
    main()
