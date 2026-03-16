#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Set, Tuple


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


def op(operator_type: str, operands: Sequence[Any], subtype: str | None = None) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "script_element_type": "Operator",
        "operator_type": operator_type,
        "operands": list(operands),
    }
    if subtype:
        payload["operator_subtype"] = subtype
    return payload


def effect(set_ptr: Dict[str, Any], to_script: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "effect_type": "Bounded Number Effect",
        "Set": {
            "script_element_type": "Pointer",
            "pointer_type": "Bounded Number Pointer",
            "character": set_ptr["character"],
            "keyring": list(set_ptr["keyring"]),
            "coefficient": 1.0,
        },
        "to": to_script,
    }


def string_const(value: str) -> Dict[str, Any]:
    return {
        "script_element_type": "Pointer",
        "pointer_type": "String Constant",
        "value": value,
    }


def collect_pointer_characters(node: Any, out: Set[str]) -> None:
    if isinstance(node, dict):
        if node.get("pointer_type") == "Bounded Number Pointer" and node.get("character"):
            out.add(str(node["character"]))
        for value in node.values():
            collect_pointer_characters(value, out)
        return
    if isinstance(node, list):
        for item in node:
            collect_pointer_characters(item, out)


def scene_characters(encounter: Dict[str, Any], fallback_chars: Sequence[str]) -> List[str]:
    chars: Set[str] = set()
    collect_pointer_characters(encounter, chars)
    if not chars:
        chars.update(fallback_chars[:2])
    ordered = [char_id for char_id in fallback_chars if char_id in chars]
    extras = sorted(char_id for char_id in chars if char_id not in ordered)
    return ordered + extras


def authored_scalar_keys(data: Dict[str, Any]) -> List[str]:
    keys: List[str] = []
    for prop in data.get("authored_properties", []) or []:
        prop_name = prop.get("property_name")
        if not isinstance(prop_name, str):
            continue
        if prop_name.startswith("p"):
            continue
        keys.append(prop_name)
    return keys or [
        "Influence",
        "Risk_Stasis",
        "Countercraft",
        "Transgression_Order",
        "Cohesion_Fragmentation",
        "Cosmic_Ambition_Humility",
    ]


def latent_key(key: str) -> str:
    return f"p{key}"


def encounter_act(encounter_index: int, total_encounters: int) -> int:
    ratio = (encounter_index + 1) / max(total_encounters, 1)
    if ratio <= 0.20:
        return 1
    if ratio <= 0.40:
        return 2
    if ratio <= 0.60:
        return 3
    if ratio <= 0.80:
        return 4
    return 5


def weighted_desirability(
    cast: Sequence[str],
    keys: Sequence[str],
    act: int,
    option_index: int,
    reaction_index: int,
) -> Dict[str, Any]:
    operands: List[Dict[str, Any]] = []
    for idx, char_id in enumerate(cast):
        key_a = keys[(option_index + reaction_index + idx) % len(keys)]
        key_b = keys[(option_index + reaction_index + idx + 2) % len(keys)]
        key_pa = latent_key(key_a)
        key_pb = latent_key(key_b)
        base_weight = max(0.18, 0.46 - idx * 0.08)
        if act >= 4 and idx == 0:
            base_weight += 0.06
        term = op(
            "Addition",
            [
                bn_ptr(char_id, key_a, round(base_weight, 3)),
                bn_ptr(char_id, key_b, round(max(0.10, base_weight * 0.6), 3)),
                bn_ptr(char_id, key_pa, round(max(0.08, base_weight * 0.45), 3)),
            ],
        )
        if act <= 3:
            term = op(
                "Arithmetic Mean",
                [
                    term,
                    bn_ptr(char_id, key_pb, 0.22),
                    bn_const(0.03 + reaction_index * 0.01),
                ],
            )
        else:
            term = op(
                "Addition",
                [
                    term,
                    op(
                        "Absolute Value",
                        [
                            op(
                                "Subtraction",
                                [
                                    bn_ptr(char_id, key_a),
                                    bn_ptr(char_id, key_b),
                                ],
                            )
                        ]
                    ),
                    op("Multiplication", [bn_ptr(char_id, key_pa), bn_const(0.42)]),
                ],
            )
        operands.append(term)
    if len(operands) == 1:
        return operands[0]
    return op("Addition", operands + [bn_const(0.02 * act)])


