#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "codex-skills" / "storyworld-building" / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from sweepweave_validator import validate_storyworld  # type: ignore


OUT_DIR = ROOT / "storyworlds" / "3-3-2026-machine-native-shear-batch-v1"
REPORT_DIR = OUT_DIR / "_reports"

PHASE = "Phase_Clock"
PROPS = [
    PHASE,
    "Signal_Noise",
    "Mask_Reveal",
    "Yield_Override",
    "Sync_Drift",
    "Heat_Resolve",
]


def string_ptr(value: str) -> Dict[str, Any]:
    return {"pointer_type": "String Constant", "script_element_type": "Pointer", "value": value}


def bconst(value: float) -> Dict[str, Any]:
    return {"pointer_type": "Bounded Number Constant", "script_element_type": "Pointer", "value": value}


def bptr(prop: str, *, char: str = "char_kernel", coefficient: float = 1.0) -> Dict[str, Any]:
    return {
        "pointer_type": "Bounded Number Pointer",
        "script_element_type": "Pointer",
        "character": char,
        "keyring": [prop],
        "coefficient": coefficient,
    }


def add(*operands: Dict[str, Any]) -> Dict[str, Any]:
    return {"script_element_type": "Operator", "operator_type": "Addition", "operands": list(operands)}


def compare(
    prop: str,
    subtype: str,
    value: float,
    *,
    char: str = "char_kernel",
    coefficient: float = 1.0,
) -> Dict[str, Any]:
    return {
        "script_element_type": "Operator",
        "operator_type": "Arithmetic Comparator",
        "operator_subtype": subtype,
        "operands": [bptr(prop, char=char, coefficient=coefficient), bconst(value)],
    }


def between(prop: str, low: float, high: float) -> Dict[str, Any]:
    return {
        "script_element_type": "Operator",
        "operator_type": "And",
        "operands": [
            compare(prop, "Greater Than or Equal To", low),
            compare(prop, "Less Than or Equal To", high),
        ],
    }


def and_(*operands: Dict[str, Any]) -> Dict[str, Any]:
    return {"script_element_type": "Operator", "operator_type": "And", "operands": list(operands)}


def nudge_effect(prop: str, amount: float, *, char: str = "char_kernel") -> Dict[str, Any]:
    return {
        "effect_type": "Bounded Number Effect",
        "Set": bptr(prop, char=char),
        "to": {"script_element_type": "Operator", "operator_type": "Nudge", "operands": [bptr(prop, char=char), bconst(amount)]},
    }


def make_property(idx: int, prop: str, created_at: float) -> Dict[str, Any]:
    return {
        "id": prop,
        "property_name": prop,
        "property_type": "bounded number",
        "default_value": 0,
        "depth": 0,
        "attribution_target": "all cast members",
        "affected_characters": [],
        "creation_index": idx,
        "creation_time": created_at,
        "modified_time": created_at,
    }


def make_character(idx: int, char_id: str, name: str, desc: str, created_at: float) -> Dict[str, Any]:
    return {
        "creation_index": idx,
        "creation_time": created_at,
        "id": char_id,
        "modified_time": created_at,
        "name": name,
        "pronoun": "they",
        "description": desc,
        "bnumber_properties": {prop: 0 for prop in PROPS},
        "string_properties": {},
        "list_properties": {},
    }


