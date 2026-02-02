"""
Monte Carlo rehearsal simulator for SweepWeave storyworlds.
Ports the Rehearsal.gd / AutoRehearsal.gd engine logic to Python.

Usage:
  python monte_carlo_rehearsal.py storyworld.json [--runs 10000] [--seed 42]

Output: ending distribution, dead-end rate, property distributions,
        late-game blocking rate, secret reachability.
"""
import json
import random
import sys
from collections import Counter, defaultdict


def eval_script(script, state):
    """Recursively evaluate a SweepWeave script expression."""
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
    if pt == "String Constant":
        return script.get("value", "")

    if ot == "Arithmetic Comparator":
        sub = script["operator_subtype"]
        left = eval_script(script["operands"][0], state)
        right = eval_script(script["operands"][1], state)
        ops = {
            "Greater Than or Equal To": lambda a, b: a >= b, "GTE": lambda a, b: a >= b,
            "Less Than or Equal To": lambda a, b: a <= b, "LTE": lambda a, b: a <= b,
            "Greater Than": lambda a, b: a > b, "GT": lambda a, b: a > b,
            "Less Than": lambda a, b: a < b, "LT": lambda a, b: a < b,
            "Equal To": lambda a, b: a == b, "EQ": lambda a, b: a == b,
            "Not Equal To": lambda a, b: a != b, "NEQ": lambda a, b: a != b,
        }
        return ops.get(sub, lambda a, b: False)(left, right)

    if ot == "And":
        return all(eval_script(op, state) for op in script["operands"])
    if ot == "Or":
        return any(eval_script(op, state) for op in script["operands"])
    if ot == "Addition":
        return sum(eval_script(op, state) for op in script["operands"])
    if ot == "Multiplication":
        r = 1.0
        for op in script["operands"]:
            r *= eval_script(op, state)
        return r
    if ot == "Absolute Value":
        return abs(eval_script(script["operands"][0], state))
    if ot == "Nudge":
        cur = eval_script(script["operands"][0], state)
        delta = eval_script(script["operands"][1], state)
        return max(-1.0, min(1.0, cur + delta))

    return script.get("value", 0.0)


def apply_effects(reaction, state):
    for ae in reaction.get("after_effects", []):
        if ae.get("effect_type") == "Bounded Number Effect":
            char = ae["Set"]["character"]
            prop = ae["Set"]["keyring"][0]
            new_val = eval_script(ae["to"], state)
            state[(char, prop)] = max(-1.0, min(1.0, new_val))


def select_reaction(option, state):
    best, best_d = None, -999
    for rxn in option.get("reactions", []):
        d = eval_script(rxn.get("desirability_script", 0), state)
        if d is None: d = 0
        if isinstance(d, bool): d = 1.0 if d else 0.0
        if d > best_d:
            best_d, best = d, rxn
    return best


def build_chain(data):
    """Build linear consequence chain from page_0000 onward."""
    enc_by_id = {e["id"]: e for e in data["encounters"]}
    chain, visited = [], set()
    current_id = "page_0000"
    while current_id and current_id != "wild" and current_id not in visited:
        if current_id not in enc_by_id:
            break
        visited.add(current_id)
        enc = enc_by_id[current_id]
        chain.append(enc)
        next_id = None
        for opt in enc.get("options", []):
            for rxn in opt.get("reactions", []):
                cid = rxn.get("consequence_id", "")
                if cid:
                    next_id = cid
                    break
            if next_id:
                break
        current_id = next_id
    return chain


