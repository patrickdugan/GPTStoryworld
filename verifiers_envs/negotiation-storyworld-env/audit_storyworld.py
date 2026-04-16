#!/usr/bin/env python3
"""Audit diplomacy storyworld reaction logic/effects quality."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


AST_DYNAMIC_TYPES = {
    "Blend",
    "Nudge",
    "Average",
    "Proximity",
    "Maximum",
    "Minimum",
    "ArithmeticNegation",
    "IfThen",
}


def iter_nodes(node: Any) -> Iterable[Dict[str, Any]]:
    if isinstance(node, dict):
        if "type" in node:
            yield node
        for value in node.values():
            yield from iter_nodes(value)
    elif isinstance(node, list):
        for value in node:
            yield from iter_nodes(value)


def iter_legacy_nodes(node: Any) -> Iterable[Dict[str, Any]]:
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from iter_legacy_nodes(value)
    elif isinstance(node, list):
        for value in node:
            yield from iter_legacy_nodes(value)


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
        p2 = str(n.get("perceivedCharacterId2", "")).strip()
        if p2:
            return True
    return False


def has_dynamic_logic(node: Any) -> bool:
    return any(n.get("type") in AST_DYNAMIC_TYPES for n in iter_nodes(node))


def legacy_has_p1(node: Any) -> bool:
    for n in iter_legacy_nodes(node):
        if n.get("pointer_type") != "Bounded Number Pointer":
            continue
        keyring = n.get("keyring") or []
        if isinstance(keyring, list) and len(keyring) == 2:
            return True
    return False


def legacy_has_p2(node: Any) -> bool:
    for n in iter_legacy_nodes(node):
        if n.get("pointer_type") != "Bounded Number Pointer":
            continue
        keyring = n.get("keyring") or []
        if isinstance(keyring, list) and len(keyring) >= 3:
            return True
    return False


def legacy_has_dynamic_logic(node: Any) -> bool:
    for n in iter_legacy_nodes(node):
        op = str(n.get("operator_type", "")).strip()
        if op in AST_DYNAMIC_TYPES:
            return True
    return False


def legacy_is_constant(node: Any) -> bool:
    if not isinstance(node, dict):
        return True
    if node.get("script_element_type") == "Pointer":
        return node.get("pointer_type") in {
            "Bounded Number Constant",
            "Boolean Constant",
            "String Constant",
        }
    if node.get("script_element_type") == "Operator":
        operands = node.get("operands", []) or []
        if not operands:
            return True
        return all(legacy_is_constant(op) for op in operands)
    return False


def audit_storyworld(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    authored = data.get("authored_properties", [])
    depth_by_id = {}
    for prop in authored:
        if isinstance(prop, dict) and prop.get("id"):
            try:
                depth_by_id[str(prop["id"])] = int(prop.get("depth", 0))
            except (TypeError, ValueError):
                depth_by_id[str(prop["id"])] = 0

    trust_depth = depth_by_id.get("Trust")
    threat_depth = depth_by_id.get("Threat")

    failures: List[Dict[str, Any]] = []
    reactions_total = 0
    reactions_non_constant = 0
    reactions_with_p1 = 0
    reactions_with_p2 = 0
    reactions_dynamic_effects = 0
    reversal_effects = 0

    for encounter in data.get("encounters", []) or []:
        encounter_id = encounter.get("id", "")
        for option in encounter.get("options", []) or []:
            option_id = option.get("id", "")
            for reaction in option.get("reactions", []) or []:
                if not isinstance(reaction, dict):
                    continue
                reactions_total += 1
                reaction_id = reaction.get("id", "")

                inc = reaction.get("inclination_ast") or reaction.get("desirability_ast")
                legacy_inc = reaction.get("desirability_script")
                if isinstance(inc, dict):
                    root_type = str(inc.get("type", ""))
                    is_non_constant = root_type != "Constant"
                    has_p1_term = has_p1(inc)
                    has_p2_term = has_p2(inc)
                elif isinstance(legacy_inc, dict):
                    is_non_constant = not legacy_is_constant(legacy_inc)
                    has_p1_term = legacy_has_p1(legacy_inc)
                    has_p2_term = legacy_has_p2(legacy_inc)
                else:
                    failures.append(
                        {
                            "encounter": encounter_id,
                            "option": option_id,
                            "reaction": reaction_id,
                            "issue": "missing_inclination_ast",
                        }
                    )
                    continue

                if is_non_constant:
                    reactions_non_constant += 1
                else:
                    failures.append(
                        {
                            "encounter": encounter_id,
                            "option": option_id,
                            "reaction": reaction_id,
                            "issue": "constant_inclination",
                        }
                    )

                if has_p1_term:
                    reactions_with_p1 += 1
                else:
                    failures.append(
                        {
                            "encounter": encounter_id,
                            "option": option_id,
                            "reaction": reaction_id,
                            "issue": "no_pvalue_term",
                        }
                    )

                if has_p2_term:
                    reactions_with_p2 += 1
                else:
                    failures.append(
                        {
                            "encounter": encounter_id,
                            "option": option_id,
                            "reaction": reaction_id,
                            "issue": "no_p2value_term",
                        }
                    )

                effects = reaction.get("effects")
                legacy_effects = reaction.get("after_effects")
                effect_nodes = effects if isinstance(effects, list) and effects else legacy_effects
                if not isinstance(effect_nodes, list) or len(effect_nodes) == 0:
                    failures.append(
                        {
                            "encounter": encounter_id,
                            "option": option_id,
                            "reaction": reaction_id,
                            "issue": "empty_effects",
                        }
                    )
                    continue

                reaction_effect_dynamic = False
                for effect in effect_nodes:
                    if not isinstance(effect, dict):
                        continue
                    value_ast = effect.get("value")
                    if isinstance(value_ast, dict):
                        if value_ast.get("type") != "Constant":
                            if has_dynamic_logic(value_ast):
                                reaction_effect_dynamic = True
                            if any(n.get("type") == "ArithmeticNegation" for n in iter_nodes(value_ast)):
                                reversal_effects += 1
                        else:
                            failures.append(
                                {
                                    "encounter": encounter_id,
                                    "option": option_id,
                                    "reaction": reaction_id,
                                    "issue": "constant_effect_value",
                                }
                            )
                        continue

                    legacy_value = effect.get("to")
                    if isinstance(legacy_value, dict) and not legacy_is_constant(legacy_value):
                        if legacy_has_dynamic_logic(legacy_value):
                            reaction_effect_dynamic = True
                        if any(
                            str(n.get("operator_type", "")).strip() == "ArithmeticNegation"
                            for n in iter_legacy_nodes(legacy_value)
                        ):
                            reversal_effects += 1
                    else:
                        failures.append(
                            {
                                "encounter": encounter_id,
                                "option": option_id,
                                "reaction": reaction_id,
                                "issue": "constant_effect_value",
                            }
                        )

                if reaction_effect_dynamic:
                    reactions_dynamic_effects += 1
                else:
                    failures.append(
                        {
                            "encounter": encounter_id,
                            "option": option_id,
                            "reaction": reaction_id,
                            "issue": "no_dynamic_effect_logic",
                        }
                    )

    if trust_depth is not None and trust_depth < 2:
        failures.append({"issue": "trust_depth_lt_2", "depth": trust_depth})
    if threat_depth is not None and threat_depth < 2:
        failures.append({"issue": "threat_depth_lt_2", "depth": threat_depth})

    def frac(n: int, d: int) -> float:
        return round((n / d), 4) if d else 0.0

    return {
        "storyworld_path": str(path),
        "reactions_total": reactions_total,
        "coverage": {
            "non_constant_inclination": frac(reactions_non_constant, reactions_total),
            "with_pvalue_term": frac(reactions_with_p1, reactions_total),
            "with_p2value_term": frac(reactions_with_p2, reactions_total),
            "with_dynamic_effects": frac(reactions_dynamic_effects, reactions_total),
        },
        "authored_property_depth": {
            "Trust": trust_depth,
            "Threat": threat_depth,
        },
        "reversal_effect_nodes": reversal_effects,
        "failure_count": len(failures),
        "failures": failures,
        "ok": len(failures) == 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--storyworld", required=True, help="Path to storyworld JSON")
    parser.add_argument("--out", default="", help="Optional output JSON path")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when audit fails")
    args = parser.parse_args()

    report = audit_storyworld(Path(args.storyworld))
    text = json.dumps(report, indent=2, ensure_ascii=False)

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text + "\n", encoding="utf-8")

    print(text)
    if args.strict and not report.get("ok", False):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
