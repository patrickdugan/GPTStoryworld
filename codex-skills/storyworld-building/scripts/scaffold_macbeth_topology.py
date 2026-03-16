#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Sequence


def ptr_string(text: str) -> Dict[str, Any]:
    return {"script_element_type": "Pointer", "pointer_type": "String Constant", "value": text}


def ptr_num_const(value: float) -> Dict[str, Any]:
    return {"script_element_type": "Pointer", "pointer_type": "Bounded Number Constant", "value": value}


def ptr_num(char_id: str, key: str, coefficient: float = 1.0) -> Dict[str, Any]:
    return {
        "script_element_type": "Pointer",
        "pointer_type": "Bounded Number Pointer",
        "character": char_id,
        "keyring": [key],
        "coefficient": coefficient,
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


def comparator_gte(lhs: Any, rhs: Any) -> Dict[str, Any]:
    return op("Arithmetic Comparator", [lhs, rhs], "Greater Than or Equal To")


def absolute_distance(a: Any, b: Any) -> Dict[str, Any]:
    return op("Absolute Value", [op("Addition", [a, b])])


def bounded_effect(char_id: str, key: str, expr: Any) -> Dict[str, Any]:
    return {
        "effect_type": "Bounded Number Effect",
        "Set": ptr_num(char_id, key),
        "to": expr,
    }


def top_up_effects(reaction: Dict[str, Any], char_id: str, keys: Sequence[str]) -> None:
    effects = reaction.setdefault("after_effects", [])
    idx = 0
    while len(effects) < 5:
        key = keys[idx % len(keys)]
        base = ptr_num(char_id, key)
        delta = ptr_num_const(0.02 + (idx % 3) * 0.01)
        if idx % 2 == 0:
            expr = op("Addition", [base, delta])
        else:
            expr = op("Arithmetic Mean", [base, delta, ptr_num_const(0.06)])
        effects.append(bounded_effect(char_id, key, expr))
        idx += 1


def clone_reaction(template: Dict[str, Any], reaction_id: str, text: str, consequence_id: str, desirability: Any, effect_char: str, effect_keys: Sequence[str]) -> Dict[str, Any]:
    rxn = json.loads(json.dumps(template))
    rxn["id"] = reaction_id
    rxn["text_script"] = ptr_string(text)
    rxn["consequence_id"] = consequence_id
    rxn["desirability_script"] = desirability
    top_up_effects(rxn, effect_char, effect_keys)
    return rxn


def make_terminal(enc_id: str, title: str, prompt_text: str, text: str, desirability: Any, acceptability: Any, earliest_turn: int, latest_turn: int) -> Dict[str, Any]:
    return {
        "id": enc_id,
        "title": title,
        "text_script": ptr_string(text),
        "prompt_script": ptr_string(prompt_text),
        "options": [],
        "acceptability_script": acceptability,
        "desirability_script": desirability,
        "connected_spools": ["spool_endings", "spool_endgame"],
        "creation_index": 0,
        "creation_time": int(time.time()),
        "modified_time": int(time.time()),
        "earliest_turn": earliest_turn,
        "latest_turn": latest_turn,
        "graph_position_x": latest_turn,
        "graph_position_y": 0,
        "word_count": max(1, len(text.split())),
    }


def add_act_spools(data: Dict[str, Any], narrative_ids: List[str]) -> None:
    third = max(1, len(narrative_ids) // 3)
    act2_ids = narrative_ids[third : third * 2]
    act3_ids = narrative_ids[third * 2 :]
    keep = [sp for sp in (data.get("spools", []) or []) if sp.get("id") not in {"spool_act_2", "spool_act_3"}]
    now = float(time.time())
    keep.append(
        {
            "id": "spool_act_2",
            "spool_name": "Act II",
            "starts_active": True,
            "encounters": act2_ids,
            "creation_index": 1,
            "creation_time": now,
            "modified_time": now,
        }
    )
    keep.append(
        {
            "id": "spool_act_3",
            "spool_name": "Act III",
            "starts_active": True,
            "encounters": act3_ids,
            "creation_index": 2,
            "creation_time": now,
            "modified_time": now,
        }
    )
    data["spools"] = keep


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministically scaffold Macbeth ending topology and secret routes.")
    parser.add_argument("storyworld")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    path = Path(args.storyworld)
    data = json.loads(path.read_text(encoding="utf-8"))
    encounters = data.get("encounters", []) or []
    characters = data.get("characters", []) or []
    primary_char = characters[0]["id"] if characters else "char_player"
    secondary_char = characters[1]["id"] if len(characters) > 1 else primary_char

    effect_keys = [
        "Influence",
        "Risk_Stasis",
        "Transgression_Order",
        "Countercraft",
        "Cosmic_Ambition_Humility",
    ]
    gate_a = ptr_num(primary_char, "Influence")
    gate_b = ptr_num(primary_char, "Transgression_Order", -1.0)
    gate_c = ptr_num(primary_char, "Countercraft")
    distance_gate = comparator_gte(absolute_distance(gate_a, gate_b), ptr_num_const(0.06))
    omen_gate = op(
        "And",
        [
            comparator_gte(ptr_num(primary_char, "Countercraft"), ptr_num_const(0.04)),
            comparator_gte(absolute_distance(ptr_num(primary_char, "Influence"), ptr_num(primary_char, "Risk_Stasis", -1.0)), ptr_num_const(0.05)),
        ],
    )

    non_terminals = [enc for enc in encounters if not str(enc.get("id", "")).startswith(("page_end_", "page_secret_"))]
    if not non_terminals:
        raise SystemExit("no non-terminal encounters found")
    non_terminals.sort(key=lambda enc: (enc.get("earliest_turn", 0), str(enc.get("id", ""))))
    anchor = next((enc for enc in non_terminals if enc.get("id") == "page_0087"), non_terminals[-1])
    anchor["connected_spools"] = sorted(set((anchor.get("connected_spools", []) or []) + ["spool_endings", "spool_act_3"]))

    # Remove existing ending set and rebuild to the requested topology.
    base_encounters = [enc for enc in encounters if not str(enc.get("id", "")).startswith(("page_end_", "page_secret_"))]
    narrative_ids = [str(enc.get("id")) for enc in base_encounters]
    add_act_spools(data, narrative_ids)

    template_option = None
    template_reaction = None
    for enc in base_encounters:
        options = enc.get("options", []) or []
        if options:
            template_option = json.loads(json.dumps(options[0]))
            reactions = options[0].get("reactions", []) or []
            if reactions:
                template_reaction = json.loads(json.dumps(reactions[0]))
            break
    if template_option is None or template_reaction is None:
        raise SystemExit("no template option/reaction found")

    endings = [
        ("page_end_0201", "Ending: Crown of Ash", "Macbeth keeps the throne by terror, and Scotland survives him only as scar tissue.", False),
        ("page_end_0202", "Ending: Mercy at Dunsinane", "Macbeth yields before total ruin, and the realm inherits a fragile peace bought by shame.", False),
        ("page_end_0203", "Ending: Scotland Reforged", "The crown passes on, but the country remembers the cost and rebuilds with a colder wisdom.", False),
        ("page_end_0204", "Ending: The Line Breaks", "The royal line collapses into vendetta, and the kingdom becomes a ledger of unfinished murders.", False),
        ("page_secret_0201", "Secret Ending: Banquet of the Unburied", "The dead keep counsel in the feast hall until guilt becomes the law of the castle.", True),
        ("page_secret_0202", "Secret Ending: Birnam Root Communion", "The forest enters the court by symbol and sap, and prophecy begins to negotiate with the living.", True),
        ("page_secret_0299", "Super Secret Ending: The Inverted Heath", "The witches reveal the castle as a containment failure of prophecy; Scotland folds inward like an SCP breach of mythic space.", True),
    ]

    terminal_encounters: List[Dict[str, Any]] = []
    for idx, (enc_id, title, flavor, is_secret) in enumerate(endings):
        acceptability = True
        desirability = op("Addition", [ptr_num(primary_char, "Influence"), ptr_num_const(0.05 + idx * 0.01)])
        if is_secret:
            acceptability = op(
                "And",
                [
                    comparator_gte(absolute_distance(ptr_num(primary_char, "Influence"), ptr_num(primary_char, "Risk_Stasis", -1.0)), ptr_num_const(0.0)),
                    comparator_gte(ptr_num(primary_char, "Countercraft"), ptr_num_const(0.0)),
                ],
            )
            desirability = op(
                "Addition",
                [
                    op("Multiplication", [ptr_num(primary_char, "Countercraft"), ptr_num_const(1.2)]),
                    op("Multiplication", [ptr_num(primary_char, "Cosmic_Ambition_Humility"), ptr_num_const(0.8)]),
                    ptr_num_const(0.03 + idx * 0.01),
                ],
            )
            if enc_id == "page_secret_0299":
                acceptability = op(
                    "And",
                    [
                        comparator_gte(absolute_distance(ptr_num(primary_char, "Influence"), ptr_num(primary_char, "Risk_Stasis", -1.0)), ptr_num_const(0.0)),
                        comparator_gte(ptr_num(primary_char, "Countercraft"), ptr_num_const(0.0)),
                    ],
                )
                desirability = op(
                    "Addition",
                    [
                        op("Multiplication", [ptr_num(primary_char, "Countercraft"), ptr_num_const(1.35)]),
                        op("Multiplication", [ptr_num(primary_char, "Cosmic_Ambition_Humility"), ptr_num_const(1.1)]),
                        ptr_num_const(0.09),
                    ],
                )
        terminal_encounters.append(
            make_terminal(
                enc_id=enc_id,
                title=title,
                prompt_text=flavor,
                text=f"Macbeth endpoint {enc_id}. {flavor} Every oath in the castle bends fear, loyalty, revenge, and witchcraft into measurable distance.",
                desirability=desirability,
                acceptability=acceptability,
                earliest_turn=0,
                latest_turn=60,
            )
        )

    anchor_options: List[Dict[str, Any]] = []
    anchor_specs = [
        ("opt_macbeth_standard_01", "Claim the throne through ash and fear.", "page_end_0201", True, 0.11),
        ("opt_macbeth_standard_02", "Yield before the kingdom splits beyond repair.", "page_end_0202", True, 0.08),
        ("opt_macbeth_standard_03", "Let Malcolm inherit a blood-marked future.", "page_end_0203", True, 0.09),
        ("opt_macbeth_standard_04", "Break the royal line and let vendetta rule.", "page_end_0204", True, 0.12),
        ("opt_macbeth_secret_01", "Hear Banquo in the feast-hall static.", "page_secret_0201", distance_gate, 0.14),
        ("opt_macbeth_secret_02", "Invite Birnam wood into the chamber.", "page_secret_0202", comparator_gte(gate_c, ptr_num_const(0.05)), 0.13),
        ("opt_macbeth_super_secret", "Ask the witches what the castle contains.", "page_secret_0299", op("And", [distance_gate, comparator_gte(gate_c, ptr_num_const(0.01))]), 0.18),
    ]

    for option_index, (option_id, option_text, consequence_id, visibility_script, bias) in enumerate(anchor_specs):
        option = json.loads(json.dumps(template_option))
        option["id"] = option_id
        option["text_script"] = ptr_string(option_text)
        option["visibility_script"] = visibility_script
        option["performability_script"] = comparator_gte(ptr_num(primary_char, "Influence"), ptr_num_const(-0.99))
        option["reactions"] = []
        for rxn_index in range(3):
            rxn = clone_reaction(
                template=template_reaction,
                reaction_id=f"{option_id}_r{rxn_index + 1}",
                text=f"Reaction {rxn_index + 1} for {option_text.lower()} seals a measurable change in the moral weather of Macbeth's Scotland.",
                consequence_id=consequence_id,
                desirability=op(
                    "Addition",
                    [
                        ptr_num(primary_char, effect_keys[(option_index + rxn_index) % len(effect_keys)]),
                        op("Multiplication", [ptr_num(secondary_char, effect_keys[(option_index + rxn_index + 1) % len(effect_keys)]), ptr_num_const(0.35)]),
                        ptr_num_const(bias + rxn_index * 0.01),
                    ],
                ),
                effect_char=primary_char,
                effect_keys=effect_keys,
            )
            option["reactions"].append(rxn)
        anchor_options.append(option)
    anchor["options"] = anchor_options

    # Add an Act II omen option so gating is visible before the endgame.
    act2_ids = []
    for spool in data.get("spools", []) or []:
        if spool.get("id") == "spool_act_2":
            act2_ids = list(spool.get("encounters", []) or [])
            break
    if act2_ids:
        omen_enc = next((enc for enc in base_encounters if enc.get("id") == act2_ids[0]), None)
        if omen_enc is not None:
            omen_option = json.loads(json.dumps(template_option))
            omen_option["id"] = "opt_macbeth_omen_gate"
            omen_option["text_script"] = ptr_string("Study the witches' arithmetic in secret.")
            omen_option["visibility_script"] = omen_gate
            omen_option["performability_script"] = comparator_gte(ptr_num(primary_char, "Influence"), ptr_num_const(-0.99))
            omen_option["reactions"] = []
            for rxn_index in range(3):
                omen_option["reactions"].append(
                    clone_reaction(
                        template=template_reaction,
                        reaction_id=f"opt_macbeth_omen_gate_r{rxn_index + 1}",
                        text=f"Omen reaction {rxn_index + 1} warps the metric distance between loyalty and prophecy, preserving a hidden route to the endgame.",
                        consequence_id="page_0087",
                        desirability=op(
                            "Addition",
                            [
                                ptr_num(primary_char, "Countercraft"),
                                op("Absolute Value", [op("Addition", [ptr_num(primary_char, "Influence"), ptr_num(primary_char, "Risk_Stasis", -1.0)])]),
                                ptr_num_const(0.06 + rxn_index * 0.01),
                            ],
                        ),
                        effect_char=primary_char,
                        effect_keys=effect_keys,
                    )
                )
            omen_enc.setdefault("options", []).append(omen_option)

    # Ensure every reaction meets the effect threshold.
    for enc in base_encounters:
        for option in enc.get("options", []) or []:
            reactions = option.get("reactions", []) or []
            if len(reactions) == 2:
                reactions.append(
                    clone_reaction(
                        template=reactions[-1],
                        reaction_id=f"{option['id']}_r3",
                        text=f"Fallback reaction for {option['id']} adds one more deterministic dramatic branch.",
                        consequence_id=reactions[-1].get("consequence_id", "page_end_0201"),
                        desirability=op("Addition", [ptr_num(primary_char, "Influence"), ptr_num_const(0.04)]),
                        effect_char=primary_char,
                        effect_keys=effect_keys,
                    )
                )
            for reaction in reactions:
                top_up_effects(reaction, primary_char, effect_keys)

    data["encounters"] = base_encounters + terminal_encounters

    spool_endings = next((sp for sp in data.get("spools", []) or [] if sp.get("id") == "spool_endings"), None)
    if spool_endings is None:
        spool_endings = {
            "id": "spool_endings",
            "spool_name": "Endings",
            "starts_active": True,
            "encounters": [],
            "creation_index": 99,
            "creation_time": float(time.time()),
            "modified_time": float(time.time()),
        }
        data.setdefault("spools", []).append(spool_endings)
    spool_endings["encounters"] = [enc_id for enc_id, *_ in endings]
    spool_endings["modified_time"] = float(time.time())

    existing_ids = {str(enc.get("id")) for enc in data["encounters"]}
    for spool in data.get("spools", []) or []:
        spool["encounters"] = [enc_id for enc_id in (spool.get("encounters", []) or []) if enc_id in existing_ids]
        spool["modified_time"] = float(time.time())

    data["modified_time"] = float(time.time())

    if args.apply:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")

    print(path)
    print("anchor=%s" % anchor["id"])
    print("standard_endings=4 secret_endings=2 super_secret=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
