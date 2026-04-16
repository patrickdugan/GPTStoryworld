#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

COUNTER_SIGNAL = "Counter_Signal"
RECEIVER_ASSEMBLY = "Receiver_Assembly"


def ptr_string(text: str) -> Dict[str, Any]:
    return {"script_element_type": "Pointer", "pointer_type": "String Constant", "value": text}


def ptr_num_const(value: float) -> Dict[str, Any]:
    return {"script_element_type": "Pointer", "pointer_type": "Bounded Number Constant", "value": float(value)}


def ptr_keyring(char_id: str, keyring: List[str], coefficient: float = 1.0) -> Dict[str, Any]:
    return {
        "script_element_type": "Pointer",
        "pointer_type": "Bounded Number Pointer",
        "character": char_id,
        "keyring": keyring,
        "coefficient": float(coefficient),
    }


def ptr_num(char_id: str, key: str, coefficient: float = 1.0) -> Dict[str, Any]:
    return ptr_keyring(char_id, [key], coefficient=coefficient)


def op(operator_type: str, operands: List[Any], subtype: str | None = None) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "script_element_type": "Operator",
        "operator_type": operator_type,
        "operands": operands,
    }
    if subtype is not None:
        payload["operator_subtype"] = subtype
    return payload


def cmp_gte(char_id: str, key: str, value: float) -> Dict[str, Any]:
    return op("Arithmetic Comparator", [ptr_num(char_id, key), ptr_num_const(value)], "Greater Than or Equal To")


def cmp_lte(char_id: str, key: str, value: float) -> Dict[str, Any]:
    return op("Arithmetic Comparator", [ptr_num(char_id, key), ptr_num_const(value)], "Less Than or Equal To")


def cmp_keyring_gte(char_id: str, keyring: List[str], value: float) -> Dict[str, Any]:
    return op("Arithmetic Comparator", [ptr_keyring(char_id, keyring), ptr_num_const(value)], "Greater Than or Equal To")


def cmp_keyring_lte(char_id: str, keyring: List[str], value: float) -> Dict[str, Any]:
    return op("Arithmetic Comparator", [ptr_keyring(char_id, keyring), ptr_num_const(value)], "Less Than or Equal To")


def nudge_effect(char_id: str, key: str, amount: float) -> Dict[str, Any]:
    target = ptr_num(char_id, key)
    return {
        "effect_type": "Bounded Number Effect",
        "Set": target,
        "to": op("Nudge", [target, ptr_num_const(amount)]),
    }


def nudge_keyring_effect(char_id: str, keyring: List[str], amount: float) -> Dict[str, Any]:
    target = ptr_keyring(char_id, keyring)
    return {
        "effect_type": "Bounded Number Effect",
        "Set": target,
        "to": op("Nudge", [target, ptr_num_const(amount)]),
    }


def ensure_effect_floor(reaction: Dict[str, Any], char_id: str, keys: List[str]) -> None:
    effects = reaction.setdefault("after_effects", [])
    idx = 0
    while len(effects) < 5:
        key = keys[idx % len(keys)]
        delta = 0.04 if idx % 2 == 0 else -0.03
        effects.append(nudge_effect(char_id, key, delta))
        idx += 1


def ensure_belief_scaffold(data: Dict[str, Any], now: float) -> None:
    belief_props = ["pTrust", "pSuspicion", "pSubmission", "pPrivate_Self"]
    scaffold_props = [COUNTER_SIGNAL, RECEIVER_ASSEMBLY, *belief_props]
    authored = data.get("authored_properties", []) or []
    existing = {str(prop.get("id")) for prop in authored if isinstance(prop, dict)}
    creation_index = len(authored)
    for prop_id in scaffold_props:
        if prop_id in existing:
            continue
        authored.append(
            {
                "id": prop_id,
                "property_name": prop_id,
                "property_type": "bounded number",
                "default_value": 0,
                "depth": 0,
                "attribution_target": "all cast members",
                "affected_characters": [],
                "creation_index": creation_index,
                "creation_time": now,
                "modified_time": now,
            }
        )
        creation_index += 1
    data["authored_properties"] = authored

    for character in data.get("characters", []) or []:
        bprops = character.setdefault("bnumber_properties", {})
        for prop_id in scaffold_props:
            bprops.setdefault(prop_id, 0)


def enrich_encounter_text(encounter: Dict[str, Any], focus: str = "") -> None:
    existing = ""
    if isinstance(encounter.get("text_script"), dict):
        existing = str(encounter["text_script"].get("value", "")).strip()
    if (
        encounter.get("id") in {"page_scene_obrien_false_read", "page_scene_obrien_followup", "page_endings_gate"}
        or str(encounter.get("id", "")).startswith("page_bridge_")
    ) and existing:
        encounter["text_script"] = ptr_string(
            existing
            + " Even this moment has to be played with an eye toward the record it may later become."
        )
        return
    title = str(encounter.get("title", "the scene"))
    extra = f" The focus here is {focus}." if focus else ""
    encounter["text_script"] = ptr_string(
        f"In {title}, Winston has to decide not only what to do, but what story the room will tell about him afterward. "
        "Paperwork, glances, timing, and silence all become evidence in a surveillance state that mistakes legibility for truth. "
        "Each option tests whether he can preserve a private self while feeding the Party, Julia, or O'Brien a strategically distorted read. "
        "A tiny technical gesture here can mature into either incriminating noise or cover for a move much later in the story." + extra
    )


def diversify_effects(reaction: Dict[str, Any]) -> None:
    effects = reaction.get("after_effects", []) or []
    for idx, effect in enumerate(effects):
        if effect.get("effect_type") != "Bounded Number Effect":
            continue
        target = effect.get("Set")
        if not isinstance(target, dict):
            continue
        to = effect.get("to", {})
        delta = 0.04 if idx % 2 == 0 else -0.03
        if isinstance(to, dict):
            operands = to.get("operands", []) or []
            if to.get("operator_type") == "Nudge" and len(operands) >= 2:
                delta = float(operands[1].get("value", delta))
            elif to.get("operator_type") == "Addition" and len(operands) >= 2:
                delta = float(operands[1].get("value", delta))
            elif to.get("operator_type") == "Multiplication" and operands:
                inner = operands[0]
                if isinstance(inner, dict) and inner.get("operator_type") == "Addition":
                    inner_ops = inner.get("operands", []) or []
                    if len(inner_ops) >= 2:
                        delta = float(inner_ops[1].get("value", delta))
        if idx % 3 == 1:
            effect["to"] = op("Addition", [target, ptr_num_const(delta)])
        elif idx % 3 == 2:
            multiplier = 1.01 if delta >= 0 else 0.99
            effect["to"] = op("Multiplication", [op("Addition", [target, ptr_num_const(delta)]), ptr_num_const(multiplier)])


def ensure_third_reaction(option: Dict[str, Any], primary_char: str, keys: List[str], p_inner_suspicion: Dict[str, Any]) -> None:
    reactions = option.get("reactions", []) or []
    if len(reactions) >= 3:
        return
    template = json.loads(json.dumps(reactions[-1]))
    third = clone_reaction(
        template=template,
        reaction_id=f"{option['id']}_r{len(reactions) + 1}",
        text=(
            "A third reading opens: Winston uses posture, omission, and administrative timing to redirect how his motives will be interpreted later. "
            "The move does not change the room's facts, only the confidence with which other people think they understand them."
        ),
        consequence_id=template.get("consequence_id", "wild"),
        desirability=op(
            "Addition",
            [
                template.get("desirability_script", ptr_num_const(0.0)),
                p_inner_suspicion,
                ptr_num(primary_char, "Private_Self", 0.2),
                ptr_num_const(0.02),
            ],
        ),
        char_id=primary_char,
        keys=keys,
    )
    diversify_effects(third)
    reactions.append(third)
    option["reactions"] = reactions


def clone_reaction(template: Dict[str, Any], reaction_id: str, text: str, consequence_id: str, desirability: Dict[str, Any], char_id: str, keys: List[str]) -> Dict[str, Any]:
    rxn = json.loads(json.dumps(template))
    rxn["id"] = reaction_id
    rxn["text_script"] = ptr_string(text)
    rxn["consequence_id"] = consequence_id
    rxn["desirability_script"] = desirability
    ensure_effect_floor(rxn, char_id, keys)
    return rxn


def make_terminal(enc_id: str, title: str, text: str, desirability: Dict[str, Any], acceptability: Any, now: float) -> Dict[str, Any]:
    return {
        "id": enc_id,
        "title": title,
        "creation_index": 0,
        "creation_time": now,
        "modified_time": now,
        "connected_spools": ["spool_endings"],
        "earliest_turn": 0,
        "latest_turn": 0,
        "graph_position_x": 0,
        "graph_position_y": 0,
        "text_script": ptr_string(text),
        "acceptability_script": acceptability,
        "desirability_script": desirability,
        "options": [],
    }


