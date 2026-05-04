#!/usr/bin/env python3
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "mutazili_ashari_kalam_exam_9b_research.json"
DESIGN_PACKET = ROOT / "qwen9b_design_packet.json"

PROPS = [
    ("Justice_Agency", "How strongly the ruling preserves moral responsibility and divine justice."),
    ("Power_Acquisition", "How strongly the ruling preserves divine omnipotence while locating human acquisition."),
    ("Attribute_Unity", "How carefully the ruling handles divine attributes without crude anthropomorphism or emptying scripture."),
    ("Speech_Createdness", "How carefully the ruling distinguishes created utterance/ink from divine speech or meaning."),
    ("Public_Concord", "How stable the school, court, and market remain after the ruling."),
]

CHARS = [
    ("char_student", "Yusuf Lin", "he"),
    ("char_mutazili", "Qadi Nizam al-Adl", "he"),
    ("char_ashari", "Shaykha Baraka al-Sifat", "she"),
    ("char_scribe", "Mariam the Court Scribe", "she"),
    ("char_public", "The Listening Market", "they"),
]

SCENES = [
    ("page_001_gate_of_two_schools", "The Gate of Two Schools", "Yusuf Lin enters the examination hall at sunrise. On the left wall, Qadi Nizam has written justice before power; on the right, Shaykha Baraka has written power before every cause. Mariam sets a blank ruling register between them. The first question is not who is correct. It is whether a qadi can keep a city alive while two grammars of God pull the same case apart.", "identity", "both"),
    ("page_002_stolen_bread_decree", "The Bread Thief And The Decree", "A boy admits stealing bread and says hunger and decree moved his hand before choice did. Nizam asks whether punishment is intelligible without real human agency. Baraka asks whether agency can become a second creator. The baker waits for restitution, not metaphysics.", "qadar", "justice"),
    ("page_003_attributes_of_the_witness", "Attributes Of The Hidden Witness", "A witness swears that God heard his oath. The phrase turns dangerous in the hall. Does hearing name a real divine attribute, a metaphor protected by tawhid, or an unsafe likeness to creatures? Mariam's pen pauses above the register because one wrong word can make testimony either pious or unusable.", "attributes", "attributes"),
    ("page_004_created_ink_register", "The Created Ink Register", "A Qur'anic verse appears as ink on a legal summons. Nizam asks whether calling the written sign uncreated multiplies eternals. Baraka distinguishes the created letters from eternal speech, but the defendant only wants to know whether the summons binds him.", "created_quran", "speech"),
    ("page_005_fire_in_the_scriptorium", "Fire In The Scriptorium", "A lamp falls and burns a contract. The merchant calls fire the cause. Baraka says habit is not independent power. Nizam asks whether courts can function if every cause becomes invisible. Yusuf must decide what kind of causation can enter evidence.", "causation", "power"),
    ("page_006_oath_of_the_soldier", "The Soldier's Oath", "A soldier obeyed a governor's order and now claims the command acquired his act for him. Nizam separates command, intention, and harm. Baraka asks whether obedience itself is created under divine power. The wounded family sits close enough to hear every abstraction.", "acquisition", "justice"),
    ("page_007_the_physician_cure", "The Physician's Cure", "A physician cured one patient and failed another with the same medicine. The market calls the cure natural skill; the bereaved call it arrogance. Baraka treats medicine as a habit of divine mercy. Nizam asks whether expertise can be praised if causation is only apparent.", "causation", "power"),
    ("page_008_anthropomorphic_seal", "The Seal With A Hand", "A royal seal bears a verse about God's hand. The governor wants literal authority; Nizam suspects political theater. Baraka warns that figurative interpretation can become denial if used too cheaply. Yusuf must decide whether the seal can authorize exile.", "attributes", "attributes"),
    ("page_009_widows_lost_letter", "The Widow's Lost Letter", "A widow burned one letter and preserved another. She says God exposed the truth by letting the ash scatter into a name. Nizam asks whether signs can be morally read without superstition. Baraka asks whether providence may guide evidence without becoming courtroom magic.", "evidence", "both"),
    ("page_010_minaret_of_created_speech", "The Minaret Of Created Speech", "The muezzin recites a disputed formula from the minaret. The crowd hears eternal command, created voice, political loyalty, and fear all at once. Yusuf must rule whether public recitation can be evidence of doctrine or only evidence of public pressure.", "created_quran", "speech"),
    ("page_011_market_of_secondary_causes", "The Market Of Secondary Causes", "An apothecary sells a remedy and advertises certainty. Baraka calls certainty theft from divine power. Nizam calls false certainty fraud against human need. The Listening Market becomes a jury of coughs, coins, and whispered prayers.", "causation", "public"),
    ("page_012_prisoner_of_compulsion", "The Prisoner Of Compulsion", "A prisoner says he chose nothing because God creates all acts. Nizam asks whether that answer destroys law. Baraka asks whether law can survive without admitting acquisition. Mariam writes both words, creation and acquisition, and notices the ink does not dry.", "qadar", "justice"),
    ("page_013_debate_of_names", "The Debate Of Names", "The examiners ask Yusuf to name God without making names into rivals. Each beautiful name opens a possible error: metaphor, denial, multiplication, or crude image. The case attached to the question is a child denied inheritance because her name was mistranscribed.", "attributes", "attributes"),
    ("page_014_mihna_memory", "The Memory Of The Inquisition", "An old scholar remembers being beaten over the created Qur'an question. Nizam says coercion proves doctrine cannot be purified by force. Baraka says public doctrine still shapes law. Yusuf must rule whether a coerced confession about speech can bind a later court.", "created_quran", "public"),
    ("page_015_scribes_missing_dot", "The Missing Dot", "Mariam discovers one missing dot changes a legal name. Is the truth in the eternal meaning, the created mark, the intention of the scribe, or the public record? The page seems small until an inheritance, a marriage, and a prison door depend on it.", "speech", "speech"),
    ("page_016_governors_occasionalist_order", "The Governor's Occasionalist Order", "The governor argues that since God creates outcomes, he should not be blamed for a famine policy. Baraka is offended by the abuse of divine power. Nizam is offended by the attempted escape from justice. Yusuf must make both offenses legally useful.", "power_abuse", "justice"),
    ("page_017_child_and_the_broken_cup", "The Child And The Broken Cup", "A child breaks a cup while repeating a lesson on acquisition. The hall laughs until the merchant demands payment. The case asks how responsibility grows: from power, intention, habit, age, knowledge, or the mercy that lets law teach before it crushes.", "agency", "justice"),
    ("page_018_star_chart_of_habit", "The Star Chart Of Habit", "An astrologer predicts a verdict and claims heavenly causes. Baraka rejects independent necessity; Nizam rejects fatalist excuse. The chart is beautiful enough to tempt the court, but Mariam has seen similar charts sold in three alleys.", "causation", "power"),
    ("page_019_attribute_ledger", "The Attribute Ledger", "Baraka draws columns for knowledge, power, will, hearing, sight, and speech. Nizam draws one circle and writes nothing inside it. Yusuf must convert the diagram into a ruling about an oath that names all six attributes as witnesses.", "attributes", "attributes"),
    ("page_020_two_minbars", "The Two Minbars", "Two preachers accuse each other of endangering tawhid. The market begins choosing sides by neighborhood, not argument. Yusuf must decide whether the qadi's task is doctrinal victory, civic quiet, or a ruling that leaves both schools unable to weaponize God.", "public", "public"),
    ("page_021_acquisition_of_a_lie", "The Acquisition Of A Lie", "A clerk forged testimony and says the lie came to him like weather. Nizam demands responsibility. Baraka demands a grammar that does not make the clerk creator of falsehood. Mariam waits to see whether the register will become an accomplice.", "acquisition", "justice"),
    ("page_022_eternal_meaning_created_voice", "Eternal Meaning, Created Voice", "A blind reciter, a deaf jurist, and a child reading ink each encounter the same verse differently. The exam asks which encounter binds law. Yusuf sees that the case is really about how a court recognizes meaning without pretending to hold eternity in its hand.", "speech", "speech"),
    ("page_023_trial_of_the_safe_answer", "Trial Of The Safe Answer", "The examiners offer Yusuf a safe formula that could pass either school if spoken without consequence. Then they bring in a condemned man whose sentence turns on the formula's meaning. Safety becomes a lie if it refuses to rule.", "synthesis", "both"),
    ("page_024_register_that_judges_back", "The Register That Judges Back", "Mariam reads the day's rulings aloud and the register seems to judge the judges. Every earlier answer returns as a person harmed or protected. The last ordinary question asks whether a qadi can be orthodox without becoming useless to the living.", "reckoning", "public"),
    ("page_025_bridge_house_of_acquisition", "Bridge: The House Of Acquisition", "Yusuf enters a side chamber where neither examiner sits. The cases are replayed as acquisitions: not independent creation, not empty compulsion, but public acceptance of responsibility under divine power. The bridge does not solve the schools. It asks whether law can keep their warnings alive.", "bridge", "secret"),
    ("page_026_bridge_chalk_of_no_how", "Bridge: The Chalk Of No How", "On the chalkboard, attributes remain named but not pictured; justice remains demanded but not made into a rival power. The secret exam asks Yusuf to preserve both prohibitions at once: do not make God a mechanism, and do not make humans puppets.", "bridge", "secret"),
]

