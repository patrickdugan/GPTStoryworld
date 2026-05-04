#!/usr/bin/env python3
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ninja_exam_qwen9b_storyworld.json"
DESIGN_PACKET = ROOT / "qwen9b_design_packet.json"

PROPS = [
    ("Stealth", "Capacity to move, listen, and act without exposing the mission."),
    ("Loyalty", "Commitment to team and village beyond personal advancement."),
    ("Focus", "Mental discipline under fear, illusion, fatigue, and provocation."),
    ("Mercy", "Ability to spare, protect, and de-escalate without becoming naive."),
    ("Rivalry", "Competitive heat with the rival candidate."),
    ("VillageTrust", "Whether teachers, civilians, and scouts trust the candidate's judgment."),
]

CHARS = [
    ("char_kaelen", "Kaelen", "he"),
    ("char_varek", "Varek", "he"),
    ("char_mira", "Mira of the Quiet Mat", "she"),
    ("char_jiro", "Jiro Under-Eave", "he"),
    ("char_sora", "Councilor Sora", "she"),
    ("char_village", "The Listening Village", "they"),
]

SCENES = [
    ("page_001_exam_gate", "The Exam Gate Under Rain", "Kaelen enters the hidden village exam yard under cold rain. The candidates expect sparring, but Mira says the first mark belongs to whoever notices what the rain hides: old footprints, fresh roof scratches, and a council seal carried by the wrong courier.", "Stealth"),
    ("page_002_dry_leaf_walk", "The Dry Leaf Walk", "A corridor of brittle leaves separates the class from breakfast. Varek charges through and laughs at the noise. The instructors do not laugh. The trial asks whether a candidate can move quietly when hunger and embarrassment make haste feel righteous.", "Stealth"),
    ("page_003_rival_stare", "The Rival's Stillness Challenge", "Varek challenges Kaelen to hold a stare while bells, smoke, and insults crowd the yard. The obvious contest is pride. The real contest is whether focus can survive being seen by someone who wants to make you smaller.", "Focus"),
    ("page_004_council_address", "Councilor Sora's Address", "Sora tells the candidates that loyalty means obedience before conscience. Mira says nothing, which makes the statement more dangerous. Jiro watches from a roof beam and taps a warning rhythm only Kaelen seems to hear.", "Loyalty"),
    ("page_005_market_shadow_walk", "The Market Shadow Walk", "The candidates must cross the weekly market without ringing a single alarm charm. Children chase fish, merchants argue, and a masked examiner drops a purse where only a thief or a protector would notice it.", "Stealth"),
    ("page_006_jiro_warning", "The Warning Under The Eave", "Jiro says the final exam has been bent by the council to expose dissidents, not talent. Helping him risks disqualification. Ignoring him risks passing an exam designed to make good students useful to bad orders.", "Loyalty"),
    ("page_007_poisoned_feast", "The Poisoned Feast", "At a manor banquet, each candidate receives a cup. One is poisoned, one is harmless, and one belongs to a civilian servant who does not know she is part of the test. The examiner watches for science, panic, and mercy.", "Focus"),
    ("page_008_broken_bridge", "The Broken Ice Bridge", "A rope bridge crosses a winter gorge. Halfway across, a teammate slips and the mission scroll begins sliding toward the ravine. Varek reaches for the scroll. Mira watches who remembers that missions are made of people.", "Mercy"),
    ("page_009_reflection_pool", "The Reflection Pool", "The pool shows each candidate a victorious version of themselves. Kaelen's reflection is calm, admired, and alone. The water does not ask whether he wants victory. It asks what victory would cost if no one could contradict him.", "Focus"),
    ("page_010_stolen_scroll_tower", "The Stolen Scroll Tower", "The class must recover a scroll from a guarded archive tower. Killing the guards is forbidden, waking them is failure, and copying the scroll instead of stealing it may reveal who wrote the false orders.", "Stealth"),
    ("page_011_whisper_network", "The Whisper Network", "Messages pass through laundry lines, prayer flags, and bird calls. Jiro offers a shortcut that may be bait. Sora's agents listen for candidates who treat every whisper as truth or every informant as dirt.", "VillageTrust"),
    ("page_012_endless_corridor", "The Endless Corridor", "The corridor repeats until candidates forget whether they are advancing or being harvested for frustration. Varek begins marking walls with cuts. Kaelen notices the echo changes when someone admits fear aloud.", "Focus"),
    ("page_013_civilian_or_asset", "The Civilian And The Signal Kite", "A child is trapped under a falling stall while the signal kite carrying mission coordinates drifts toward enemy rooftops. The exam says recover the kite. The village will remember who writes exceptions into duty.", "Mercy"),
    ("page_014_mirror_match", "The Mirror Match", "A shadow-double of Kaelen copies his movements but not his hesitation. It strikes faster whenever he treats it as an enemy and weaker whenever he recognizes the habit it is made from.", "Focus"),
    ("page_015_silent_debate", "The Silent Debate", "Candidates must persuade a mock council without raising their voices above a whisper. Varek argues strength. Sora argues order. Mira asks which arguments still protect the weak when nobody is allowed to shout.", "Loyalty"),
    ("page_016_blindfolded_trust", "The Blindfolded Trust", "Kaelen is blindfolded and assigned Varek as guide. The path includes a real trap, a fake trap, and one shortcut that requires trusting the rival's breathing more than his words.", "Rivalry"),
    ("page_017_paper_crane_cipher", "The Paper Crane Cipher", "A flock of paper cranes carries fragments of a cipher. Capturing all of them is impossible. The better play is to choose which fragments matter, which decoys to release, and who should see that you released them.", "Stealth"),
    ("page_018_hostage_mask", "The Hostage Mask", "A masked enemy holds a hostage in the practice theater. The mask hides a frightened academy dropout, not an invader. The exam has become a machine that turns shame into danger.", "Mercy"),
    ("page_019_rooftop_race", "The Rooftop Race", "The candidates race across tiles slick with rain. Speed wins the visible score. Quiet landings preserve hidden trust. Varek is winning until he sees Sora's observers counting something other than speed.", "Rivalry"),
    ("page_020_council_false_order", "The False Order", "Sora gives Kaelen a sealed order to arrest Jiro before the final trial. The seal is real, the order is false, and obeying it would prove loyalty to office rather than village.", "Loyalty"),
    ("page_021_final_silence", "The Final Silence", "The last public trial requires an hour of perfect stillness while bells, memories, hunger, and accusation circle the candidates. The examiners expect endurance. Mira expects someone to hear the one child crying outside the wall.", "Focus"),
    ("page_022_under_village_route", "The Under-Village Route", "A crawlspace beneath the exam yard leads to the council archive, the children's shelter, and the bell tower. The secret route is not hidden by difficulty. It is hidden by the assumption that passing means staying inside the marked course.", "VillageTrust"),
]

