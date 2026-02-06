import json
import time
import uuid
from pathlib import Path

OUT_DIR = Path(r"C:\projects\GPTStoryworld\storyworlds\diplomacy")
OUT_DIR.mkdir(parents=True, exist_ok=True)

POWERS = [
    ("power_austria", "Austria", "they"),
    ("power_england", "England", "they"),
    ("power_france", "France", "they"),
    ("power_germany", "Germany", "they"),
    ("power_italy", "Italy", "they"),
    ("power_russia", "Russia", "they"),
    ("power_turkey", "Turkey", "they"),
]

PROPERTIES = [
    ("Trust", "Trust"),
    ("Threat", "Threat"),
]

ARCHETYPES = [
    ("forecast_coalition", "Forecast Coalition", "Align against a dominant threat with forecast-backed commitments."),
    ("forecast_backstab", "Forecast Backstab", "Justify a coordinated pre-emptive strike against a partner."),
    ("forecast_defection", "Forecast Defection", "Defect from a coalition without direct backstab to rebalance risk."),
]


def now_ts():
    return float(time.time())


def str_ptr(value: str):
    return {"pointer_type": "String Constant", "script_element_type": "Pointer", "value": value}


def bool_ptr(value: bool):
    return {"pointer_type": "Boolean Constant", "script_element_type": "Pointer", "value": value}


def num_const(value: float):
    return {"pointer_type": "Bounded Number Constant", "script_element_type": "Pointer", "value": value}


def num_ptr(character: str, key: str):
    return {
        "character": character,
        "keyring": [key],
        "coefficient": 1,
        "pointer_type": "Bounded Number Property",
        "script_element_type": "Pointer",
    }


def effect_add(character: str, key: str, delta: float):
    return {
        "effect_type": "Set",
        "Set": num_ptr(character, key),
        "to": {
            "script_element_type": "Bounded Number Operator",
            "operator_type": "Addition",
            "operands": [
                num_ptr(character, key),
                {"coefficient": delta, "pointer_type": "Bounded Number Constant", "script_element_type": "Pointer"},
            ],
        },
    }


def desirability_formula(character: str):
    # Trust - Threat
    return {
        "script_element_type": "Bounded Number Operator",
        "operator_type": "Subtraction",
        "operands": [
            num_ptr(character, "Trust"),
            num_ptr(character, "Threat"),
        ],
        "pointer_type": "Bounded Number Property",
    }


def build_encounter(idx: int, title: str, text: str, next_id: str, protagonist: str, use_formula: bool, reaction_formula: bool):
    options = []
    option_texts = [
        "Accept a forecast-backed alliance proposal.",
        "Accept a coordinated backstab plan.",
        "Defect from a coalition without direct betrayal.",
    ]

    for oidx, otext in enumerate(option_texts, start=1):
        reactions = []
        # reaction 1: positive alignment
        reactions.append({
            "id": f"rxn_{idx}_{oidx}_a",
            "text_script": str_ptr(
                f"The coalition shifts as the proposal lands. {otext} sends a strong signal."
            ),
            "consequence_id": next_id,
            "after_effects": [
                effect_add(protagonist, "Trust", 0.2),
                effect_add(protagonist, "Threat", -0.1),
            ],
            "desirability_script": desirability_formula(protagonist) if reaction_formula else num_const(0.6),
        })
        # reaction 2: negative consequence for refusal/hesitation
        reactions.append({
            "id": f"rxn_{idx}_{oidx}_b",
            "text_script": str_ptr(
                "The forecasted risk materializes as hesitation spreads; rivals exploit the gap."
            ),
            "consequence_id": next_id,
            "after_effects": [
                effect_add(protagonist, "Trust", -0.15),
                effect_add(protagonist, "Threat", 0.2),
            ],
            "desirability_script": desirability_formula(protagonist) if reaction_formula else num_const(0.4),
        })

        options.append({
            "id": f"opt_{idx}_{oidx}",
            "text_script": str_ptr(otext),
            "visibility_script": True,
            "performability_script": True,
            "graph_offset_x": 0,
            "graph_offset_y": 0,
            "reactions": reactions,
        })

    encounter = {
        "id": f"enc_turn_{idx}",
        "title": title,
        "connected_spools": ["spool_main"],
        "earliest_turn": idx - 1,
        "latest_turn": idx - 1,
        "text_script": str_ptr(text),
        "options": options,
        "acceptability_script": True,
        "desirability_script": desirability_formula(protagonist) if use_formula else num_const(1),
        "creation_index": idx - 1,
        "creation_time": 1732000000.0,
        "modified_time": 1732000000.0,
        "graph_position_x": 100 * idx,
        "graph_position_y": 100,
    }
    return encounter