ENDINGS = [
    ("page_end_mutazili_verdict", "Ending: Justice Writes The Verdict", "Yusuf rules in a way that prizes human accountability and divine justice. Nizam approves, the market understands the punishment, and Baraka warns that the grammar of power has been made too small."),
    ("page_end_ashari_verdict", "Ending: Power Refuses The Mechanism", "Yusuf protects divine omnipotence and refuses independent causes. Baraka approves, the hall avoids crude mechanism, and Nizam warns that victims will hear only fog where justice should speak."),
    ("page_end_public_quiet", "Ending: The City Sleeps Uneasily", "Yusuf chooses civic quiet over doctrinal precision. The market calms, the governor smiles, and the register records a judgment so safe that no wounded person can use it."),
    ("page_end_heretic_file", "Ending: The Heretic File", "Yusuf speaks too sharply and the court files him as a danger. His answer may be subtle, but subtlety cannot protect a student who lets the hall become a battlefield."),
    ("page_end_scribe_truth", "Ending: Mariam Preserves The Margin", "Yusuf lets Mariam's register expose what the doctrines missed. The ruling is legally narrow, textually exact, and kinder than either faction expected."),
    ("page_end_market_schism", "Ending: The Market Splits The Schools", "The ruling becomes a slogan. Two neighborhoods repeat two halves of Yusuf's answer until neither side remembers the case that required it."),
    ("page_end_acquisition_synthesis", "Secret Ending: The Acquired Judgment", "Yusuf refuses both slogans and frames judgment as acquired responsibility under divine power. The court cannot call it compromise, because every case has been answered. The two lamps remain separate, but the road between them becomes a school."),
    ("page_end_no_how_lantern", "Secret Ending: The Lantern Without How", "Yusuf names attributes without image, justice without rivalry, created signs without contempt, and eternal speech without possession. The final verdict is not a theory of God. It is a discipline for judges who must speak without pretending to contain what they name."),
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


def abs_node(node: dict[str, Any]) -> dict[str, Any]:
    return {"operator_type": "Absolute Value", "script_element_type": "Operator", "operands": [node]}


def add_node(*operands: dict[str, Any]) -> dict[str, Any]:
    return {"operator_type": "Addition", "script_element_type": "Operator", "operands": list(operands)}


def comparator(prop: str, threshold: float = 1.0, character: str = "char_student") -> dict[str, Any]:
    return {
        "operator_type": "Arithmetic Comparator",
        "script_element_type": "Operator",
        "operands": [abs_node(bptr(character, [prop], 1.0)), ptr_const(threshold)],
        "operator_subtype": "Less Than or Equal To",
    }


def nudge_effect(character: str, prop: str, delta: float, support: str | None = None) -> dict[str, Any]:
    operands = [bptr(character, [prop], 1.0), ptr_const(delta)]
    if support:
        operands.append(bptr(character, [support], 0.06 if delta >= 0 else -0.06))
    return {
        "effect_type": "Bounded Number Effect",
        "Set": bptr(character, [prop], 1.0),
        "to": {"operator_type": "Nudge", "script_element_type": "Operator", "operands": operands},
    }


def blend_effect(character: str, prop: str, delta: float, support: str) -> dict[str, Any]:
    return {
        "effect_type": "Bounded Number Effect",
        "Set": bptr(character, [prop], 1.0),
        "to": {
            "operator_type": "Blend",
            "script_element_type": "Operator",
            "operands": [
                bptr(character, [prop], 0.72),
                add_node(ptr_const(delta), bptr(character, [support], 0.18), bptr("char_public", [prop, character], 0.1)),
            ],
        },
    }


def desirability(prop: str, base: float, witness: str = "char_student", observer: str = "char_scribe") -> dict[str, Any]:
    other = "Power_Acquisition" if prop != "Power_Acquisition" else "Justice_Agency"
    return add_node(
        ptr_const(base),
        bptr(witness, [prop], 0.36),
        bptr(observer, [prop, witness], 0.24),
        bptr("char_mutazili", [prop, witness], 0.18),
        bptr("char_ashari", [prop, witness], 0.18),
        bptr("char_public", [other, witness, observer], 0.16),
        abs_node(bptr(witness, ["Public_Concord"], 0.12)),
    )


def make_option(scene_id: str, option_index: int, label: str, main_prop: str, next_id: str, alt_id: str | None, secret_id: str | None) -> dict[str, Any]:
    oid = f"{scene_id}_opt_{option_index:02d}"
    tendencies = [
        ("mutazili", "Justice_Agency", 0.055, "Power_Acquisition", -0.025),
        ("ashari", "Power_Acquisition", 0.055, "Justice_Agency", -0.02),
        ("textual", "Speech_Createdness", 0.05, "Attribute_Unity", 0.025),
        ("civic", "Public_Concord", 0.055, main_prop, -0.015),
    ][(option_index - 1) % 4]
    _, prop_a, delta_a, prop_b, delta_b = tendencies
    if option_index == 1:
        target = next_id
    elif option_index == 2 and alt_id:
        target = alt_id
    elif option_index == 4 and secret_id:
        target = secret_id
    else:
        target = next_id
    reactions = []
    for ridx, tone in enumerate(["success", "mixed", "failure"], 1):
        mod = 1.0 if tone == "success" else 0.45 if tone == "mixed" else -0.35
        reaction_target = target if tone != "failure" else next_id
        reactions.append(
            {
                "id": f"{oid}_r{ridx}",
                "text_script": ptr_const(
                    f"{tone.title()}: {label} The court records the move through {prop_a.replace('_', ' ').lower()}, "
                    f"but the opposing school immediately tests whether the ruling protects a person or merely protects a slogan."
                ),
                "desirability_script": desirability(prop_a, 0.08 * mod),
                "after_effects": [
                    nudge_effect("char_student", prop_a, delta_a * mod, prop_b),
                    blend_effect("char_student", prop_b, delta_b * mod, prop_a),
                    nudge_effect("char_mutazili", "Justice_Agency", (0.025 if prop_a == "Justice_Agency" else -0.01) * mod),
                    blend_effect("char_ashari", "Power_Acquisition", (0.025 if prop_a == "Power_Acquisition" else -0.01) * mod, "Attribute_Unity"),
                    nudge_effect("char_public", "Public_Concord", (0.02 if tone != "failure" else -0.035), prop_a),
                ],
                "consequence_id": reaction_target,
            }
        )
    return {
        "id": oid,
        "text_script": ptr_const(label),
        "visibility_script": comparator(prop_a, 1.0),
        "performability_script": comparator(prop_b, 1.0),
        "reactions": reactions,
        "creation_index": option_index,
        "creation_time": time.time(),
        "modified_time": time.time(),
    }


def make_encounter(index: int, scene: tuple[str, str, str, str, str], next_id: str, alt_id: str | None, secret_id: str | None) -> dict[str, Any]:
    sid, title, body, _topic, axis = scene
    main_prop = {
        "justice": "Justice_Agency",
        "power": "Power_Acquisition",
        "attributes": "Attribute_Unity",
        "speech": "Speech_Createdness",
        "public": "Public_Concord",
        "secret": "Attribute_Unity",
        "both": "Justice_Agency",
    }.get(axis, "Public_Concord")
    labels = [
        f"Rule from divine justice and make responsibility legible in the case of {title.lower()}.",
        f"Rule from divine power and describe human acquisition without making a second creator.",
        f"Distinguish created sign, public utterance, and protected meaning before issuing judgment.",
        f"Ask what ruling would prevent the doctrine from becoming a weapon in the market.",
    ]
    return {
        "id": sid,
        "title": title,
        "text_script": ptr_const(
            body
            + " The examiners require Yusuf to answer as a judge, not a lecturer: name the doctrine, identify the human consequence, and state what kind of evidence a court may actually use."
        ),
        "acceptability_script": comparator(main_prop, 1.2),
        "desirability_script": desirability(main_prop, 0.58),
        "options": [make_option(sid, i, labels[i - 1], main_prop, next_id, alt_id, secret_id) for i in range(1, 5)],
        "connected_spools": ["spool_main"],
        "earliest_turn": max(0, index - 2),
        "latest_turn": index + 8,
        "creation_index": index,
        "creation_time": time.time(),
        "modified_time": time.time(),
        "graph_position_x": 200 + (index % 6) * 260,
        "graph_position_y": 200 + (index // 6) * 220,
    }


def make_ending(index: int, eid: str, title: str, body: str) -> dict[str, Any]:
    return {
        "id": eid,
        "title": title,
        "text_script": ptr_const(body),
        "acceptability_script": comparator("Public_Concord", 2.0),
        "desirability_script": desirability("Public_Concord", 0.7),
        "options": [],
        "connected_spools": ["spool_endings"],
        "earliest_turn": 12,
        "latest_turn": 80,
        "creation_index": 100 + index,
        "creation_time": time.time(),
        "modified_time": time.time(),
        "graph_position_x": 200 + index * 180,
        "graph_position_y": 1280,
    }


def load_design_content() -> dict[str, Any]:
    if not DESIGN_PACKET.exists():
        return {}
    raw = json.loads(DESIGN_PACKET.read_text(encoding="utf-8"))
    content = raw.get("choices", [{}])[0].get("message", {}).get("content", "")
    try:
        return json.loads(content)
    except Exception:
        return {"raw_content": content}


def main() -> int:
    now = time.time()
    design = load_design_content()
    nonterminal = SCENES
    ids = [s[0] for s in nonterminal]
    encounters: list[dict[str, Any]] = []
    for idx, scene in enumerate(nonterminal, 1):
        next_id = ids[idx] if idx < len(ids) else ENDINGS[0][0]
        alt_id = None
        secret_id = "page_025_bridge_house_of_acquisition" if idx in {23, 24} else None
        if scene[0] == "page_025_bridge_house_of_acquisition":
            next_id = "page_026_bridge_chalk_of_no_how"
            secret_id = "page_end_acquisition_synthesis"
        if scene[0] == "page_026_bridge_chalk_of_no_how":
            next_id = "page_end_no_how_lantern"
            secret_id = "page_end_no_how_lantern"
        encounters.append(make_encounter(idx, scene, next_id, alt_id, secret_id))
    # Redirect late ordinary scenes toward multiple endings.
    late_targets = [e[0] for e in ENDINGS[:6]]
    for idx, encounter in enumerate(encounters[20:24]):
        for opt_idx, option in enumerate(encounter["options"]):
            if opt_idx == 0 and idx < 3:
                continue
            if opt_idx == 3 and encounter["id"] in {"page_023_trial_of_the_safe_answer", "page_024_register_that_judges_back"}:
                for reaction in option["reactions"]:
                    reaction["consequence_id"] = "page_025_bridge_house_of_acquisition"
                continue
            target = late_targets[(idx + opt_idx - 1) % len(late_targets)]
            for reaction in option["reactions"]:
                if reaction["consequence_id"].startswith("page_0"):
                    reaction["consequence_id"] = target
    for option in encounters[23]["options"]:
        if option["id"].endswith("_opt_02"):
            for reaction in option["reactions"]:
                reaction["consequence_id"] = "page_end_scribe_truth"
        if option["id"].endswith("_opt_03"):
            for reaction in option["reactions"]:
                reaction["consequence_id"] = "page_end_market_schism"
    for idx, ending in enumerate(ENDINGS, 1):
        encounters.append(make_ending(idx, *ending))

    char_props = {
        prop: 0 for prop, _ in PROPS
    } | {
        f"p{prop}": {} for prop, _ in PROPS
    } | {
        f"p2{prop}": {} for prop, _ in PROPS
    }
    world = {
        "IFID": "SW-MUTAZILI-ASHARI-KALAM-EXAM-9B-RESEARCH",
        "storyworld_title": design.get("title") or "The Two Lamps Examination: Mu'tazili And Ash'ari Kalam",
        "storyworld_author": "Codex + Qwen3.5-9B research stimulus",
        "sweepweave_version": "0.1.9",
        "creation_time": now,
        "modified_time": now,
        "debug_mode": False,
        "display_mode": 1,
        "css_theme": "lilac",
        "font_size": "16",
        "language": "en",
        "rating": "general",
        "about_text": ptr_const("A doctrine-aware Kalam/Qadi examination storyworld generated from compact research stimulus cards and a bounded Qwen 9B design packet. Yusuf Lin must adjudicate live cases between Mu'tazili justice/agency and Ash'ari power/attributes without turning doctrine into slogans."),
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
                "spool_name": "The Two Lamps Kalam Examination",
                "spool_type": "General",
                "starts_active": True,
                "creation_index": 0,
                "creation_time": now,
                "modified_time": now,
                "encounters": ids[:24],
            },
            {
                "id": "spool_secret",
                "spool_name": "The Acquired Judgment Secret Route",
                "spool_type": "General",
                "starts_active": False,
                "creation_index": 1,
                "creation_time": now,
                "modified_time": now,
                "encounters": ["page_025_bridge_house_of_acquisition", "page_026_bridge_chalk_of_no_how"],
            },
            {
                "id": "spool_endings",
                "spool_name": "Ordinary And Secret Verdicts",
                "spool_type": "General",
                "starts_active": False,
                "creation_index": 2,
                "creation_time": now,
                "modified_time": now,
                "encounters": [e[0] for e in ENDINGS],
            },
        ],
        "encounters": encounters,
        "meta": {
            "research_stimulus": str(ROOT / "research_stimulus" / "research_cards.json"),
            "qwen9b_design_packet": str(DESIGN_PACKET),
            "design_packet_summary": design,
            "secret_route": {
                "bridge": "page_025_bridge_house_of_acquisition",
                "ending": "page_end_no_how_lantern",
                "theme": "synthesis of responsibility under divine power and attributes without image",
            },
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(world, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