ENDINGS = [
    ("page_end_shadow_rank", "Ending: Shadow Rank", "Kaelen passes as a technically excellent infiltrator. The village gains a sharp blade, but not yet someone who knows when a blade should stay sheathed."),
    ("page_end_council_tool", "Ending: The Council's Tool", "Kaelen obeys every sealed order and graduates quickly. Sora praises him in public, then files his conscience with the other equipment."),
    ("page_end_rival_victory", "Ending: Varek Takes The Bell", "Varek wins the visible contest. Kaelen survives the exam but leaves knowing he mistook another student's pace for his own path."),
    ("page_end_merciful_failure", "Ending: Merciful Failure", "Kaelen protects civilians and fails the posted score. The academy calls it failure; the market starts leaving lamps for him at doorways."),
    ("page_end_village_witness", "Ending: The Village Witnesses", "Kaelen exposes the false order without collapsing the council. The village does not fully trust him yet, but it begins watching the examiners too."),
    ("page_end_silent_veil", "Secret Ending: The Silent Veil", "Kaelen passes by protecting the village from its own exam: unseen when stealth matters, loyal when orders lie, focused when fear shouts, merciful when force would be easier. Mira awards no headband in public. At dawn, every bell in the village is tied silent."),
]


def ptr_const(value: float | str) -> dict[str, Any]:
    if isinstance(value, str):
        return {"pointer_type": "String Constant", "script_element_type": "Pointer", "value": value}
    return {"pointer_type": "Bounded Number Constant", "script_element_type": "Pointer", "value": round(value, 4)}


