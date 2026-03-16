#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


def bn_const(value: float) -> Dict[str, Any]:
    return {
        "script_element_type": "Pointer",
        "pointer_type": "Bounded Number Constant",
        "value": float(value),
    }


def bn_ptr(char_id: str, key: str, coefficient: float = 1.0) -> Dict[str, Any]:
    return {
        "script_element_type": "Pointer",
        "pointer_type": "Bounded Number Pointer",
        "character": str(char_id),
        "keyring": [str(key)],
        "coefficient": float(coefficient),
    }


def op(operator_type: str, operands: List[Any], subtype: Optional[str] = None) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "script_element_type": "Operator",
        "operator_type": operator_type,
        "operands": operands,
    }
    if subtype:
        payload["operator_subtype"] = subtype
    return payload


def cmp_gte(pointer: Dict[str, Any], threshold: float) -> Dict[str, Any]:
    return op("Arithmetic Comparator", [pointer, bn_const(threshold)], "Greater Than or Equal To")


def cmp_lte(pointer: Dict[str, Any], threshold: float) -> Dict[str, Any]:
    return op("Arithmetic Comparator", [pointer, bn_const(threshold)], "Less Than or Equal To")


def abs_diff(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    return op("Absolute Value", [op("Subtraction", [a, b])])


def add_to_script(existing: Optional[Dict[str, Any]], extra: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(existing, dict):
        return extra
    return op("Addition", [existing, extra])


def find_encounter(data: Dict[str, Any], encounter_id: str) -> Optional[Dict[str, Any]]:
    for encounter in data.get("encounters", []) or []:
        if encounter.get("id") == encounter_id:
            return encounter
    return None


def find_option_by_consequence(encounter: Dict[str, Any], consequence_id: str) -> Optional[Dict[str, Any]]:
    for option in encounter.get("options", []) or []:
        for reaction in option.get("reactions", []) or []:
            if reaction.get("consequence_id") == consequence_id:
                return option
    return None


def reinforce(data: Dict[str, Any], anchor_id: str, secret_id: str) -> Dict[str, Any]:
    out = json.loads(json.dumps(data))
    anchor = find_encounter(out, anchor_id)
    secret = find_encounter(out, secret_id)
    if anchor is None:
        raise SystemExit(f"anchor encounter not found: {anchor_id}")
    if secret is None:
        raise SystemExit(f"secret encounter not found: {secret_id}")

    cast = [str(char.get("id")) for char in out.get("characters", []) or [] if char.get("id")]
    main_char = cast[0] if cast else "char_player"
    witness_char = cast[1] if len(cast) > 1 else main_char

    secret_option = find_option_by_consequence(anchor, secret_id)
    if secret_option is None:
        raise SystemExit(f"no option under {anchor_id} leads to {secret_id}")

    influence = bn_ptr(main_char, "Influence")
    countercraft = bn_ptr(main_char, "Countercraft")
    transgression = bn_ptr(main_char, "Transgression_Order")
    p_countercraft = bn_ptr(main_char, "pCountercraft")
    p_influence = bn_ptr(main_char, "pInfluence")
    witness_grudge = bn_ptr(witness_char, "Grudge")

    # Make the secret branch easier to see while preserving non-trivial gating.
    secret_option["visibility_script"] = op(
        "Or",
        [
            cmp_gte(countercraft, 0.02),
            op(
                "And",
                [
                    cmp_gte(abs_diff(influence, transgression), 0.03),
                    cmp_gte(p_countercraft, 0.01),
                ],
            ),
        ],
    )

    secret_option["performability_script"] = op(
        "Or",
        [
            cmp_gte(influence, -0.98),
            cmp_gte(p_influence, 0.0),
        ],
    )

    for idx, reaction in enumerate(secret_option.get("reactions", []) or []):
        reaction["desirability_script"] = add_to_script(
            reaction.get("desirability_script"),
            op(
                "Addition",
                [
                    op("Multiplication", [countercraft, bn_const(0.35 + idx * 0.05)]),
                    op("Multiplication", [p_countercraft, bn_const(0.25)]),
                    op("Multiplication", [witness_grudge, bn_const(0.12)]),
                    bn_const(0.06),
                ],
            ),
        )
        effects = reaction.setdefault("after_effects", [])
        effects.append(
            {
                "effect_type": "Bounded Number Effect",
                "Set": bn_ptr(main_char, "Countercraft"),
                "to": op("Addition", [countercraft, bn_const(0.06)]),
            }
        )
        effects.append(
            {
                "effect_type": "Bounded Number Effect",
                "Set": bn_ptr(main_char, "Influence"),
                "to": op("Arithmetic Mean", [influence, p_countercraft, bn_const(0.08)]),
            }
        )

    secret["acceptability_script"] = op(
        "Or",
        [
            cmp_gte(influence, 0.08),
            cmp_gte(transgression, 0.08),
            op(
                "And",
                [
                    cmp_gte(countercraft, 0.03),
                    cmp_gte(p_countercraft, 0.01),
                ],
            ),
        ],
    )
    secret["desirability_script"] = op(
        "Addition",
        [
            op("Multiplication", [influence, bn_const(0.7)]),
            op("Multiplication", [transgression, bn_const(0.7)]),
            op("Multiplication", [countercraft, bn_const(0.45)]),
            op("Multiplication", [p_countercraft, bn_const(0.35)]),
            bn_const(0.08),
        ],
    )
    secret["modified_time"] = int(time.time())
    out["modified_time"] = float(time.time())
    return out


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reinforce the super-secret route in a storyworld.")
    parser.add_argument("input_json")
    parser.add_argument("--out-json", required=True)
    parser.add_argument("--anchor-id", default="page_0087")
    parser.add_argument("--secret-id", default="page_secret_0299")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input_json).resolve()
    out_path = Path(args.out_json).resolve()
    data = json.loads(input_path.read_text(encoding="utf-8"))
    rewritten = reinforce(data, anchor_id=args.anchor_id, secret_id=args.secret_id)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(rewritten, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