def run_monte_carlo(data, num_runs=10000, seed=42):
    random.seed(seed)
    chain = build_chain(data)
    endings = [e for e in data["encounters"] if e["id"].startswith("page_end_")]
    secrets = [e for e in data["encounters"] if e["id"].startswith("page_secret_")]

    spool_map = {}
    for sp in data.get("spools", []):
        for eid in sp.get("encounters", []):
            spool_map[eid] = sp["spool_name"]

    ending_counts = Counter()
    dead_ends = 0
    prop_sums = defaultdict(float)
    prop_sq = defaultdict(float)
    late_blocks, late_total = 0, 0
    secret_hits = Counter()

    for _ in range(num_runs):
        state = {}
        for enc in chain:
            eid = enc["id"]
            spool = spool_map.get(eid, "")
            if spool.startswith("Age "):
                age = int(spool.split(" ")[1])
                if age >= 14:
                    if not bool(eval_script(enc.get("acceptability_script", True), state)):
                        late_blocks += 1
                    late_total += 1

            visible = [(i, o) for i, o in enumerate(enc.get("options", []))
                       if eval_script(o.get("visibility_script", True), state)]
            if not visible:
                continue
            _, chosen = random.choice(visible)
            rxn = select_reaction(chosen, state)
            if rxn:
                apply_effects(rxn, state)

        for sec in secrets:
            if eval_script(sec.get("acceptability_script", True), state):
                secret_hits[sec["id"]] += 1

        best_end, best_d = None, -999
        for end in endings:
            if eval_script(end.get("acceptability_script", True), state):
                d = eval_script(end.get("desirability_script", 0), state)
                if isinstance(d, bool): d = 1.0 if d else 0.0
                if d > best_d:
                    best_d, best_end = d, end

        if best_end:
            ending_counts[best_end["id"]] += 1
        else:
            dead_ends += 1
            ending_counts["DEAD_END"] += 1

        for (char, prop), val in state.items():
            key = f"{char}.{prop}"
            prop_sums[key] += val
            prop_sq[key] += val * val

    return {
        "chain_length": len(chain),
        "num_endings": len(endings),
        "num_secrets": len(secrets),
        "num_runs": num_runs,
        "ending_counts": ending_counts,
        "dead_ends": dead_ends,
        "late_blocks": late_blocks,
        "late_total": late_total,
        "secret_hits": secret_hits,
        "prop_sums": prop_sums,
        "prop_sq": prop_sq,
        "endings": endings,
    }


def print_report(r):
    N = r["num_runs"]
    print(f"\nChain: {r['chain_length']} encounters | {r['num_endings']} endings | {r['num_secrets']} secrets")
    print("=" * 70)
    print(f"MONTE CARLO RESULTS ({N} runs)")
    print("=" * 70)

    print("\n--- Ending Distribution ---")
    for eid, count in sorted(r["ending_counts"].items(), key=lambda x: -x[1]):
        pct = count / N * 100
        bar = "#" * int(pct / 2)
        print(f"  {eid:35s} {count:6d} ({pct:5.1f}%) {bar}")

    print(f"\n  Dead-end rate: {r['dead_ends']}/{N} ({r['dead_ends']/N*100:.1f}%)")

    print(f"\n--- Late-Game Gate Blocking ---")
    if r["late_total"] > 0:
        print(f"  {r['late_blocks']}/{r['late_total']} blocked ({r['late_blocks']/r['late_total']*100:.1f}%)")

    print(f"\n--- Secret Reachability ---")
    for sid in sorted(r["secret_hits"].keys()):
        c = r["secret_hits"][sid]
        print(f"  {sid:40s} {c:6d} ({c/N*100:.1f}%)")
    if not r["secret_hits"]:
        print("  None reachable")

    print(f"\n--- Property Distributions ---")
    for pk in sorted(r["prop_sums"].keys()):
        mean = r["prop_sums"][pk] / N
        var = r["prop_sq"][pk] / N - mean * mean
        std = var ** 0.5 if var > 0 else 0
        print(f"  {pk:45s}  mean={mean:+.4f}  std={std:.4f}")

    print(f"\n--- Unreachable Endings ---")
    for end in r["endings"]:
        if end["id"] not in r["ending_counts"]:
            print(f"  {end['id']}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python monte_carlo_rehearsal.py storyworld.json [--runs N] [--seed S]")
        sys.exit(1)

    path = sys.argv[1]
    runs = 10000
    seed = 42
    for i, arg in enumerate(sys.argv):
        if arg == "--runs" and i + 1 < len(sys.argv):
            runs = int(sys.argv[i + 1])
        if arg == "--seed" and i + 1 < len(sys.argv):
            seed = int(sys.argv[i + 1])

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    result = run_monte_carlo(data, num_runs=runs, seed=seed)
    print_report(result)
