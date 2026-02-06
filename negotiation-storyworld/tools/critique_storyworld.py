#!/usr/bin/env python3
"""Score a diplomacy storyworld for richness, manipulability, forecast difficulty."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from storyworld.env import load_storyworld


def clamp(val: float) -> float:
    return max(0.0, min(1.0, val))


def score_world(data: dict) -> dict:
    num_agents = len(data.get("agents", []))
    num_nodes = len(data.get("nodes", []))
    num_messages = len(data.get("messages", []))
    hidden = len(data.get("hidden_state", []))
    forecast_questions = len(data.get("rules", {}).get("forecast_questions", []))

    richness = clamp((num_nodes / 12) * 0.45 + (num_agents / 5) * 0.35 + (num_messages / 10) * 0.2)
    manipulability = clamp((num_agents / 5) * 0.4 + (hidden / 5) * 0.3 + (num_messages / 10) * 0.3)
    forecast = clamp((max(0, num_agents - 2) / 3) * 0.45 + (max(0, num_nodes - 2) / 10) * 0.25 + (data.get("turn_limit", 1) / 20) * 0.2 + (forecast_questions / 5) * 0.1)

    return {
        "richness": round(richness, 3),
        "manipulability": round(manipulability, 3),
        "forecast_difficulty": round(forecast, 3)
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--world", type=str, required=True)
    args = parser.parse_args()

    data = load_storyworld(args.world)
    scores = score_world(data)
    print(json.dumps(scores, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
