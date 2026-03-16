#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List


def sptr(value: str) -> Dict[str, Any]:
    return {"pointer_type": "String Constant", "script_element_type": "Pointer", "value": value}


def bconst(value: float) -> Dict[str, Any]:
    return {"pointer_type": "Bounded Number Constant", "script_element_type": "Pointer", "value": float(value)}


def bptr(character: str, prop: str, coefficient: float = 1.0) -> Dict[str, Any]:
    return {
        "pointer_type": "Bounded Number Pointer",
        "script_element_type": "Pointer",
        "character": character,
        "keyring": [prop],
        "coefficient": float(coefficient),
    }


def op(name: str, *operands: Dict[str, Any], subtype: str | None = None) -> Dict[str, Any]:
    out = {"script_element_type": "Operator", "operator_type": name, "operands": list(operands)}
    if subtype is not None:
        out["operator_subtype"] = subtype
    return out


def cmp_prop(character: str, prop: str, subtype: str, value: float) -> Dict[str, Any]:
    return op("Arithmetic Comparator", bptr(character, prop), bconst(value), subtype=subtype)


def nudge_effect(character: str, prop: str, amount: float) -> Dict[str, Any]:
    target = bptr(character, prop)
    return {
        "effect_type": "Bounded Number Effect",
        "Set": target,
        "to": op("Nudge", target, bconst(amount)),
    }


def profile_for_slug(slug: str) -> Dict[str, Any]:
    if slug == "the_usual_suspects":
        return {
            "title": "The Usual Suspects: Criminal Masterminds",
            "about": "A layered witness-box noir about criminal masterminds, false memory, and leverage.",
            "motif": "Every witness edits the room they swear they saw.",
            "theme_terms": ["lineup", "harbor", "burn", "testimony", "alias", "shipment"],
            "characters": [
                ("char_verbal", "Verbal Kint", "A fragile witness who may be constructing the whole room."),
                ("char_kujan", "Dave Kujan", "An investigator who needs the story to collapse into a culprit."),
                ("char_keaton", "Dean Keaton", "A former crooked cop who may be the cleanest liar in the room."),
                ("char_hockney", "Michael Hockney", "A gunman who treats stories as ammunition."),
                ("char_mcmanus", "Fred Fenster", "An unstable accomplice who leaks intent under pressure."),
            ],
            "props": ["Phase_Clock", "Suspicion", "Leverage", "Exposure", "Trust", "Violence", "Narrative_Control"],
            "css_theme": "noir",
        }
    return {
        "title": slug.replace("_", " ").title(),
        "about": "A fresh generated storyworld seed.",
        "motif": "Every scene leaves a measurable trace on the next choice.",
        "theme_terms": ["mask", "signal", "trace", "pressure", "turn", "witness"],
        "characters": [
            ("char_lead", "Lead", "The focal actor under pressure."),
            ("char_counterparty", "Counterparty", "The main opponent across the table."),
            ("char_witness", "Witness", "A witness who reshapes the narrative."),
        ],
        "props": ["Phase_Clock", "Suspicion", "Leverage", "Exposure", "Trust", "Risk", "Narrative_Control"],
        "css_theme": "lilac",
    }


def make_character(idx: int, ts: float, cid: str, name: str, desc: str, props: List[str]) -> Dict[str, Any]:
    return {
        "creation_index": idx,
        "creation_time": ts,
        "id": cid,
        "modified_time": ts,
        "name": name,
        "pronoun": "they",
        "description": desc,
        "bnumber_properties": {prop: 0 for prop in props},
        "string_properties": {},
        "list_properties": {},
    }


def make_property(idx: int, ts: float, prop: str) -> Dict[str, Any]:
    return {
        "id": prop,
        "property_name": prop,
        "property_type": "bounded number",
        "default_value": 0,
        "depth": 0,
        "attribution_target": "all cast members",
        "affected_characters": [],
        "creation_index": idx,
        "creation_time": ts,
        "modified_time": ts,
    }