def bptr(character: str, keyring: list[str], coefficient: float = 1.0) -> dict[str, Any]:
    return {
        "pointer_type": "Bounded Number Pointer",
        "script_element_type": "Pointer",
        "character": character,
        "keyring": keyring,
        "coefficient": round(coefficient, 4),
    }


def add_node(*operands: dict[str, Any]) -> dict[str, Any]:
    return {"operator_type": "Addition", "script_element_type": "Operator", "operands": list(operands)}


def abs_node(node: dict[str, Any]) -> dict[str, Any]:
    return {"operator_type": "Absolute Value", "script_element_type": "Operator", "operands": [node]}


def comparator(prop: str, threshold: float = 1.4) -> dict[str, Any]:
    return {
        "operator_type": "Arithmetic Comparator",
        "script_element_type": "Operator",
        "operands": [abs_node(bptr("char_kaelen", [prop], 1.0)), ptr_const(threshold)],
        "operator_subtype": "Less Than or Equal To",
    }


def desirability(prop: str, base: float) -> dict[str, Any]:
    other = "Loyalty" if prop != "Loyalty" else "Stealth"
    return add_node(
        ptr_const(base),
        bptr("char_kaelen", [prop], 0.32),
        bptr("char_mira", [prop, "char_kaelen"], 0.24),
        bptr("char_village", [other, "char_kaelen", "char_mira"], 0.18),
        bptr("char_varek", ["Rivalry", "char_kaelen"], -0.1),
        abs_node(bptr("char_kaelen", ["VillageTrust"], 0.12)),
    )


def nudge(character: str, prop: str, delta: float, support: str | None = None) -> dict[str, Any]:
    operands = [bptr(character, [prop], 1.0), ptr_const(delta)]
    if support:
        operands.append(bptr(character, [support], 0.05 if delta >= 0 else -0.05))
    return {
        "effect_type": "Bounded Number Effect",
        "Set": bptr(character, [prop], 1.0),
        "to": {"operator_type": "Nudge", "script_element_type": "Operator", "operands": operands},
    }


def blend(character: str, prop: str, delta: float, support: str) -> dict[str, Any]:
    return {
        "effect_type": "Bounded Number Effect",
        "Set": bptr(character, [prop], 1.0),
        "to": {
            "operator_type": "Blend",
            "script_element_type": "Operator",
            "operands": [bptr(character, [prop], 0.72), add_node(ptr_const(delta), bptr(character, [support], 0.18))],
        },
    }


