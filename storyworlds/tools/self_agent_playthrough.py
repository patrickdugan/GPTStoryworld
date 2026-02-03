import argparse
import json
import os
import random
import time

from monte_carlo_spool import eval_script, apply_effects, select_reaction, starting_encounter, run_episode, rare_endings, run_monte_carlo


def collect_acceptability_conditions(script, out):
    if script is True or script is False:
        return
    if isinstance(script, dict):
        if script.get("operator_type") == "Arithmetic Comparator":
            left = script.get("operands", [None, None])[0]
            right = script.get("operands", [None, None])[1]
            if isinstance(left, dict) and left.get("pointer_type") == "Bounded Number Pointer":
                char = left.get("character")
                keyring = left.get("keyring") or []
                if char and keyring and isinstance(right, dict) and right.get("pointer_type") == "Bounded Number Constant":
                    out.append((char, keyring[0], script.get("operator_subtype"), right.get("value", 0.0)))
        for v in script.values():
            collect_acceptability_conditions(v, out)
    elif isinstance(script, list):
        for v in script:
            collect_acceptability_conditions(v, out)


def build_targets(data, rare_ids):
    enc_by_id = {e["id"]: e for e in data.get("encounters", [])}
    targets = []
    for eid in rare_ids:
        enc = enc_by_id.get(eid)
        if not enc:
            continue
        conds = []
        collect_acceptability_conditions(enc.get("acceptability_script", True), conds)
        targets.extend(conds)
    return targets


def option_effects(option, state):
    rxn = select_reaction(option, state)
    effects = []
    if not rxn:
        return effects
    for ae in rxn.get("after_effects", []) or []:
        if ae.get("effect_type") != "Bounded Number Effect":
            continue
        set_ptr = ae.get("Set", {})
        char = set_ptr.get("character")
        keyring = set_ptr.get("keyring") or []
        if not char or not keyring:
            continue
        to = ae.get("to", {})
        if to.get("operator_type") != "Nudge":
            continue
        delta = to.get("operands", [{}, {}])[1].get("value", 0.0)
        effects.append((char, keyring[0], delta))
    return effects


def score_option(option, state, targets, weights):
    effects = option_effects(option, state)
    score = weights.get(option.get("id", ""), 0.0)

    for (char, prop, op, thresh) in targets:
        cur = state.get((char, prop), 0.0)
        best_delta = 0.0
        for ec, ep, delta in effects:
            if ec == char and ep == prop:
                best_delta += delta
        if op in ("Greater Than or Equal To", "Greater Than"):
            if cur < thresh:
                score += max(0.0, best_delta) * 2.0
            else:
                score += max(0.0, best_delta)
        elif op in ("Less Than or Equal To", "Less Than"):
            if cur > thresh:
                score += max(0.0, -best_delta) * 2.0
            else:
                score += max(0.0, -best_delta)
    return score


def run_agent_episode(data, rng, targets, weights, max_steps=200):
    enc_by_id = {e["id"]: e for e in data.get("encounters", [])}
    state = {}
    eid = starting_encounter(data)
    turns = 0
    history = []

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
            return (eid if ok else "page_end_fallback"), turns, state, history

        visible = [o for o in options if eval_script(o.get("visibility_script", True), state)]
        if not visible:
            return "DEAD_END", turns, state, history

        scored = [(score_option(o, state, targets, weights), o) for o in visible]
        scored.sort(key=lambda x: x[0], reverse=True)
        chosen = scored[0][1]
        history.append(chosen.get("id"))

        rxn = select_reaction(chosen, state)
        if rxn:
            apply_effects(rxn, state)
            next_id = rxn.get("consequence_id")
        else:
            next_id = None

        turns += 1
        if not next_id:
            return "DEAD_END", turns, state, history
        eid = next_id

    return "TIMEOUT", turns, state, history


def adjust_weights(weights, history, success, step=0.02):
    for opt_id in history:
        if success:
            weights[opt_id] = weights.get(opt_id, 0.0) + step
        else:
            weights[opt_id] = weights.get(opt_id, 0.0) - step


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("storyworld")
    parser.add_argument("--runs", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max_plays", type=int, default=50)
    parser.add_argument("--model", default="self_agent_v1")
    parser.add_argument("--reports_dir", default="reports")
    args = parser.parse_args()

    with open(args.storyworld, encoding="utf-8") as f:
        data = json.load(f)

    ending_counts = run_monte_carlo(data, runs=args.runs, seed=args.seed)
    all_endings = [e["id"] for e in data.get("encounters", []) if e["id"].startswith("page_end_")]
    rare = rare_endings(ending_counts, all_endings)

    targets = build_targets(data, rare)
    rng = random.Random(args.seed)

    first_ending = None
    first_turns = None
    first_state = None

    weights = {}
    plays_to_rare = None
    rare_hit = None

    for play in range(1, args.max_plays + 1):
        ending, turns, state, history = run_agent_episode(data, rng, targets, weights)
        if first_ending is None:
            first_ending = ending
            first_turns = turns
            first_state = {f"{c}.{p}": v for (c, p), v in state.items()}
        success = ending in rare
        adjust_weights(weights, history, success)
        if success:
            plays_to_rare = play
            rare_hit = ending
            break

    report = {
        "storyworld": data.get("IFID") or data.get("title"),
        "model": args.model,
        "unix_time": int(time.time()),
        "plays": play,
        "first_ending": first_ending,
        "first_turns": first_turns,
        "first_end_state": first_state,
        "rare_endings": rare,
        "plays_to_rare": plays_to_rare,
        "rare_ending_hit": rare_hit,
    }

    def _sanitize(text):
        out = []
        for ch in text.lower():
            if ch.isalnum():
                out.append(ch)
            else:
                out.append("_")
        return "".join(out).strip("_")

    name = _sanitize(data.get("title", "storyworld"))
    safe_model = _sanitize(args.model)
    out_dir = args.reports_dir
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{name}_{safe_model}_{report['unix_time']}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(out_path)


if __name__ == "__main__":
    main()
