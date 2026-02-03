import argparse
import json
import os
import time

from monte_carlo_spool import run_monte_carlo, rare_endings
from self_agent_playthrough import build_targets, run_agent_episode


def tighten_acceptability(enc, step):
    script = enc.get("acceptability_script", True)
    if script is True:
        return 0
    return _tighten_script(script, step)

def loosen_acceptability(enc, step):
    script = enc.get("acceptability_script", True)
    if script is True:
        return 0
    return _loosen_script(script, step)


def _tighten_script(script, step):
    changed = 0
    if isinstance(script, dict):
        if script.get("operator_type") == "Arithmetic Comparator":
            subtype = script.get("operator_subtype")
            operands = script.get("operands", [None, None])
            right = operands[1] if len(operands) > 1 else None
            if isinstance(right, dict) and right.get("pointer_type") == "Bounded Number Constant":
                val = right.get("value", 0.0)
                if subtype in ("Greater Than or Equal To", "Greater Than"):
                    right["value"] = min(1.0, val + step)
                    changed += 1
                elif subtype in ("Less Than or Equal To", "Less Than"):
                    right["value"] = max(-1.0, val - step)
                    changed += 1
        for v in script.values():
            changed += _tighten_script(v, step)
    elif isinstance(script, list):
        for v in script:
            changed += _tighten_script(v, step)
    return changed

def _loosen_script(script, step):
    changed = 0
    if isinstance(script, dict):
        if script.get("operator_type") == "Arithmetic Comparator":
            subtype = script.get("operator_subtype")
            operands = script.get("operands", [None, None])
            right = operands[1] if len(operands) > 1 else None
            if isinstance(right, dict) and right.get("pointer_type") == "Bounded Number Constant":
                val = right.get("value", 0.0)
                if subtype in ("Greater Than or Equal To", "Greater Than"):
                    right["value"] = max(-1.0, val - step)
                    changed += 1
                elif subtype in ("Less Than or Equal To", "Less Than"):
                    right["value"] = min(1.0, val + step)
                    changed += 1
        for v in script.values():
            changed += _loosen_script(v, step)
    elif isinstance(script, list):
        for v in script:
            changed += _loosen_script(v, step)
    return changed

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("storyworld")
    parser.add_argument("--target_plays", type=int, default=5)
    parser.add_argument("--runs", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max_plays", type=int, default=50)
    parser.add_argument("--max_iters", type=int, default=5)
    parser.add_argument("--step", type=float, default=0.005)
    parser.add_argument("--reports_dir", default="reports")
    parser.add_argument("--model", default="self_agent_v1")
    args = parser.parse_args()

    with open(args.storyworld, encoding="utf-8") as f:
        data = json.load(f)

    enc_by_id = {e["id"]: e for e in data.get("encounters", [])}

    iterations = []
    for it in range(1, args.max_iters + 1):
        ending_counts = run_monte_carlo(data, runs=args.runs, seed=args.seed + it)
        all_endings = [e["id"] for e in data.get("encounters", []) if e["id"].startswith("page_end_")]
        rare = rare_endings(ending_counts, all_endings)
        targets = build_targets(data, rare)

        plays_to_rare = None
        rare_hit = None
        state = None
        rng_seed = args.seed + it * 100

        from random import Random
        rng = Random(rng_seed)

        weights = {}
        for play in range(1, args.max_plays + 1):
            ending, turns, state, history = run_agent_episode(data, rng, targets, weights)
            if ending in rare:
                plays_to_rare = play
                rare_hit = ending
                break
            # simple memory: penalize choices on failure
            for opt_id in history:
                weights[opt_id] = weights.get(opt_id, 0.0) - 0.02

        iterations.append({
            "iteration": it,
            "rare_endings": rare,
            "plays_to_rare": plays_to_rare,
            "rare_ending_hit": rare_hit,
            "ending_counts": dict(ending_counts),
        })

        if plays_to_rare is not None and plays_to_rare >= args.target_plays:
            break

        # adjust gates for rare endings
        for eid in rare:
            enc = enc_by_id.get(eid)
            if not enc:
                continue
            if plays_to_rare is None:
                enc["earliest_turn"] = max(enc.get("earliest_turn", 0) - 1, 10)
                loosen_acceptability(enc, args.step)
            else:
                enc["earliest_turn"] = min(enc.get("earliest_turn", 0) + 1, 20)
                tighten_acceptability(enc, args.step)

    with open(args.storyworld, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    report = {
        "storyworld": data.get("IFID") or data.get("title"),
        "model": args.model,
        "unix_time": int(time.time()),
        "target_plays": args.target_plays,
        "iterations": iterations,
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
    out_path = os.path.join(out_dir, f"{name}_{safe_model}_tune_{report['unix_time']}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(out_path)


if __name__ == "__main__":
    main()