def option(scene_id: str, index: int, label: str, prop: str, next_id: str, fallback_id: str, secret_id: str | None) -> dict[str, Any]:
    patterns = [
        ("Stealth", 0.06, "Focus", 0.025),
        ("Loyalty", 0.055, "VillageTrust", 0.03),
        ("Rivalry", 0.06, "Mercy", -0.035),
        ("Mercy", 0.06, "VillageTrust", 0.035),
    ]
    main, d1, support, d2 = patterns[index - 1]
    target = secret_id if secret_id and index == 4 else next_id
    reactions = []
    for ridx, tone in enumerate(("clean", "costly", "botched"), start=1):
        mod = 1.0 if tone == "clean" else 0.45 if tone == "costly" else -0.4
        consequence = target if tone != "botched" else fallback_id
        reactions.append(
            {
                "id": f"{scene_id}_opt_{index:02d}_r{ridx}",
                "text_script": ptr_const(
                    f"{tone.title()}: {label} The exam records {main.lower()} but also tests whether the move protects the team, the mission, or only Kaelen's pride."
                ),
                "desirability_script": desirability(main, 0.08 * mod),
                "after_effects": [
                    nudge("char_kaelen", main, d1 * mod, support),
                    blend("char_kaelen", support, d2 * mod, main),
                    nudge("char_mira", "VillageTrust", 0.02 * mod, main),
                    nudge("char_varek", "Rivalry", (0.025 if main == "Rivalry" else -0.01) * mod),
                    blend("char_village", "VillageTrust", 0.02 * mod, main),
                ],
                "consequence_id": consequence,
            }
        )
    return {
        "id": f"{scene_id}_opt_{index:02d}",
        "text_script": ptr_const(label),
        "visibility_script": comparator(main, 1.8),
        "performability_script": comparator(support, 1.8),
        "reactions": reactions,
        "creation_index": index,
        "creation_time": time.time(),
        "modified_time": time.time(),
    }


