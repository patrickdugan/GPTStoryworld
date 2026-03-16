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


def bn_target(char, prop, target_value):
    return {
        "pointer_type": "Target Value",
        "script_element_type": "Pointer",
        "character_id": char,
        "property_name": prop,
        "target_value": target_value
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


def subtract(a, b):
    return {
        "operator_type": "Subtraction",
        "script_element_type": "Operator",
        "operands": [a, b],
    }


def min(a, b):
    return {
        "operator_type": "Minimum",
        "script_element_type": "Operator",
        "operands": [a, b],
    }


def max(a, b):
    return {
        "operator_type": "Maximum",
        "script_element_type": "Operator",
        "operands": [a, b],
    }


def clamp(val, low, high):
    return {
        "operator_type": "Clamp",
        "script_element_type": "Operator",
        "operands": [val, low, high],
    }


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
    warped = mul(distance, bn_const(warp_factor))
    return clamp(warped, bn_const(-0.1), bn_const(0.1))


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
    ap.add_argument("--character", default="char_player")
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
    ap.add_argument("--warp-factor", type=float, default=2.5, help="Warp factor for metric distance calculations")
    ap.add_argument("--distance-prop", default="Fear", help="Property for distance calculations")
    ap.add_argument("--distance-ref", type=float, default=0.5, help="Reference value for distance calculations")
    args = ap.parse_args()

    with open(args.storyworld, "r", encoding="utf-8") as f:
        data = json.load(f)

    endings = [e for e in data.get("encounters", []) if e.get("id", "").startswith("page_end_")]
    the_end = next((e for e in endings if e.get("id") == args.ending_id), None)
    if the_end is None:
        print(f"Ending {args.ending_id} not found")
        sys.exit(1)

    if args.apply:
        accept_script = None
        if not the_end.get("acceptability_script"):
            # Default: both props should be >= accept-threshold
            cond_a = cmp_gte(args.character, args.prop_a, args.accept_threshold)
            cond_b = cmp_gte(args.character, args.prop_b, args.accept_threshold)
            accept_script = or_gate(cond_a, cond_b)
            the_end["acceptability_script"] = accept_script

        if not the_end.get("desirability_script"):
            # Default: weight * the average of the two props
            ptr_a = bn_ptr(args.character, args.prop_a)
            ptr_b = bn_ptr(args.character, args.prop_b)
            avg = mul(add(ptr_a, ptr_b), bn_const(0.5))
            the_end["desirability_script"] = mul(avg, bn_const(args.weight))
        
        # Enhance with distance warping
        warp_script = warp_distance(args.character, args.distance_prop, args.distance_ref, args.warp_factor)
        the_end["desirability_script"] = add(the_end["desirability_script"], mul(bn_const(args.bias), warp_script))

        # Optional: clamp to target range
        if args.target_min is not None or args.target_max is not None:
            ds = the_end["desirability_script"]
            if ds is not None:
                low = bn_const(args.target_min) if args.target_min is not None else bn_const(-float('inf'))
                high = bn_const(args.target_max) if args.target_max is not None else bn_const(float('inf'))
                the_end["desirability_script"] = clamp(ds, low, high)

        with open(args.storyworld, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("Applied late-stage balance to ending.")

    mc = load_mc_module()
    report = mc.run_monte_carlo(data, num_runs=args.runs, seed=args.seed)
    total = report["num_runs"]

    print("\nEnding distribution:")
    for k, v in report["ending_counts"].most_common():
        print(f"  {k:30s} {v:6d} ({(v/total)*100:5.1f}%)")

    # Summarize quality metrics
    metrics = compute_metrics(data)
    print("\nQuality metrics:")
    for k, v in metrics.items():
        target = POLISH_THRESHOLDS.get(k, None)
        good = target is None or v >= target
        print(f"  {k:30s} {v:6.2f} {'PASS' if good else 'FAIL'}")

if __name__ == "__main__":
    main()