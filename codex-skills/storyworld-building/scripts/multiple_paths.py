import argparse
import json
import random
from collections import Counter, defaultdict

from polish_metrics import POLISH_THRESHOLDS, compute_metrics


def eval_script(script, state):
    if script is True:
        return True
    if script is False:
        return False
    if isinstance(script, (int, float)):
        return script
    if not isinstance(script, dict):
        return script

    pt = script.get("pointer_type")
    ot = script.get("operator_type")

    if pt == "Bounded Number Constant":
        return script["value"]
    if pt == "Bounded Number Pointer":
        char = script["character"]
        prop = script["keyring"][0]
        coeff = script.get("coefficient", 1.0)
        return state.get((char, prop), 0.0) * coeff
    if pt == "Boolean Constant":
        return script.get("value", False)
    if pt == "String Constant":
        return script.get("value", "")

    if ot == "Arithmetic Comparator":
        sub = script["operator_subtype"]
        left = eval_script(script["operands"][0], state)
        right = eval_script(script["operands"][1], state)
        ops = {
            "Greater Than or Equal To": lambda a, b: a >= b,
            "Less Than or Equal To": lambda a, b: a <= b,
            "Greater Than": lambda a, b: a > b,
            "Less Than": lambda a, b: a < b,
            "Equal To": lambda a, b: a == b,
            "Not Equal To": lambda a, b: a != b,
        }
        return ops.get(sub, lambda a, b: False)(left, right)

    if ot == "And":
        return all(eval_script(op, state) for op in script["operands"])
    if ot == "Or":
        return any(eval_script(op, state) for op in script["operands"])
    if ot == "Addition":
        return sum(eval_script(op, state) for op in script["operands"])
    if ot == "Multiplication":
        values = [eval_script(op, state) for op in script["operands"]]
        out = 1.0
        for v in values:
            out *= v
        return out

    return False




def apply_effects(reaction, state):
    for eff in reaction.get("after_effects", []):
        if eff.get("effect_type") != "Bounded Number Effect":
            continue
        target = eff.get("Set", {})
        if target.get("pointer_type") != "Bounded Number Pointer":
            continue
        char = target.get("character")
        prop = target.get("keyring", [None])[0]
        if not char or not prop:
            continue
        to = eff.get("to", {})
        if to.get("operator_type") == "Nudge":
            operands = to.get("operands", [])
            delta = 0.0
            for op in operands:
                if op.get("pointer_type") == "Bounded Number Constant":
                    delta = op.get("value", 0.0)
            key = (char, prop)
            state[key] = state.get(key, 0.0) + float(delta)


def select_reaction(option, state):
    best = None
    best_score = -1e9
    for rxn in option.get("reactions", []):
        d = eval_script(rxn.get("desirability_script", 0), state)
        if isinstance(d, bool):
            d = 1.0 if d else 0.0
        if d > best_score:
            best_score = d
            best = rxn
    return best


def build_spool_sequence(data):
    enc_by_id = {e["id"]: e for e in data.get("encounters", []) if e.get("id")}
    spools = sorted(data.get("spools", []), key=lambda s: s.get("creation_index", 0))
    sequence = []
    for sp in spools:
        if sp.get("id") == "spool_endings" or sp.get("spool_name") == "Endings":
            continue
        ids = sp.get("encounters", [])
        spool_encs = [enc_by_id[eid] for eid in ids if eid in enc_by_id]
        if spool_encs:
            sequence.append(spool_encs)
    return sequence


def detect_endings(data):
    endings = []
    seen = set()
    for enc in data.get("endings", []):
        eid = enc.get("id")
        if eid and eid not in seen:
            endings.append(enc)
            seen.add(eid)
    if not endings:
        endings = [e for e in data.get("encounters", []) if e.get("id", "").startswith("page_end_")]
    return endings


def detect_secrets(data):
    return [e for e in data.get("encounters", []) if e.get("id", "").startswith("page_secret_")]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("storyworld")
    parser.add_argument("--runs", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-steps", type=int, default=40)
    args = parser.parse_args()

    random.seed(args.seed)
    with open(args.storyworld, "r", encoding="utf-8") as f:
        data = json.load(f)

    sequence = build_spool_sequence(data)
    endings = detect_endings(data)
    secrets = detect_secrets(data)

    gate_hits = Counter()
    path_hits = defaultdict(Counter)

    for _ in range(args.runs):
        state = {}
        path = []
        steps = 0
        for spool_encs in sequence:
            k = min(3, len(spool_encs))
            for enc in random.sample(spool_encs, k):
                if steps >= args.max_steps:
                    break
                if not bool(eval_script(enc.get("acceptability_script", True), state)):
                    continue
                options = [o for o in enc.get("options", []) if eval_script(o.get("visibility_script", True), state)]
                if not options:
                    continue
                opt = random.choice(options)
                rxn = select_reaction(opt, state)
                if rxn:
                    apply_effects(rxn, state)
                path.append(enc.get("id", ""))
                steps += 1
        path_sig = " > ".join([p for p in path if p])[:200]

        for end in endings:
            eid = end.get("id")
            if eid and bool(eval_script(end.get("acceptability_script", True), state)):
                gate_hits[eid] += 1
                path_hits[eid][path_sig] += 1

        for sec in secrets:
            sid = sec.get("id")
            if sid and bool(eval_script(sec.get("acceptability_script", True), state)):
                gate_hits[sid] += 1
                path_hits[sid][path_sig] += 1

    print(f"Runs: {args.runs}")
    for gate, count in gate_hits.most_common():
        pct = (count / args.runs) * 100.0
        print(f"- {gate}: {count} ({pct:.1f}%)")
        top_paths = path_hits[gate].most_common(3)
        for sig, c in top_paths:
            share = (c / max(count, 1)) * 100.0
            print(f"  path {share:.1f}%: {sig}")

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
    for gate, count in gate_hits.items():
        if gate.startswith("page_secret_"):
            secret_hits.append((gate, count / args.runs * 100.0))
    for gate, pct in secret_hits:
        status = "OK" if pct >= POLISH_THRESHOLDS["secret_reachability_pct"] else "LOW"
        print(f"- Secret reachability {gate}: {pct:.1f}% (target {POLISH_THRESHOLDS['secret_reachability_pct']}) -> {status}")


if __name__ == "__main__":
    main()