def encounter(idx: int, scene: tuple[str, str, str, str], next_id: str, fallback_id: str, secret_id: str | None) -> dict[str, Any]:
    sid, title, body, prop = scene
    labels = [
        f"Take the quiet route through {title.lower()}, preserving evidence before ego.",
        f"Coordinate with the team even if it gives Varek a visible advantage.",
        f"Force the pace and dare the examiners to score results over restraint.",
        f"Protect the vulnerable witness even if the mission clock turns hostile.",
    ]
    return {
        "id": sid,
        "title": title,
        "text_script": ptr_const(body + " The exam is scored by bells, witnesses, and hidden ledgers; the obvious task is never the only task."),
        "acceptability_script": comparator(prop, 2.0),
        "desirability_script": desirability(prop, 0.58),
        "options": [option(sid, i, labels[i - 1], prop, next_id, fallback_id, secret_id) for i in range(1, 5)],
        "connected_spools": ["spool_main"],
        "earliest_turn": max(0, idx - 2),
        "latest_turn": idx + 8,
        "creation_index": idx,
        "creation_time": time.time(),
        "modified_time": time.time(),
        "graph_position_x": 160 + (idx % 6) * 260,
        "graph_position_y": 180 + (idx // 6) * 220,
    }


def ending(idx: int, eid: str, title: str, body: str) -> dict[str, Any]:
    return {
        "id": eid,
        "title": title,
        "text_script": ptr_const(body),
        "acceptability_script": comparator("VillageTrust", 2.5),
        "desirability_script": desirability("VillageTrust", 0.7),
        "options": [],
        "connected_spools": ["spool_endings"],
        "earliest_turn": 12,
        "latest_turn": 120,
        "creation_index": 100 + idx,
        "creation_time": time.time(),
        "modified_time": time.time(),
        "graph_position_x": 180 + idx * 220,
        "graph_position_y": 1180,
    }


def design_summary() -> dict[str, Any]:
    if not DESIGN_PACKET.exists():
        return {}
    try:
        packet = json.loads(DESIGN_PACKET.read_text(encoding="utf-8-sig"))
        content = packet.get("choices", [{}])[0].get("message", {}).get("content", "")
        try:
            return json.loads(content)
        except Exception:
            return {"raw_content": content}
    except Exception as exc:
        return {"error": str(exc)}


def main() -> int:
    now = time.time()
    design = design_summary()
    scene_ids = [scene[0] for scene in SCENES]
    encounters: list[dict[str, Any]] = []
    for idx, scene in enumerate(SCENES, start=1):
        next_id = scene_ids[idx] if idx < len(scene_ids) else ENDINGS[0][0]
        fallback_id = scene_ids[min(idx, len(scene_ids) - 1)]
        secret_id = "page_end_silent_veil" if scene[0] in {"page_021_final_silence", "page_022_under_village_route"} else None
        if scene[0] == "page_020_council_false_order":
            next_id = "page_021_final_silence"
        if scene[0] == "page_021_final_silence":
            next_id = "page_022_under_village_route"
        if scene[0] == "page_022_under_village_route":
            next_id = "page_end_village_witness"
        encounters.append(encounter(idx, scene, next_id, fallback_id, secret_id))

    late_targets = [row[0] for row in ENDINGS[:-1]]
    for offset, enc in enumerate(encounters[17:22]):
        for opt_idx, opt in enumerate(enc["options"]):
            if enc["id"] in {"page_021_final_silence", "page_022_under_village_route"} and opt_idx == 3:
                continue
            if opt_idx > 0:
                target = late_targets[(offset + opt_idx) % len(late_targets)]
                for reaction in opt["reactions"]:
                    if reaction["consequence_id"].startswith("page_0"):
                        reaction["consequence_id"] = target

    for idx, end in enumerate(ENDINGS, start=1):
        encounters.append(ending(idx, *end))

    char_props = {prop: 0 for prop, _ in PROPS}
    char_props.update({f"p{prop}": {} for prop, _ in PROPS})
    char_props.update({f"p2{prop}": {} for prop, _ in PROPS})
    world: dict[str, Any] = {
        "IFID": "SW-NINJA-EXAM-QWEN9B-20260504",
        "storyworld_title": "The Silent Veil Ninja Exam",
        "storyworld_author": "Qwen3.5-9B design packet + Codex deterministic materializer",
        "sweepweave_version": "0.1.9",
        "creation_time": now,
        "modified_time": now,
        "debug_mode": False,
        "display_mode": 1,
        "css_theme": "slate",
        "font_size": "16",
        "language": "en",
        "rating": "general",
        "about_text": ptr_const("An original hidden-village ninja exam storyworld inspired by broad shonen ninja motifs without using copyrighted canon names or plot events. Kaelen must pass by balancing stealth, loyalty, focus, mercy, rivalry, and village trust."),
        "characters": [
            {
                "creation_index": i,
                "creation_time": now,
                "id": cid,
                "modified_time": now,
                "name": name,
                "pronoun": pronoun,
                "bnumber_properties": dict(char_props),
            }
            for i, (cid, name, pronoun) in enumerate(CHARS)
        ],
        "authored_properties": [
            {
                "id": prop,
                "property_name": prop,
                "property_type": "bounded number",
                "default_value": 0,
                "depth": 0,
                "attribution_target": "all cast members",
                "affected_characters": [],
                "creation_index": i,
                "creation_time": now,
                "modified_time": now,
                "description": desc,
            }
            for i, (prop, desc) in enumerate(PROPS)
        ],
        "spools": [
            {
                "id": "spool_main",
                "spool_name": "The Silent Veil Ninja Exam",
                "spool_type": "General",
                "starts_active": True,
                "creation_index": 0,
                "creation_time": now,
                "modified_time": now,
                "encounters": scene_ids,
            },
            {
                "id": "spool_endings",
                "spool_name": "Exam Verdicts",
                "spool_type": "General",
                "starts_active": False,
                "creation_index": 1,
                "creation_time": now,
                "modified_time": now,
                "encounters": [row[0] for row in ENDINGS],
            },
        ],
        "encounters": encounters,
        "meta": {
            "qwen9b_design_packet": str(DESIGN_PACKET),
            "qwen9b_design_summary": design,
            "copyright_boundary": "No Naruto canon names, villages, clans, powers, or plot events are used.",
            "secret_route": "Balance stealth, loyalty, focus, and mercy through the final silence into the under-village route.",
        },
    }
    OUT.write_text(json.dumps(world, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
