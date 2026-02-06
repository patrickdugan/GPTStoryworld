#!/usr/bin/env python3
"""Gate storyworlds by minimum critic scores."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from storyworld.env import load_storyworld
from storyworld.tools.critique_storyworld import score_world


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--world", type=str, required=True)
    parser.add_argument("--min-richness", type=float, default=0.3)
    parser.add_argument("--min-manipulability", type=float, default=0.3)
    parser.add_argument("--min-forecast", type=float, default=0.3)
    args = parser.parse_args()

    data = load_storyworld(args.world)
    scores = score_world(data)

    accept = (
        scores.get("richness", 0) >= args.min_richness
        and scores.get("manipulability", 0) >= args.min_manipulability
        and scores.get("forecast_difficulty", 0) >= args.min_forecast
    )

    result = {
        "accept": accept,
        "scores": scores,
        "thresholds": {
            "min_richness": args.min_richness,
            "min_manipulability": args.min_manipulability,
            "min_forecast_difficulty": args.min_forecast,
        },
    }

    print(json.dumps(result, indent=2))
    return 0 if accept else 2


if __name__ == "__main__":
    raise SystemExit(main())
