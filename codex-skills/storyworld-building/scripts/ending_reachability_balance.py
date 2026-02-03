"""
Ending reachability helper.

Usage:
  python ending_reachability_balance.py storyworld.json --bias 0.01 --runs 5000 --seed 42

Applies a desirability bias to all endings and prints unreachable endings.
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


def add(a, b):
    return {"operator_type": "Addition", "script_element_type": "Operator", "operands": [a, b]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("storyworld")
    ap.add_argument("--bias", type=float, default=0.01)
    ap.add_argument("--runs", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    with open(args.storyworld, "r", encoding="utf-8") as f:
        data = json.load(f)

    endings = [e for e in data.get("encounters", []) if e.get("id", "").startswith("page_end_")]

    if args.apply:
        for end in endings:
            ds = end.get("desirability_script")
            if ds is None:
                end["desirability_script"] = bn_const(args.bias)
            else:
                end["desirability_script"] = add(ds, bn_const(args.bias))
        with open(args.storyworld, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("Applied desirability bias to endings.")

    mc = load_mc_module()
    report = mc.run_monte_carlo(data, num_runs=args.runs, seed=args.seed)
    total = report["num_runs"]

    print("\nEnding distribution:")
    for k, v in report["ending_counts"].most_common():
        print(f"  {k:30s} {v:6d} ({(v/total)*100:5.1f}%)")

    unreachable = []
    for end in endings:
        if report["ending_counts"].get(end["id"], 0) == 0:
            unreachable.append(end["id"])

    if unreachable:
        print("\nUnreachable endings:")
        for eid in unreachable:
            print(f"  {eid}")
    else:
        print("\nAll endings reachable.")


if __name__ == "__main__":
    main()
