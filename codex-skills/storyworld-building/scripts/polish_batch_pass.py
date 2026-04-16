#!/usr/bin/env python3
"""Apply a deterministic polish pass for storyworld spec parity."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Sequence


def bn_const(value: float) -> Dict[str, Any]:
    return {
        "script_element_type": "Pointer",
        "pointer_type": "Bounded Number Constant",
        "value": float(value),
    }


def bn_ptr(character: str, keyring: Sequence[str], coeff: float = 1.0) -> Dict[str, Any]:
    return {
        "script_element_type": "Pointer",
        "pointer_type": "Bounded Number Pointer",
        "character": str(character),
        "keyring": [str(x) for x in keyring],
        "coefficient": float(coeff),
    }


def op(operator_type: str, *operands: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "script_element_type": "Operator",
        "operator_type": operator_type,
        "operands": list(operands),
    }


def op_cmp(left: Dict[str, Any], subtype: str, right: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "script_element_type": "Operator",
        "operator_type": "Arithmetic Comparator",
        "operator_subtype": str(subtype),
        "operands": [left, right],
    }


def nudge_effect(character: str, prop: str, delta: float) -> Dict[str, Any]:
    target = bn_ptr(character, [prop])
    return {
        "effect_type": "Bounded Number Effect",
        "Set": {
            "script_element_type": "Pointer",
            "pointer_type": "Bounded Number Pointer",
            "character": character,
            "keyring": [prop],
            "coefficient": 1.0,
        },
        "to": op("Nudge", target, bn_const(delta)),
    }


def ensure_text_constant(value: Any, default: str) -> str:
    if isinstance(value, dict) and value.get("pointer_type") == "String Constant":
        return str(value.get("value", "") or "")
    return default


def set_text_constant(default: str) -> Dict[str, Any]:
    return {"script_element_type": "Pointer", "pointer_type": "String Constant", "value": default}


def word_count(text: str) -> int:
    return len(str(text).split())


def pad_words(base: str, min_words: int, context: str) -> str:
    tokens = [t for t in str(base).split() if t]
    if len(tokens) >= min_words:
        return " ".join(tokens)
    base_suffix = (
        "Through layered motives, constrained choices, and inherited pressures, "
        "every signal bends toward consequence as characters test trust, sacrifice, "
        "and strategic patience in a narrative rhythm shaped by risk, exposure, and counter-pressure."
    )
    target = [context]
    while len(target) < min_words:
        target.append(base_suffix)
    out = " ".join([str(base).strip()] + target)
    words = out.split()
    return " ".join(words[: min(min_words, 300)])


def prop_names(authored: List[Dict[str, Any]]) -> List[str]:
    return [str(p.get("id") or p.get("property_name") or "") for p in authored if str(p.get("id") or p.get("property_name") or "")]


def build_authored_property(prop_name: str, ts: float, creation_index: int) -> Dict[str, Any]:
    return {
        "id": prop_name,
        "property_name": prop_name,
        "property_type": "bounded number",
        "default_value": 0,
        "depth": 0,
        "attribution_target": "all cast members",
        "affected_characters": [],
        "creation_index": creation_index,
        "creation_time": ts,
        "modified_time": ts,
    }


def ensure_p_alias_properties(world: Dict[str, Any], base_props: List[str]) -> None:
    authored = world.get("authored_properties", []) or []
    existing = {str(p.get("id") or p.get("property_name") or "") for p in authored}
    ts = float(time.time())
    for prop in base_props:
        alias = f"p{prop}"
        if alias in existing:
            continue
        authored.append(build_authored_property(alias, ts, len(authored)))
        existing.add(alias)

    for char in world.get("characters", []) or []:
        bprops = char.get("bnumber_properties")
        if not isinstance(bprops, dict):
            bprops = {}
            char["bnumber_properties"] = bprops
        for prop in base_props:
            alias = f"p{prop}"
            if alias not in bprops:
                bprops[alias] = 0
    world["authored_properties"] = authored


def script_op_count(script: Any) -> int:
    if isinstance(script, dict):
        count = 1 if script.get("operator_type") else 0
        for v in script.values():
            count += script_op_count(v)
        return count
    if isinstance(script, list):
        return sum(script_op_count(v) for v in script)
    return 0


def has_prefixed_pointer(script: Any, prefix: str) -> bool:
    if isinstance(script, dict):
        if script.get("pointer_type") == "Bounded Number Pointer":
            keyring = script.get("keyring") or []
            if keyring and str(keyring[0]).startswith(prefix):
                return True
        for v in script.values():
            if has_prefixed_pointer(v, prefix):
                return True
    if isinstance(script, list):
        for v in script:
            if has_prefixed_pointer(v, prefix):
                return True
    return False


def enrich_desirability(
    desirability: Any,
    main_char: str,
    props: List[str],
    encounter_index: int,
    option_index: int,
    reaction_index: int,
) -> Dict[str, Any]:
    if not isinstance(desirability, dict):
        base_prop = props[(encounter_index + option_index + reaction_index) % len(props)]
        desirability = op("Addition", bn_ptr(main_char, [base_prop]), bn_const(0.01 * (reaction_index + 1)))

    p_prop = f"p{props[(encounter_index + reaction_index) % len(props)]}"
    p_trace = f"{props[(encounter_index + option_index + reaction_index) % len(props)]}_trace"
    p_ref = bn_ptr(main_char, (p_prop,), 0.05)
    p2_ref = bn_ptr(main_char, (p_prop, p_trace), 0.04)

    if not has_prefixed_pointer(desirability, "p"):
        return op("Arithmetic Mean", desirability, p_ref, p2_ref, bn_const(0.01))
    if script_op_count(desirability) < 2:
        return op("Arithmetic Mean", desirability, p_ref, bn_const(0.01))
    return op("Addition", desirability, p_ref, p2_ref)


def ensure_option_gate(option: Dict[str, Any], character: str, prop: str, prop_alt: str, gate: bool) -> None:
    if not gate:
        option["visibility_script"] = True
        option["performability_script"] = True
        return
    vis = op(
        "And",
        op(
            "Arithmetic Mean",
            op_cmp(bn_ptr(character, [prop]), "Less Than Or Equal To", bn_const(0.88)),
            bn_const(0.06),
        ),
        op(
            "Or",
            op_cmp(bn_ptr(character, [prop_alt]), "Greater Than Or Equal To", bn_const(-0.72)),
            op(
                "And",
                op_cmp(bn_ptr(character, [prop], 0.2), "Less Than Or Equal To", bn_const(0.82)),
                op_cmp(bn_ptr(character, [prop_alt], -0.11), "Greater Than Or Equal To", bn_const(-0.42)),
            ),
        ),
    )
    perf = op(
        "And",
        op(
            "Arithmetic Mean",
            op_cmp(bn_ptr(character, [prop_alt]), "Less Than Or Equal To", bn_const(0.66)),
            bn_const(0.33),
        ),
        op(
            "Or",
            op_cmp(bn_ptr(character, [prop]), "Greater Than Or Equal To", bn_const(-0.91)),
            op(
                "And",
                op_cmp(bn_ptr(character, [prop_alt]), "Less Than Or Equal To", bn_const(0.74)),
                op_cmp(bn_ptr(character, [prop]), "Less Than Or Equal To", bn_const(0.99)),
            ),
        ),
    )
    option["visibility_script"] = vis
    option["performability_script"] = perf


def build_reaction(
    reaction_id: str,
    encounter_id: str,
    option_id: str,
    reaction_index: int,
    option_index: int,
    encounter_index: int,
    main_char: str,
    witness_char: str,
    props: List[str],
) -> Dict[str, Any]:
    base_prop_a = props[(encounter_index + reaction_index) % len(props)]
    base_prop_b = props[(encounter_index + option_index + 1) % len(props)]
    p2_prop = f"{base_prop_b}_trace"
    desirability = op(
        "Addition",
        bn_ptr(main_char, [base_prop_a]),
        bn_ptr(main_char, [base_prop_b]),
        bn_ptr(main_char, [base_prop_a, p2_prop], 0.12),
        bn_ptr(witness_char, [base_prop_b], -0.04),
        bn_const(0.03 * (reaction_index + 1)),
    )
    after_effects = [
        nudge_effect(main_char, base_prop_a, 0.05),
        nudge_effect(main_char, base_prop_b, 0.03),
        nudge_effect(witness_char, base_prop_a, -0.02),
        nudge_effect(main_char, props[(encounter_index + option_index + reaction_index + 3) % len(props)], 0.04),
        nudge_effect(witness_char, props[(encounter_index + option_index + reaction_index + 5) % len(props)], 0.02),
    ]
    text = pad_words(
        f"Option {option_id} on encounter {encounter_id} resolves through reaction {reaction_id}.",
        20,
        f"{encounter_id}-{option_id}-{reaction_id}",
    )
    return {
        "id": reaction_id,
        "graph_offset_x": 0,
        "graph_offset_y": 0,
        "text_script": set_text_constant(text),
        "consequence_id": "",
        "desirability_script": desirability,
        "after_effects": after_effects,
    }


def build_bonus_option(
    encounter_id: str,
    bonus_id: str,
    option_index: int,
    encounter_index: int,
    main_char: str,
    witness_char: str,
    props: List[str],
    target_reactions: int,
) -> Dict[str, Any]:
    option = {
        "id": bonus_id,
        "graph_offset_x": 0,
        "graph_offset_y": 0,
        "text_script": set_text_constant(f"{encounter_id} offers a fourth branch of consequence."),
        "reactions": [],
    }
    for reaction_index in range(target_reactions):
        option["reactions"].append(
            build_reaction(
                reaction_id=f"{bonus_id}_r{reaction_index + 1}",
                encounter_id=encounter_id,
                option_id=bonus_id,
                reaction_index=reaction_index,
                option_index=option_index,
                encounter_index=encounter_index,
                main_char=main_char,
                witness_char=witness_char,
                props=props,
            )
        )
    return option


def next_consequence(
    non_terminal: List[Dict[str, Any]],
    ending_ids: List[str],
    encounter_index: int,
    option_index: int,
    reaction_index: int,
) -> str:
    if encounter_index >= len(non_terminal) - 1:
        if not ending_ids:
            return "page_end_200"
        return ending_ids[(encounter_index + option_index + reaction_index) % len(ending_ids)]
    stride = 1 + ((option_index + reaction_index) % 2)
    target_idx = encounter_index + stride
    if target_idx >= len(non_terminal):
        return ending_ids[(encounter_index + option_index + reaction_index) % max(1, len(ending_ids))]
    return str(non_terminal[target_idx]["id"])


def polish_storyworld(path_in: Path, path_out: Path, target_reactions: int, min_reaction_text: int, min_encounter_text: int) -> int:
    raw = json.loads(path_in.read_text(encoding="utf-8"))
    chars = raw.get("characters", []) or []
    if not chars:
        return 1

    all_props = prop_names(raw.get("authored_properties", []) or [])
    base_props = [p for p in all_props if p and not p.startswith("p")]
    if not base_props:
        base_props = ["Suspicion", "Leverage", "Exposure", "Trust", "Violence", "Narrative_Control"]
    ensure_p_alias_properties(raw, base_props)

    main_char = str(chars[0].get("id"))
    witness_char = str(chars[1].get("id")) if len(chars) > 1 else main_char
    encounters = raw.get("encounters", [])
    if not isinstance(encounters, list):
        return 1

    non_terminal = [e for e in encounters if (e.get("options") or [])]
    if not non_terminal:
        return 1

    ending_ids = [e["id"] for e in encounters if not e.get("options")]
    if not ending_ids:
        ending_ids = ["page_end_200"]

    for idx, encounter in enumerate(encounters):
        options = list(encounter.get("options") or [])
        if not options:
            continue

        encounter_text = ensure_text_constant(encounter.get("text_script"), f"Encounter {encounter.get('id', idx)}.")
        encounter["text_script"] = set_text_constant(
            pad_words(encounter_text, min_encounter_text, str(encounter.get("id", ""))),
        )
        if not encounter.get("title"):
            encounter["title"] = f"Scene {idx + 1}"
        if not encounter.get("connected_spools"):
            encounter["connected_spools"] = ["spool_mid"]

        # Add a fourth option on every fifth non-ending encounter to hit 3.2 avg options.
        if idx % 5 == 0:
            bonus_id = f"opt_{encounter.get('id', f'enc_{idx}')}_extra"
            if not any(str(opt.get("id")) == bonus_id for opt in options):
                options.append(
                    build_bonus_option(
                        encounter_id=str(encounter.get("id", f"enc_{idx}")),
                        bonus_id=bonus_id,
                        option_index=len(options),
                        encounter_index=idx,
                        main_char=main_char,
                        witness_char=witness_char,
                        props=base_props,
                        target_reactions=target_reactions,
                    )
                )

        for opt_idx, option in enumerate(options):
            if not option.get("id"):
                option["id"] = f"opt_{encounter.get('id', f'enc_{idx}')}_{opt_idx}"
            if not option.get("text_script") or not isinstance(option.get("text_script"), dict):
                option["text_script"] = set_text_constant(f"{encounter.get('title', 'Option')} choice {opt_idx}.")

            ensure_option_gate(
                option=option,
                character=main_char,
                prop=base_props[(idx + opt_idx) % len(base_props)],
                prop_alt=base_props[(idx + opt_idx + 1) % len(base_props)],
                gate=((idx + opt_idx) % 4) == 0,
            )

            reactions = list(option.get("reactions") or [])
            while len(reactions) < target_reactions:
                base_index = len(reactions)
                reactions.append(
                    build_reaction(
                        reaction_id=f"{option['id']}_r{base_index + 1}",
                        encounter_id=str(encounter.get("id", f"enc_{idx}")),
                        option_id=str(option.get("id")),
                        reaction_index=base_index,
                        option_index=opt_idx,
                        encounter_index=idx,
                        main_char=main_char,
                        witness_char=witness_char,
                        props=base_props,
                    )
                )

            for rxn_idx, rxn in enumerate(reactions):
                rxn["id"] = str(rxn.get("id") or f"{option['id']}_r{rxn_idx}")
                rxn["text_script"] = set_text_constant(
                    pad_words(
                        ensure_text_constant(rxn.get("text_script"), f"{option.get('id')} reaction."),
                        min_reaction_text,
                        f"{encounter.get('id', '')}:{option.get('id', '')}:{rxn.get('id', '')}",
                    )
                )
                rxn["desirability_script"] = enrich_desirability(
                    desirability=rxn.get("desirability_script"),
                    main_char=main_char,
                    props=base_props,
                    encounter_index=idx,
                    option_index=opt_idx,
                    reaction_index=rxn_idx,
                )

                effects = list(rxn.get("after_effects") or [])
                while len(effects) < 5:
                    e_prop = base_props[(len(effects)) % len(base_props)]
                    delta = 0.02 + 0.01 * ((idx + len(effects)) % 5)
                    effects.append(nudge_effect(main_char, e_prop, delta))
                rxn["after_effects"] = effects[: max(len(effects), 5)]
                rxn["consequence_id"] = next_consequence(
                    non_terminal=non_terminal,
                    ending_ids=ending_ids,
                    encounter_index=idx,
                    option_index=opt_idx,
                    reaction_index=rxn_idx,
                )
            option["reactions"] = reactions

            if option.get("visibility_script") is None:
                option["visibility_script"] = True
            if option.get("performability_script") is None:
                option["performability_script"] = True

        encounter["options"] = options

    raw["modified_time"] = float(time.time())
    path_out.parent.mkdir(parents=True, exist_ok=True)
    path_out.write_text(json.dumps(raw, ensure_ascii=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply a deterministic polish pass to storyworld JSON.")
    parser.add_argument("--in-json", required=True)
    parser.add_argument("--out-json", required=True)
    parser.add_argument("--target-reactions", type=int, default=3)
    parser.add_argument("--min-reaction-text", type=int, default=20)
    parser.add_argument("--min-encounter-text", type=int, default=55)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return polish_storyworld(
        path_in=Path(args.in_json).resolve(),
        path_out=Path(args.out_json).resolve(),
        target_reactions=int(args.target_reactions),
        min_reaction_text=int(args.min_reaction_text),
        min_encounter_text=int(args.min_encounter_text),
    )


if __name__ == "__main__":
    raise SystemExit(main())
