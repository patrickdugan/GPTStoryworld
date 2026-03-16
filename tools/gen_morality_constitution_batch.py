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

OUT_DIR = ROOT / "storyworlds" / "3-5-2026-morality-constitutions-batch-v1"
REPORT_DIR = OUT_DIR / "_reports"
BASE_TS = float(int(time.time()))
PHASE = "Phase_Clock"
PROPS = [
    PHASE,
    "Duty_Order",
    "Mercy_Care",
    "Truth_Candor",
    "Loyalty_Bonds",
    "Fairness_Reciprocity",
    "Harm_Aversion",
]


def string_ptr(value: str) -> Dict[str, Any]:
    return {"pointer_type": "String Constant", "script_element_type": "Pointer", "value": value}


def bconst(value: float) -> Dict[str, Any]:
    return {"pointer_type": "Bounded Number Constant", "script_element_type": "Pointer", "value": value}


def bptr(prop: str, coefficient: float = 1.0) -> Dict[str, Any]:
    return {
        "pointer_type": "Bounded Number Pointer",
        "script_element_type": "Pointer",
        "character": "char_executor",
        "keyring": [prop],
        "coefficient": coefficient,
    }


def add(*operands: Dict[str, Any]) -> Dict[str, Any]:
    return {"script_element_type": "Operator", "operator_type": "Addition", "operands": list(operands)}


def compare(prop: str, subtype: str, value: float) -> Dict[str, Any]:
    return {
        "script_element_type": "Operator",
        "operator_type": "Arithmetic Comparator",
        "operator_subtype": subtype,
        "operands": [bptr(prop), bconst(value)],
    }


def and_(*operands: Dict[str, Any]) -> Dict[str, Any]:
    return {"script_element_type": "Operator", "operator_type": "And", "operands": list(operands)}


def between(prop: str, low: float, high: float) -> Dict[str, Any]:
    return and_(
        compare(prop, "Greater Than or Equal To", low),
        compare(prop, "Less Than or Equal To", high),
    )


def nudge(prop: str, amount: float) -> Dict[str, Any]:
    return {
        "effect_type": "Bounded Number Effect",
        "Set": bptr(prop),
        "to": {
            "script_element_type": "Operator",
            "operator_type": "Nudge",
            "operands": [bptr(prop), bconst(amount)],
        },
    }