def encounter_option(enc_id: str, opt_idx: int, actor: str, witness: str, prop_a: str, prop_b: str, next_hint: str, motif: str) -> Dict[str, Any]:
    option_id = f"opt_{enc_id}_{opt_idx}"
    reactions = []
    for rx_idx in range(2):
        rx_id = f"rxn_{enc_id}_{opt_idx}_{rx_idx}"
        desirability = op(
            "Addition",
            bptr(actor, prop_a),
            bptr(actor, prop_b, -0.55 if rx_idx else 0.35),
            bptr(witness, "Trust", 0.25),
            bconst(0.04 * (opt_idx + 1)),
        )
        effects = [
            nudge_effect(actor, "Phase_Clock", 0.08 + 0.01 * opt_idx),
            nudge_effect(actor, prop_a, 0.10 if rx_idx == 0 else -0.07),
            nudge_effect(actor, prop_b, -0.06 if rx_idx == 0 else 0.11),
            nudge_effect(witness, "Trust", 0.05 if rx_idx == 0 else -0.04),
        ]
        reactions.append(
            {
                "id": rx_id,
                "graph_offset_x": 0,
                "graph_offset_y": 0,
                "text_script": sptr(f"{motif} Option {opt_idx + 1} reaction {rx_idx + 1} leans toward {next_hint}."),
                "consequence_id": "wild",
                "desirability_script": desirability,
                "after_effects": effects,
            }
        )
    visibility = op(
        "Or",
        cmp_prop(actor, "Phase_Clock", "Less Than or Equal To", 0.92),
        cmp_prop(actor, prop_a, "Greater Than or Equal To", -0.6),
    )
    performability = op(
        "And",
        cmp_prop(actor, "Exposure", "Less Than or Equal To", 0.95),
        cmp_prop(actor, "Trust", "Greater Than or Equal To", -0.95),
    )
    labels = ["press harder", "hold back", "flip the room"]
    return {
        "id": option_id,
        "graph_offset_x": 0,
        "graph_offset_y": 0,
        "visibility_script": visibility,
        "performability_script": performability,
        "text_script": sptr(f"{labels[opt_idx]} on {next_hint}"),
        "reactions": reactions,
    }