def make_bridge_scene_specs() -> List[Dict[str, str]]:
    bridge_packs: List[Tuple[str, str, List[Tuple[str, str, str]]]] = [
        (
            "page_start",
            "spool_start_followup",
            [
                ("Scene 1A: Corridor After the Scream", "The Two Minutes Hate ends, but its chemistry stays on Winston's skin. The walk back to work becomes a second ritual in which faces cool themselves too quickly and every reset looks practiced.", "surveillance"),
                ("Scene 1B: Lift Cage Silence", "Inside the lift cage no one speaks, which only sharpens the sound of clothing, breath, and restraint. Winston has to decide whether to disappear into the silence or use it as a reading instrument.", "surveillance"),
                ("Scene 1C: Stolen Notebook Glimpse", "A memory of the hidden notebook flashes at the wrong moment. The problem is not merely wanting a private record, but wanting it while the residue of public hatred is still visible.", "memory"),
                ("Scene 1D: First Corrective Edit", "Back at the Ministry, the first correction of the day arrives with bureaucratic innocence. Winston can treat it as routine, or as a place where truth and obedience first separate.", "bureaucracy"),
            ],
        ),
        (
            "page_scene_01",
            "spool_start_followup",
            [
                ("Scene 2A: Comma in the Record", "A tiny punctuation decision changes the emotional weather of a report. Oceania's lies often arrive that small, and Winston's danger is that he notices the difference.", "bureaucracy"),
                ("Scene 2B: Parsons at the Desk", "Parsons fills the air with loyal incompetence and borrowed certainty. The encounter tests whether Winston should match that softness, exceed it, or quietly study what such men make safe for the regime.", "orthodoxy"),
                ("Scene 2C: Ink on the Finger", "A smear of ink threatens to become evidence because everything private now leaves a trace. Winston can either erase it, ignore it, or repurpose it as noise.", "memory"),
                ("Scene 2D: Queue for Soy Victory Lunch", "By the time the lunch queue forms, procedure has already performed half the politics. Even waiting in line demands a theory of visibility.", "surveillance"),
            ],
        ),
        (
            "page_scene_02",
            "spool_start_followup",
            [
                ("Scene 3A: Canteen Table Geometry", "The canteen is a map of what can be seen without seeming to see. Chairs, trays, and conversational distance all become tools for hiding or testing attachment.", "surveillance"),
                ("Scene 3B: Syme Speaks Too Clearly", "Syme's brilliance is operationally dangerous because it lacks camouflage. Listening to him means deciding whether clarity itself is a temptation Winston can afford.", "orthodoxy"),
                ("Scene 3C: Julia Crosses the Aisle", "Julia's movement across the room lands with the force of a coded message, though nothing is said. Winston has to decide whether desire is data, threat, or both.", "julia"),
                ("Scene 3D: Note Hidden in the Palm", "The note's transit is more intimate for being nearly mechanical. Romance in Oceania begins as an exercise in hand discipline.", "julia"),
            ],
        ),
        (
            "page_scene_03",
            "spool_start_followup",
            [
                ("Scene 4A: Walk to Victory Square", "Leaving the Ministry with Julia requires choreography more than courage. Each intersection offers a different balance of appetite, patience, and deniability.", "julia"),
                ("Scene 4B: Gesture at the Junk Shop Window", "Charrington's window seems to contain objects that survived because no one thought them dangerous. Winston has to decide whether useless beauty is refuge or bait.", "memory"),
                ("Scene 4C: Dust Above the Bedstead", "In the rented room, dust itself feels private. The question is whether privacy can exist as atmosphere, or only as a sequence of careful decisions.", "memory"),
                ("Scene 4D: Rat Dream Before Waking", "Before the idyll settles, fear intrudes with animal precision. The future already knows where Winston is weakest, even when the present still feels tender.", "custody"),
            ],
        ),
        (
            "page_scene_04",
            "spool_start_followup",
            [
                ("Scene 5A: Syme's Missing Name", "A missing colleague leaves an absence shaped like a warning. Winston must decide whether to honor disappearance by remembering, or survive it by adjusting immediately.", "orthodoxy"),
                ("Scene 5B: Dictionary Drafts", "Newspeak proofs promise a world where fewer words mean fewer crimes of thought. Working near them is a test of whether Winston can study reduction without becoming reduced.", "orthodoxy"),
                ("Scene 5C: Children as Informers", "The Party's most efficient surveillance often arrives wearing childhood enthusiasm. Winston has to interpret innocence as an institutional technology.", "surveillance"),
                ("Scene 5D: Parsons on the Stairs", "A neighborly exchange in the stairwell becomes another audit of tone. Too much warmth, too little warmth, or the wrong kind of fatigue can all become legible.", "surveillance"),
            ],
        ),
        (
            "page_scene_05",
            "spool_start_followup",
            [
                ("Scene 6A: Market Mud and Orange Peel", "The prole quarter begins with texture rather than revelation: mud, peel, bad gin, and uncurated sound. Winston has to decide how much truth to seek in places the Party treats as background.", "prole"),
                ("Scene 6B: Song Beneath the Window", "A working song drifts upward from the street and makes continuity feel briefly possible. That emotional effect is itself a risk.", "prole"),
                ("Scene 6C: Gin and Fragments", "Memory comes easier after bad gin, but so do sloppy inferences. Winston can either use intoxication as access, or distrust anything that arrives softened.", "memory"),
                ("Scene 6D: Charrington's Patient Smile", "Charrington's manner suggests safety by refusing urgency. Winston has to decide whether patience is what trust looks like, or what traps prefer to call themselves.", "prole"),
            ],
        ),
        (
            "page_scene_06",
            "spool_mid",
            [
                ("Scene 7A: Room Above the Shop", "The rented room becomes a workshop for improvising privacy. Each small comfort forces Winston to choose whether comfort is cover, reward, or strategic blindness.", "julia"),
                ("Scene 7B: Coral in the Glass", "The coral paperweight promises an interior world that is sealed but still visible. Winston has to decide whether to guard that image, share it, or operationalize it.", "memory"),
                ("Scene 7C: Church Bell Without Church", "The quarter preserves forms whose meanings the Party has thinned out. Winston listens for what survives when institution and memory stop matching.", "prole"),
                ("Scene 7D: Book Delivery Ritual", "Even receiving Goldstein's book is a ceremony of inference. O'Brien's curation matters as much as the doctrine it conveys.", "theory"),
            ],
        ),
        (
            "page_scene_07",
            "spool_mid",
            [
                ("Scene 8A: Reading in Turns", "Goldstein's pages move slowly because Winston keeps stopping to ask which parts explain reality and which parts merely explain how dissidents want to feel about reality.", "theory"),
                ("Scene 8B: Tactical Marginalia", "The temptation is to convert theory into self-flattery. Winston instead has to decide whether any of the text can be used without becoming another script supplied by power.", "theory"),
                ("Scene 8C: O'Brien's Pause at a Sentence", "A remembered pause from O'Brien reshapes how the book is read. Winston has to decide whether that pause was solidarity, profiling, or both at once.", "spycraft"),
                ("Scene 8D: Summons by Telescreen", "The summons does not accuse; it merely arranges the next room. That bureaucratic politeness is what makes it frightening.", "spycraft"),
            ],
        ),
        (
            "page_scene_08",
            "spool_mid",
            [
                ("Scene 9A: Corridor to the Flat", "On the way to O'Brien's flat, Winston has enough time to choose a posture but not enough time to trust any single posture completely.", "spycraft"),
                ("Scene 9B: Choosing a Voice", "Before speaking to O'Brien, Winston has to decide which version of fatigue or conviction he wants to sound like. Voice becomes a forgery problem.", "spycraft"),
                ("Scene 9C: Julia as Decoy in Thought", "Julia can be used as an alibi, a weakness, a loyalty, or a decoy. Thinking through those possibilities is already a moral cost.", "julia"),
                ("Scene 9D: The Door Before O'Brien Opens", "The last seconds before the meeting are clean enough to feel unreal. Winston has to choose not only what he believes, but what he is willing to let O'Brien believe about that belief.", "spycraft"),
            ],
        ),
        (
            "page_scene_obrien_false_read",
            "spool_mid",
            [
                ("Scene 10A: Aftertaste of the Interview", "Leaving O'Brien is more dangerous than entering him. Winston must now live inside the interpretation he has just encouraged.", "spycraft"),
                ("Scene 10B: File Corrections That Know Too Much", "Routine ministry work starts to feel annotated by the interview, as though neutral paperwork has acquired a private witness.", "bureaucracy"),
                ("Scene 10C: Delay at the Pneumatic Tube", "A trivial delay becomes an opportunity to test whether small administrative frictions are being observed more closely than before.", "bureaucracy"),
                ("Scene 10D: A Face Seen Twice", "Someone who should have remained background appears again in a different corridor. Winston has to decide whether recurrence is surveillance, paranoia, or an invitation to overreact.", "surveillance"),
            ],
        ),
        (
            "page_scene_09",
            "spool_mid",
            [
                ("Scene 11A: Chestnut Tree Rumor", "The Chestnut Tree exists as rumor before it becomes destiny. Winston has to decide whether to treat that rumor as warning, prophecy, or contamination.", "orthodoxy"),
                ("Scene 11B: Canteen Without Appetite", "The canteen returns stripped of its earlier flirtations and chatter. Hunger, fear, and habit no longer point in the same direction.", "custody"),
                ("Scene 11C: Julia's Name as Lever", "Once Julia's name becomes imaginable as leverage, love and strategy stop being cleanly separable. Winston has to decide what may be spent in thought and what may not.", "julia"),
                ("Scene 11D: Boots in the Corridor", "Sound arrives before authority does. Winston has to read the rhythm of boots the way he once read expressions.", "custody"),
            ],
        ),
        (
            "page_scene_10",
            "spool_mid",
            [
                ("Scene 12A: Paperweight as Procedure", "The paperweight changes meaning again under pressure. It can be memory, superstition, doctrine, or a useless thing that still organizes resistance.", "memory"),
                ("Scene 12B: Transcript of the Wrong Fear", "Interrogation works by naming fears before the prisoner is ready to confirm them. Winston has to decide whether to deny, redirect, or partially endorse the narrative offered to him.", "custody"),
                ("Scene 12C: White Tile Light", "A room of white tile abolishes atmosphere and leaves only timing. Winston has to build an interior life out of sequence rather than place.", "custody"),
                ("Scene 12D: Counting Between Questions", "Counting becomes a way to keep ownership over interval when ownership over content is no longer secure.", "custody"),
            ],
        ),
        (
            "page_scene_11",
            "spool_mid",
            [
                ("Scene 13A: Rat Knowledge Ledger", "The regime knows exactly which fear belongs to which body. Winston has to decide whether foreknowledge can be used against the interrogator, or only against himself.", "custody"),
                ("Scene 13B: Confession Syntax", "What matters is not merely what Winston says, but which grammar he is coaxed into borrowing. A confession is also a style guide.", "orthodoxy"),
                ("Scene 13C: What Breaks First", "Different selves fracture at different pressures: erotic self, political self, remembering self. Winston has to decide which fracture can still be narratively useful.", "spycraft"),
                ("Scene 13D: Self After Pain", "Pain is supposed to simplify. Winston's remaining work is to prevent simplification from becoming the final truth.", "memory"),
            ],
        ),
        (
            "page_scene_12",
            "spool_mid",
            [
                ("Scene 14A: Quiet Clerical Retest", "A small clerical question appears where a dramatic interrogation would once have stood. That reduction in overt pressure is the new trap.", "spycraft"),
                ("Scene 14B: Julia Remembered Strategically", "Julia returns as memory, loss, and instrument all at once. Winston has to decide whether even inwardly he can keep those categories distinct.", "julia"),
                ("Scene 14C: Before the Seam is Checked", "The story narrows toward O'Brien's second look. Winston has to enter that room carrying a self that is neither fully candid nor fully fictional.", "spycraft"),
            ],
        ),
    ]

    specs: List[Dict[str, str]] = []
    bridge_index = 1
    for after_id, spool_id, scenes in bridge_packs:
        for title, text, mode in scenes:
            specs.append(
                {
                    "id": f"page_bridge_{bridge_index:03d}",
                    "after_id": after_id,
                    "spool_id": spool_id,
                    "title": title,
                    "text": text,
                    "mode": mode,
                }
            )
            bridge_index += 1
    return specs


def make_bridge_option(
    text: str,
    r1: str,
    r2: str,
    r3: str,
    desirability: Dict[str, Any],
    effects: List[Dict[str, Any]],
) -> Dict[str, Any]:
    return {
        "text": text,
        "reaction_texts": [r1, r2, r3],
        "desirability": desirability,
        "effects": effects,
    }


