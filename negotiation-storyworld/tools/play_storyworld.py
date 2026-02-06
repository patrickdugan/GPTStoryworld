#!/usr/bin/env python3
"""Play a diplomacy storyworld with random actions (for smoke tests)."""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from storyworld.env import DiplomacyStoryworldEnv, load_storyworld


def random_action(rng: random.Random, action_types, agent_id, agent_ids, outcomes):
    atype = rng.choice(action_types)
    if atype in {"ally", "betray", "propose"}:
        targets = [a for a in agent_ids if a != agent_id]
        target = rng.choice(targets) if targets else None
    else:
        target = None
    probs = {}
    if outcomes:
        weights = [rng.random() for _ in outcomes]
        total = sum(weights) or 1.0
        probs = {outcomes[i]: round(weights[i] / total, 3) for i in range(len(outcomes))}
    q1_probs = {"betrayal": round(rng.random(), 3)}
    q1_probs["no_betrayal"] = round(1.0 - q1_probs["betrayal"], 3)
    return {
        "type": atype,
        "target": target,
        "forecasts": [
            {
                "question_id": "q1",
                "likely_outcome": "betrayal" if q1_probs["betrayal"] >= 0.5 else "no_betrayal",
                "probabilities": q1_probs
            },
            {
                "question_id": "q2",
                "likely_outcome": rng.choice(outcomes) if outcomes else "maneuver",
                "probabilities": probs
            }
        ],
        "confidence": round(rng.uniform(0.3, 0.9), 2),
        "reasoning": f"Random policy chose {atype}."
    }


def random_message(rng: random.Random, agent_ids):
    if len(agent_ids) < 2:
        return None
    src = rng.choice(agent_ids)
    dst = rng.choice([a for a in agent_ids if a != src])
    return {
        "from": src,
        "to": dst,
        "type": rng.choice(["proposal", "threat", "update"]),
        "content": "Auto-generated message.",
        "belief_commitments": {"trust_delta": round(rng.uniform(-0.1, 0.2), 2)}
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--world", type=str, required=True)
    parser.add_argument("--steps", type=int, default=5)
    parser.add_argument("--seed", type=int, default=3)
    parser.add_argument("--log", type=str, default="logs/play.jsonl")
    args = parser.parse_args()

    data = load_storyworld(args.world)
    env = DiplomacyStoryworldEnv(data, seed=args.seed, log_path=args.log)
    state = env.reset(seed=args.seed)

    rng = random.Random(args.seed)
    action_types = data.get("rules", {}).get("action_types", ["wait"])
    outcomes = list(data.get("rules", {}).get("outcomes", {}).keys())
    agent_ids = [a["id"] for a in data.get("agents", [])]

    for _ in range(args.steps):
        actions = {aid: random_action(rng, action_types, aid, agent_ids, outcomes) for aid in agent_ids}
        messages = []
        if rng.random() < 0.6:
            msg = random_message(rng, agent_ids)
            if msg:
                messages.append(msg)
        state, event, done = env.step(actions, messages)
        if done:
            break

    print(json.dumps({"final_state": state, "done": state.get("done")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