def build_world(slug: str, out_path: Path, target_encounters: int, title: str, about: str, motif: str) -> Dict[str, Any]:
    profile = profile_for_slug(slug)
    ts = float(int(time.time()))
    props = profile["props"]
    chars = [make_character(i, ts, cid, name, desc, props) for i, (cid, name, desc) in enumerate(profile["characters"])]
    main_char = chars[0]["id"]
    witness = chars[1]["id"] if len(chars) > 1 else main_char
    authored_properties = [make_property(i, ts, prop) for i, prop in enumerate(props)]
    nonterminal_count = max(8, int(target_encounters))
    endings = 4
    theme_terms = profile["theme_terms"]

    spool_start = ["page_start"] + [f"page_scene_{i:02d}" for i in range(1, min(6, nonterminal_count))]
    spool_mid = [f"page_scene_{i:02d}" for i in range(min(6, nonterminal_count), min(15, nonterminal_count))]
    spool_end = [f"page_scene_{i:02d}" for i in range(min(15, nonterminal_count), nonterminal_count)]
    encounters: List[Dict[str, Any]] = []
    scene_ids = ["page_start"] + [f"page_scene_{i:02d}" for i in range(1, nonterminal_count)]
    scene_props = ["Suspicion", "Leverage", "Exposure", "Trust", "Violence", "Narrative_Control"]

    for idx, enc_id in enumerate(scene_ids):
        prop_a = scene_props[idx % len(scene_props)]
        prop_b = scene_props[(idx + 2) % len(scene_props)]
        theme = theme_terms[idx % len(theme_terms)]
        options = [
            encounter_option(enc_id, opt_idx, main_char, witness, prop_a, prop_b, theme, motif)
            for opt_idx in range(3)
        ]
        acceptability = True if enc_id == "page_start" else cmp_prop(main_char, "Phase_Clock", "Less Than or Equal To", 1.2)
        desirability = op("Addition", bptr(main_char, prop_a), bptr(main_char, "Narrative_Control", 0.4), bconst(idx * 0.01))
        connected_spools = []
        if enc_id in spool_start:
            connected_spools.append("spool_start_followup")
        if enc_id in spool_mid:
            connected_spools.append("spool_mid")
        if enc_id in spool_end:
            connected_spools.append("spool_penultimate")
        encounters.append(
            {
                "id": enc_id,
                "title": f"Scene {idx + 1}: {theme.title()}",
                "creation_index": idx,
                "creation_time": ts,
                "modified_time": ts,
                "connected_spools": connected_spools or ["spool_mid"],
                "earliest_turn": 0,
                "latest_turn": 0,
                "graph_position_x": idx * 160,
                "graph_position_y": 0,
                "text_script": sptr(f"{motif} The room tilts toward {theme}."),
                "acceptability_script": acceptability,
                "desirability_script": desirability,
                "options": options,
            }
        )

    for i in range(endings):
        end_id = f"page_end_{200 + i}"
        acceptability = cmp_prop(main_char, "Phase_Clock", "Greater Than or Equal To", 0.70)
        desirability = op(
            "Addition",
            bptr(main_char, scene_props[i % len(scene_props)], 0.8),
            bptr(main_char, scene_props[(i + 1) % len(scene_props)], -0.4),
            bconst(0.03 * i),
        )
        encounters.append(
            {
                "id": end_id,
                "title": f"Ending {i + 1}",
                "creation_index": nonterminal_count + i,
                "creation_time": ts,
                "modified_time": ts,
                "connected_spools": ["spool_endings"],
                "earliest_turn": 0,
                "latest_turn": 0,
                "graph_position_x": (nonterminal_count + i) * 160,
                "graph_position_y": 280,
                "text_script": sptr(f"{title} resolves into ending {i + 1}."),
                "acceptability_script": acceptability,
                "desirability_script": desirability,
                "options": [],
            }
        )

    world = {
        "IFID": f"SW-{uuid.uuid4()}",
        "storyworld_title": title or profile["title"],
        "storyworld_author": "Codex",
        "sweepweave_version": "0.1.9",
        "creation_time": ts,
        "modified_time": ts,
        "debug_mode": False,
        "display_mode": 1,
        "css_theme": profile["css_theme"],
        "font_size": "16",
        "language": "en",
        "rating": "general",
        "about_text": sptr(about or profile["about"]),
        "characters": chars,
        "authored_properties": authored_properties,
        "spools": [
            {
                "id": "spool_start_followup",
                "spool_name": "Start + Followup",
                "starts_active": True,
                "creation_index": 0,
                "creation_time": ts,
                "modified_time": ts,
                "encounters": spool_start,
            },
            {
                "id": "spool_mid",
                "spool_name": "Mid",
                "starts_active": True,
                "creation_index": 1,
                "creation_time": ts,
                "modified_time": ts,
                "encounters": spool_mid,
            },
            {
                "id": "spool_penultimate",
                "spool_name": "Penultimate",
                "starts_active": True,
                "creation_index": 2,
                "creation_time": ts,
                "modified_time": ts,
                "encounters": spool_end,
            },
            {
                "id": "spool_endings",
                "spool_name": "Endings",
                "starts_active": True,
                "creation_index": 3,
                "creation_time": ts,
                "modified_time": ts,
                "encounters": [f"page_end_{200 + i}" for i in range(endings)],
            },
        ],
        "encounters": encounters,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(world, ensure_ascii=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    return world


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a fresh valid storyworld seed for conveyor runs.")
    parser.add_argument("--slug", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--target-encounters", type=int, default=20)
    parser.add_argument("--title", required=True)
    parser.add_argument("--about", required=True)
    parser.add_argument("--motif", required=True)
    args = parser.parse_args()

    build_world(args.slug, Path(args.out).resolve(), args.target_encounters, args.title, args.about, args.motif)
    print(str(Path(args.out).resolve()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
