"""
Late-stage tail tuning helper.

Usage:
  python late_stage_tail_tuning.py storyworld.json \
    --dominant page_end_resilient --multiplier 1.2 --bias 0.02 \
    --tails page_end_layla,page_end_jordan_refuse_nikah \
    --runs 5000 --seed 42 --apply
"""
import argparse
import json
import os
import importlib.util


def load_mc_module():
    here = os.path.dirname(os.path.abspath(__file__))
    mc_path = os.path.join(here, "monte_carlo_rehearsal.py")
    spec = importlib.util.spec_from_file_location("monte_carlo_rehearsal", mc_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def bn_const(val):
    return {"pointer_type": "Bounded Number Constant", "script_element_type": "Pointer", "value": val}


def mul(a, b):
    return {"operator_type": "Multiplication", "script_element_type": "Operator", "operands": [a, b]}


def add(a, b):
    return {"operator_type": "Addition", "script_element_type": "Operator", "operands": [a, b]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("storyworld")
    ap.add_argument("--dominant", required=True)
    ap.add_argument("--multiplier", type=float, default=1.0)
    ap.add_argument("--bias", type=float, default=0.01)
    ap.add_argument("--tails", required=True)
    ap.add_argument("--runs", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    with open(args.storyworld, "r", encoding="utf-8") as f:
        data = json.load(f)

    enc_by_id = {e["id"]: e for e in data.get("encounters", [])}
    dominant = enc_by_id.get(args.dominant)
    tails = [t.strip() for t in args.tails.split(",") if t.strip()]

    if args.apply:
        if dominant:
            ds = dominant.get("desirability_script", bn_const(0.0))
            dominant["desirability_script"] = mul(ds, bn_const(args.multiplier))

        for t in tails:
            end = enc_by_id.get(t)
            if not end:
                continue
            ds = end.get("desirability_script", bn_const(0.0))
            end["desirability_script"] = add(ds, bn_const(args.bias))

        with open(args.storyworld, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("Applied tail tuning.")

    mc = load_mc_module()
    report = mc.run_monte_carlo(data, num_runs=args.runs, seed=args.seed)
    total = report["num_runs"]
    print("\nEnding distribution:")
    for k, v in report["ending_counts"].most_common():
        print(f"  {k:30s} {v:6d} ({(v/total)*100:5.1f}%)")


if __name__ == "__main__":
    main()
