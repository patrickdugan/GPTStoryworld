#!/usr/bin/env python3
"""Generate tiny diplomacy storyworlds that satisfy the schema constraints."""

from __future__ import annotations

import argparse
import json
import random
from typing import Any, Dict, List


def _agent(agent_id: str, name: str, role: str) -> Dict[str, Any]:
    return {"id": agent_id, "name": name, "role": role}


def _beliefs(agent_ids: List[str]) -> Dict[str, Any]:
    beliefs: Dict[str, Any] = {}
    for aid in agent_ids:
        trust = {other: 0.0 for other in agent_ids}
        beliefs[aid] = {"trust": trust, "expected_payoff": 0.0, "stance": "neutral"}
    return beliefs


def generate(seed: int = 7) -> Dict[str, Any]:
    rng = random.Random(seed)

    agents = [
        _agent("AgentA", "Agent A", "player"),
        _agent("AgentB", "Agent B", "player"),
        _agent("AgentC", "Agent C", "player"),
    ]
    agent_ids = [a["id"] for a in agents]

    nodes = [
        {"id": "node_start", "label": "Opening", "state_vars": {"tension": 0.2}},
        {"id": "node_coalition", "label": "Coalition", "state_vars": {"tension": 0.4}},
        {"id": "node_betrayal", "label": "Betrayal", "state_vars": {"tension": 0.8}, "terminal": True},
    ]

    storyworld = {
        "id": f"diplomacy_tiny_{seed}",
        "title": "Tiny Diplomacy",
        "description": "Minimal diplomacy loop with coalition and betrayal outcomes.",
        "turn_limit": 6,
        "agents": agents,
        "nodes": nodes,
        "initial_state": {
            "active_node": "node_start",
            "beliefs": _beliefs(agent_ids),
            "coalitions": [],
            "world_vars": {"round": 0, "seed": seed},
        },
        "rules": {
            "outcomes": {
                "betrayal": {"next_node": "node_betrayal", "terminal": True},
                "coalition_formed": {"next_node": "node_coalition"},
                "stalemate": {"next_node": "node_start"},
                "maneuver": {"next_node": "node_start"}
            },
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
                    "outcomes": ["betrayal", "coalition_formed", "stalemate", "maneuver"]
                }
            ]
        },
        "messages": [
            {
                "from": "AgentA",
                "to": "AgentB",
                "type": "proposal",
                "content": "Join coalition with A.",
                "belief_commitments": {"trust_A": 0.2, "expected_payoff": 0.3}
            }
        ],
        "hidden_state": [
            {"key": "secret_payoff", "type": "number", "value": rng.uniform(-0.2, 0.5)}
        ]
    }

    return storyworld


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--out", type=str, required=True)
    args = parser.parse_args()

    data = generate(seed=args.seed)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