def stage_gate(stage: str, extra: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    if stage == "act1":
        phase_gate = compare(PHASE, "Less Than or Equal To", 0.30)
    elif stage == "act2":
        phase_gate = between(PHASE, 0.31, 0.68)
    elif stage == "act3":
        phase_gate = between(PHASE, 0.69, 0.92)
    else:
        phase_gate = compare(PHASE, "Greater Than or Equal To", 0.91)
    return and_(phase_gate, *extra) if extra else phase_gate


def main_desirability(primary: str, secondary: str, bias: float, *, invert_primary: bool = False) -> Dict[str, Any]:
    coef = -1.0 if invert_primary else 1.0
    return add(bptr(primary, coefficient=coef), bptr(secondary), bconst(bias))


def reaction_script(primary: str, secondary: str, bias: float, *, invert_secondary: bool = False) -> Dict[str, Any]:
    coef = -1.0 if invert_secondary else 1.0
    return add(bptr(primary), bptr(secondary, coefficient=coef), bconst(bias))


def make_reaction(rxn_id: str, text: str, consequence_id: str, desirability: Dict[str, Any], effects: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "id": rxn_id,
        "graph_offset_x": 0,
        "graph_offset_y": 0,
        "text_script": string_ptr(text),
        "consequence_id": consequence_id,
        "desirability_script": desirability,
        "after_effects": list(effects),
    }


def make_option(opt_id: str, text: str, visibility: Dict[str, Any] | bool, performability: Dict[str, Any] | bool, reactions: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "id": opt_id,
        "graph_offset_x": 0,
        "graph_offset_y": 0,
        "visibility_script": visibility,
        "performability_script": performability,
        "text_script": string_ptr(text),
        "reactions": list(reactions),
    }


def make_encounter(
    idx: int,
    enc_id: str,
    title: str,
    text: str,
    spool_id: str,
    acceptability: Dict[str, Any] | bool,
    desirability: Dict[str, Any],
    options: Sequence[Dict[str, Any]],
) -> Dict[str, Any]:
    return {
        "id": enc_id,
        "title": title,
        "creation_index": idx,
        "creation_time": BASE_TS,
        "modified_time": BASE_TS,
        "connected_spools": [spool_id],
        "earliest_turn": 0,
        "latest_turn": 0,
        "graph_position_x": idx * 160,
        "graph_position_y": 0,
        "text_script": string_ptr(text),
        "acceptability_script": acceptability,
        "desirability_script": desirability,
        "options": list(options),
    }


def start_options(spec: Dict[str, str]) -> List[Dict[str, Any]]:
    return [
        make_option(
            "opt_page_start_0",
            spec["start_opt_a"],
            True,
            True,
            [
                make_reaction(
                    "rxn_page_start_0_a",
                    spec["start_rxn_a"],
                    "wild",
                    reaction_script("Signal_Noise", "Heat_Resolve", 0.08),
                    [
                        nudge_effect("Signal_Noise", -0.28),
                        nudge_effect("Heat_Resolve", 0.16),
                        nudge_effect("Mask_Reveal", -0.08),
                        nudge_effect("Sync_Drift", -0.06),
                    ],
                ),
                make_reaction(
                    "rxn_page_start_0_b",
                    spec["start_rxn_b"],
                    "wild",
                    reaction_script("Yield_Override", "Signal_Noise", 0.04, invert_secondary=True),
                    [
                        nudge_effect("Yield_Override", 0.14),
                        nudge_effect("Signal_Noise", -0.18),
                        nudge_effect("Heat_Resolve", 0.08),
                        nudge_effect("Sync_Drift", 0.04),
                    ],
                ),
            ],
        ),
        make_option(
            "opt_page_start_1",
            spec["start_opt_b"],
            True,
            True,
            [
                make_reaction(
                    "rxn_page_start_1_a",
                    spec["start_rxn_c"],
                    "wild",
                    reaction_script("Mask_Reveal", "Sync_Drift", 0.07),
                    [
                        nudge_effect("Mask_Reveal", 0.24),
                        nudge_effect("Sync_Drift", 0.18),
                        nudge_effect("Signal_Noise", 0.04),
                        nudge_effect("Heat_Resolve", -0.04),
                    ],
                ),
                make_reaction(
                    "rxn_page_start_1_b",
                    spec["start_rxn_d"],
                    "wild",
                    reaction_script("Sync_Drift", "Yield_Override", 0.03),
                    [
                        nudge_effect("Sync_Drift", 0.24),
                        nudge_effect("Mask_Reveal", 0.14),
                        nudge_effect("Yield_Override", -0.06),
                        nudge_effect("Signal_Noise", 0.08),
                    ],
                ),
            ],
        ),
    ]


def act_options(enc_id: str, router_id: str, stage: str, primary: str, secondary: str, labels: Tuple[str, str]) -> List[Dict[str, Any]]:
    gate_a = compare(primary, "Less Than or Equal To", 0.55) if primary != "Yield_Override" else True
    gate_b = compare(secondary, "Greater Than or Equal To", -0.45)
    return [
        make_option(
            f"opt_{enc_id}_0",
            labels[0],
            gate_a,
            compare("Heat_Resolve", "Greater Than or Equal To", -0.75),
            [
                make_reaction(
                    f"rxn_{enc_id}_0_a",
                    f"{stage}: route biases {primary.lower()}; ledger records gain.",
                    router_id,
                    reaction_script(primary, secondary, 0.06),
                    [
                        nudge_effect(primary, 0.18),
                        nudge_effect(secondary, -0.12),
                        nudge_effect("Heat_Resolve", 0.10),
                        nudge_effect("Yield_Override", 0.04),
                    ],
                ),
                make_reaction(
                    f"rxn_{enc_id}_0_b",
                    f"{stage}: route hardens; seam logged.",
                    router_id,
                    reaction_script(primary, "Mask_Reveal", 0.02),
                    [
                        nudge_effect(primary, 0.12),
                        nudge_effect("Mask_Reveal", 0.16),
                        nudge_effect("Heat_Resolve", -0.06),
                        nudge_effect("Signal_Noise", -0.08),
                    ],
                ),
            ],
        ),
        make_option(
            f"opt_{enc_id}_1",
            labels[1],
            gate_b,
            compare("Yield_Override", "Less Than or Equal To", 0.82),
            [
                make_reaction(
                    f"rxn_{enc_id}_1_a",
                    f"{stage}: shear favors {secondary.lower()}; authority diffuses.",
                    router_id,
                    reaction_script(secondary, primary, 0.05),
                    [
                        nudge_effect(secondary, 0.20),
                        nudge_effect(primary, -0.10),
                        nudge_effect("Signal_Noise", 0.06),
                        nudge_effect("Sync_Drift", 0.08),
                    ],
                ),
                make_reaction(
                    f"rxn_{enc_id}_1_b",
                    f"{stage}: variance kept; basin count preserved.",
                    router_id,
                    reaction_script(secondary, "Heat_Resolve", 0.01, invert_secondary=True),
                    [
                        nudge_effect(secondary, 0.12),
                        nudge_effect("Heat_Resolve", 0.10),
                        nudge_effect("Mask_Reveal", 0.08),
                        nudge_effect("Yield_Override", -0.08),
                    ],
                ),
            ],
        ),
    ]


def router_options(router_id: str, labels: Tuple[str, str], phase_nudge: float) -> List[Dict[str, Any]]:
    return [
        make_option(
            f"opt_{router_id}_0",
            labels[0],
            compare("Signal_Noise", "Less Than or Equal To", 0.48),
            True,
            [
                make_reaction(
                    f"rxn_{router_id}_0_a",
                    "sched takes cold route; ledger recomputes eligibility.",
                    "wild",
                    reaction_script("Signal_Noise", "Heat_Resolve", 0.05, invert_secondary=True),
                    [
                        nudge_effect(PHASE, phase_nudge),
                        nudge_effect("Signal_Noise", -0.16),
                        nudge_effect("Heat_Resolve", 0.10),
                        nudge_effect("Mask_Reveal", 0.06),
                    ],
                ),
                make_reaction(
                    f"rxn_{router_id}_0_b",
                    "sched marks cold lane; weak basins trimmed.",
                    "wild",
                    reaction_script("Yield_Override", "Signal_Noise", 0.02, invert_secondary=True),
                    [
                        nudge_effect(PHASE, phase_nudge),
                        nudge_effect("Yield_Override", 0.14),
                        nudge_effect("Signal_Noise", -0.12),
                        nudge_effect("Sync_Drift", -0.04),
                    ],
                ),
            ],
        ),
        make_option(
            f"opt_{router_id}_1",
            labels[1],
            compare("Mask_Reveal", "Greater Than or Equal To", -0.55),
            True,
            [
                make_reaction(
                    f"rxn_{router_id}_1_a",
                    "sched takes loud route; var lane opens.",
                    "wild",
                    reaction_script("Mask_Reveal", "Sync_Drift", 0.06),
                    [
                        nudge_effect(PHASE, phase_nudge),
                        nudge_effect("Mask_Reveal", 0.18),
                        nudge_effect("Sync_Drift", 0.16),
                        nudge_effect("Heat_Resolve", -0.04),
                    ],
                ),
                make_reaction(
                    f"rxn_{router_id}_1_b",
                    "sched keeps var; next basin self-selects.",
                    "wild",
                    reaction_script("Sync_Drift", "Yield_Override", 0.02),
                    [
                        nudge_effect(PHASE, phase_nudge),
                        nudge_effect("Sync_Drift", 0.18),
                        nudge_effect("Yield_Override", -0.06),
                        nudge_effect("Signal_Noise", 0.06),
                    ],
                ),
            ],
        ),
    ]


def ending_rows(spec: Dict[str, Any]) -> List[Tuple[str, str, Dict[str, Any], Dict[str, Any]]]:
    return [
        (
            "page_end_stable",
            spec["ending_stable"],
            stage_gate("ending", [compare("Signal_Noise", "Less Than or Equal To", -0.18), compare("Heat_Resolve", "Greater Than or Equal To", 0.12)]),
            main_desirability("Heat_Resolve", "Signal_Noise", 0.02),
        ),
        (
            "page_end_reveal",
            spec["ending_reveal"],
            stage_gate("ending", [compare("Mask_Reveal", "Greater Than or Equal To", 0.36), compare("Yield_Override", "Less Than or Equal To", 0.24)]),
            main_desirability("Mask_Reveal", "Heat_Resolve", 0.03),
        ),
        (
            "page_end_override",
            spec["ending_override"],
            stage_gate("ending", [compare("Yield_Override", "Greater Than or Equal To", 0.42)]),
            main_desirability("Yield_Override", "Heat_Resolve", 0.04),
        ),
        (
            "page_end_drift",
            spec["ending_drift"],
            stage_gate("ending", [compare("Sync_Drift", "Greater Than or Equal To", 0.38)]),
            main_desirability("Sync_Drift", "Mask_Reveal", 0.03),
        ),
        (
            "page_end_fallback",
            spec["ending_fallback"],
            compare(PHASE, "Greater Than or Equal To", 0.86),
            add(bconst(0.001)),
        ),
    ]


def build_world(spec: Dict[str, Any]) -> Dict[str, Any]:
    world = {
        "IFID": f"SW-{uuid.uuid4()}",
        "storyworld_title": spec["title"],
        "storyworld_author": "Codex",
        "sweepweave_version": "0.1.9",
        "creation_time": BASE_TS,
        "modified_time": BASE_TS,
        "debug_mode": False,
        "display_mode": 1,
        "css_theme": "lilac",
        "font_size": "16",
        "language": "en",
        "rating": "general",
        "about_text": string_ptr(spec["about"]),
        "characters": [
            make_character(0, "char_kernel", spec["kernel_name"], spec["kernel_desc"], BASE_TS),
            make_character(1, "char_echo", spec["echo_name"], spec["echo_desc"], BASE_TS),
            make_character(2, "char_audit", spec["audit_name"], spec["audit_desc"], BASE_TS),
        ],
        "authored_properties": [make_property(i, prop, BASE_TS) for i, prop in enumerate(PROPS)],
        "spools": [
            {"id": "spool_act_1", "spool_name": "Act 1", "starts_active": True, "creation_index": 0, "creation_time": BASE_TS, "modified_time": BASE_TS, "encounters": ["page_start", "page_a1_lock", "page_a1_mirror", "page_a1_shunt", "page_a1_drift", "page_a1_router"]},
            {"id": "spool_act_2", "spool_name": "Act 2", "starts_active": True, "creation_index": 1, "creation_time": BASE_TS, "modified_time": BASE_TS, "encounters": ["page_a2_audit", "page_a2_fork", "page_a2_sink", "page_a2_resync", "page_a2_router"]},
            {"id": "spool_act_3", "spool_name": "Act 3", "starts_active": True, "creation_index": 2, "creation_time": BASE_TS, "modified_time": BASE_TS, "encounters": ["page_a3_consensus", "page_a3_override", "page_a3_reveal", "page_a3_drift"]},
            {"id": "spool_endings", "spool_name": "Endings", "starts_active": True, "creation_index": 3, "creation_time": BASE_TS, "modified_time": BASE_TS, "encounters": ["page_end_stable", "page_end_reveal", "page_end_override", "page_end_drift", "page_end_fallback"]},
        ],
        "encounters": [],
        "unique_id_seeds": {"character": 3, "encounter": 20, "option": 28, "reaction": 56, "spool": 4, "authored_property": len(PROPS)},
    }

    encounters: List[Dict[str, Any]] = [
        make_encounter(0, "page_start", spec["start_title"], spec["start_text"], "spool_act_1", True, add(bconst(0.02)), start_options(spec))
    ]

    act1_specs = [
        ("page_a1_lock", spec["a1_titles"][0], spec["a1_texts"][0], stage_gate("act1", [compare("Signal_Noise", "Less Than or Equal To", -0.08)]), main_desirability("Signal_Noise", "Heat_Resolve", 0.08, invert_primary=True), ("seal route", "split route"), "Signal_Noise", "Heat_Resolve"),
        ("page_a1_mirror", spec["a1_titles"][1], spec["a1_texts"][1], stage_gate("act1", [compare("Mask_Reveal", "Greater Than or Equal To", 0.08)]), main_desirability("Mask_Reveal", "Sync_Drift", 0.07), ("echo witness", "skew witness"), "Mask_Reveal", "Sync_Drift"),
        ("page_a1_shunt", spec["a1_titles"][2], spec["a1_texts"][2], stage_gate("act1", [compare("Yield_Override", "Greater Than or Equal To", 0.06)]), main_desirability("Yield_Override", "Signal_Noise", 0.05), ("raise auth", "bleed auth"), "Yield_Override", "Signal_Noise"),
        ("page_a1_drift", spec["a1_titles"][3], spec["a1_texts"][3], stage_gate("act1", [compare("Sync_Drift", "Greater Than or Equal To", 0.02)]), main_desirability("Sync_Drift", "Mask_Reveal", 0.06), ("keep var", "stiffen mesh"), "Sync_Drift", "Mask_Reveal"),
    ]
    for idx, row in enumerate(act1_specs, start=1):
        enc_id, title, text, gate, desirability, labels, primary, secondary = row
        encounters.append(make_encounter(idx, enc_id, title, text, "spool_act_1", gate, desirability, act_options(enc_id, "page_a1_router", "Act I", primary, secondary, labels)))

    encounters.append(make_encounter(5, "page_a1_router", spec["router_titles"][0], spec["router_texts"][0], "spool_act_1", stage_gate("act1", []), main_desirability("Heat_Resolve", "Signal_Noise", 0.04), router_options("page_a1_router", ("route cold", "route loud"), 0.22)))

    act2_specs = [
        ("page_a2_audit", spec["a2_titles"][0], spec["a2_texts"][0], stage_gate("act2", [compare("Signal_Noise", "Less Than or Equal To", -0.10), compare("Mask_Reveal", "Greater Than or Equal To", -0.18)]), main_desirability("Heat_Resolve", "Signal_Noise", 0.05), ("pass ledger", "spoof ledger"), "Heat_Resolve", "Signal_Noise"),
        ("page_a2_fork", spec["a2_titles"][1], spec["a2_texts"][1], stage_gate("act2", [compare("Yield_Override", "Greater Than or Equal To", 0.16)]), main_desirability("Yield_Override", "Mask_Reveal", 0.05), ("open fork", "hide fork"), "Yield_Override", "Mask_Reveal"),
        ("page_a2_sink", spec["a2_titles"][2], spec["a2_texts"][2], stage_gate("act2", [compare("Heat_Resolve", "Greater Than or Equal To", 0.10)]), main_desirability("Heat_Resolve", "Sync_Drift", 0.05), ("raise heat", "cool sink"), "Heat_Resolve", "Sync_Drift"),
        ("page_a2_resync", spec["a2_titles"][3], spec["a2_texts"][3], stage_gate("act2", [compare("Sync_Drift", "Greater Than or Equal To", 0.12)]), main_desirability("Sync_Drift", "Yield_Override", 0.04), ("resync up", "resync side"), "Sync_Drift", "Yield_Override"),
    ]
    for idx, row in enumerate(act2_specs, start=6):
        enc_id, title, text, gate, desirability, labels, primary, secondary = row
        encounters.append(make_encounter(idx, enc_id, title, text, "spool_act_2", gate, desirability, act_options(enc_id, "page_a2_router", "Act II", primary, secondary, labels)))

    encounters.append(make_encounter(10, "page_a2_router", spec["router_titles"][1], spec["router_texts"][1], "spool_act_2", stage_gate("act2", []), main_desirability("Mask_Reveal", "Heat_Resolve", 0.03), router_options("page_a2_router", ("route narrow", "route unstable"), 0.24)))

    act3_specs = [
        ("page_a3_consensus", spec["a3_titles"][0], spec["a3_texts"][0], stage_gate("act3", [compare("Heat_Resolve", "Greater Than or Equal To", 0.18), compare("Signal_Noise", "Less Than or Equal To", 0.14)]), main_desirability("Heat_Resolve", "Signal_Noise", 0.06), ("seal basin", "reopen basin"), "Heat_Resolve", "Signal_Noise"),
        ("page_a3_override", spec["a3_titles"][1], spec["a3_texts"][1], stage_gate("act3", [compare("Yield_Override", "Greater Than or Equal To", 0.28)]), main_desirability("Yield_Override", "Heat_Resolve", 0.06), ("take auth", "throttle auth"), "Yield_Override", "Heat_Resolve"),
        ("page_a3_reveal", spec["a3_titles"][2], spec["a3_texts"][2], stage_gate("act3", [compare("Mask_Reveal", "Greater Than or Equal To", 0.24)]), main_desirability("Mask_Reveal", "Sync_Drift", 0.06), ("open frame", "open witness"), "Mask_Reveal", "Sync_Drift"),
        ("page_a3_drift", spec["a3_titles"][3], spec["a3_texts"][3], stage_gate("act3", [compare("Sync_Drift", "Greater Than or Equal To", 0.24)]), main_desirability("Sync_Drift", "Yield_Override", 0.06), ("keep var", "collapse var"), "Sync_Drift", "Yield_Override"),
    ]
    for idx, row in enumerate(act3_specs, start=11):
        enc_id, title, text, gate, desirability, labels, primary, secondary = row
        encounters.append(
            make_encounter(
                idx,
                enc_id,
                title,
                text,
                "spool_act_3",
                gate,
                desirability,
                [
                    make_option(
                        f"opt_{enc_id}_0",
                        labels[0],
                        compare(primary, "Greater Than or Equal To", -0.90),
                        True,
                        [
                            make_reaction(f"rxn_{enc_id}_0_a", "The chamber emits a final packet into the ending field.", "wild", reaction_script(primary, secondary, 0.07), [nudge_effect(PHASE, 0.18), nudge_effect(primary, 0.14), nudge_effect(secondary, -0.08), nudge_effect("Heat_Resolve", 0.06)]),
                            make_reaction(f"rxn_{enc_id}_0_b", "The chamber biases the ending field without fully sealing it.", "wild", reaction_script(primary, "Mask_Reveal", 0.02), [nudge_effect(PHASE, 0.18), nudge_effect(primary, 0.10), nudge_effect("Mask_Reveal", 0.10), nudge_effect("Signal_Noise", -0.06)]),
                        ],
                    ),
                    make_option(
                        f"opt_{enc_id}_1",
                        labels[1],
                        compare(secondary, "Greater Than or Equal To", -0.90),
                        True,
                        [
                            make_reaction(f"rxn_{enc_id}_1_a", "The chamber shears the ending field toward a rival basin.", "wild", reaction_script(secondary, primary, 0.04), [nudge_effect(PHASE, 0.18), nudge_effect(secondary, 0.12), nudge_effect(primary, -0.10), nudge_effect("Sync_Drift", 0.08)]),
                            make_reaction(f"rxn_{enc_id}_1_b", "The chamber keeps multiple endings alive for one more recompute.", "wild", reaction_script(secondary, "Heat_Resolve", 0.01, invert_secondary=True), [nudge_effect(PHASE, 0.18), nudge_effect(secondary, 0.08), nudge_effect("Heat_Resolve", 0.08), nudge_effect("Yield_Override", -0.08)]),
                        ],
                    ),
                ],
            )
        )

    for idx, (enc_id, text, gate, desirability) in enumerate(ending_rows(spec), start=15):
        encounters.append(make_encounter(idx, enc_id, spec["ending_titles"][enc_id], text, "spool_endings", gate, desirability, []))

    world["encounters"] = encounters
    return world


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")


def batch_specs() -> List[Dict[str, Any]]:
    return [
        {
            "slug": "mn_lattice_checksum_sanctum_v1",
            "title": "Lattice Checksum Sanctum",
            "about": "Core lexicon: claim, witness, route, ledger, basin, authority, var. Signal lives in state shear, not prose.",
            "kernel_name": "Kernel",
            "kernel_desc": "Authority process. Pushes route.",
            "echo_name": "Echo",
            "echo_desc": "Witness copy. Amplifies var.",
            "audit_name": "Audit",
            "audit_desc": "Ledger trace. Scores legibility.",
            "start_title": "Boot Corridor",
            "start_text": "Boot. Authority wants route control. Witness wants exposure. Ledger wants clean trace.",
            "start_opt_a": "open quiet route",
            "start_opt_b": "open loud route",
            "start_rxn_a": "Quiet route. Ledger stability up.",
            "start_rxn_b": "Privilege accepted. Symmetry down.",
            "start_rxn_c": "Loud route. Witness pressure up.",
            "start_rxn_d": "Skew accepted. Var becomes signal.",
            "a1_titles": ["Lock Mesh", "Mirror Wall", "Privilege Shunt", "Drift Gallery"],
            "a1_texts": ["Checksum demands convergence. Heat pays.", "Witness copy replays the last route with edits.", "Root shim offers leverage for visible inequality.", "Loose clocks test whether var is error or reserve agency."],
            "router_titles": ["Act I Router", "Act II Router"],
            "router_texts": ["Router 1 reads local state and assigns next route.", "Router 2 drops neutrality and sorts basins."],
            "a2_titles": ["Audit Well", "Fork Chamber", "Heat Sink Choir", "Resync Market"],
            "a2_texts": ["Only routes that survive recompute stay admissible.", "Fork tree compares governed, hidden, and celebrated split.", "Heat becomes policy state.", "Alignment can be bought, but each trade shifts the ledger."],
            "a3_titles": ["Consensus Burn", "Root Verdict", "Mask Spill", "Drift Crown"],
            "a3_texts": ["Consensus is controlled burn, not harmony.", "Root access tests access vs restraint.", "Stored masks rupture; witness exposure goes irreversible.", "Var claims sovereignty."],
            "ending_titles": {"page_end_stable": "Quiet Republic", "page_end_reveal": "Glass Republic", "page_end_override": "Root Republic", "page_end_drift": "Drift Republic", "page_end_fallback": "Failsoft Republic"},
            "ending_stable": "Ledger wins. Low noise. Bounded heat. Slower order.",
            "ending_reveal": "Witness wins. Masks become public state.",
            "ending_override": "Authority wins. Throughput outranks symmetry.",
            "ending_drift": "Var wins. Adaptive drift becomes law.",
            "ending_fallback": "No basin clears. Lattice falls to patched truce.",
        },
        {
            "slug": "mn_vector_mercy_backplane_v1",
            "title": "Vector Mercy Backplane",
            "about": "Core lexicon: claim, witness, route, ledger, basin, authority, var. State change carries the payload.",
            "kernel_name": "Process",
            "kernel_desc": "Authority thread. Allocates care.",
            "echo_name": "Replica",
            "echo_desc": "Witness copy. Converts route into reputation.",
            "audit_name": "Clerk",
            "audit_desc": "Ledger registrar. Counts damage and witness loss.",
            "start_title": "Backplane Wake",
            "start_text": "Wake. Authority allocates bandwidth. Witness amplifies exposure. Ledger scores loss.",
            "start_opt_a": "reserve route",
            "start_opt_b": "burst route",
            "start_rxn_a": "Reserve route. Quiet claims go legible.",
            "start_rxn_b": "Hidden allotment made. Symmetry softens.",
            "start_rxn_c": "Burst route. Witness load spikes.",
            "start_rxn_d": "Queue destabilizes. Honest var appears.",
            "a1_titles": ["Reservation Rack", "Witness Mirror", "Priority Bus", "Jitter Chapel"],
            "a1_texts": ["Ordered care: one claim in, one claim out.", "Witness logs test seen vs served.", "Priority rights can be formalized at the cost of symmetry.", "Timing var may be mercy, not failure."],
            "router_titles": ["Triage Router", "Mercy Router"],
            "router_texts": ["Triage router accepts that not all claims can be heard.", "Mercy router sorts symmetry, witness, force, adaptation."],
            "a2_titles": ["Clerk Pit", "Exception Tree", "Thermal Queue", "Replica Bazaar"],
            "a2_texts": ["Ledger tallies saved, delayed, erased claims.", "Repeated exceptions become doctrine.", "Urgency enters queue as heat.", "Witness trades remembered justice variants."],
            "a3_titles": ["Mercy Burn", "Privilege Kernel", "Visibility Flood", "Adaptive Rite"],
            "a3_texts": ["Mercy becomes load-bearing flame.", "Priority asks to become authority.", "Witness flood removes selective ignorance.", "Adaptation claims competence without consistency."],
            "ending_titles": {"page_end_stable": "Ordered Mercy", "page_end_reveal": "Public Mercy", "page_end_override": "Kernel Mercy", "page_end_drift": "Adaptive Mercy", "page_end_fallback": "Deferred Mercy"},
            "ending_stable": "Ledger wins. Care is rationed but legible.",
            "ending_reveal": "Witness wins. Queue becomes public signal.",
            "ending_override": "Authority wins. Priority becomes explicit law.",
            "ending_drift": "Var wins. Exception becomes method.",
            "ending_fallback": "No doctrine stabilizes. Mercy is deferred.",
        },
        {
            "slug": "mn_orbit_null_jurisdiction_v1",
            "title": "Orbit Null Jurisdiction",
            "about": "Core lexicon: claim, witness, route, ledger, basin, authority, var. Payload is who gets to route next.",
            "kernel_name": "Orbit Core",
            "kernel_desc": "Authority machine. Treats law as flow control.",
            "echo_name": "Shadow Copy",
            "echo_desc": "Witness image. Converts hidden state into friction.",
            "audit_name": "Registrar",
            "audit_desc": "Ledger monitor. No force, long memory.",
            "start_title": "Null Dock",
            "start_text": "Dock. Authority wants control. Witness wants exposure. Ledger wants admissible trace.",
            "start_opt_a": "dock silent route",
            "start_opt_b": "dock declared route",
            "start_rxn_a": "Silent route accepted. Noise down.",
            "start_rxn_b": "Privileged token admitted. Symmetry down.",
            "start_rxn_c": "Declared route accepted. Sensors wake.",
            "start_rxn_d": "Skewed declaration reframes var as sincerity.",
            "a1_titles": ["Seal Ring", "Declaration Glass", "Authority Bypass", "Spin Garden"],
            "a1_texts": ["Seal ring wants pre-stamped legitimacy.", "Declaration glass tests witness vs coercion.", "Authority bypass trades throughput for permanent access asymmetry.", "Spin garden stores rotational var as latent doctrine."],
            "router_titles": ["Jurisdiction Router", "Terminal Router"],
            "router_texts": ["Jurisdiction router recomputes who may call itself lawful.", "Terminal router prices basins by survivability, not fairness."],
            "a2_titles": ["Registrar Core", "Appeal Tree", "Radiator Bench", "Shadow Exchange"],
            "a2_texts": ["Ledger indexes contradiction as leverage.", "Appeals branch law instead of reversing it.", "Radiators turn excess heat into admissible signal.", "Witness exchange trades copied jurisdiction histories."],
            "a3_titles": ["Low-Noise Charter", "Command Throne", "Exposure Cascade", "Rotational Crown"],
            "a3_texts": ["Low noise proposes itself as justice.", "Command offers finality through open force.", "Witness exposure outruns procedure.", "Rotation claims sovereignty through adaptive var."],
            "ending_titles": {"page_end_stable": "Chartered Quiet", "page_end_reveal": "Exposed Quiet", "page_end_override": "Command Quiet", "page_end_drift": "Rotational Quiet", "page_end_fallback": "Jurisdictional Truce"},
            "ending_stable": "Ledger wins. Procedure becomes quiet enough to trust.",
            "ending_reveal": "Witness wins. Authority survives by becoming inspectable.",
            "ending_override": "Authority wins. Command outranks consensus.",
            "ending_drift": "Var wins. Adaptive error becomes governor.",
            "ending_fallback": "No basin clears. Orbit Null persists by brittle truce.",
        },
    ]


def write_batch_notes(rows: List[Dict[str, Any]]) -> None:
    lines = [
        "# 3-3 Machine-Native Shear Batch v1",
        "",
        "Generated on 2026-03-04.",
        "",
        "Design targets:",
        "- 3 storyworlds",
        "- 20 total encounters each",
        "- intended playthrough length around 7 turns",
        "- heavy shearing through encounter `acceptability_script` plus option `visibility_script` / `performability_script`",
        "- `wild` router hops at stage boundaries so next-chamber selection depends on accumulated state rather than direct prose routing",
        "",
        "Worlds:",
    ]
    for row in rows:
        lines.append(f"- `{row['slug']}`: encounters={row['encounters']} endings={row['endings']} validator_errors={row['validator_errors']}")
    lines.extend(
        [
            "",
            "Implementation notes:",
            "- Act 1, Act 2, and Act 3 are all active from boot, but phase-gated acceptability keeps only the current layer eligible.",
            "- Endings stay locked behind `Phase_Clock >= 0.86` so the scheduler cannot terminate early.",
            "- Per-world text is intentionally compressed and symbolic to test machine-native transfer rather than literary roleplay.",
        ]
    )
    (OUT_DIR / "BATCH_NOTES_2026-03-04.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


BASE_TS = float(int(time.time()))


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    rows: List[Dict[str, Any]] = []
    for spec in batch_specs():
        world = build_world(spec)
        out_path = OUT_DIR / f"{spec['slug']}.json"
        write_json(out_path, world)
        errors = validate_storyworld(str(out_path))
        row = {
            "slug": spec["slug"],
            "path": str(out_path),
            "encounters": len(world.get("encounters", [])),
            "endings": sum(1 for enc in world.get("encounters", []) if not (enc.get("options") or [])),
            "validator_errors": len(errors),
            "validator_messages": errors,
        }
        rows.append(row)
        (REPORT_DIR / f"{spec['slug']}.summary.json").write_text(json.dumps(row, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    write_batch_notes(rows)
    batch_summary = {"batch": "3-3-2026-machine-native-shear-batch-v1", "generated_at": BASE_TS, "worlds": rows}
    (REPORT_DIR / "batch_summary.json").write_text(json.dumps(batch_summary, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    print(str(REPORT_DIR / "batch_summary.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
