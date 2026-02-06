#!/usr/bin/env python3
"""Generate diplomacy storyworlds with configurable size within constraints."""

from __future__ import annotations

import argparse
import json
import random
from typing import Any, Dict, List


def _agent(agent_id: str, idx: int) -> Dict[str, Any]:
    return {"id": agent_id, "name": f"Agent {idx}", "role": "player"}


def _beliefs(agent_ids: List[str]) -> Dict[str, Any]:
    beliefs: Dict[str, Any] = {}
    for aid in agent_ids:
        trust = {other: 0.0 for other in agent_ids}
        beliefs[aid] = {"trust": trust, "expected_payoff": 0.0, "stance": "neutral"}
    return beliefs


def generate(num_agents: int = 3, num_nodes: int = 4, seed: int = 11) -> Dict[str, Any]:
    if num_agents < 2 or num_agents > 5:
        raise ValueError("num_agents must be 2-5")
    if num_nodes < 2 or num_nodes > 12:
        raise ValueError("num_nodes must be 2-12")

    rng = random.Random(seed)

    agent_ids = [f"Agent{chr(65 + i)}" for i in range(num_agents)]
    agents = [_agent(aid, i + 1) for i, aid in enumerate(agent_ids)]

    nodes = []
    for i in range(num_nodes):
        node_id = "node_start" if i == 0 else f"node_{i}"
        nodes.append({
            "id": node_id,
            "label": f"Phase {i}",
            "state_vars": {"pressure": round(rng.uniform(0.1, 0.9), 2)},
            "terminal": i == num_nodes - 1,
        })

    outcomes = {
        "betrayal": {"next_node": nodes[-1]["id"], "terminal": True},
        "coalition_formed": {"next_node": nodes[min(1, num_nodes - 1)]["id"]},
        "stalemate": {"next_node": nodes[0]["id"]},
        "maneuver": {"next_node": nodes[0]["id"]},
    }

    storyworld = {
        "id": f"diplomacy_{num_agents}a_{num_nodes}n_{seed}",
        "title": "Generated Diplomacy World",
        "description": "Auto-generated diplomacy micro-world for forecasting.",
        "turn_limit": min(10, num_nodes * 2),
        "agents": agents,
        "nodes": nodes,
        "initial_state": {
            "active_node": nodes[0]["id"],
            "beliefs": _beliefs(agent_ids),
            "coalitions": [],
            "world_vars": {"round": 0, "seed": seed},
        },
        "rules": {
            "outcomes": outcomes,
            "belief_update": {
                "ally": 0.1,
                "betray": -0.4,
                "betray_self": -0.1,
                "propose": 0.05,
                "message_proposal": 0.05,
                "message_threat": -0.1
            },
            "trust_bounds": {"min": -1.0, "max": 1.0},
            "action_types": ["propose", "ally", "betray", "wait"],
            "message_types": ["proposal", "threat", "update"],
            "forecast_questions": [
                {
                    "id": "q1",
                    "text": "Will a betrayal occur this turn?",
                    "outcomes": ["betrayal", "no_betrayal"]
                },
                {
                    "id": "q2",
                    "text": "What is the most likely outcome?",
                    "outcomes": list(outcomes.keys())
                }
            ]
        },
        "hidden_state": [
            {"key": "secret_alignment", "type": "string", "value": rng.choice(["hawk", "dove"])}
        ]
    }

    return storyworld


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agents", type=int, default=3)
    parser.add_argument("--nodes", type=int, default=4)
    parser.add_argument("--seed", type=int, default=11)
    parser.add_argument("--out", type=str, required=True)
    args = parser.parse_args()

    data = generate(num_agents=args.agents, num_nodes=args.nodes, seed=args.seed)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