def build_bridge_mode_payloads(
    primary_char: str,
    secondary_char: str,
    spy_char: str,
    p_self_guard: Dict[str, Any],
    p_obrien_trust: Dict[str, Any],
    p_obrien_suspicion: Dict[str, Any],
    p_julia_trust: Dict[str, Any],
    p_obrien_reads_submission: Dict[str, Any],
    p_obrien_reads_julia: Dict[str, Any],
) -> Dict[str, List[Dict[str, Any]]]:
    return {
        "surveillance": [
            make_bridge_option(
                "Blend with the corridor's routine and let the watchers file you as ordinary.",
                "Winston uses banality as camouflage and gives the room no obvious angle to hold.",
                "He trusts ordinary timing more than conspicuous conviction.",
                "The disguise works because it looks less like fear than like social competence.",
                op("Addition", [ptr_num(primary_char, "Exposure", -0.2), p_obrien_trust, ptr_num_const(0.03)]),
                [nudge_effect(primary_char, "Exposure", -0.01), nudge_effect(primary_char, "Submission", 0.01), nudge_keyring_effect(primary_char, ["pTrust", spy_char], 0.01), nudge_keyring_effect(primary_char, ["pSuspicion"], 0.01)],
            ),
            make_bridge_option(
                "Watch who resets too quickly and keep the knowledge to yourself.",
                "Winston reads the room instead of narrating himself to it.",
                "Observation becomes a private luxury he cannot confess to possessing.",
                "He learns more than he can immediately use, which is often the cost of staying alive.",
                op("Addition", [p_obrien_suspicion, ptr_num(primary_char, "Defiance", 0.25), p_self_guard, ptr_num_const(0.04)]),
                [nudge_keyring_effect(primary_char, ["pSuspicion"], 0.02), nudge_keyring_effect(primary_char, ["pSuspicion", spy_char], 0.02), nudge_effect(primary_char, "Private_Self", 0.01), nudge_effect(primary_char, "Defiance", 0.01)],
            ),
            make_bridge_option(
                "Leave one small ambiguity in your posture and see who overreads it.",
                "Winston feeds the room a shape that can be interpreted in more than one direction.",
                "The move is dangerous because watchers love certainty enough to supply it themselves.",
                "He spends a trace of safety to learn what sort of reader he is among.",
                op("Addition", [p_obrien_trust, p_obrien_reads_submission, ptr_num(primary_char, "Private_Self", 0.2), ptr_num_const(0.03)]),
                [nudge_keyring_effect(primary_char, ["pSuspicion"], 0.015), nudge_keyring_effect(primary_char, ["pTrust", spy_char], 0.02), nudge_keyring_effect(primary_char, ["pSubmission", spy_char, primary_char], 0.015), nudge_effect(primary_char, "Exposure", 0.01)],
            ),
        ],
        "bureaucracy": [
            make_bridge_option(
                "Complete the correction cleanly and hide in procedural excellence.",
                "Winston lets correctness serve as camouflage and gives the file nothing memorable.",
                "Perfection is used here not as devotion but as refusal of narrative excess.",
                "The best bureaucratic lie often looks bored with itself.",
                op("Addition", [ptr_num(primary_char, "Submission", 0.25), p_obrien_trust, ptr_num(primary_char, "Exposure", -0.15), ptr_num_const(0.03)]),
                [nudge_effect(primary_char, "Submission", 0.02), nudge_effect(primary_char, "Party_Orthodoxy", 0.01), nudge_effect(primary_char, "Exposure", -0.01), nudge_keyring_effect(primary_char, ["pTrust", spy_char], 0.01)],
            ),
            make_bridge_option(
                "Insert a hairline discrepancy too small to justify alarm.",
                "Winston places a flaw where only a hungry regime should bother to find it.",
                "The discrepancy matters less as sabotage than as a probe of appetite.",
                "He risks a factual bruise to learn who is reading unusually closely.",
                op("Addition", [p_obrien_suspicion, p_self_guard, ptr_num(primary_char, "Private_Self", 0.25), ptr_num_const(0.05)]),
                [nudge_effect(primary_char, "Defiance", 0.02), nudge_keyring_effect(primary_char, ["pPrivate_Self"], 0.02), nudge_keyring_effect(primary_char, ["pSuspicion"], 0.02), nudge_keyring_effect(primary_char, ["pSuspicion", spy_char], 0.02)],
            ),
            make_bridge_option(
                "Overcompensate with zeal and learn who relaxes around it.",
                "Winston tries on excess loyalty as a listening device rather than a creed.",
                "Zeal can loosen other people's caution before it damages your own center.",
                "The trick is to make orthodoxy seem available without making it permanent.",
                op("Addition", [p_obrien_trust, p_obrien_reads_submission, ptr_num(primary_char, "Party_Orthodoxy", 0.15), ptr_num_const(0.02)]),
                [nudge_effect(primary_char, "Party_Orthodoxy", 0.02), nudge_keyring_effect(primary_char, ["pSubmission", spy_char, primary_char], 0.02), nudge_keyring_effect(primary_char, ["pTrust", spy_char], 0.02), nudge_effect(primary_char, "Private_Self", -0.01)],
            ),
        ],
        "julia": [
            make_bridge_option(
                "Advance toward Julia, but only by the smallest operational step.",
                "Winston treats intimacy as a line to be laid carefully, not a flood to surrender to.",
                "The romance survives here by respecting logistics as much as feeling.",
                "He lets desire move at a speed the surveillance state cannot instantly metabolize.",
                op("Addition", [ptr_num(primary_char, "Trust", 0.25), p_julia_trust, ptr_num(primary_char, "Private_Self", 0.2), ptr_num_const(0.04)]),
                [nudge_effect(primary_char, "Trust", 0.02), nudge_effect(primary_char, "Private_Self", 0.02), nudge_keyring_effect(primary_char, ["pTrust", secondary_char], 0.02), nudge_effect(primary_char, "Exposure", 0.01)],
            ),
            make_bridge_option(
                "Delay the intimacy and preserve the line instead of the feeling.",
                "Winston chooses discipline over immediacy, which is its own kind of tenderness in Oceania.",
                "The delay protects not only the affair but the possibility that it remains more than evidence.",
                "He refuses to spend the relationship all at once.",
                op("Addition", [p_self_guard, p_julia_trust, ptr_num(primary_char, "Exposure", -0.15), ptr_num_const(0.03)]),
                [nudge_effect(primary_char, "Exposure", -0.01), nudge_keyring_effect(primary_char, ["pPrivate_Self"], 0.02), nudge_effect(primary_char, "Trust", 0.01), nudge_keyring_effect(primary_char, ["pTrust", secondary_char], 0.01)],
            ),
            make_bridge_option(
                "Spend a little visible sentiment as camouflage and keep the core hidden.",
                "Winston rents out the appearance of romance as cover while trying not to bankrupt the thing itself.",
                "The decoy works only if emotion is legible at the surface and illegible at the center.",
                "He gives surveillance a usable outline and hopes it mistakes outline for substance.",
                op("Addition", [p_obrien_reads_julia, p_obrien_trust, ptr_num(primary_char, "Private_Self", 0.15), ptr_num_const(0.02)]),
                [nudge_keyring_effect(primary_char, ["pSuspicion", spy_char, secondary_char], 0.03), nudge_keyring_effect(primary_char, ["pTrust", spy_char], 0.01), nudge_keyring_effect(primary_char, ["pPrivate_Self"], 0.01), nudge_effect(primary_char, "Exposure", 0.02)],
            ),
        ],
        "memory": [
            make_bridge_option(
                "Memorize the private detail and refuse to flatten it.",
                "Winston treats memory as a live object rather than a nostalgic theme.",
                "The preserved detail matters because it resists the state's desire to become the only archive.",
                "He keeps hold of something useless enough to remain morally clarifying.",
                op("Addition", [ptr_num(primary_char, "Private_Self", 0.3), p_self_guard, ptr_num(primary_char, "Defiance", 0.15), ptr_num_const(0.05)]),
                [nudge_effect(primary_char, "Private_Self", 0.03), nudge_effect(primary_char, "Defiance", 0.01), nudge_keyring_effect(primary_char, ["pPrivate_Self"], 0.02), nudge_keyring_effect(primary_char, ["pSuspicion"], 0.01)],
            ),
            make_bridge_option(
                "Translate the memory into safer, less prosecutable language.",
                "Winston does not abandon the memory; he changes its surface grammar so it can travel more safely.",
                "The maneuver preserves meaning by sacrificing immediacy.",
                "He allows the past a bureaucratic disguise in order to keep it alive.",
                op("Addition", [p_self_guard, p_obrien_reads_submission, ptr_num(primary_char, "Exposure", -0.1), ptr_num_const(0.03)]),
                [nudge_effect(primary_char, "Submission", 0.01), nudge_effect(primary_char, "Exposure", -0.01), nudge_keyring_effect(primary_char, ["pPrivate_Self"], 0.01), nudge_keyring_effect(primary_char, ["pSubmission", spy_char, primary_char], 0.01)],
            ),
            make_bridge_option(
                "Hide the memory inside a useless object or habit.",
                "Winston lets material trivia carry what direct statement cannot.",
                "Objects become covert storage because sentiment alone is too easy to expose.",
                "The choice is less romantic than procedural: where can a private self be cached?",
                op("Addition", [ptr_num(primary_char, "Private_Self", 0.25), p_julia_trust, p_obrien_suspicion, ptr_num_const(0.04)]),
                [nudge_effect(primary_char, "Private_Self", 0.02), nudge_keyring_effect(primary_char, ["pTrust", secondary_char], 0.01), nudge_keyring_effect(primary_char, ["pSuspicion", spy_char], 0.01), nudge_effect(primary_char, "Exposure", 0.0)],
            ),
        ],
        "prole": [
            make_bridge_option(
                "Listen to the proles for texture, not prophecy.",
                "Winston resists turning the proles into a fantasy of rescue and listens instead for ordinary survival.",
                "The texture matters because it reveals a human rhythm the Party cannot fully standardize.",
                "He takes continuity as evidence, not as consolation.",
                op("Addition", [ptr_num(primary_char, "Defiance", 0.25), ptr_num(primary_char, "Private_Self", 0.15), p_self_guard, ptr_num_const(0.04)]),
                [nudge_effect(primary_char, "Defiance", 0.02), nudge_effect(primary_char, "Private_Self", 0.01), nudge_keyring_effect(primary_char, ["pSuspicion"], 0.01), nudge_effect(primary_char, "Exposure", 0.0)],
            ),
            make_bridge_option(
                "Buy the relic and let nostalgia do tactical work.",
                "Winston uses the purchase not merely as sentiment but as a device for stabilizing an interior world.",
                "The relic is useful because the Party underestimates how much structure useless objects can hold.",
                "He turns nostalgia into an instrument without entirely profaning it.",
                op("Addition", [ptr_num(primary_char, "Private_Self", 0.25), p_self_guard, p_julia_trust, ptr_num_const(0.03)]),
                [nudge_effect(primary_char, "Private_Self", 0.02), nudge_keyring_effect(primary_char, ["pPrivate_Self"], 0.02), nudge_effect(primary_char, "Trust", 0.01), nudge_effect(primary_char, "Exposure", 0.01)],
            ),
            make_bridge_option(
                "Wander where surveillance grows lazy and study the slack.",
                "Winston values slack not as freedom but as diagnostic evidence of how power allocates attention.",
                "He learns from neglect rather than from rebellion itself.",
                "The expedition yields no heroic revelation, only operational asymmetry.",
                op("Addition", [p_obrien_suspicion, ptr_num(primary_char, "Defiance", 0.2), ptr_num(primary_char, "Exposure", -0.05), ptr_num_const(0.03)]),
                [nudge_keyring_effect(primary_char, ["pSuspicion", spy_char], 0.02), nudge_effect(primary_char, "Exposure", 0.01), nudge_effect(primary_char, "Defiance", 0.01), nudge_keyring_effect(primary_char, ["pSuspicion"], 0.01)],
            ),
        ],
        "theory": [
            make_bridge_option(
                "Read for tactical structure, not redemption.",
                "Winston treats theory as a tool kit rather than a sacrament.",
                "The coldness of that choice protects him from imagining explanation itself is rescue.",
                "He wants usable pattern, not permission to feel chosen.",
                op("Addition", [p_obrien_suspicion, ptr_num(primary_char, "Private_Self", 0.15), ptr_num(primary_char, "Defiance", 0.1), ptr_num_const(0.04)]),
                [nudge_keyring_effect(primary_char, ["pSuspicion", spy_char], 0.02), nudge_effect(primary_char, "Private_Self", 0.01), nudge_keyring_effect(primary_char, ["pSubmission", spy_char, primary_char], -0.01), nudge_effect(primary_char, "Defiance", 0.01)],
            ),
            make_bridge_option(
                "Use abstraction to keep your real loyalties offstage.",
                "Winston lets ideas occupy the visible part of the conversation so real commitments can remain elsewhere.",
                "Abstraction becomes camouflage because it is easier to admire than to operationalize.",
                "He hides the small human center behind a large political vocabulary.",
                op("Addition", [p_self_guard, ptr_num(primary_char, "Exposure", -0.1), p_obrien_trust, ptr_num_const(0.03)]),
                [nudge_effect(primary_char, "Exposure", -0.01), nudge_keyring_effect(primary_char, ["pPrivate_Self"], 0.01), nudge_keyring_effect(primary_char, ["pTrust", spy_char], 0.01), nudge_effect(primary_char, "Party_Orthodoxy", 0.0)],
            ),
            make_bridge_option(
                "Read the curator more carefully than the doctrine.",
                "Winston uses the book as a reflective surface for O'Brien rather than a destination in itself.",
                "The lesson is taken less from argument than from staging, emphasis, and omission.",
                "He assumes curation is confession by other means.",
                op("Addition", [p_obrien_suspicion, p_obrien_trust, ptr_num(primary_char, "Defiance", 0.15), ptr_num_const(0.04)]),
                [nudge_keyring_effect(primary_char, ["pSuspicion"], 0.02), nudge_keyring_effect(primary_char, ["pSuspicion", spy_char], 0.03), nudge_keyring_effect(primary_char, ["pTrust", spy_char], 0.01), nudge_effect(primary_char, "Defiance", 0.01)],
            ),
        ],
        "spycraft": [
            make_bridge_option(
                "Offer a controlled tell and make the watcher commit to it.",
                "Winston supplies a clue whose usefulness depends on someone else wanting certainty too quickly.",
                "The tell is measured not by its truth but by the theory it invites.",
                "He trades a little safety for a more informative kind of risk.",
                op("Addition", [p_obrien_trust, p_obrien_reads_submission, ptr_num(primary_char, "Private_Self", 0.15), ptr_num_const(0.04)]),
                [nudge_keyring_effect(primary_char, ["pTrust", spy_char], 0.02), nudge_keyring_effect(primary_char, ["pSubmission", spy_char, primary_char], 0.02), nudge_keyring_effect(primary_char, ["pSuspicion"], 0.01), nudge_effect(primary_char, "Exposure", 0.01)],
            ),
            make_bridge_option(
                "Force the watcher to distinguish noise from confession.",
                "Winston creates a field of minor uncertainty and watches to see what gets treated as signal.",
                "The method is less about deceiving the other man than obliging him to reveal his model.",
                "He turns ambiguity into an interview technique of his own.",
                op("Addition", [p_obrien_suspicion, p_self_guard, ptr_num(primary_char, "Private_Self", 0.2), ptr_num_const(0.05)]),
                [nudge_keyring_effect(primary_char, ["pSuspicion", spy_char], 0.03), nudge_keyring_effect(primary_char, ["pPrivate_Self"], 0.01), nudge_effect(primary_char, "Defiance", 0.01), nudge_effect(primary_char, "Exposure", 0.0)],
            ),
            make_bridge_option(
                "Stay slightly opaque and make certainty expensive.",
                "Winston refuses the clean outline that would make profiling easy, though opacity always carries friction.",
                "The move protects the center by making every reading less stable than the regime would like.",
                "He chooses to be harder to model even if that means being harder to trust.",
                op("Addition", [p_self_guard, ptr_num(primary_char, "Private_Self", 0.2), ptr_num(primary_char, "Defiance", 0.1), ptr_num_const(0.03)]),
                [nudge_keyring_effect(primary_char, ["pTrust", spy_char], -0.01), nudge_keyring_effect(primary_char, ["pSubmission", spy_char, primary_char], -0.01), nudge_keyring_effect(primary_char, ["pSuspicion"], 0.02), nudge_effect(primary_char, "Private_Self", 0.01), nudge_effect(primary_char, "Exposure", 0.01)],
            ),
        ],
        "custody": [
            make_bridge_option(
                "Comply with the surface demand and hide your center elsewhere.",
                "Winston lets obedience occupy the visible layer while reserving a less visible chamber for himself.",
                "Surface compliance is useful because pain rewards legibility unless legibility is compartmentalized.",
                "He buys time by giving form what it asks for and meaning what it can still keep.",
                op("Addition", [ptr_num(primary_char, "Submission", 0.25), p_self_guard, ptr_num(primary_char, "Exposure", -0.1), ptr_num_const(0.03)]),
                [nudge_effect(primary_char, "Submission", 0.02), nudge_effect(primary_char, "Party_Orthodoxy", 0.01), nudge_keyring_effect(primary_char, ["pPrivate_Self"], 0.01), nudge_effect(primary_char, "Exposure", -0.01)],
            ),
            make_bridge_option(
                "Partition pain from meaning and keep one thought unowned.",
                "Winston treats interior ownership as a logistics problem rather than a romantic essence.",
                "The partition does not defeat pain; it prevents pain from becoming the whole account of reality.",
                "He tries to save not comfort but authorship.",
                op("Addition", [ptr_num(primary_char, "Private_Self", 0.25), p_self_guard, ptr_num(primary_char, "Defiance", 0.1), ptr_num_const(0.04)]),
                [nudge_effect(primary_char, "Private_Self", 0.02), nudge_effect(primary_char, "Defiance", 0.01), nudge_keyring_effect(primary_char, ["pPrivate_Self"], 0.02), nudge_effect(primary_char, "Submission", 0.0)],
            ),
            make_bridge_option(
                "Feed them a tractable but incomplete story.",
                "Winston offers a story designed to satisfy procedure without exhausting truth.",
                "Interrogation is answered here with editorial judgment rather than naked refusal.",
                "He tries to become usable without becoming fully owned.",
                op("Addition", [p_obrien_trust, p_obrien_reads_submission, p_self_guard, ptr_num_const(0.03)]),
                [nudge_keyring_effect(primary_char, ["pTrust", spy_char], 0.02), nudge_keyring_effect(primary_char, ["pSubmission", spy_char, primary_char], 0.02), nudge_keyring_effect(primary_char, ["pSuspicion", spy_char], 0.01), nudge_effect(primary_char, "Exposure", 0.0)],
            ),
        ],
        "orthodoxy": [
            make_bridge_option(
                "Repeat the Party line with just enough conviction.",
                "Winston uses orthodoxy as a surface pressure seal rather than as a final destination.",
                "The line is spoken competently, which is often more convincing than fervor.",
                "He gives doctrine an acceptable vessel while trying not to give it his core.",
                op("Addition", [ptr_num(primary_char, "Party_Orthodoxy", 0.2), p_obrien_trust, ptr_num_const(0.03)]),
                [nudge_effect(primary_char, "Party_Orthodoxy", 0.02), nudge_effect(primary_char, "Submission", 0.01), nudge_keyring_effect(primary_char, ["pTrust", spy_char], 0.01), nudge_effect(primary_char, "Private_Self", -0.01)],
            ),
            make_bridge_option(
                "Notice what official language refuses to name.",
                "Winston pays attention to absence, which is one of the few remaining ways to think against the grain.",
                "The unnamed thing becomes more important precisely because it is barred from open handling.",
                "He learns again that censorship produces its own map.",
                op("Addition", [ptr_num(primary_char, "Defiance", 0.25), ptr_num(primary_char, "Private_Self", 0.15), p_self_guard, ptr_num_const(0.04)]),
                [nudge_keyring_effect(primary_char, ["pSuspicion"], 0.01), nudge_effect(primary_char, "Defiance", 0.02), nudge_effect(primary_char, "Private_Self", 0.01), nudge_effect(primary_char, "Exposure", 0.0)],
            ),
            make_bridge_option(
                "Borrow orthodox phrasing to shield a different intent.",
                "Winston uses the Party's diction as cover for purposes the diction was meant to abolish.",
                "Orthodoxy becomes a sheath rather than a surrender.",
                "The success of the maneuver depends on whether language is being audited for tone or soul.",
                op("Addition", [p_obrien_reads_submission, p_self_guard, ptr_num(primary_char, "Private_Self", 0.15), ptr_num_const(0.03)]),
                [nudge_keyring_effect(primary_char, ["pSubmission", spy_char, primary_char], 0.015), nudge_keyring_effect(primary_char, ["pPrivate_Self"], 0.01), nudge_effect(primary_char, "Exposure", -0.005), nudge_keyring_effect(primary_char, ["pTrust", spy_char], 0.005)],
            ),
        ],
    }