def reaction_effects(
    cast: Sequence[str],
    keys: Sequence[str],
    act: int,
    option_index: int,
    reaction_index: int,
) -> List[Dict[str, Any]]:
    effects: List[Dict[str, Any]] = []
    for idx, char_id in enumerate(cast[:3]):
        key_a = keys[(option_index + idx) % len(keys)]
        key_b = keys[(option_index + reaction_index + idx + 1) % len(keys)]
        key_pa = latent_key(key_a)
        ptr_a = bn_ptr(char_id, key_a)
        ptr_b = bn_ptr(char_id, key_b)
        ptr_pa = bn_ptr(char_id, key_pa)
        if act <= 3:
            if idx == 0:
                to_script = op("Addition", [ptr_a, op("Multiplication", [ptr_pa, bn_const(0.12)])])
            elif idx == 1:
                to_script = op("Arithmetic Mean", [ptr_a, ptr_b, ptr_pa])
            else:
                to_script = op("Nudge", [ptr_a, bn_const(0.02 + reaction_index * 0.01)])
        else:
            if idx == 0:
                to_script = op(
                    "Addition",
                    [
                        op("Multiplication", [ptr_a, bn_const(-0.82 if act == 4 else -0.95)]),
                        op("Multiplication", [ptr_pa, bn_const(0.18)]),
                    ],
                )
            elif idx == 1:
                to_script = op("Addition", [ptr_a, op("Multiplication", [ptr_b, bn_const(0.18)]), ptr_pa])
            else:
                to_script = op("Arithmetic Mean", [ptr_a, bn_const(0.12), ptr_b, ptr_pa])
        effects.append(effect(ptr_a, to_script))
    while len(effects) < 5:
        char_id = cast[len(effects) % len(cast)]
        key = keys[(option_index + reaction_index + len(effects)) % len(keys)]
        ptr = bn_ptr(char_id, key)
        ptr_latent = bn_ptr(char_id, latent_key(key))
        if act <= 3:
            if len(effects) % 2 == 0:
                to_script = op("Addition", [ptr, op("Multiplication", [ptr_latent, bn_const(0.09)])])
            else:
                to_script = op("Nudge", [ptr, bn_const(0.02)])
        else:
            if len(effects) % 2 == 0:
                to_script = op("Arithmetic Mean", [ptr, ptr_latent, bn_const(0.08)])
            else:
                to_script = op("Addition", [ptr, bn_const(0.05)])
        effects.append(effect(ptr, to_script))
    return effects


def ensure_text_trace(reaction: Dict[str, Any], cast: Sequence[str], act: int) -> None:
    text_script = reaction.get("text_script")
    if not isinstance(text_script, dict) or text_script.get("pointer_type") != "String Constant":
        reaction["text_script"] = string_const("")
        text_script = reaction["text_script"]
    cast_label = ", ".join(char_id.replace("char_", "") for char_id in cast[:3])
    text_script["value"] = (
        f"{text_script.get('value', '').strip()} "
        f"[act {act} weighting: {cast_label}; {'dramatic inversion' if act >= 4 else 'conservative nudge'}]"
    ).strip()


def next_version_path(input_path: Path) -> Path:
    stem = input_path.stem
    if "_v" in stem and stem.rsplit("_v", 1)[1].isdigit():
        prefix, version = stem.rsplit("_v", 1)
        next_version = int(version) + 1
        new_stem = f"{prefix}_v{next_version}"
    else:
        new_stem = f"{stem}_v2"
    return input_path.with_name(new_stem + input_path.suffix)


def rewrite_world(data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    out = json.loads(json.dumps(data))
    all_chars = [str(char.get("id")) for char in out.get("characters", []) or [] if char.get("id")]
    scalar_keys = authored_scalar_keys(out)
    encounters = out.get("encounters", []) or []
    rewritten_reactions = 0
    dramatic_reactions = 0
    per_act_counts = {str(i): 0 for i in range(1, 6)}
    for enc_index, encounter in enumerate(encounters):
        options = encounter.get("options", []) or []
        if not options:
            continue
        act = encounter_act(enc_index, len(encounters))
        cast = scene_characters(encounter, all_chars)
        for opt_index, option in enumerate(options):
            for rxn_index, reaction in enumerate(option.get("reactions", []) or []):
                reaction["desirability_script"] = weighted_desirability(cast, scalar_keys, act, opt_index, rxn_index)
                reaction["after_effects"] = reaction_effects(cast, scalar_keys, act, opt_index, rxn_index)
                ensure_text_trace(reaction, cast, act)
                rewritten_reactions += 1
                per_act_counts[str(act)] += 1
                if act >= 4:
                    dramatic_reactions += 1
    out["modified_time"] = float(time.time())
    report = {
        "storyworld_title": out.get("storyworld_title") or out.get("title"),
        "encounter_count": len(encounters),
        "rewritten_reactions": rewritten_reactions,
        "dramatic_reactions": dramatic_reactions,
        "acts": per_act_counts,
        "scalar_keys": scalar_keys,
        "character_ids": all_chars,
    }
    return out, report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Systematically rewrite desirability/effect formulas across a storyworld.")
    parser.add_argument("input_json")
    parser.add_argument("--out-json", default=None)
    parser.add_argument("--report-out", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input_json).resolve()
    data = json.loads(input_path.read_text(encoding="utf-8"))
    rewritten, report = rewrite_world(data)
    out_path = Path(args.out_json).resolve() if args.out_json else next_version_path(input_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(rewritten, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    report_path = Path(args.report_out).resolve() if args.report_out else out_path.with_suffix(".desirability_report.json")
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    print(out_path)
    print(report_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