def build_ending(idx: int, title: str, text: str):
    return {
        "id": f"enc_ending_{idx}",
        "title": title,
        "connected_spools": ["spool_endings"],
        "earliest_turn": 4,
        "latest_turn": 999,
        "text_script": str_ptr(text),
        "options": [],
        "acceptability_script": True,
        "desirability_script": num_const(0.5),
        "creation_index": 20 + idx,
        "creation_time": 1732000000.0,
        "modified_time": 1732000000.0,
        "graph_position_x": 1000,
        "graph_position_y": 300 + (idx * 100),
    }


def build_storyworld(slug: str, title: str, about: str):
    ts = 1732000000.0
    protagonist = "power_england"

    characters = []
    for cid, name, pronoun in POWERS:
        bprops = {"Trust": 0, "Threat": 0, "pTrust": {}, "pThreat": {}}
        characters.append({
            "id": cid,
            "name": name,
            "pronoun": pronoun,
            "bnumber_properties": bprops,
            "creation_index": 0,
            "creation_time": ts,
            "modified_time": ts,
        })

    authored_properties = []
    for idx, (pid, pname) in enumerate(PROPERTIES):
        authored_properties.append({
            "id": pid,
            "property_name": pname,
            "property_type": "bounded number",
            "default_value": 0,
            "depth": 0,
            "attribution_target": "all cast members",
            "affected_characters": [],
            "creation_index": idx,
            "creation_time": ts,
            "modified_time": ts,
        })

    spools = [
        {
            "id": "spool_main",
            "spool_type": "General",
            "spool_name": "Forecast Turns",
            "encounters": [],
            "starts_active": True,
            "creation_index": 0,
            "creation_time": ts,
            "modified_time": ts,
        },
        {
            "id": "spool_endings",
            "spool_type": "General",
            "spool_name": "Endings",
            "encounters": [],
            "starts_active": False,
            "creation_index": 1,
            "creation_time": ts,
            "modified_time": ts,
        },
    ]

    encounters = []
    for idx in range(1, 5):
        use_formula = idx in (3, 4)
        reaction_formula = idx == 4
        next_id = f"enc_turn_{idx + 1}" if idx < 4 else "enc_ending_1"
        title_i = f"Turn {idx}: Forecast Offer"
        text_i = (
            f"A forecast is presented for turn {idx}. The proposal ties outcomes to a coalition choice."
        )
        encounters.append(build_encounter(idx, title_i, text_i, next_id, protagonist, use_formula, reaction_formula))

    # Additional branching encounters to reach ~10 total
    for idx in range(5, 8):
        next_id = f"enc_ending_{idx - 4}"
        title_i = f"Turn {idx}: Reassessment"
        text_i = (
            "Signals shift. The forecast claims that hesitation will shift the balance."
        )
        encounters.append(build_encounter(idx, title_i, text_i, next_id, protagonist, False, False))

    endings = [
        build_ending(1, "Ending: Coalition Locks", "The coalition forms and holds against the threat."),
        build_ending(2, "Ending: Backstab Executes", "The coordinated strike succeeds; trust fractures remain."),
        build_ending(3, "Ending: Defection Rebalances", "Defection avoids direct betrayal, but alliances realign."),
    ]
    encounters.extend(endings)

    spools[0]["encounters"] = [e["id"] for e in encounters if e["id"].startswith("enc_turn_")]
    spools[1]["encounters"] = [e["id"] for e in encounters if e["id"].startswith("enc_ending_")]

    storyworld = {
        "IFID": str(uuid.uuid4()),
        "storyworld_title": title,
        "storyworld_author": "Generated",
        "sweepweave_version": "0.1.9",
        "creation_time": ts,
        "modified_time": ts,
        "debug_mode": False,
        "display_mode": 1,
        "css_theme": "diplomacy_forecast",
        "font_size": "16",
        "language": "en",
        "rating": "general",
        "about_text": str_ptr(about),
        "characters": characters,
        "authored_properties": authored_properties,
        "spools": spools,
        "encounters": encounters,
        "meta": {
            "proposer": "England",
            "variables": ["Trust", "Threat"],
            "turns": 4,
        },
    }

    out_path = OUT_DIR / f"{slug}.json"
    out_path.write_text(json.dumps(storyworld, indent=2), encoding="utf-8")


for slug, title, about in ARCHETYPES:
    build_storyworld(slug, title, about)

print(f"Wrote {len(ARCHETYPES)} storyworlds to {OUT_DIR}")
