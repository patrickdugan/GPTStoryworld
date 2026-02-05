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


def load_mc_module():
    here = os.path.dirname(os.path.abspath(__file__))
    mc_path = os.path.join(here, "monte_carlo_rehearsal.py")
    spec = importlib.util.spec_from_file_location("monte_carlo_rehearsal", mc_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


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
