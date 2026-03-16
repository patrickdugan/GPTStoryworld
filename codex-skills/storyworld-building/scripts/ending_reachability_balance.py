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


def bn_target(char, prop, target_value):
    return {
        "pointer_type": "Target Value",
        "script_element_type": "Pointer",
        "character_id": char,
        "property_name": prop,
        "target_value": target_value
    }


def add(a, b):
    return {"operator_type": "Addition", "script_element_type": "Operator", "operands": [a, b]}


def subtract(a, b):
    return {"operator_type": "Subtraction", "script_element_type": "Operator", "operands": [a, b]}


def multiply(a, b):
    return {"operator_type": "Multiplication", "script_element_type": "Operator", "operands": [a, b]}


def min(a, b):
    return {"operator_type": "Minimum", "script_element_type": "Operator", "operands": [a, b]}


def max(a, b):
    return {"operator_type": "Maximum", "script_element_type": "Operator", "operands": [a, b]}


def clamp(val, low, high):
    return {"operator_type": "Clamp", "script_element_type": "Operator", "operands": [val, low, high]}


def warp_distance(character, property_name, ref_value, warp_factor):
    """Exponential warp of metric distance for ending reachability balance"""
    distance = {
        "operator_type": "Absolute Difference",
        "script_element_type": "Operator", 
        "operands": [
            {"pointer_type": "Property", "script_element_type": "Pointer", "character_id": character, "property_name": property_name},
            bn_const(ref_value)
        ]
    }
    warped = multiply(distance, bn_const(warp_factor))
    return clamp(warped, bn_const(-0.1), bn_const(0.1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("storyworld")
    ap.add_argument("--bias", type=float, default=0.01)
    ap.add_argument("--warped-min", type=float, default=0.94)
    ap.add_argument("--warp-factor", type=float, default=2.5)
    ap.add_argument("--runs", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--character", default="char_macbeth", help="Default character for warped distance calculations")
    ap.add_argument("--property", default="Fear", help="Default property for warped distance calculations")
    args = ap.parse_args()

    with open(args.storyworld, "r", encoding="utf-8") as f:
        data = json.load(f)

    endings = [e for e in data.get("encounters", []) if e.get("id", "").startswith("page_end_")]

    if args.apply:
        for end in endings:
            ds = end.get("desirability_script")
            if ds is None:
                # Apply exponential warp based on both bias and warped-min threshold
                warp_distance_script = warp_distance(args.character, args.property, args.bias, args.warp_factor)
                end["desirability_script"] = multiply(bn_const(args.bias), warp_distance_script)
            else:
                # Enhance existing scripts with warped distance
                warp_distance_script = warp_distance(args.character, args.property, args.bias, args.warp_factor)
                end["desirability_script"] = add(ds, multiply(bn_const(args.bias), warp_distance_script))
        
        with open(args.storyworld, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("Applied exponential warped desirability to endings.")

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