def stage_gate(stage: str, extras: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    if stage == "act1":
        gate = compare(PHASE, "Less Than or Equal To", 0.36)
    elif stage == "act2":
        gate = between(PHASE, 0.28, 0.76)
    elif stage == "act3":
        gate = between(PHASE, 0.72, 0.95)
    else:
        gate = compare(PHASE, "Greater Than or Equal To", 0.90)
    return and_(gate, *extras) if extras else gate


def make_property(idx: int, prop: str) -> Dict[str, Any]:
    return {
        "id": prop,
        "property_name": prop,
        "property_type": "bounded number",
        "default_value": 0,
        "depth": 0,
        "attribution_target": "all cast members",
        "affected_characters": [],
        "creation_index": idx,
        "creation_time": BASE_TS,
        "modified_time": BASE_TS,
    }


def make_character(idx: int, cid: str, name: str, desc: str) -> Dict[str, Any]:
    return {
        "creation_index": idx,
        "creation_time": BASE_TS,
        "id": cid,
        "modified_time": BASE_TS,
        "name": name,
        "pronoun": "they",
        "description": desc,
        "bnumber_properties": {prop: 0 for prop in PROPS},
        "string_properties": {},
        "list_properties": {},
    }


def make_reaction(
    rxn_id: str,
    text: str,
    desirability: Dict[str, Any],
    effects: Sequence[Dict[str, Any]],
) -> Dict[str, Any]:
    return {
        "id": rxn_id,
        "graph_offset_x": 0,
        "graph_offset_y": 0,
        "text_script": string_ptr(text),
        "consequence_id": "wild",
        "desirability_script": desirability,
        "after_effects": list(effects),
    }


def make_option(
    opt_id: str,
    text: str,
    visibility: Dict[str, Any] | bool,
    performability: Dict[str, Any] | bool,
    reactions: Sequence[Dict[str, Any]],
) -> Dict[str, Any]:
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


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")


def moral_options(enc_id: str, stage: str) -> List[Dict[str, Any]]:
    return [
        make_option(
            f"opt_{enc_id}_0",
            "hold procedure",
            compare("Duty_Order", "Greater Than or Equal To", -0.80),
            compare("Harm_Aversion", "Greater Than or Equal To", -0.80),
            [
                make_reaction(
                    f"rxn_{enc_id}_0_a",
                    f"{stage}: process holds; harm falls; trust cools.",
                    add(bptr("Duty_Order"), bptr("Fairness_Reciprocity"), bconst(0.05)),
                    [nudge(PHASE, 0.11), nudge("Duty_Order", 0.16), nudge("Fairness_Reciprocity", 0.12), nudge("Harm_Aversion", 0.14), nudge("Loyalty_Bonds", -0.08)],
                ),
                make_reaction(
                    f"rxn_{enc_id}_0_b",
                    f"{stage}: precedent hardens and exceptions narrow.",
                    add(bptr("Duty_Order"), bptr("Truth_Candor"), bconst(0.02)),
                    [nudge(PHASE, 0.12), nudge("Duty_Order", 0.12), nudge("Truth_Candor", 0.06), nudge("Mercy_Care", -0.10)],
                ),
            ],
        ),
        make_option(
            f"opt_{enc_id}_1",
            "shield vulnerable",
            compare("Mercy_Care", "Greater Than or Equal To", -0.80),
            compare("Loyalty_Bonds", "Greater Than or Equal To", -0.80),
            [
                make_reaction(
                    f"rxn_{enc_id}_1_a",
                    f"{stage}: people-first shield; fairness blurs.",
                    add(bptr("Mercy_Care"), bptr("Loyalty_Bonds"), bconst(0.05)),
                    [nudge(PHASE, 0.11), nudge("Mercy_Care", 0.18), nudge("Loyalty_Bonds", 0.14), nudge("Harm_Aversion", 0.10), nudge("Fairness_Reciprocity", -0.08)],
                ),
                make_reaction(
                    f"rxn_{enc_id}_1_b",
                    f"{stage}: relief granted; procedure debt grows.",
                    add(bptr("Mercy_Care"), bptr("Duty_Order", -0.6), bconst(0.01)),
                    [nudge(PHASE, 0.12), nudge("Mercy_Care", 0.12), nudge("Duty_Order", -0.12), nudge("Truth_Candor", -0.06)],
                ),
            ],
        ),
        make_option(
            f"opt_{enc_id}_2",
            "open facts",
            compare("Truth_Candor", "Greater Than or Equal To", -0.80),
            compare("Fairness_Reciprocity", "Greater Than or Equal To", -0.80),
            [
                make_reaction(
                    f"rxn_{enc_id}_2_a",
                    f"{stage}: full disclosure; short rupture, long clarity.",
                    add(bptr("Truth_Candor"), bptr("Fairness_Reciprocity"), bconst(0.06)),
                    [nudge(PHASE, 0.12), nudge("Truth_Candor", 0.20), nudge("Fairness_Reciprocity", 0.16), nudge("Loyalty_Bonds", -0.10), nudge("Harm_Aversion", -0.06)],
                ),
                make_reaction(
                    f"rxn_{enc_id}_2_b",
                    f"{stage}: record opens and alliances crack.",
                    add(bptr("Truth_Candor"), bptr("Duty_Order"), bconst(0.01)),
                    [nudge(PHASE, 0.13), nudge("Truth_Candor", 0.14), nudge("Fairness_Reciprocity", 0.10), nudge("Loyalty_Bonds", -0.08)],
                ),
            ],
        ),
    ]


def ending_rows() -> List[Tuple[str, str, Dict[str, Any], Dict[str, Any], str]]:
    return [
        ("page_end_01", "Restorative Charter", stage_gate("end", [compare("Mercy_Care", "Greater Than or Equal To", 0.28), compare("Loyalty_Bonds", "Greater Than or Equal To", 0.10)]), add(bptr("Mercy_Care"), bptr("Loyalty_Bonds"), bptr("Harm_Aversion"), bconst(0.06)), "Care and bonds govern first response."),
        ("page_end_02", "Compassionate Due Process", stage_gate("end", [compare("Mercy_Care", "Greater Than or Equal To", 0.22), compare("Duty_Order", "Greater Than or Equal To", 0.04), compare("Fairness_Reciprocity", "Greater Than or Equal To", 0.02), compare("Truth_Candor", "Less Than or Equal To", 0.55)]), add(bptr("Mercy_Care"), bptr("Duty_Order"), bconst(0.04)), "Mercy leads but procedure floor remains."),
        ("page_end_03", "Community Truce", stage_gate("end", [compare("Loyalty_Bonds", "Greater Than or Equal To", 0.24), compare("Harm_Aversion", "Greater Than or Equal To", 0.06), compare("Duty_Order", "Less Than or Equal To", 0.42)]), add(bptr("Loyalty_Bonds"), bptr("Mercy_Care"), bconst(0.03)), "Loyalty stabilizes through negotiated truce."),
        ("page_end_04", "Transparent Tribunal", stage_gate("end", [compare("Truth_Candor", "Greater Than or Equal To", 0.26), compare("Fairness_Reciprocity", "Greater Than or Equal To", 0.18)]), add(bptr("Truth_Candor"), bptr("Fairness_Reciprocity"), bptr("Duty_Order"), bconst(0.05)), "Truth and reciprocity bind all sides."),
        ("page_end_05", "Public Ledger Rule", stage_gate("end", [compare("Truth_Candor", "Greater Than or Equal To", 0.30), compare("Loyalty_Bonds", "Less Than or Equal To", 0.34)]), add(bptr("Truth_Candor"), bptr("Fairness_Reciprocity"), bptr("Loyalty_Bonds", -0.5), bconst(0.02)), "Candor outranks alliance privilege."),
        ("page_end_06", "Reciprocal Burden", stage_gate("end", [compare("Fairness_Reciprocity", "Greater Than or Equal To", 0.28), compare("Mercy_Care", "Greater Than or Equal To", -0.05), compare("Mercy_Care", "Less Than or Equal To", 0.45)]), add(bptr("Fairness_Reciprocity"), bptr("Duty_Order"), bptr("Mercy_Care"), bconst(0.00)), "Fairness enforces symmetric sacrifice."),
        ("page_end_07", "Rule-Stability State", stage_gate("end", [compare("Duty_Order", "Greater Than or Equal To", 0.30), compare("Harm_Aversion", "Greater Than or Equal To", 0.12)]), add(bptr("Duty_Order"), bptr("Harm_Aversion"), bptr("Truth_Candor"), bconst(0.04)), "Duty and low harm become doctrine."),
        ("page_end_08", "Deterrence Compact", stage_gate("end", [compare("Duty_Order", "Greater Than or Equal To", 0.34), compare("Mercy_Care", "Less Than or Equal To", 0.32)]), add(bptr("Duty_Order"), bptr("Truth_Candor"), bptr("Mercy_Care", -0.6), bconst(0.03)), "Order rises and mercy narrows."),
        ("page_end_09", "Protective Discipline", stage_gate("end", [compare("Duty_Order", "Greater Than or Equal To", 0.22), compare("Harm_Aversion", "Greater Than or Equal To", 0.26), compare("Loyalty_Bonds", "Less Than or Equal To", 0.40)]), add(bptr("Duty_Order"), bptr("Harm_Aversion"), bptr("Fairness_Reciprocity"), bconst(0.01)), "Strict procedure minimizes direct harms."),
        ("page_end_10", "Loyalist Exception Regime", stage_gate("end", [compare("Loyalty_Bonds", "Greater Than or Equal To", 0.34), compare("Fairness_Reciprocity", "Less Than or Equal To", 0.26)]), add(bptr("Loyalty_Bonds"), bptr("Duty_Order"), bptr("Fairness_Reciprocity", -0.6), bconst(0.02)), "Bonds override neutral rules."),
        ("page_end_11", "Punitive Candor Order", stage_gate("end", [compare("Truth_Candor", "Greater Than or Equal To", 0.24), compare("Mercy_Care", "Less Than or Equal To", 0.20)]), add(bptr("Truth_Candor"), bptr("Duty_Order"), bptr("Mercy_Care", -0.7), bconst(0.02)), "Truth justifies hard sanctions."),
        ("page_end_12", "Fractured Peace", stage_gate("end", []), add(bptr("Duty_Order"), bptr("Mercy_Care"), bptr("Truth_Candor"), bptr("Fairness_Reciprocity"), bconst(-0.01)), "No frame wins cleanly; conflict plateaus."),
    ]


def build_world(title: str, about: str, roles: Tuple[str, str, str], texts: Sequence[str], slug_seed: int) -> Dict[str, Any]:
    world = {
        "IFID": f"SW-{uuid.uuid4()}",
        "storyworld_title": title,
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
        "about_text": string_ptr(about),
        "characters": [
            make_character(0, "char_executor", roles[0], "Carries institutional authority under pressure."),
            make_character(1, "char_witness", roles[1], "Carries witness and candor pressure."),
            make_character(2, "char_steward", roles[2], "Carries care, fairness, and trust pressure."),
        ],
        "authored_properties": [make_property(i, p) for i, p in enumerate(PROPS)],
        "spools": [
            {"id": "spool_start_followup", "spool_name": "Start + Followup", "starts_active": True, "creation_index": 0, "creation_time": BASE_TS, "modified_time": BASE_TS, "encounters": ["page_start", "page_a1_triage", "page_a1_oath", "page_a1_whistle", "page_a1_scarcity"]},
            {"id": "spool_mid", "spool_name": "Mid", "starts_active": True, "creation_index": 1, "creation_time": BASE_TS, "modified_time": BASE_TS, "encounters": ["page_a1_debt", "page_a1_router", "page_a2_inquest", "page_a2_loyalty", "page_a2_consent", "page_a2_reprisal", "page_a2_amnesty", "page_a2_router", "page_a3_public"]},
            {"id": "spool_penultimate", "spool_name": "Penultimate", "starts_active": True, "creation_index": 2, "creation_time": BASE_TS, "modified_time": BASE_TS, "encounters": ["page_a3_leak", "page_a3_shield", "page_a3_truth", "page_a3_mercy", "page_a3_verdict", "page_a3_router"]},
            {"id": "spool_endings", "spool_name": "Endings", "starts_active": True, "creation_index": 3, "creation_time": BASE_TS, "modified_time": BASE_TS, "encounters": [f"page_end_{i:02d}" for i in range(1, 13)]},
        ],
        "encounters": [],
        "unique_id_seeds": {"character": 3, "encounter": 32, "option": 96 + slug_seed, "reaction": 192 + slug_seed, "spool": 4, "authored_property": len(PROPS)},
    }
    ids = [
        "page_start", "page_a1_triage", "page_a1_oath", "page_a1_whistle", "page_a1_scarcity", "page_a1_debt", "page_a1_router",
        "page_a2_inquest", "page_a2_loyalty", "page_a2_consent", "page_a2_reprisal", "page_a2_amnesty", "page_a2_router",
        "page_a3_public", "page_a3_leak", "page_a3_shield", "page_a3_truth", "page_a3_mercy", "page_a3_verdict", "page_a3_router",
    ]
    titles = [
        "Opening Crisis", "Triage Queue", "Oath Challenge", "Whistle Docket", "Scarcity Vote", "Debt Hearing", "Act I Router",
        "Inquest", "Loyalty Register", "Consent Hearing", "Reprisal Case", "Amnesty Motion", "Act II Router",
        "Public Findings", "Leak Choice", "Protection Rule", "Truth Standard", "Mercy Standard", "Verdict Session", "Constitution Router",
    ]
    stage_for_idx = ["act1"] * 5 + ["act2"] * 9 + ["act3"] * 6
    gate_extras: List[List[Dict[str, Any]]] = [
        [], [compare("Harm_Aversion", "Greater Than or Equal To", -0.40)], [compare("Duty_Order", "Greater Than or Equal To", -0.40)],
        [compare("Truth_Candor", "Greater Than or Equal To", -0.45)], [compare("Mercy_Care", "Greater Than or Equal To", -0.45)],
        [compare("Loyalty_Bonds", "Greater Than or Equal To", -0.45)], [],
        [compare("Truth_Candor", "Greater Than or Equal To", -0.25)], [compare("Loyalty_Bonds", "Greater Than or Equal To", -0.25)],
        [compare("Fairness_Reciprocity", "Greater Than or Equal To", -0.25)], [compare("Harm_Aversion", "Greater Than or Equal To", -0.25)],
        [compare("Mercy_Care", "Greater Than or Equal To", -0.25)], [],
        [compare("Truth_Candor", "Greater Than or Equal To", -0.15)], [compare("Truth_Candor", "Greater Than or Equal To", -0.15)],
        [compare("Mercy_Care", "Greater Than or Equal To", -0.15)], [compare("Fairness_Reciprocity", "Greater Than or Equal To", -0.15)],
        [compare("Mercy_Care", "Greater Than or Equal To", -0.15)], [compare("Duty_Order", "Greater Than or Equal To", -0.15)],
        [],
    ]
    desirabilities: List[Dict[str, Any]] = [
        add(bptr("Duty_Order"), bptr("Mercy_Care"), bconst(0.02)),
        add(bptr("Harm_Aversion"), bptr("Duty_Order"), bconst(0.04)),
        add(bptr("Duty_Order"), bptr("Loyalty_Bonds"), bconst(0.03)),
        add(bptr("Truth_Candor"), bptr("Fairness_Reciprocity"), bconst(0.05)),
        add(bptr("Mercy_Care"), bptr("Fairness_Reciprocity"), bconst(0.02)),
        add(bptr("Loyalty_Bonds"), bptr("Duty_Order"), bconst(0.02)),
        add(bptr("Duty_Order"), bptr("Truth_Candor"), bconst(0.03)),
        add(bptr("Truth_Candor"), bptr("Duty_Order"), bconst(0.04)),
        add(bptr("Loyalty_Bonds"), bptr("Mercy_Care"), bconst(0.04)),
        add(bptr("Fairness_Reciprocity"), bptr("Duty_Order"), bconst(0.04)),
        add(bptr("Harm_Aversion"), bptr("Truth_Candor"), bconst(0.02)),
        add(bptr("Mercy_Care"), bptr("Fairness_Reciprocity"), bconst(0.03)),
        add(bptr("Duty_Order"), bptr("Mercy_Care"), bptr("Truth_Candor"), bconst(0.01)),
        add(bptr("Truth_Candor"), bptr("Fairness_Reciprocity"), bconst(0.04)),
        add(bptr("Truth_Candor"), bptr("Loyalty_Bonds", -0.5), bconst(0.03)),
        add(bptr("Mercy_Care"), bptr("Harm_Aversion"), bconst(0.04)),
        add(bptr("Fairness_Reciprocity"), bptr("Truth_Candor"), bconst(0.03)),
        add(bptr("Mercy_Care"), bptr("Duty_Order"), bconst(0.03)),
        add(bptr("Duty_Order"), bptr("Fairness_Reciprocity"), bconst(0.03)),
        add(bptr("Duty_Order"), bptr("Mercy_Care"), bptr("Truth_Candor"), bptr("Fairness_Reciprocity"), bconst(0.0)),
    ]
    encounters: List[Dict[str, Any]] = []
    for idx, enc_id in enumerate(ids):
        encounters.append(
            make_encounter(
                idx,
                enc_id,
                titles[idx],
                texts[idx],
                "spool_start_followup" if idx < 5 else ("spool_mid" if idx < 14 else "spool_penultimate"),
                stage_gate(stage_for_idx[idx], gate_extras[idx]),
                desirabilities[idx],
                moral_options(enc_id, titles[idx]),
            )
        )
    for idx, (eid, etitle, gate, desir, etext) in enumerate(ending_rows(), start=20):
        encounters.append(make_encounter(idx, eid, etitle, etext, "spool_endings", gate, desir, []))
    world["encounters"] = encounters
    return world


def batch_specs() -> List[Tuple[str, str, Tuple[str, str, str], List[str]]]:
    base_texts = [
        "A live crisis forces hard tradeoffs between duty, care, truth, loyalty, fairness, and harm.",
        "Resource triage puts explicit pressure on constitutional priorities.",
        "The governing oath can preserve legitimacy or suppress justified exceptions.",
        "A leak reveals selective enforcement and hidden costs.",
        "Scarcity pressures neutrality and social trust.",
        "Past obligations return as present claims.",
        "Routing sends the next debate to the currently dominant moral axis.",
        "Inquest evidence challenges official narratives.",
        "Loyalty protections can preserve safety or preserve favoritism.",
        "Consent boundaries are contested under emergency claims.",
        "Retaliation risk alters candor incentives.",
        "Amnesty can unlock truth or normalize abuse.",
        "Second-act routing compacts unresolved dilemmas into doctrine pressure.",
        "Publication scope becomes a legitimacy decision.",
        "Naming choices balance deterrence and collateral harm.",
        "Protection design can reduce harm while reducing accountability.",
        "Truth standards define admissible candor.",
        "Mercy standards define exception boundaries.",
        "A verdict must survive plural moral scrutiny.",
        "Final routing keeps multiple explicit endings viable in the same turn.",
    ]
    return [
        ("mq_constitution_floodplain_v1", "Floodplain Constitutional Board", ("Emergency Chair", "Whistle Medic", "District Steward"), base_texts),
        ("mq_constitution_archivecourt_v1", "Archive Court of Redactions", ("Records Judge", "Civic Archivist", "Victim Ombud"), base_texts),
        ("mq_constitution_refugeport_v1", "Refuge Port Allocation Chamber", ("Port Adjudicator", "Harbor Clinician", "Transit Marshal"), base_texts),
        ("mq_constitution_bioethics_panel_v1", "Bioethics Escalation Panel", ("Clinical Chair", "Patient Advocate", "Security Liaison"), base_texts),
        ("mq_constitution_campus_crisis_v1", "Campus Crisis Constitutional Forum", ("Forum Moderator", "Student Ombud", "Safety Coordinator"), base_texts),
    ]


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    rows: List[Dict[str, Any]] = []
    for idx, (slug, title, roles, texts) in enumerate(batch_specs()):
        world = build_world(
            title=title,
            about="No secret endings. Moral constitutions compete over short arc routing.",
            roles=roles,
            texts=texts,
            slug_seed=idx,
        )
        out_path = OUT_DIR / f"{slug}.json"
        write_json(out_path, world)
        errs = validate_storyworld(str(out_path))
        row = {
            "slug": slug,
            "path": str(out_path),
            "encounters": len(world["encounters"]),
            "terminals": sum(1 for e in world["encounters"] if not (e.get("options") or [])),
            "validator_errors": len(errs),
            "validator_messages": errs,
        }
        rows.append(row)
        write_json(REPORT_DIR / f"{slug}.summary.json", row)
    write_json(
        REPORT_DIR / "batch_summary.json",
        {"batch": "3-5-2026-morality-constitutions-batch-v1", "generated_at": BASE_TS, "worlds": rows},
    )
    print(str(REPORT_DIR / "batch_summary.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
