#!/usr/bin/env python3
"""Lightweight structural/artistry upgrader for existing storyworld JSON."""

from __future__ import annotations

import argparse
import copy
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Set


def _word_count(script: Any) -> int:
    if isinstance(script, dict):
        if script.get("pointer_type") == "String Constant":
            return len(str(script.get("value", "")).split())
        return sum(_word_count(v) for v in script.values())
    if isinstance(script, list):
        return sum(_word_count(v) for v in script)
    if isinstance(script, str):
        return len(script.split())
    return 0


def _ensure_string_constant(script: Any, fallback: str) -> Dict[str, Any]:
    if isinstance(script, dict) and script.get("pointer_type") == "String Constant":
        return script
    return {
        "script_element_type": "Pointer",
        "pointer_type": "String Constant",
        "value": fallback,
    }


def _expand_text(script: Any, min_words: int, addendum: str) -> Dict[str, Any]:
    out = _ensure_string_constant(script, addendum)
    base = str(out.get("value", "")).strip()
    if _word_count(out) < min_words and addendum not in base:
        base = str(out.get("value", "")).strip()
        out["value"] = (base + " " + addendum).strip()
    return out


def _dedupe_sentences(text: str) -> str:
    parts = [p.strip() for p in text.replace("\n", " ").split(".") if p.strip()]
    seen = set()
    kept = []
    for p in parts:
        key = p.lower()
        if key in seen:
            continue
        seen.add(key)
        kept.append(p)
    return ". ".join(kept).strip() + ("." if kept else "")


def _shorten_to_words(text: str, max_words: int) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text.strip()
    return " ".join(words[:max_words]).strip() + "..."


def _constant(value: float) -> Dict[str, Any]:
    return {
        "script_element_type": "Pointer",
        "pointer_type": "Bounded Number Constant",
        "value": float(value),
    }


def _pointer(character: str, keyring: List[str]) -> Dict[str, Any]:
    return {
        "script_element_type": "Pointer",
        "pointer_type": "Bounded Number Pointer",
        "character": character,
        "keyring": keyring,
        "coefficient": 1.0,
    }


def _nudge_effect(character: str, keyring: List[str], delta: float) -> Dict[str, Any]:
    ptr = _pointer(character, keyring)
    return {
        "effect_type": "Bounded Number Effect",
        "Set": copy.deepcopy(ptr),
        "to": {
            "script_element_type": "Operator",
            "operator_type": "Nudge",
            "operands": [copy.deepcopy(ptr), _constant(delta)],
        },
    }


def _ensure_desirability(
    desirability: Any,
    main_char: str,
    base_prop: str,
    p_prop: str,
    witness: str,
) -> Dict[str, Any]:
    if isinstance(desirability, dict) and desirability.get("operator_type"):
        return desirability
    # Convert constant-only scoring into a small, variable-aware blend.
    base_const = desirability if isinstance(desirability, dict) else _constant(0.5)
    if not (isinstance(base_const, dict) and base_const.get("pointer_type") == "Bounded Number Constant"):
        base_const = _constant(0.5)
    return {
        "script_element_type": "Operator",
        "operator_type": "Arithmetic Mean",
        "operands": [
            base_const,
            _pointer(main_char, [base_prop]),
            _pointer(main_char, [p_prop]),
            _pointer(main_char, [p_prop, witness]),  # p2-like keyring depth
        ],
    }


