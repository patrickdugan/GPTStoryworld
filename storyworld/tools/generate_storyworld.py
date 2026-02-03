#!/usr/bin/env python3
"""Generate diplomacy storyworld JSON files."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from storyworld.generators import generate_tiny_world, generate_diplomacy_world
from storyworld.validators.validate_storyworld import validate


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", choices=["tiny", "diplomacy"], default="tiny")
    parser.add_argument("--agents", type=int, default=3)
    parser.add_argument("--nodes", type=int, default=4)
    parser.add_argument("--seed", type=int, default=11)
    parser.add_argument("--out", type=str, required=True)
    parser.add_argument("--validate", action="store_true")
    args = parser.parse_args()

    if args.type == "tiny":
        data = generate_tiny_world(seed=args.seed)
    else:
        data = generate_diplomacy_world(num_agents=args.agents, num_nodes=args.nodes, seed=args.seed)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    if args.validate:
        return validate(out_path, Path(__file__).resolve().parents[1] / "schema", strict=False)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
