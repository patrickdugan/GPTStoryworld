#!/usr/bin/env python3
"""Project storyworld reaction formulas into a compact fixed-dimension vector."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable


def iter_nodes(node: Any) -> Iterable[Dict[str, Any]]:
    if isinstance(node, dict):
        if "type" in node:
            yield node
        for value in node.values():
            yield from iter_nodes(value)
    elif isinstance(node, list):
        for value in node:
            yield from iter_nodes(value)


def node_depth(node: Any) -> int:
    if isinstance(node, dict):
        depths = [node_depth(v) for v in node.values()]
        return 1 + (max(depths) if depths else 0)
    if isinstance(node, list):
        depths = [node_depth(v) for v in node]
        return 1 + (max(depths) if depths else 0)
    return 0


def has_p1(node: Any) -> bool:
    for n in iter_nodes(node):
        if n.get("type") != "BNumberProperty":
            continue
        p1 = str(n.get("perceivedCharacterId", "")).strip()
        p2 = str(n.get("perceivedCharacterId2", "")).strip()
        if p1 and not p2:
            return True
    return False


def has_p2(node: Any) -> bool:
    for n in iter_nodes(node):
        if n.get("type") != "BNumberProperty":
            continue
        if str(n.get("perceivedCharacterId2", "")).strip():
            return True
    return False


def ratio(num: int | float, den: int | float) -> float:
    return round(float(num) / float(den), 4) if den else 0.0


def project(path: Path) -> Dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))

    reactions_total = 0
    non_constant_inclination = 0
    with_p1 = 0
    with_p2 = 0
    inclination_node_total = 0
    inclination_depth_total = 0

    effects_total = 0
    dynamic_effect_values = 0
    effect_blend = 0
    effect_nudge = 0
    effect_reversal = 0
    effect_average = 0
    effect_proximity = 0

    for encounter in data.get("encounters", []) or []:
        for option in encounter.get("options", []) or []:
            for reaction in option.get("reactions", []) or []:
                if not isinstance(reaction, dict):
                    continue
                reactions_total += 1

                inc = reaction.get("inclination_ast") or reaction.get("desirability_ast") or {}
                if isinstance(inc, dict):
                    if inc.get("type") != "Constant":
                        non_constant_inclination += 1
                    if has_p1(inc):
                        with_p1 += 1
                    if has_p2(inc):
                        with_p2 += 1

                    inc_nodes = list(iter_nodes(inc))
                    inclination_node_total += len(inc_nodes)
                    inclination_depth_total += node_depth(inc)

                effects = reaction.get("effects")
                if not isinstance(effects, list):
                    continue
                effects_total += len(effects)
                for effect in effects:
                    if not isinstance(effect, dict):
                        continue
                    value = effect.get("value")
                    if not isinstance(value, dict):
                        continue
                    if value.get("type") != "Constant":
                        dynamic_effect_values += 1
                    nodes = list(iter_nodes(value))
                    if any(n.get("type") == "Blend" for n in nodes):
                        effect_blend += 1
                    if any(n.get("type") == "Nudge" for n in nodes):
                        effect_nudge += 1
                    if any(n.get("type") == "ArithmeticNegation" for n in nodes):
                        effect_reversal += 1
                    if any(n.get("type") == "Average" for n in nodes):
                        effect_average += 1
                    if any(n.get("type") == "Proximity" for n in nodes):
                        effect_proximity += 1

    vector = [
        float(reactions_total),
        ratio(non_constant_inclination, reactions_total),
        ratio(with_p1, reactions_total),
        ratio(with_p2, reactions_total),
        ratio(inclination_node_total, reactions_total),
        ratio(inclination_depth_total, reactions_total),
        ratio(effects_total, reactions_total),
        ratio(dynamic_effect_values, effects_total),
        ratio(effect_blend, effects_total),
        ratio(effect_nudge, effects_total),
        ratio(effect_reversal, effects_total),
        ratio(effect_average, effects_total),
        ratio(effect_proximity, effects_total),
    ]

    return {
        "storyworld_path": str(path),
        "vector_schema": [
            "n_reactions",
            "pct_non_constant_inclination",
            "pct_inclination_with_p1",
            "pct_inclination_with_p2",
            "avg_inclination_nodes",
            "avg_inclination_depth",
            "avg_effects_per_reaction",
            "pct_effect_values_dynamic",
            "pct_effects_with_blend",
            "pct_effects_with_nudge",
            "pct_effects_with_reversal",
            "pct_effects_with_average",
            "pct_effects_with_proximity",
        ],
        "vector": vector,
        "summary": {
            "reactions_total": reactions_total,
            "effects_total": effects_total,
            "inclination_node_total": inclination_node_total,
            "inclination_depth_total": inclination_depth_total,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--storyworld", required=True, help="Path to storyworld JSON")
    parser.add_argument("--out", default="", help="Optional output JSON file path")
    args = parser.parse_args()

    projection = project(Path(args.storyworld))
    text = json.dumps(projection, indent=2, ensure_ascii=False)

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text + "\n", encoding="utf-8")

    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