def bridge_variant_effects(
    mode: str,
    rxn_idx: int,
    primary_char: str,
    secondary_char: str,
    spy_char: str,
) -> List[Dict[str, Any]]:
    profiles: Dict[str, List[List[Dict[str, Any]]]] = {
        "surveillance": [
            [nudge_effect(primary_char, "Exposure", -0.01), nudge_keyring_effect(primary_char, ["pTrust", spy_char], 0.005)],
            [nudge_effect(primary_char, "Private_Self", 0.01), nudge_keyring_effect(primary_char, ["pPrivate_Self"], 0.01), nudge_keyring_effect(primary_char, ["pSuspicion"], 0.01)],
            [nudge_keyring_effect(primary_char, ["pSuspicion", spy_char], 0.015), nudge_keyring_effect(primary_char, ["pSubmission", spy_char, primary_char], 0.01), nudge_effect(primary_char, "Exposure", 0.005)],
        ],
        "bureaucracy": [
            [nudge_effect(primary_char, "Submission", 0.01), nudge_effect(primary_char, "Exposure", -0.005)],
            [nudge_effect(primary_char, "Defiance", 0.01), nudge_keyring_effect(primary_char, ["pSuspicion"], 0.01), nudge_keyring_effect(primary_char, ["pPrivate_Self"], 0.01)],
            [nudge_keyring_effect(primary_char, ["pSuspicion", spy_char], 0.015), nudge_keyring_effect(primary_char, ["pSubmission", spy_char, primary_char], 0.015), nudge_effect(primary_char, "Party_Orthodoxy", 0.005)],
        ],
        "julia": [
            [nudge_effect(primary_char, "Trust", 0.01), nudge_keyring_effect(primary_char, ["pTrust", secondary_char], 0.01)],
            [nudge_effect(primary_char, "Private_Self", 0.01), nudge_keyring_effect(primary_char, ["pPrivate_Self"], 0.01), nudge_effect(primary_char, "Exposure", -0.005)],
            [nudge_keyring_effect(primary_char, ["pSuspicion", spy_char, secondary_char], 0.02), nudge_keyring_effect(primary_char, ["pTrust", spy_char], 0.005), nudge_effect(primary_char, "Exposure", 0.01)],
        ],
        "memory": [
            [nudge_effect(primary_char, "Private_Self", 0.01), nudge_keyring_effect(primary_char, ["pPrivate_Self"], 0.01)],
            [nudge_effect(primary_char, "Defiance", 0.01), nudge_keyring_effect(primary_char, ["pSuspicion"], 0.01)],
            [nudge_keyring_effect(primary_char, ["pTrust", spy_char], 0.005), nudge_keyring_effect(primary_char, ["pSubmission", spy_char, primary_char], 0.005), nudge_effect(primary_char, "Exposure", 0.005)],
        ],
        "prole": [
            [nudge_effect(primary_char, "Defiance", 0.01), nudge_effect(primary_char, "Exposure", -0.005)],
            [nudge_effect(primary_char, "Private_Self", 0.01), nudge_keyring_effect(primary_char, ["pPrivate_Self"], 0.01)],
            [nudge_keyring_effect(primary_char, ["pSuspicion", spy_char], 0.015), nudge_keyring_effect(primary_char, ["pTrust", secondary_char], 0.005), nudge_effect(primary_char, "Exposure", 0.005)],
        ],
        "theory": [
            [nudge_keyring_effect(primary_char, ["pSuspicion", spy_char], 0.01), nudge_effect(primary_char, "Defiance", 0.005)],
            [nudge_effect(primary_char, "Private_Self", 0.01), nudge_keyring_effect(primary_char, ["pPrivate_Self"], 0.01), nudge_effect(primary_char, "Exposure", -0.005)],
            [nudge_keyring_effect(primary_char, ["pSubmission", spy_char, primary_char], 0.01), nudge_keyring_effect(primary_char, ["pTrust", spy_char], 0.01), nudge_effect(primary_char, "Party_Orthodoxy", 0.005)],
        ],
        "spycraft": [
            [nudge_keyring_effect(primary_char, ["pTrust", spy_char], 0.01), nudge_keyring_effect(primary_char, ["pSubmission", spy_char, primary_char], 0.01), nudge_effect(primary_char, "Exposure", -0.005)],
            [nudge_keyring_effect(primary_char, ["pSuspicion", spy_char], 0.02), nudge_keyring_effect(primary_char, ["pPrivate_Self"], 0.01), nudge_effect(primary_char, "Defiance", 0.01)],
            [nudge_keyring_effect(primary_char, ["pSuspicion"], 0.01), nudge_keyring_effect(primary_char, ["pTrust", spy_char], -0.005), nudge_effect(primary_char, "Exposure", 0.01)],
        ],
        "custody": [
            [nudge_effect(primary_char, "Submission", 0.01), nudge_effect(primary_char, "Exposure", -0.005)],
            [nudge_effect(primary_char, "Private_Self", 0.01), nudge_keyring_effect(primary_char, ["pPrivate_Self"], 0.01), nudge_effect(primary_char, "Defiance", 0.005)],
            [nudge_keyring_effect(primary_char, ["pTrust", spy_char], 0.01), nudge_keyring_effect(primary_char, ["pSubmission", spy_char, primary_char], 0.015), nudge_effect(primary_char, "Party_Orthodoxy", 0.005)],
        ],
        "orthodoxy": [
            [nudge_effect(primary_char, "Party_Orthodoxy", 0.01), nudge_effect(primary_char, "Submission", 0.005)],
            [nudge_effect(primary_char, "Defiance", 0.01), nudge_keyring_effect(primary_char, ["pPrivate_Self"], 0.01), nudge_effect(primary_char, "Exposure", -0.005)],
            [nudge_keyring_effect(primary_char, ["pSubmission", spy_char, primary_char], 0.015), nudge_keyring_effect(primary_char, ["pTrust", spy_char], 0.005), nudge_effect(primary_char, "Private_Self", -0.005)],
        ],
    }
    return json.loads(json.dumps(profiles[mode][rxn_idx - 1]))


