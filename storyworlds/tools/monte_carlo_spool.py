import argparse
import json
import random
from collections import Counter


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
        return script.get("value", 0.0)
    if pt == "Bounded Number Pointer":
        char = script.get("character")
        keyring = script.get("keyring") or []
        coeff = script.get("coefficient", 1.0)
        if not char or not keyring:
            return 0.0
        return state.get((char, keyring[0]), 0.0) * coeff
    if pt == "String Constant":
        return script.get("value", "")

    if ot == "Arithmetic Comparator":
        sub = script.get("operator_subtype")
        left = eval_script(script.get("operands", [None, None])[0], state)
        right = eval_script(script.get("operands", [None, None])[1], state)
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
        return all(eval_script(op, state) for op in script.get("operands", []))
    if ot == "Or":
        return any(eval_script(op, state) for op in script.get("operands", []))
    if ot == "Addition":
        return sum(eval_script(op, state) for op in script.get("operands", []))
    if ot == "Multiplication":
        r = 1.0
        for op in script.get("operands", []):
            r *= eval_script(op, state)
        return r
    if ot == "Absolute Value":
        return abs(eval_script(script.get("operands", [None])[0], state))
    if ot == "Nudge":
        cur = eval_script(script.get("operands", [None, None])[0], state)
        delta = eval_script(script.get("operands", [None, None])[1], state)
        return max(-1.0, min(1.0, cur + delta))

    return script.get("value", 0.0)


def apply_effects(reaction, state):
    for ae in reaction.get("after_effects", []) or []:
        if ae.get("effect_type") != "Bounded Number Effect":
            continue
        set_ptr = ae.get("Set", {})
        char = set_ptr.get("character")
        keyring = set_ptr.get("keyring") or []
        if not char or not keyring:
            continue
        new_val = eval_script(ae.get("to", {}), state)
        state[(char, keyring[0])] = max(-1.0, min(1.0, new_val))


def select_reaction(option, state):
    best = None
    best_d = -999
    for rxn in option.get("reactions", []) or []:
        d = eval_script(rxn.get("desirability_script", 0), state)
        if d is None:
            d = 0
        if isinstance(d, bool):
            d = 1.0 if d else 0.0
        if d > best_d:
            best_d = d
            best = rxn
    return best


def starting_encounter(data):
    spools = [s for s in data.get("spools", []) if s.get("starts_active")]
    spools.sort(key=lambda s: s.get("creation_index", 0))
    for sp in spools:
        encs = sp.get("encounters") or []
        if encs:
            return encs[0]
    encounters = data.get("encounters", [])
    return encounters[0]["id"] if encounters else None


def run_episode(data, rng, max_steps=200):
    enc_by_id = {e["id"]: e for e in data.get("encounters", [])}
    state = {}
    eid = starting_encounter(data)
    if not eid:
        return "DEAD_END", 0, state

    turns = 0
    while turns < max_steps and eid in enc_by_id:
        enc = enc_by_id[eid]
        options = enc.get("options", []) or []

        if not options:
            ok = True
            if turns < enc.get("earliest_turn", 0):
                ok = False
            if turns > enc.get("latest_turn", 999999):
                ok = False
            if not eval_script(enc.get("acceptability_script", True), state):
                ok = False
            return (eid if ok else "page_end_fallback"), turns, state

        visible = [o for o in options if eval_script(o.get("visibility_script", True), state)]
        if not visible:
            return "DEAD_END", turns, state

        chosen = rng.choice(visible)
        rxn = select_reaction(chosen, state)
        if rxn:
            apply_effects(rxn, state)
            next_id = rxn.get("consequence_id")
        else:
            next_id = None

        turns += 1
        if not next_id:
            return "DEAD_END", turns, state
        eid = next_id

    return "TIMEOUT", turns, state


def rare_endings(ending_counts, all_endings, bottom_pct=0.2):
    counts = []
    for eid in all_endings:
        if eid in ("DEAD_END", "TIMEOUT"):
            continue
        counts.append((eid, ending_counts.get(eid, 0)))
    if not counts:
        return []
    counts.sort(key=lambda x: x[1])
    n = max(1, int(len(counts) * bottom_pct))
    return [eid for eid, _ in counts[:n]]


def run_monte_carlo(data, runs=2000, seed=42):
    rng = random.Random(seed)
    ending_counts = Counter()
    for _ in range(runs):
        end_id, _, _ = run_episode(data, rng)
        ending_counts[end_id] += 1
    return ending_counts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("storyworld")
    parser.add_argument("--runs", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    with open(args.storyworld, encoding="utf-8") as f:
        data = json.load(f)

    ending_counts = run_monte_carlo(data, runs=args.runs, seed=args.seed)
    total = sum(ending_counts.values()) or 1
    print("Ending Distribution")
    for eid, count in sorted(ending_counts.items(), key=lambda x: -x[1]):
        pct = count / total * 100
        print(f"  {eid:35s} {count:6d} ({pct:5.1f}%)")

    all_endings = [e["id"] for e in data.get("encounters", []) if e["id"].startswith("page_end_")]
    rare = rare_endings(ending_counts, all_endings)
    print("\nRare endings (bottom 20%)")
    for eid in rare:
        print(f"  {eid}")


if __name__ == "__main__":
    main()