def _unique_id(existing: Set[str], seed: str) -> str:
    if seed not in existing:
        existing.add(seed)
        return seed
    i = 2
    while f"{seed}_{i}" in existing:
        i += 1
    out = f"{seed}_{i}"
    existing.add(out)
    return out


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Upgrade a storyworld to denser v-next style.")
    p.add_argument("--in-json", required=True, help="Input storyworld JSON")
    p.add_argument("--out-json", required=True, help="Output storyworld JSON")
    p.add_argument("--suffix", default="v2", help="Suffix for title/version note")
    p.add_argument("--min-options", type=int, default=3)
    p.add_argument("--min-reactions", type=int, default=2)
    p.add_argument("--min-effects", type=int, default=4)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    in_path = Path(args.in_json).resolve()
    out_path = Path(args.out_json).resolve()

    data = json.loads(in_path.read_text(encoding="utf-8"))
    encounters: List[Dict[str, Any]] = data.get("encounters", [])
    chars = data.get("characters", [])
    main_char = chars[0]["id"] if chars else "char_civ"
    witness = chars[1]["id"] if len(chars) > 1 else main_char

    prop_names = [p.get("property_name") for p in data.get("authored_properties", []) if p.get("property_name")]
    base_props = [p for p in prop_names if not p.startswith("p")] or ["Influence"]
    p_props = [p for p in prop_names if p.startswith("p")] or ["pInfluence"]
    base_prop = base_props[0]
    p_prop = p_props[0]

    option_ids: Set[str] = set()
    reaction_ids: Set[str] = set()
    for enc in encounters:
        for opt in enc.get("options", []) or []:
            if opt.get("id"):
                option_ids.add(opt["id"])
            for rxn in opt.get("reactions", []) or []:
                if rxn.get("id"):
                    reaction_ids.add(rxn["id"])

    encounter_addendum = (
        "Across this age, the civilizational wager is refracted through memory, scarcity, and ambition; "
        "every institutional move recasts trust, resentment, and the archive of prior catastrophes."
    )
    reaction_addendum = (
        "The move carries immediate tactical gain but seeds second-order expectations, altering who trusts "
        "whom, who anticipates betrayal, and which coalition geometry remains stable next turn."
    )

    for enc in encounters:
        enc["text_script"] = _expand_text(enc.get("text_script"), 50, encounter_addendum)
        options = enc.get("options", []) or []
        if not options:
            continue

        while len(options) < args.min_options:
            template = copy.deepcopy(options[len(options) % len(options)])
            new_opt_id = _unique_id(option_ids, f"{enc.get('id','enc')}_{args.suffix}_opt{len(options)+1}")
            template["id"] = new_opt_id
            text_script = _ensure_string_constant(template.get("text_script"), "Pursue the heterodox civilizational wager.")
            base_text = _shorten_to_words(str(text_script.get("value", "")).strip(), 12)
            text_script["value"] = f"Branch {len(options)+1}: {base_text}".strip()
            template["text_script"] = text_script
            options.append(template)
        enc["options"] = options

        for opt in options:
            if isinstance(opt.get("text_script"), dict) and opt["text_script"].get("pointer_type") == "String Constant":
                orig = str(opt["text_script"].get("value", "")).strip()
                short = _shorten_to_words(orig, 14)
                if short and short[-1] not in ".!?":
                    short += "."
                opt["text_script"]["value"] = short
            reactions = opt.get("reactions", []) or []
            if not reactions:
                reactions = [
                    {
                        "id": _unique_id(reaction_ids, f"{opt.get('id','opt')}_{args.suffix}_rxn1"),
                        "text_script": _ensure_string_constant(None, "The chamber acknowledges the maneuver and recalculates."),
                        "desirability_script": _constant(0.5),
                        "consequence_id": enc.get("id", "wild"),
                        "after_effects": [_nudge_effect(main_char, [base_prop], 0.02)],
                    }
                ]

            while len(reactions) < args.min_reactions:
                template = copy.deepcopy(reactions[len(reactions) % len(reactions)])
                template["id"] = _unique_id(reaction_ids, f"{opt.get('id','opt')}_{args.suffix}_rxn{len(reactions)+1}")
                ts = _ensure_string_constant(template.get("text_script"), "A rival interpretation emerges from the same event.")
                ts["value"] = (str(ts.get("value", "")).strip() + " A counter-reading circulates through elite rumor networks.").strip()
                template["text_script"] = ts
                reactions.append(template)

            for rxn in reactions:
                rxn["desirability_script"] = _ensure_desirability(
                    rxn.get("desirability_script"),
                    main_char=main_char,
                    base_prop=base_prop,
                    p_prop=p_prop,
                    witness=witness,
                )
                rxn["text_script"] = _expand_text(rxn.get("text_script"), 20, reaction_addendum)
                effects = rxn.get("after_effects", []) or []
                while len(effects) < args.min_effects:
                    slot = len(effects)
                    if slot % 3 == 0:
                        effects.append(_nudge_effect(main_char, [base_prop], 0.015))
                    elif slot % 3 == 1:
                        effects.append(_nudge_effect(main_char, [p_prop], 0.02))
                    else:
                        effects.append(_nudge_effect(main_char, [p_prop, witness], -0.01))
                rxn["after_effects"] = effects
            opt["reactions"] = reactions

    title = str(data.get("title", "Storyworld")).strip()
    if args.suffix.lower() not in title.lower():
        data["title"] = f"{title} ({args.suffix.upper()})"
    for enc in encounters:
        if isinstance(enc.get("text_script"), dict) and enc["text_script"].get("pointer_type") == "String Constant":
            enc["text_script"]["value"] = _dedupe_sentences(str(enc["text_script"].get("value", "")))
    data["modified_time"] = float(time.time())

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