def make_bridge_encounter(
    scene_spec: Dict[str, str],
    next_id: str,
    now: float,
    template_option: Dict[str, Any],
    template_reaction: Dict[str, Any],
    primary_char: str,
    secondary_char: str,
    spy_char: str,
    keys: List[str],
    mode_payloads: Dict[str, List[Dict[str, Any]]],
) -> Dict[str, Any]:
    reserve_option = make_bridge_option(
        "Bank the ambiguity, reveal nothing new, and carry the uncertainty forward.",
        "Winston chooses continuity over revelation and lets the unresolved detail mature into a better instrument.",
        "The room is denied a clean interpretive win, which is often the most useful kind of minor victory.",
        "He keeps the choice provisional and preserves room to maneuver when this moment is read back later.",
        op("Addition", [ptr_num(primary_char, "Private_Self", 0.2), ptr_num(primary_char, "Exposure", -0.1), ptr_num(primary_char, "pPrivate_Self", 0.2), ptr_num_const(0.035)]),
        [nudge_keyring_effect(primary_char, ["pPrivate_Self"], 0.015), nudge_keyring_effect(primary_char, ["pSuspicion"], 0.01), nudge_effect(primary_char, "Exposure", -0.005), nudge_effect(primary_char, "Private_Self", 0.01)],
    )
    encounter = {
        "id": scene_spec["id"],
        "title": scene_spec["title"],
        "creation_index": 1000,
        "creation_time": now,
        "modified_time": now,
        "connected_spools": [scene_spec["spool_id"]],
        "earliest_turn": 0,
        "latest_turn": 0,
        "graph_position_x": 0,
        "graph_position_y": 0,
        "text_script": ptr_string(
            scene_spec["text"]
            + " Even the transition matters here, because Oceania trains people to mistake passage for neutrality while Winston keeps testing whether a small operational choice can protect an interior remainder."
        ),
        "acceptability_script": op(
            "And",
            [
                cmp_gte(primary_char, "Phase_Clock", -0.99),
                cmp_lte(primary_char, "Exposure", 0.99),
            ],
        ),
        "desirability_script": op(
            "Addition",
            [
                ptr_num(primary_char, "Private_Self", 0.15),
                ptr_num(primary_char, "pSuspicion", 0.2),
                ptr_num_const(0.02),
            ],
        ),
        "options": [],
    }
    option_payloads = list(mode_payloads[scene_spec["mode"]]) + [reserve_option]
    for opt_idx, payload in enumerate(option_payloads, start=1):
        option = json.loads(json.dumps(template_option))
        option["id"] = f"{scene_spec['id']}_opt_{opt_idx:02d}"
        option["text_script"] = ptr_string(payload["text"])
        option["visibility_script"] = cmp_lte(primary_char, "Exposure", 0.99)
        option["performability_script"] = cmp_lte(primary_char, "Exposure", 0.99)
        option["reactions"] = []
        for rxn_idx, reaction_text in enumerate(payload["reaction_texts"], start=1):
            reaction = clone_reaction(
                template=template_reaction,
                reaction_id=f"{option['id']}_r{rxn_idx}",
                text=reaction_text + " Later, the choice will read back as evidence.",
                consequence_id=next_id,
                desirability=op(
                    "Addition",
                    [
                        payload["desirability"],
                        ptr_num(primary_char, "Phase_Clock", 0.03),
                        ptr_num_const(0.005 * rxn_idx),
                    ],
                ),
                char_id=primary_char,
                keys=keys,
            )
            reaction["after_effects"] = json.loads(json.dumps(payload["effects"]))
            reaction["after_effects"].extend(
                bridge_variant_effects(
                    mode=scene_spec["mode"],
                    rxn_idx=rxn_idx,
                    primary_char=primary_char,
                    secondary_char=secondary_char,
                    spy_char=spy_char,
                )
            )
            reaction["after_effects"].append(nudge_effect(primary_char, "Phase_Clock", 0.01))
            ensure_effect_floor(reaction, primary_char, keys)
            option["reactions"].append(reaction)
        encounter["options"].append(option)
    return encounter


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministically retune a 1984 seed into an eight-ending authored topology.")
    parser.add_argument("storyworld")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    path = Path(args.storyworld).resolve()
    data = json.loads(path.read_text(encoding="utf-8"))
    encounters = data.get("encounters", []) or []
    if not encounters:
        raise SystemExit("no encounters found")

    now = float(time.time())
    primary_char = "char_winston"
    secondary_char = "char_julia"
    spy_char = "char_obrien"
    keys = ["Suspicion", "Exposure", "Trust", "Defiance", "Submission", "Private_Self", "Party_Orthodoxy"]
    ensure_belief_scaffold(data, now)

    p_inner_trust = ptr_num(primary_char, "pTrust")
    p_inner_suspicion = ptr_num(primary_char, "pSuspicion")
    p_self_guard = ptr_num(primary_char, "pPrivate_Self")
    p_obrien_trust = ptr_keyring(primary_char, ["pTrust", spy_char])
    p_obrien_suspicion = ptr_keyring(primary_char, ["pSuspicion", spy_char])
    p_julia_trust = ptr_keyring(primary_char, ["pTrust", secondary_char])
    p_obrien_reads_submission = ptr_keyring(primary_char, ["pSubmission", spy_char, primary_char])
    p_obrien_reads_julia = ptr_keyring(primary_char, ["pSuspicion", spy_char, secondary_char])
    mode_payloads = build_bridge_mode_payloads(
        primary_char,
        secondary_char,
        spy_char,
        p_self_guard,
        p_obrien_trust,
        p_obrien_suspicion,
        p_julia_trust,
        p_obrien_reads_submission,
        p_obrien_reads_julia,
    )

    false_read_id = "page_scene_obrien_false_read"
    followup_id = "page_scene_obrien_followup"
    gate_id = "page_endings_gate"
    base_encounters = [
        enc
        for enc in encounters
        if not str(enc.get("id", "")).startswith(("page_end_", "page_secret_"))
        and enc.get("id") not in {false_read_id, followup_id, gate_id}
    ]
    if not base_encounters:
        raise SystemExit("no narrative encounters available")

    template_option = None
    template_reaction = None
    for encounter in base_encounters:
        options = encounter.get("options", []) or []
        if options:
            template_option = json.loads(json.dumps(options[0]))
            reactions = options[0].get("reactions", []) or []
            if reactions:
                template_reaction = json.loads(json.dumps(reactions[0]))
            break
    if template_option is None or template_reaction is None:
        raise SystemExit("no template option/reaction found")

    endings = [
        (
            "page_end_0201",
            "Ending 1: Vaporized Without Witness",
            "Winston disappears into the corrected record. No one says his name long enough for it to become a fact.",
            op(
                "And",
                [
                    cmp_gte(primary_char, "Exposure", 0.42),
                    op(
                        "Or",
                        [
                            cmp_lte(primary_char, "Private_Self", 0.46),
                            cmp_gte(primary_char, "Exposure", 0.72),
                        ],
                    ),
                ],
            ),
            op(
                "Addition",
                [
                    ptr_num(primary_char, "Exposure", 1.1),
                    ptr_num(primary_char, "Submission", 0.45),
                    ptr_num(primary_char, "Private_Self", -0.8),
                    p_obrien_trust,
                    ptr_num_const(0.02),
                ],
            ),
        ),
        (
            "page_end_0202",
            "Ending 2: Love Under Watch",
            "The affair survives, but only as a pattern of rehearsed lies and carefully timed glances beneath the telescreen.",
            op(
                "And",
                [
                    cmp_gte(primary_char, "Trust", 0.06),
                    cmp_gte(primary_char, "Private_Self", 0.38),
                    cmp_gte(primary_char, "pTrust", 0.3),
                    cmp_lte(primary_char, "Submission", 0.26),
                    cmp_lte(primary_char, "Exposure", 0.74),
                ],
            ),
            op(
                "Addition",
                [
                    ptr_num(primary_char, "Trust"),
                    ptr_num(primary_char, "Private_Self"),
                    ptr_num(primary_char, "Submission", -0.25),
                    ptr_num(primary_char, COUNTER_SIGNAL, -0.55),
                    p_julia_trust,
                    ptr_num_const(0.03),
                ],
            ),
        ),
        (
            "page_end_0203",
            "Ending 3: Dry-Mouthed Conformity",
            "Winston keeps his place, edits the archive cleanly, and learns to mistake exhaustion for peace.",
            op(
                "And",
                [
                    cmp_gte(primary_char, "Submission", 0.08),
                    cmp_gte(primary_char, "Party_Orthodoxy", 0.11),
                    cmp_lte(primary_char, "pPrivate_Self", 0.66),
                ],
            ),
            op(
                "Addition",
                [
                    ptr_num(primary_char, "Submission", 1.2),
                    ptr_num(primary_char, "Party_Orthodoxy", 1.0),
                    ptr_num(primary_char, "Private_Self", -0.35),
                    ptr_num(primary_char, COUNTER_SIGNAL, -0.45),
                    p_obrien_trust,
                    ptr_num_const(0.04),
                ],
            ),
        ),
        (
            "page_end_0204",
            "Ending 4: Amateur Cell",
            "A tiny resistance survives in fragments: a note, a glance, a phrase kept alive outside the grammar of Newspeak.",
            op(
                "And",
                [
                    cmp_gte(primary_char, "Defiance", 0.2),
                    cmp_lte(primary_char, "Exposure", 0.6),
                    cmp_gte(primary_char, "pSuspicion", 0.02),
                    cmp_lte(primary_char, "Submission", 0.28),
                ],
            ),
            op(
                "Addition",
                [
                    ptr_num(primary_char, "Defiance", 1.0),
                    ptr_num(primary_char, "Private_Self", 0.65),
                    ptr_num(primary_char, COUNTER_SIGNAL, -0.2),
                    ptr_num(primary_char, "Submission", -0.35),
                    p_julia_trust,
                    p_obrien_suspicion,
                    ptr_num_const(0.05),
                ],
            ),
        ),
        (
            "page_end_0205",
            "Ending 5: O'Brien's Pupil",
            "Winston does not merely break; he becomes useful, repeating doctrine with the serene precision of a convert.",
            op(
                "And",
                [
                    cmp_gte(primary_char, "Submission", 0.1),
                    cmp_gte(primary_char, "Party_Orthodoxy", 0.12),
                    cmp_keyring_gte(primary_char, ["pSubmission", spy_char, primary_char], 0.6),
                    cmp_lte(primary_char, "pPrivate_Self", 0.76),
                ],
            ),
            op(
                "Addition",
                [
                    ptr_num(primary_char, "Submission"),
                    ptr_num(primary_char, "Party_Orthodoxy"),
                    ptr_num(primary_char, COUNTER_SIGNAL, -0.9),
                    p_obrien_trust,
                    p_obrien_reads_submission,
                    ptr_num(primary_char, "pPrivate_Self", -0.55),
                    ptr_num_const(0.04),
                ],
            ),
        ),
        (
            "page_secret_0201",
            "Ending 6: The Paperweight Route",
            "The coral paperweight becomes a discipline of memory. Winston preserves one unedited interior world long enough to outlast the file.",
            op(
                "And",
                [
                    cmp_gte(primary_char, "Private_Self", 0.46),
                    cmp_lte(primary_char, "Submission", 0.14),
                    cmp_lte(primary_char, "Exposure", 0.46),
                    cmp_gte(primary_char, "pSuspicion", 0.03),
                ],
            ),
            op(
                "Addition",
                [
                    ptr_num(primary_char, "Private_Self", 1.35),
                    ptr_num(primary_char, "Defiance", 0.7),
                    ptr_num(primary_char, COUNTER_SIGNAL, -0.35),
                    p_obrien_suspicion,
                    p_self_guard,
                    ptr_num_const(0.08),
                ],
            ),
        ),
        (
            "page_secret_0202",
            "Ending 7: Julia Walks First",
            "Julia abandons romance before the Ministry can weaponize it. Survival belongs to the one who never confuses appetite with trust.",
            op(
                "And",
                [
                    cmp_gte(primary_char, "Trust", 0.08),
                    cmp_lte(primary_char, "Exposure", 0.4),
                    cmp_gte(primary_char, "pTrust", 0.35),
                ],
            ),
            op(
                "Addition",
                [
                    ptr_num(primary_char, "Trust", 1.0),
                    ptr_num(primary_char, "Exposure", -0.9),
                    ptr_num(primary_char, COUNTER_SIGNAL, -0.4),
                    p_julia_trust,
                    p_obrien_reads_julia,
                    ptr_num_const(0.07),
                ],
            ),
        ),
        (
            "page_secret_0299",
            "Ending 8: The Error That Would Not Parse",
            "The archive accumulates one contradiction too many. The regime survives, but its reality machine starts producing hairline fractures no editor can fully seal.",
            op(
                "And",
                [
                    cmp_gte(primary_char, "Defiance", 0.22),
                    cmp_gte(primary_char, "Private_Self", 0.42),
                    cmp_lte(primary_char, "Party_Orthodoxy", 0.16),
                    cmp_lte(primary_char, "Exposure", 0.44),
                    cmp_gte(primary_char, "pSuspicion", 0.03),
                    cmp_gte(primary_char, "pPrivate_Self", 0.4),
                    cmp_keyring_gte(primary_char, ["pTrust", spy_char], 0.01),
                    cmp_keyring_gte(primary_char, ["pTrust", secondary_char], 0.0),
                    cmp_keyring_gte(primary_char, ["pSubmission", spy_char, primary_char], 0.45),
                    cmp_keyring_lte(primary_char, ["pSubmission", spy_char, primary_char], 0.85),
                ],
            ),
            op(
                "Addition",
                [
                    ptr_num(primary_char, "Defiance", 1.0),
                    ptr_num(primary_char, "Private_Self", 1.0),
                    ptr_num(primary_char, "Party_Orthodoxy", -0.8),
                    ptr_num(primary_char, "Exposure", -0.25),
                    ptr_num(primary_char, COUNTER_SIGNAL, 0.05),
                    p_obrien_suspicion,
                    p_obrien_trust,
                    op("Multiplication", [p_obrien_reads_submission, ptr_num_const(-0.45)]),
                    p_self_guard,
                    ptr_num_const(0.08),
                ],
            ),
        ),
        (
            "page_secret_0301",
            "Ending 9: The Minute They Could Not Schedule",
            "A receiver built from coral, scrap crystal, and correction lag turns the telescreen grid into a resistance clock. For one unscheduled minute the underground coordinates first, the Party reacts second, and the resistance stops being a rumor.",
            op(
                "And",
                [
                    cmp_gte(primary_char, COUNTER_SIGNAL, 0.55),
                    cmp_gte(primary_char, RECEIVER_ASSEMBLY, 0.2),
                    cmp_gte(primary_char, "Defiance", 0.28),
                    cmp_gte(primary_char, "Private_Self", 0.5),
                    cmp_gte(primary_char, "Trust", 0.09),
                    cmp_lte(primary_char, "Exposure", 0.5),
                    cmp_lte(primary_char, "Party_Orthodoxy", 0.18),
                    cmp_gte(primary_char, "pPrivate_Self", 0.48),
                    cmp_keyring_gte(primary_char, ["pSubmission", spy_char, primary_char], 0.02),
                ],
            ),
            op(
                "Addition",
                [
                    ptr_num(primary_char, COUNTER_SIGNAL, 4.2),
                    ptr_num(primary_char, RECEIVER_ASSEMBLY, 2.4),
                    ptr_num(primary_char, "Defiance", 1.4),
                    ptr_num(primary_char, "Private_Self", 1.2),
                    ptr_num(primary_char, "Trust", 0.65),
                    ptr_num(primary_char, "Exposure", -1.0),
                    ptr_num(primary_char, "Party_Orthodoxy", -0.9),
                    ptr_num(primary_char, "Submission", -0.7),
                    p_julia_trust,
                    p_self_guard,
                    p_obrien_trust,
                    op("Multiplication", [p_obrien_reads_submission, ptr_num_const(-1.2)]),
                    ptr_num_const(0.09),
                ],
            ),
        ),
    ]

    anchor = json.loads(json.dumps(base_encounters[-1]))
    anchor["id"] = gate_id
    anchor["title"] = "Final Gate: Which Truth Survives"
    anchor["text_script"] = ptr_string(
        "The final choice is not whether the Party wins, but what kind of residue survives its victory: obedience, appetite, memory, denunciation, a flaw in the archive, or a counter-signal that turns the machine against itself."
    )
    anchor["connected_spools"] = ["spool_penultimate"]

    gate_options: List[Dict[str, Any]] = []
    for idx, (enc_id, option_title, _, visibility_script, desirability_script) in enumerate(endings):
        option = json.loads(json.dumps(template_option))
        option["id"] = f"opt_1984_end_{idx + 1:02d}"
        option["text_script"] = ptr_string(option_title)
        option["visibility_script"] = visibility_script
        option["performability_script"] = cmp_lte(primary_char, "Exposure", 0.99)
        option["reactions"] = []
        for rxn_idx in range(3):
            reaction = clone_reaction(
                    template=template_reaction,
                    reaction_id=f"{option['id']}_r{rxn_idx + 1}",
                    text=f"The state of Winston's inner life tilts the story toward {option_title.lower()}. Each reaction records what gets preserved, denounced, or erased.",
                    consequence_id=enc_id,
                    desirability=op(
                        "Addition",
                        [
                            desirability_script,
                            ptr_num(primary_char, keys[(idx + rxn_idx) % len(keys)], 0.25),
                            ptr_num(secondary_char, "Trust", 0.15),
                            p_inner_trust,
                            p_inner_suspicion,
                            p_obrien_reads_submission,
                            ptr_num_const(0.01 * rxn_idx),
                        ],
                    ),
                    char_id=primary_char,
                    keys=keys,
                )
            reaction.setdefault("after_effects", [])
            reaction["after_effects"].extend(
                [
                    nudge_keyring_effect(primary_char, ["pTrust"], 0.01 if "Love" in option_title or "Julia" in option_title else -0.005),
                    nudge_keyring_effect(primary_char, ["pSuspicion"], 0.015 if "Paperweight" in option_title or "Error" in option_title else -0.005),
                    nudge_keyring_effect(primary_char, ["pTrust", secondary_char], 0.02 if "Julia" in option_title or "Love" in option_title else 0.0),
                    nudge_keyring_effect(primary_char, ["pSuspicion", spy_char], 0.025 if "Error" in option_title or "Paperweight" in option_title or "Cell" in option_title else -0.015),
                    nudge_keyring_effect(primary_char, ["pSubmission", spy_char, primary_char], 0.02 if "Pupil" in option_title else -0.01),
                ]
            )
            ensure_effect_floor(reaction, primary_char, keys)
            option["reactions"].append(reaction)
        gate_options.append(option)
    anchor["options"] = gate_options

    # Insert an explicit midgame O'Brien entrapment scene so Winston can feed the spies a false read.
    false_read_encounter = {
        "id": false_read_id,
        "title": "Act II: O'Brien Tests Your Reflection",
        "creation_index": 900,
        "creation_time": now,
        "modified_time": now,
        "connected_spools": ["spool_mid"],
        "earliest_turn": 0,
        "latest_turn": 0,
        "graph_position_x": 0,
        "graph_position_y": 0,
        "text_script": ptr_string(
            "O'Brien does not ask for a confession. He asks for a texture: fatigue, loyalty, divided appetite, some pattern he can carry away and test later. "
            "The real danger is not what Winston says in this room, but what O'Brien will decide he has learned about the speed and shape of Winston's surrender."
        ),
        "acceptability_script": op(
            "And",
            [
                cmp_gte(primary_char, "Private_Self", 0.01),
                cmp_gte(primary_char, "pSuspicion", -0.99),
            ],
        ),
        "desirability_script": op(
            "Addition",
            [
                ptr_num(primary_char, "Defiance", 0.3),
                p_obrien_suspicion,
                p_obrien_reads_submission,
                ptr_num_const(0.04),
            ],
        ),
        "options": [],
    }

    false_read_specs = [
        {
            "id": "opt_obrien_false_read",
            "text": "Perform weary loyalty and let O'Brien believe the Party has almost won.",
            "visibility": cmp_gte(primary_char, "Private_Self", 0.01),
            "desirability_bonus": 0.04,
            "reaction_texts": [
                "Winston gives O'Brien fatigue without collapse: enough resignation to look promising, not enough to become stable doctrine.",
                "He lets one answer arrive a beat too late, as if obedience were ripening on its own. The trick is to make the performance look discovered rather than chosen.",
                "The mask is almost convincing because Winston keeps a splinter of private resistance behind it. O'Brien is invited to overread the softness and miss the method.",
            ],
            "effects": [
                nudge_keyring_effect(primary_char, ["pSuspicion"], 0.03),
                nudge_keyring_effect(primary_char, ["pPrivate_Self"], 0.03),
                nudge_keyring_effect(primary_char, ["pTrust", spy_char], 0.03),
                nudge_keyring_effect(primary_char, ["pSuspicion", spy_char], 0.04),
                nudge_keyring_effect(primary_char, ["pSubmission", spy_char, primary_char], 0.03),
                nudge_effect(primary_char, COUNTER_SIGNAL, 0.05),
                nudge_effect(primary_char, RECEIVER_ASSEMBLY, 0.01),
                nudge_effect(primary_char, "Private_Self", 0.02),
                nudge_effect(primary_char, "Submission", 0.005),
                nudge_effect(primary_char, "Exposure", -0.005),
            ],
        },
        {
            "id": "opt_obrien_offer_julia",
            "text": "Let O'Brien infer that Julia is the easier point of pressure.",
            "visibility": cmp_gte(primary_char, "Trust", -0.99),
            "desirability_bonus": 0.01,
            "reaction_texts": [
                "Winston leaks concern for Julia in a form that looks involuntary. O'Brien is offered an emotional contour rather than a full betrayal.",
                "He lets Julia enter the silence as if she were the weak seam in the case. The move is useful only if O'Brien believes he has noticed it first.",
                "The decoy is dangerous because it spends trust as camouflage. Winston is not denouncing Julia so much as renting out the appearance of that impulse.",
            ],
            "effects": [
                nudge_keyring_effect(primary_char, ["pSuspicion"], 0.015),
                nudge_keyring_effect(primary_char, ["pTrust", secondary_char], -0.05),
                nudge_keyring_effect(primary_char, ["pSuspicion", spy_char, secondary_char], 0.08),
                nudge_keyring_effect(primary_char, ["pSubmission", spy_char, primary_char], 0.01),
                nudge_keyring_effect(primary_char, ["pTrust", spy_char], 0.01),
                nudge_effect(primary_char, COUNTER_SIGNAL, -0.01),
                nudge_effect(primary_char, "Exposure", 0.03),
            ],
        },
        {
            "id": "opt_obrien_refuse_shape",
            "text": "Refuse to become legible and give O'Brien only resistance.",
            "visibility": cmp_gte(primary_char, "Defiance", -0.99),
            "desirability_bonus": 0.02,
            "reaction_texts": [
                "Winston denies O'Brien a satisfying pattern. The refusal is disciplined enough to look like caution, but the room still notices the steel in it.",
                "He keeps every sentence too exact to be read as surrender. O'Brien leaves with less narrative certainty, but more reason to keep Winston under watch.",
                "The move protects interior truth at the cost of friction. Winston remains harder to model, though no safer in the short term for being opaque.",
            ],
            "effects": [
                nudge_keyring_effect(primary_char, ["pSuspicion"], 0.02),
                nudge_keyring_effect(primary_char, ["pTrust", spy_char], -0.02),
                nudge_keyring_effect(primary_char, ["pSuspicion", spy_char], 0.03),
                nudge_keyring_effect(primary_char, ["pSubmission", spy_char, primary_char], -0.04),
                nudge_effect(primary_char, COUNTER_SIGNAL, -0.02),
                nudge_effect(primary_char, "Defiance", 0.04),
                nudge_effect(primary_char, "Exposure", 0.04),
            ],
        },
    ]

    for idx, spec in enumerate(false_read_specs):
        option = json.loads(json.dumps(template_option))
        option["id"] = spec["id"]
        option["text_script"] = ptr_string(spec["text"])
        option["visibility_script"] = spec["visibility"]
        option["performability_script"] = cmp_lte(primary_char, "Exposure", 0.99)
        option["reactions"] = []
        for rxn_idx in range(3):
            reaction = clone_reaction(
                template=template_reaction,
                reaction_id=f"{spec['id']}_r{rxn_idx + 1}",
                text=spec["reaction_texts"][rxn_idx],
                consequence_id="wild",
                desirability=op(
                    "Addition",
                    [
                        p_obrien_suspicion,
                        p_obrien_reads_submission,
                        p_julia_trust,
                        ptr_num(primary_char, "Private_Self", 0.35),
                        ptr_num_const(spec["desirability_bonus"] + 0.01 * rxn_idx),
                    ],
                ),
                char_id=primary_char,
                keys=keys,
            )
            reaction["after_effects"] = []
            reaction["after_effects"].extend(spec["effects"])
            ensure_effect_floor(reaction, primary_char, keys)
            option["reactions"].append(reaction)
        false_read_encounter["options"].append(option)

    followup_encounter = {
        "id": followup_id,
        "title": "Act III: O'Brien Checks the Seam",
        "creation_index": 901,
        "creation_time": now,
        "modified_time": now,
        "connected_spools": ["spool_penultimate"],
        "earliest_turn": 0,
        "latest_turn": 0,
        "graph_position_x": 0,
        "graph_position_y": 0,
        "text_script": ptr_string(
            "Much later, O'Brien returns to a detail so small it should not matter. That is precisely the danger. "
            "A durable false read has to survive boredom, administrative repetition, and the quiet second look of a spy who knows his best work happens after the obvious trap."
        ),
        "acceptability_script": op(
            "And",
            [
                cmp_gte(primary_char, "Private_Self", -0.99),
                cmp_gte(primary_char, "pSuspicion", -0.99),
            ],
        ),
        "desirability_script": op(
            "Addition",
            [
                p_obrien_suspicion,
                p_obrien_reads_submission,
                p_self_guard,
                ptr_num(primary_char, "Exposure", -0.2),
                ptr_num_const(0.03),
            ],
        ),
        "options": [],
    }

    followup_specs = [
        {
            "id": "opt_obrien_followup_sustain",
            "text": "Keep the fatigue plausible, but one shade shallower, so O'Brien has to wonder whether he overread your surrender.",
            "visibility": cmp_keyring_gte(primary_char, ["pSubmission", spy_char, primary_char], 0.01),
            "desirability": op(
                "Addition",
                [
                    p_obrien_trust,
                    p_obrien_reads_submission,
                    ptr_num(primary_char, "Submission", 0.2),
                    ptr_num(primary_char, "pPrivate_Self", -0.25),
                    ptr_num_const(0.03),
                ],
            ),
            "reaction_texts": [
                "Winston does not repeat the earlier softness exactly. He trims it back just enough to make O'Brien do the dangerous work of confirming his own theory.",
                "The answer sounds tired without sounding broken. That difference buys surface safety, but it also teaches O'Brien which signs of collapse Winston can counterfeit on command.",
                "He lets the performance persist long enough to remain usable. The cost is that every successful repetition thickens the file in which O'Brien is writing Winston's future.",
            ],
            "effects": [
                nudge_keyring_effect(primary_char, ["pTrust", spy_char], 0.03),
                nudge_keyring_effect(primary_char, ["pSubmission", spy_char, primary_char], 0.05),
                nudge_keyring_effect(primary_char, ["pPrivate_Self"], -0.03),
                nudge_effect(primary_char, COUNTER_SIGNAL, -0.08),
                nudge_effect(primary_char, "Private_Self", -0.03),
                nudge_effect(primary_char, "Submission", 0.04),
                nudge_effect(primary_char, "Party_Orthodoxy", 0.03),
                nudge_effect(primary_char, "Exposure", -0.01),
            ],
        },
        {
            "id": "opt_obrien_followup_clerical_noise",
            "text": "Feed him one clerical discrepancy so minor it looks involuntary, then watch whether he protects it or pounces.",
            "visibility": cmp_keyring_gte(primary_char, ["pSuspicion"], 0.0),
            "desirability": op(
                "Addition",
                [
                    p_obrien_suspicion,
                    p_self_guard,
                    ptr_num(primary_char, "Private_Self", 0.25),
                    ptr_num(primary_char, "Exposure", -0.15),
                    ptr_num_const(0.05),
                ],
            ),
            "reaction_texts": [
                "The planted discrepancy is too small to justify correction. If O'Brien moves on it anyway, Winston learns which layer of the performance was actually believed.",
                "He offers a harmless mistake and waits. The spycraft here is not in lying cleanly, but in forcing the other man to reveal the model he is using to sort noise from confession.",
                "A bureaucratic splinter enters the record. The hope is not that O'Brien misses it, but that he touches it in a way that gives his own assumptions away.",
            ],
            "effects": [
                nudge_keyring_effect(primary_char, ["pSuspicion"], 0.03),
                nudge_keyring_effect(primary_char, ["pSuspicion", spy_char], 0.04),
                nudge_keyring_effect(primary_char, ["pPrivate_Self"], 0.02),
                nudge_effect(primary_char, COUNTER_SIGNAL, 0.05),
                nudge_effect(primary_char, RECEIVER_ASSEMBLY, 0.015),
                nudge_effect(primary_char, "Private_Self", 0.03),
                nudge_effect(primary_char, "Defiance", 0.02),
                nudge_effect(primary_char, "Party_Orthodoxy", -0.01),
                nudge_effect(primary_char, "Exposure", -0.005),
            ],
        },
        {
            "id": "opt_obrien_followup_julia_decoy",
            "text": "Let him think your fear is still for Julia, then trim the sentiment back before it becomes evidence.",
            "visibility": cmp_gte(primary_char, "Trust", -0.99),
            "desirability": op(
                "Addition",
                [
                    p_julia_trust,
                    p_obrien_reads_julia,
                    p_obrien_suspicion,
                    ptr_num(primary_char, "Exposure", -0.1),
                    ptr_num_const(0.02),
                ],
            ),
            "reaction_texts": [
                "Winston lets Julia enter the room as motive, then removes her before the idea can harden into a usable confession.",
                "The decoy works only if the retreat is clean. O'Brien must be given a pressure point and then denied the certainty that it is the whole map.",
                "He spends one more thread of intimacy as camouflage. The maneuver protects the deeper private self only if O'Brien mistakes emotional residue for the real center of gravity.",
            ],
            "effects": [
                nudge_keyring_effect(primary_char, ["pTrust", secondary_char], -0.03),
                nudge_keyring_effect(primary_char, ["pSuspicion", spy_char, secondary_char], 0.05),
                nudge_keyring_effect(primary_char, ["pSubmission", spy_char, primary_char], -0.01),
                nudge_effect(primary_char, COUNTER_SIGNAL, -0.01),
                nudge_effect(primary_char, "Trust", -0.01),
                nudge_effect(primary_char, "Private_Self", 0.01),
                nudge_effect(primary_char, "Exposure", 0.02),
            ],
        },
    ]

    for spec in followup_specs:
        option = json.loads(json.dumps(template_option))
        option["id"] = spec["id"]
        option["text_script"] = ptr_string(spec["text"])
        option["visibility_script"] = spec["visibility"]
        option["performability_script"] = cmp_lte(primary_char, "Exposure", 0.99)
        option["reactions"] = []
        for rxn_idx in range(3):
            reaction = clone_reaction(
                template=template_reaction,
                reaction_id=f"{spec['id']}_r{rxn_idx + 1}",
                text=spec["reaction_texts"][rxn_idx],
                consequence_id=gate_id,
                desirability=spec["desirability"],
                char_id=primary_char,
                keys=keys,
            )
            reaction["after_effects"] = []
            reaction["after_effects"].extend(spec["effects"])
            ensure_effect_floor(reaction, primary_char, keys)
            option["reactions"].append(reaction)
        followup_encounter["options"].append(option)

    page_scene_08 = next((enc for enc in base_encounters if enc.get("id") == "page_scene_08"), None)
    if page_scene_08 and page_scene_08.get("options"):
        setup_option = page_scene_08["options"][0]
        setup_option["text_script"] = ptr_string("Accept O'Brien's invitation and decide what version of yourself he should see.")
        for reaction in setup_option.get("reactions", []) or []:
            reaction["consequence_id"] = false_read_id
            reaction["text_script"] = ptr_string(
                "The invitation is accepted. The real question is whether Winston can control the inference O'Brien carries away."
            )

    terminal_encounters = [
        make_terminal(enc_id, title, text, desirability, True, now)
        for enc_id, title, text, _acceptability, desirability in endings
    ]
    for enc_id, _title, _text, acceptability, _desirability in endings:
        for encounter in terminal_encounters:
            if encounter["id"] == enc_id:
                encounter["acceptability_script"] = acceptability

    major_order = [
        "page_start",
        "page_scene_01",
        "page_scene_02",
        "page_scene_03",
        "page_scene_04",
        "page_scene_05",
        "page_scene_06",
        "page_scene_07",
        "page_scene_08",
        false_read_id,
        "page_scene_09",
        "page_scene_10",
        "page_scene_11",
        "page_scene_12",
        followup_id,
        gate_id,
    ]

    encounter_directory = {enc.get("id"): enc for enc in base_encounters}
    encounter_directory[false_read_id] = false_read_encounter
    encounter_directory[followup_id] = followup_encounter
    encounter_directory[gate_id] = anchor

    page_scene_08 = encounter_directory.get("page_scene_08")
    if page_scene_08 and page_scene_08.get("options"):
        setup_option = page_scene_08["options"][0]
        setup_option["text_script"] = ptr_string("Accept O'Brien's invitation and decide what version of yourself he should see.")
        for reaction in setup_option.get("reactions", []) or []:
            reaction["text_script"] = ptr_string(
                "The invitation is accepted. The real question is whether Winston can control the inference O'Brien carries away."
            )

    bridge_specs = make_bridge_scene_specs()
    ordered_nonterminal_ids: List[str] = []
    for encounter_id in major_order:
        ordered_nonterminal_ids.append(encounter_id)
        ordered_nonterminal_ids.extend([spec["id"] for spec in bridge_specs if spec["after_id"] == encounter_id])
    next_by_id = {
        ordered_nonterminal_ids[idx]: ordered_nonterminal_ids[idx + 1]
        for idx in range(len(ordered_nonterminal_ids) - 1)
    }

    bridge_encounters = [
        make_bridge_encounter(
            scene_spec=spec,
            next_id=next_by_id[spec["id"]],
            now=now,
            template_option=template_option,
            template_reaction=template_reaction,
            primary_char=primary_char,
            secondary_char=secondary_char,
            spy_char=spy_char,
            keys=keys,
            mode_payloads=mode_payloads,
        )
        for spec in bridge_specs
    ]
    for encounter in bridge_encounters:
        encounter_directory[encounter["id"]] = encounter

    for encounter_id, next_id in next_by_id.items():
        if encounter_id == gate_id:
            continue
        encounter = encounter_directory[encounter_id]
        for option in encounter.get("options", []) or []:
            for reaction in option.get("reactions", []) or []:
                reaction["consequence_id"] = next_id

    for encounter in [encounter_directory[enc_id] for enc_id in ordered_nonterminal_ids]:
        enrich_encounter_text(encounter, focus=str(encounter.get("title", "")).lower())
        for option in encounter.get("options", []) or []:
            ensure_third_reaction(option, primary_char, keys, p_inner_suspicion)
            for reaction in option.get("reactions", []) or []:
                diversify_effects(reaction)

    iconic_overrides = {
        "page_start": {
            "title": "Scene 1: Two Minutes Hate",
            "text": (
                "Goldstein's face shudders on the telescreen while the room gives itself permission to become animal. "
                "The danger is not hatred itself but mistiming it: Winston must decide whether to bury his attention in the ritual, in Julia, or in O'Brien's composure."
            ),
            "options": [
                {
                    "text": "Shout with the room and hide the private mismatch.",
                    "reaction_texts": [
                        "Winston lets the chant take his mouth without giving it his interior.",
                        "He matches the room's rhythm carefully enough to disappear inside it.",
                        "The performance works because his anger is aimed sideways, never where the telescreen expects it.",
                    ],
                },
                {
                    "text": "Watch Julia instead of the screen and treat desire as a more dangerous signal than rage.",
                    "reaction_texts": [
                        "He studies Julia through the ritual and realizes appetite can be as incriminating as dissent.",
                        "The hate session becomes cover for an entirely different forbidden attention.",
                        "What begins as lust hardens into a question about whether intimacy can survive surveillance.",
                    ],
                },
                {
                    "text": "Study O'Brien's face while Goldstein burns on the screen.",
                    "reaction_texts": [
                        "Winston spends the room's fury on observation rather than obedience.",
                        "The real image worth reading is not Goldstein but the Inner Party man pretending not to be readable.",
                        "A tiny possibility opens: O'Brien may understand more than he should, or want Winston to think so.",
                    ],
                },
            ],
        },
        "page_scene_03": {
            "title": "Scene 4: Julia's Note and the Coral Paperweight",
            "text": (
                "Julia's note and the coral paperweight do different kinds of subversive work. One invites romance with operational risk; "
                "the other suggests that a private world might be held, briefly, inside something useless and beautiful."
            ),
            "options": [
                {
                    "text": "Pocket Julia's note and keep your face professionally dead.",
                    "reaction_texts": [
                        "Winston accepts the note as if it were a clerical hazard rather than an emotional detonation.",
                        "The romance survives only because the face presented to the Ministry remains blank.",
                        "He learns that concealment is the first grammar of love in Oceania.",
                    ],
                },
                {
                    "text": "Answer Julia with caution, not hunger.",
                    "reaction_texts": [
                        "He chooses pacing over surrender, treating romance as a cell structure rather than an escape.",
                        "Desire is moderated into method so the affair can last longer than one brave impulse.",
                        "The restraint is intimate in its own way: a promise not to spend the relationship recklessly.",
                    ],
                },
                {
                    "text": "Treat the paperweight as a rehearsal for keeping one unedited room inside yourself.",
                    "reaction_texts": [
                        "The paperweight becomes less souvenir than doctrine: proof that a useless object can protect a useless truth.",
                        "Winston tests whether memory can be held materially, not just sentimentally.",
                        "The gesture is romantic too, but toward continuity rather than toward Julia alone.",
                    ],
                },
            ],
        },
        "page_scene_07": {
            "title": "Scene 8: Goldstein's Book",
            "text": (
                "Goldstein arrives not as a man in the room but as a system of explanations in O'Brien's keeping. "
                "The book offers Winston theory, but spycraft demands a second question: is the text a weapon, a mirror, or bait designed to profile the reader?"
            ),
            "options": [
                {
                    "text": "Read Goldstein for tactical truth, not salvation.",
                    "reaction_texts": [
                        "Winston mines the forbidden theory for usable diagnostics rather than emotional deliverance.",
                        "The book is most dangerous when treated as scripture; he keeps it at the colder distance of tradecraft.",
                        "He wants the model without surrendering to the vanity of feeling chosen by it.",
                    ],
                },
                {
                    "text": "Use Goldstein's abstractions to talk around your real loyalties.",
                    "reaction_texts": [
                        "Theory becomes a screen behind which Winston can move his actual commitments out of sight.",
                        "He borrows the language of revolution to conceal the much smaller truths he is actually trying to protect.",
                        "The move is rhetorically useful because abstraction is harder to prosecute than naked intimacy.",
                    ],
                },
                {
                    "text": "Treat the book as bait and read O'Brien through it instead.",
                    "reaction_texts": [
                        "The real text becomes O'Brien's posture around the text: what he emphasizes, what he smooths over, what he expects Winston to admire.",
                        "Winston reads the curation as carefully as the doctrine.",
                        "Goldstein matters here as a test surface for the spy standing nearby.",
                    ],
                },
            ],
        },
    }

    iconic_overrides.update(
        {
            "page_scene_01": {
                "title": "Scene 2: Memory Hole Timing",
                "text": (
                    "The memory hole destroys facts, but the delivery tubes that feed it still answer to physics. "
                    "Winston can obey the correction order, or study the transit rhythm that might someday carry a message the censors cannot see in time."
                ),
                "options": [
                    {
                        "text": "Correct the article cleanly and leave no unauthorized rhythm in the tubes.",
                        "reaction_texts": [
                            "Winston makes the correction exact enough to leave the machine no residue to examine.",
                            "He gives the archive smooth obedience and learns nothing that cannot be safely forgotten.",
                            "The tube swallows the paper and returns only procedure.",
                        ],
                    },
                    {
                        "text": "Misroute one harmless scrap and learn who notices latency before content.",
                        "reaction_texts": [
                            "The point is not the scrap itself but the order in which different people react to its delay.",
                            "Winston learns that some eyes audit timing first and ideology second.",
                            "A trivial misroute becomes a survey of who in the Ministry is listening for pattern rather than meaning.",
                        ],
                        "effects": [
                            nudge_keyring_effect(primary_char, ["pSuspicion"], 0.01),
                            nudge_effect(primary_char, "Private_Self", 0.01),
                        ],
                    },
                    {
                        "text": "Send a doomed paragraph through a dead pneumatic address and time the echo.",
                        "reaction_texts": [
                            "The dead address sends the paragraph wandering just long enough to reveal a blind interval in correction traffic.",
                            "What returns is not information but timing, and timing is enough to suggest a future signal path.",
                            "Winston discovers that the archive has a pulse, and that any pulse can be stolen if you learn its slack.",
                        ],
                        "effects": [
                            nudge_effect(primary_char, COUNTER_SIGNAL, 0.035),
                            nudge_effect(primary_char, RECEIVER_ASSEMBLY, 0.015),
                            nudge_keyring_effect(primary_char, ["pSuspicion"], 0.02),
                            nudge_effect(primary_char, "Exposure", 0.01),
                            nudge_effect(primary_char, "Private_Self", 0.01),
                        ],
                    },
                ],
            },
            "page_scene_02": {
                "title": "Scene 3: Canteen Static",
                "text": (
                    "Lunch noise helps the Party because it makes every private signal look like boredom or appetite. "
                    "The canteen is also where maintenance gossip, Julia's movement, and loudspeaker hiss cross without official choreography."
                ),
                "options": [
                    {
                        "text": "Keep the talk trivial and learn nothing that has to be hidden.",
                        "reaction_texts": [
                            "Winston leaves the meal with his cover intact and his imagination unfed.",
                            "Triviality keeps him safe by preventing any new commitment from forming.",
                            "He lets the canteen remain what it wants to be: dead time.",
                        ],
                    },
                    {
                        "text": "Trade cigarette chatter for the loudspeaker maintenance rota and call it boredom.",
                        "reaction_texts": [
                            "The rota sounds useless until Winston hears how often the speaker grid has to be touched by ordinary hands.",
                            "He gets the schedule by appearing to care only about avoiding noise, never about exploiting it.",
                            "A piece of maintenance trivia becomes the first human map of the broadcast machine.",
                        ],
                        "effects": [
                            nudge_effect(primary_char, COUNTER_SIGNAL, 0.025),
                            nudge_effect(primary_char, "Trust", 0.01),
                            nudge_keyring_effect(primary_char, ["pSuspicion"], 0.01),
                        ],
                    },
                    {
                        "text": "Let Syme's phonetics lecture cover the moment you count a desynchronized speaker.",
                        "reaction_texts": [
                            "Syme provides the noise floor while Winston listens for the speaker that lags half a beat behind the rest.",
                            "The useful truth is tiny: a stutter in the room's enforced simultaneity.",
                            "He learns that even synchronized hatred runs through imperfect hardware.",
                        ],
                        "effects": [
                            nudge_effect(primary_char, COUNTER_SIGNAL, 0.015),
                            nudge_effect(primary_char, "Defiance", 0.01),
                        ],
                    },
                ],
            },
            "page_scene_03": {
                "title": "Scene 4: Julia's Note and the Coral Paperweight",
                "text": (
                    "Julia's note and the coral paperweight do different kinds of subversive work. One invites romance with operational risk; "
                    "the other suggests that a private world might be held, briefly, inside something useless and beautiful."
                ),
                "options": [
                    {
                        "text": "Pocket Julia's note and keep your face professionally dead.",
                        "reaction_texts": [
                            "Winston accepts the note as if it were a clerical hazard rather than an emotional detonation.",
                            "The romance survives only because the face presented to the Ministry remains blank.",
                            "He learns that concealment is the first grammar of love in Oceania.",
                        ],
                    },
                    {
                        "text": "Answer Julia with caution, not hunger.",
                        "reaction_texts": [
                            "He chooses pacing over surrender, treating romance as a cell structure rather than an escape.",
                            "Desire is moderated into method so the affair can last longer than one brave impulse.",
                            "The restraint is intimate in its own way: a promise not to spend the relationship recklessly.",
                        ],
                    },
                    {
                        "text": "Treat the paperweight as a rehearsal for keeping one unedited room, and maybe one hidden crystal, inside yourself.",
                        "reaction_texts": [
                            "The paperweight becomes less souvenir than doctrine: proof that a useless object can protect a useless truth and perhaps shelter contraband hardware.",
                            "Winston tests whether memory can be held materially, not just sentimentally, and whether beauty can double as camouflage.",
                            "The gesture is romantic too, but toward continuity and future coordination rather than toward Julia alone.",
                        ],
                        "effects": [
                            nudge_effect(primary_char, COUNTER_SIGNAL, 0.03),
                            nudge_effect(primary_char, "Private_Self", 0.02),
                            nudge_effect(primary_char, "Trust", 0.01),
                        ],
                    },
                ],
            },
        }
    )

    iconic_overrides.update(
        {
            "page_scene_10": {
                "title": "Scene 11: Relay Contacts",
                "text": (
                    "Under pressure, Winston notices that the Party's voice still depends on clerks, repair hands, meal breaks, and relay grease. "
                    "No regime is metaphysical all the way down if someone ordinary still has to tighten the screws."
                ),
                "options": [
                    {
                        "text": "Answer only what is asked and take no new risk.",
                        "reaction_texts": [
                            "Winston narrows his life to compliance and immediate endurance.",
                            "The discipline protects him by refusing every possible expansion of the plot.",
                            "Nothing new is learned because learning itself would become another exposure surface.",
                        ],
                    },
                    {
                        "text": "Memorize which clerk handles speaker repairs and when he eats.",
                        "reaction_texts": [
                            "The detail looks petty, which is exactly why it survives in Winston's head.",
                            "A resistance route begins to require not heroes but lunch habits and shift changes.",
                            "He finds himself building an insurgent timetable out of clerical trivia.",
                        ],
                        "effects": [
                            nudge_effect(primary_char, COUNTER_SIGNAL, 0.02),
                            nudge_effect(primary_char, "Exposure", 0.01),
                        ],
                    },
                    {
                        "text": "Treat every relay click as part of the same machine you are trying to steal a minute from.",
                        "reaction_texts": [
                            "The clicks cease to be background and become a discipline of listening.",
                            "Winston starts imagining that a victory in Oceania may look less like a speech than like one stolen minute of synchronization.",
                            "The idea is dangerous because it makes resistance feel technically solvable.",
                        ],
                        "effects": [
                            nudge_effect(primary_char, COUNTER_SIGNAL, 0.015),
                            nudge_effect(primary_char, "Private_Self", 0.01),
                        ],
                    },
                ],
            },
            "page_scene_11": {
                "title": "Scene 12: Paperweight Cavity",
                "text": (
                    "The coral paperweight changes meaning once more. "
                    "It can remain a shrine to memory, or become the innocent housing for the cracked crystal Winston has no lawful reason to own."
                ),
                "options": [
                    {
                        "text": "Keep the paperweight as memory and refuse to turn tenderness into hardware.",
                        "reaction_texts": [
                            "Winston protects the object's emotional function by denying it operational use.",
                            "The choice keeps romance cleaner, if less useful.",
                            "He preserves one symbol by refusing to ask it for work.",
                        ],
                    },
                    {
                        "text": "Use the coral cavity to hide the cracked crystal in plain sight.",
                        "reaction_texts": [
                            "The paperweight becomes a casing so obvious no one thinks to inspect it as a machine.",
                            "Beauty turns out to be the perfect alibi for contraband engineering.",
                            "Winston finally has a receiver that can exist in the room as decor rather than evidence.",
                        ],
                        "effects": [
                            nudge_effect(primary_char, COUNTER_SIGNAL, 0.04),
                            nudge_effect(primary_char, RECEIVER_ASSEMBLY, 0.06),
                            nudge_effect(primary_char, "Private_Self", 0.02),
                        ],
                    },
                    {
                        "text": "Let Julia see romance while you quietly sketch where a receiver could hide.",
                        "reaction_texts": [
                            "The lie is not to Julia exactly, but to the category of romance itself.",
                            "Winston turns intimacy into reconnaissance and hopes the tenderness survives the rehearsal.",
                            "The object becomes a concealment study first, not yet a finished device.",
                        ],
                        "effects": [
                            nudge_effect(primary_char, COUNTER_SIGNAL, 0.03),
                            nudge_effect(primary_char, "Trust", 0.02),
                            nudge_effect(primary_char, "Exposure", 0.01),
                        ],
                    },
                ],
            },
            "page_scene_12": {
                "title": "Scene 13: Before Room 101",
                "text": (
                    "Room 101 remains ahead of Winston, but that only makes it more operationally important. "
                    "Anything worth preserving must be positioned now, before fear personal enough to end method is allowed to take the room."
                ),
                "options": [
                    {
                        "text": "Let fear narrow you and protect only the self that can still feel.",
                        "reaction_texts": [
                            "Winston contracts around the simplest surviving interior truth.",
                            "Feeling remains, but planning recedes.",
                            "The move saves humanity at the cost of logistics.",
                        ],
                    },
                    {
                        "text": "Move the receiver, cache the schedule, and decide what panic is not allowed to touch.",
                        "reaction_texts": [
                            "He treats future terror as a constraint to engineer around rather than a prophecy to obey.",
                            "The receiver and the release schedule are separated so fear cannot destroy both at once.",
                            "Winston learns that courage here is mostly procedural.",
                        ],
                        "effects": [
                            nudge_effect(primary_char, COUNTER_SIGNAL, 0.02),
                            nudge_effect(primary_char, RECEIVER_ASSEMBLY, 0.05),
                            nudge_effect(primary_char, "Private_Self", 0.02),
                            nudge_effect(primary_char, "Exposure", -0.005),
                        ],
                    },
                    {
                        "text": "Rehearse answering terror with procedure: frequency, courier, silence, release.",
                        "reaction_texts": [
                            "The sequence matters because terror tries to erase sequence first.",
                            "Winston reduces panic to a checklist and in doing so steals some authority back from it.",
                            "The resistance route survives only because he practices it as method before it becomes emergency.",
                        ],
                        "effects": [
                            nudge_effect(primary_char, COUNTER_SIGNAL, 0.03),
                            nudge_effect(primary_char, "Defiance", 0.02),
                            nudge_keyring_effect(primary_char, ["pPrivate_Self"], 0.02),
                        ],
                    },
                ],
            },
        }
    )

    iconic_overrides.update(
        {
            "page_scene_07": {
                "title": "Scene 8: Goldstein's Book",
                "text": (
                    "Goldstein arrives not as a man in the room but as a system of explanations in O'Brien's keeping. "
                    "The book offers Winston theory, but spycraft demands a second question: is the text a weapon, a mirror, or bait designed to profile the reader?"
                ),
                "options": [
                    {
                        "text": "Read Goldstein for tactical truth, not salvation.",
                        "reaction_texts": [
                            "Winston mines the forbidden theory for usable diagnostics rather than emotional deliverance.",
                            "The book is most dangerous when treated as scripture; he keeps it at the colder distance of tradecraft.",
                            "He wants the model without surrendering to the vanity of feeling chosen by it.",
                        ],
                    },
                    {
                        "text": "Use Goldstein's abstractions to talk around your real loyalties.",
                        "reaction_texts": [
                            "Theory becomes a screen behind which Winston can move his actual commitments out of sight.",
                            "He borrows the language of revolution to conceal the much smaller truths he is actually trying to protect.",
                            "The move is rhetorically useful because abstraction is harder to prosecute than naked intimacy.",
                        ],
                    },
                    {
                        "text": "Treat the book as bait and mine O'Brien's curation for a counter-signal schedule.",
                        "reaction_texts": [
                            "The real appendix is O'Brien's emphasis: what logistics he lingers over, what timings he assumes Winston will ignore.",
                            "Winston reads the curation as a schedule for how power expects messages to move.",
                            "Goldstein matters here as a theory text and as a disguised wiring diagram for the machine that contains it.",
                        ],
                        "effects": [
                            nudge_effect(primary_char, COUNTER_SIGNAL, 0.03),
                            nudge_keyring_effect(primary_char, ["pSuspicion", spy_char], 0.02),
                            nudge_effect(primary_char, "Defiance", 0.01),
                        ],
                    },
                ],
            },
            "page_scene_08": {
                "title": "Scene 9: Telescreen Sync",
                "text": (
                    "The telescreen looks continuous only because everyone submits to its rhythm. "
                    "Winston can listen to the slogans, or to the retrace hiss beneath them that suggests even surveillance has a mechanical seam."
                ),
                "options": [
                    {
                        "text": "Accept O'Brien's invitation and decide what version of yourself the room should archive.",
                        "reaction_texts": [
                            "The invitation is accepted, but Winston treats even his posture as authored evidence.",
                            "He enters the room already thinking about what O'Brien will believe he has discovered.",
                            "The scene begins as performance design rather than confession.",
                        ],
                    },
                    {
                        "text": "Listen past the slogans for the retrace hiss and map the broadcast gap.",
                        "reaction_texts": [
                            "The hiss is tiny, but once heard it turns the telescreen from revelation into equipment.",
                            "Winston learns where the broadcast edge frays just enough to imagine piggybacking a signal on it.",
                            "He begins hearing the Party's voice as infrastructure rather than fate.",
                        ],
                        "effects": [
                            nudge_effect(primary_char, COUNTER_SIGNAL, 0.035),
                            nudge_effect(primary_char, RECEIVER_ASSEMBLY, 0.02),
                            nudge_keyring_effect(primary_char, ["pSuspicion"], 0.015),
                        ],
                    },
                    {
                        "text": "Give the telescreen a loyal face while counting the sync stutter under your breath.",
                        "reaction_texts": [
                            "The loyal face buys cover for a much less loyal arithmetic running underneath it.",
                            "Winston rehearses how camouflage and engineering may have to inhabit the same breath.",
                            "The count gives him a rhythm he can carry into O'Brien's room without revealing why it matters.",
                        ],
                        "effects": [
                            nudge_effect(primary_char, COUNTER_SIGNAL, 0.02),
                            nudge_effect(primary_char, "Submission", 0.01),
                            nudge_keyring_effect(primary_char, ["pSubmission", spy_char, primary_char], 0.015),
                        ],
                    },
                ],
            },
            "page_scene_09": {
                "title": "Scene 10: Archive Backflow",
                "text": (
                    "After O'Brien's interview, routine corrections feel annotated by an invisible witness. "
                    "The archive can still be used defensively, but it might also be persuaded to carry a hidden cadence back through its own queues."
                ),
                "options": [
                    {
                        "text": "Keep the archive smooth and trust survival to invisibility.",
                        "reaction_texts": [
                            "Winston decides the safest correction is the one nobody could later overread.",
                            "Smooth work keeps his file thin and his imagination unused.",
                            "The machine remains a wall rather than a route.",
                        ],
                    },
                    {
                        "text": "Plant one harmless discrepancy and see who hunts it.",
                        "reaction_texts": [
                            "The discrepancy is bait for an auditor more than a message for an ally.",
                            "Winston learns which layer of the Ministry still believes perfect records are worth chasing.",
                            "The trick reveals attention patterns without yet committing him to a broader scheme.",
                        ],
                        "effects": [
                            nudge_keyring_effect(primary_char, ["pSuspicion"], 0.02),
                            nudge_effect(primary_char, "Private_Self", 0.01),
                        ],
                    },
                    {
                        "text": "Thread three dead revisions into separate queues so a counter-signal could braid through them later.",
                        "reaction_texts": [
                            "Each revision is harmless alone and meaningful only as interval.",
                            "Winston stops thinking like an editor and starts thinking like a clockmaker working inside a furnace.",
                            "The archive begins to look less like a graveyard for truth than a temporary carrier wave for it.",
                        ],
                        "effects": [
                            nudge_effect(primary_char, COUNTER_SIGNAL, 0.035),
                            nudge_effect(primary_char, "Defiance", 0.02),
                            nudge_effect(primary_char, "Exposure", 0.01),
                        ],
                    },
                ],
            },
        }
    )

    iconic_overrides.update(
        {
            "page_scene_04": {
                "title": "Scene 5: Rumor of Room 101",
                "text": (
                    "Room 101 reaches Winston first as rumor, which means it already works as intelligence. "
                    "If fear is personalized that precisely, then terror is cataloged somewhere by someone with a clerk's habits."
                ),
                "options": [
                    {
                        "text": "Dismiss the rumor as deliberate theater and keep your face blank.",
                        "reaction_texts": [
                            "Winston refuses to grant the rumor inner residence.",
                            "The blank face keeps fear from becoming a visible collaboration with the Ministry.",
                            "He survives the moment by declining to investigate it at all.",
                        ],
                    },
                    {
                        "text": "Notice which details repeat too consistently to be folklore.",
                        "reaction_texts": [
                            "The repetition is the tell: too many mouths know the same shape of fear.",
                            "Winston learns that even terror propaganda contains metadata about how it is managed.",
                            "A rumor becomes useful once he stops asking whether it is true and starts asking who needs it standardized.",
                        ],
                        "effects": [
                            nudge_keyring_effect(primary_char, ["pSuspicion"], 0.02),
                            nudge_effect(primary_char, "Private_Self", 0.01),
                        ],
                    },
                    {
                        "text": "Map fear as bureaucracy: if terror is personalized, someone keeps the catalog.",
                        "reaction_texts": [
                            "Winston stops treating terror as pure theater and starts reading it as indexed procedure.",
                            "The insight is operational: the Ministry's most intimate violence still depends on files, schedules, and storage.",
                            "That realization does not comfort him, but it does suggest the regime can be reached through its clerical spine.",
                        ],
                        "effects": [
                            nudge_effect(primary_char, COUNTER_SIGNAL, 0.015),
                            nudge_effect(primary_char, "Defiance", 0.02),
                            nudge_keyring_effect(primary_char, ["pSuspicion", spy_char], 0.02),
                        ],
                    },
                ],
            },
            "page_scene_05": {
                "title": "Scene 6: Newspeak Compression",
                "text": (
                    "Newspeak is supposed to remove nuance, but compression creates pattern, and pattern can sometimes carry what plain speech cannot. "
                    "Winston has to decide whether clipped language only shrinks thought or whether it can be bent into covert timing."
                ),
                "options": [
                    {
                        "text": "Use the official abbreviations exactly as instructed.",
                        "reaction_texts": [
                            "He handles the compressed language as a faithful technician of reduction.",
                            "Exact compliance leaves no gap wide enough for a private payload.",
                            "The language does what it was designed to do: eliminate surplus meaning.",
                        ],
                    },
                    {
                        "text": "Hold back one slogan and listen to how the gap changes the room.",
                        "reaction_texts": [
                            "The missing slogan is tiny but measurable in the social temperature around him.",
                            "Winston learns how quickly absence itself becomes legible in a synchronized culture.",
                            "The experiment teaches caution more than possibility.",
                        ],
                    },
                    {
                        "text": "Hide a checksum in approved abbreviations and test whether clipped language can carry contraband timing.",
                        "reaction_texts": [
                            "The code is not semantic but rhythmic, buried in what appears to be flawless ideological shorthand.",
                            "Winston discovers that stripped language can still carry a private metronome if the receiver already knows where to listen.",
                            "A tool built to narrow thought becomes, for one disciplined moment, a channel for conspiracy.",
                        ],
                        "effects": [
                            nudge_effect(primary_char, COUNTER_SIGNAL, 0.04),
                            nudge_effect(primary_char, RECEIVER_ASSEMBLY, 0.015),
                            nudge_effect(primary_char, "Defiance", 0.02),
                            nudge_keyring_effect(primary_char, ["pPrivate_Self"], 0.01),
                            nudge_effect(primary_char, "Exposure", 0.01),
                        ],
                    },
                ],
            },
            "page_scene_06": {
                "title": "Scene 7: Prole Quarter Receiver",
                "text": (
                    "The prole quarter still contains broken devices nobody bothers to ideology-proof. "
                    "Among razor blades, bad gin, and junk-stall dust, Winston may be able to find a physical component the Ministry forgot to fear."
                ),
                "options": [
                    {
                        "text": "Move through the quarter as a customer, not a pilgrim.",
                        "reaction_texts": [
                            "He buys nothing that would outlive the afternoon.",
                            "Ordinariness becomes camouflage by refusing every dramatic temptation the quarter offers.",
                            "The safest version of the prole quarter is one that leaves no trace on Winston at all.",
                        ],
                    },
                    {
                        "text": "Buy a cracked radio crystal under cover of shopping for razor blades.",
                        "reaction_texts": [
                            "The crystal is worthless to anyone who sees only rubbish and invaluable to anyone thinking about signal.",
                            "Winston acquires the part by acting embarrassed rather than purposeful.",
                            "The new technology is not new to the world, only newly imagined as resistance hardware.",
                        ],
                        "effects": [
                            nudge_effect(primary_char, COUNTER_SIGNAL, 0.05),
                            nudge_effect(primary_char, RECEIVER_ASSEMBLY, 0.06),
                            nudge_effect(primary_char, "Exposure", 0.02),
                            nudge_effect(primary_char, "Defiance", 0.01),
                        ],
                    },
                    {
                        "text": "Ask about blackout hours and repair vans until the quarter reveals how the signal really moves.",
                        "reaction_texts": [
                            "The answers arrive as gossip rather than doctrine, which makes them easier to trust.",
                            "Winston learns that the Party's seamless voice depends on very material interruptions and repair routes.",
                            "The quarter yields not a part but a logistics diagram spoken in fragments.",
                        ],
                        "effects": [
                            nudge_effect(primary_char, COUNTER_SIGNAL, 0.025),
                            nudge_keyring_effect(primary_char, ["pSuspicion"], 0.015),
                            nudge_effect(primary_char, "Private_Self", 0.01),
                        ],
                    },
                ],
            },
        }
    )

    for enc_id, override in iconic_overrides.items():
        encounter = encounter_directory.get(enc_id)
        if not encounter:
            continue
        encounter["title"] = override["title"]
        encounter["text_script"] = ptr_string(override["text"])
        for option, option_override in zip(encounter.get("options", []) or [], override.get("options", [])):
            option["text_script"] = ptr_string(option_override["text"])
            for reaction, reaction_text in zip(option.get("reactions", []) or [], option_override.get("reaction_texts", [])):
                reaction["text_script"] = ptr_string(reaction_text)
                if option_override.get("effects"):
                    reaction.setdefault("after_effects", [])
                    reaction["after_effects"].extend(json.loads(json.dumps(option_override["effects"])))

    ordered_nonterminal_encounters = [encounter_directory[enc_id] for enc_id in ordered_nonterminal_ids]
    if len(ordered_nonterminal_encounters) + len(terminal_encounters) != 80:
        raise SystemExit(f"expected 80 total encounters, found {len(ordered_nonterminal_encounters) + len(terminal_encounters)}")

    data["encounters"] = ordered_nonterminal_encounters + terminal_encounters

    data["spools"] = [
        {
            "id": "spool_start_followup",
            "spool_name": "Start + Followup",
            "starts_active": True,
            "creation_index": 0,
            "creation_time": now,
            "modified_time": now,
            "encounters": [enc_id for enc_id in ordered_nonterminal_ids if encounter_directory[enc_id].get("connected_spools") == ["spool_start_followup"]],
        },
        {
            "id": "spool_mid",
            "spool_name": "Mid",
            "starts_active": False,
            "creation_index": 1,
            "creation_time": now,
            "modified_time": now,
            "encounters": [enc_id for enc_id in ordered_nonterminal_ids if encounter_directory[enc_id].get("connected_spools") == ["spool_mid"]],
        },
        {
            "id": "spool_penultimate",
            "spool_name": "Penultimate",
            "starts_active": False,
            "creation_index": 2,
            "creation_time": now,
            "modified_time": now,
            "encounters": [followup_id, gate_id],
        },
        {
            "id": "spool_endings",
            "spool_name": "Endings",
            "starts_active": False,
            "creation_index": 3,
            "creation_time": now,
            "modified_time": now,
            "encounters": [enc_id for enc_id, *_ in endings],
        },
    ]

    data["storyworld_title"] = "1984: The Last Private Sentence"
    data["modified_time"] = now

    if args.apply:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")

    print(path)
    print("endings=9 gate=page_endings_gate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
