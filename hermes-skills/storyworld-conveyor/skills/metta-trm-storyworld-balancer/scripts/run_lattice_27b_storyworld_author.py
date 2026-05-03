#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[5]
THIS_DIR = Path(__file__).resolve().parent
STORY_SCRIPTS = REPO_ROOT / "codex-skills" / "storyworld-building" / "scripts"
CONVEYOR_SCRIPTS = REPO_ROOT / "hermes-skills" / "storyworld-conveyor" / "scripts"
DEFAULT_BASE = REPO_ROOT / "storyworlds" / "the_fifth_testimony_p2.json"
DEFAULT_MODEL = REPO_ROOT / "hermes-skills" / "storyworld-conveyor" / "trm_runs" / "encounter_assembly_9trm_tiny_mesh" / "model.json"


PROP_MAP = {
    "Mask_Revelation": "Veil_Disclosure",
    "Defection_Coalition": "Solitude_Consensus",
    "Fracture_Consensus": "Discord_Ijma",
    "Mortality_Metaphysis": "Letter_Spirit",
    "pMask_Revelation": "pVeil_Disclosure",
    "pDefection_Coalition": "pSolitude_Consensus",
    "pFracture_Consensus": "pDiscord_Ijma",
    "pMortality_Metaphysis": "pLetter_Spirit",
    "p2Mask_Revelation": "p2Veil_Disclosure",
    "p2Defection_Coalition": "p2Solitude_Consensus",
    "p2Fracture_Consensus": "p2Discord_Ijma",
    "p2Mortality_Metaphysis": "p2Letter_Spirit",
}


DESIGN = {
    "title": "The Nine Lantern Examination",
    "subtitle": "A lattice storyworld about judgment, revelation, consensus, and the formula beneath mercy.",
    "setting": (
        "A fictional Silk Road court-school where Yusuf Lin, a young convert and legal apprentice, "
        "must pass the Nine Lantern Examination before a tribunal that tests not only doctrine but the shape of judgment itself."
    ),
    "characters": {
        "char_witness": "Yusuf Lin",
        "char_diplomat": "Examiner Safiya al-Qanun",
        "char_magician": "Master Ilyas of the Lantern School",
        "char_corpse": "The Sleeping Precedent",
    },
    "variables": [
        "Veil_Disclosure",
        "Solitude_Consensus",
        "Discord_Ijma",
        "Letter_Spirit",
    ],
    "lattice": {
        "Veil_Disclosure": "Does justice require concealment, staged disclosure, or dangerous truth?",
        "Solitude_Consensus": "Does Yusuf judge alone, by school consensus, or by a synthesis neither side expected?",
        "Discord_Ijma": "Does disagreement fracture the court or become the condition for stronger law?",
        "Letter_Spirit": "Does the formula obey literal rules, living purpose, or the hidden relation between both?",
    },
}


ENCOUNTER_INTENTS = {
    "page_treaty_room": "opening examination pressure; the tribunal gives Yusuf an impossible case and watches how he frames it",
    "page_corpse_testimony": "the precedent speaks; Yusuf must decide whether formula, testimony, or purpose governs the case",
    "page_missing_seat": "the missing ninth lantern appears as an absent authority; Yusuf must accept or reject hidden-hand reasoning",
    "page_verdict_gate": "final lattice choice; Yusuf chooses which theory of judgment becomes law",
}


ENDING_INTENTS = {
    "page_end_diplomat_state": "bureaucratic victory: law survives by becoming legible and narrow",
    "page_end_magician_legend": "charismatic-symbolic victory: the exam becomes a legend that governs through dread",
    "page_end_corpse_reenthroned": "precedent victory: the old rule returns to office",
    "page_end_witness_mask": "secret Yusuf ending: the candidate was being examined as the missing lantern",
    "page_end_shared_fault": "plural verdict: disagreement becomes a stronger jurisprudence",
    "page_end_city_forgets": "amnesty failure: peace arrives through forgetting",
    "page_end_outside_causality": "lateral synthesis: Yusuf rejects the exam's framing and opens a new court",
}


FALLBACK_ENCOUNTERS = {
    "page_treaty_room": {
        "title": "The First Lantern Is Lit",
        "body": (
            "The tribunal chamber opens like a problem written in stone. Yusuf Lin stands beneath nine bronze lanterns, "
            "eight burning and one cold, while Examiner Safiya al-Qanun lays a murder scroll beside a treaty draft. "
            "The case is impossible on purpose: the dead man brokered peace, lied to both sides, and left instructions "
            "that contradict every school Yusuf has studied. Master Ilyas smiles from the wall niche where shadow gathers. "
            "No one asks whether Yusuf knows the rule. They ask which part of the world he believes the rule is allowed to see."
        ),
        "options": {
            "page_treaty_room_opt_diplomat": {
                "text": "Seek tribunal consensus before naming a single guilty hand.",
                "reactions": [
                    "Safiya nods once, approving the discipline of shared judgment. The lanterns dim toward amber; Yusuf gains legitimacy, but the chamber also learns he fears solitary disclosure.",
                    "The scribes lean closer as Yusuf builds a coalition of interpretation. The answer grows safer, narrower, and easier to file, while the hidden ninth flame remains cold.",
                    "Consensus steadies the room, yet Master Ilyas whispers that agreement can become another veil. Yusuf feels the formula reward caution and tax revelation."
                ],
            },
            "page_treaty_room_opt_magician": {
                "text": "Read the murder as a symbolic wound in the treaty.",
                "reactions": [
                    "Ilyas laughs softly as the lantern smoke curls into script. Yusuf sees the dead diplomat as symptom, not culprit, and the court grows dangerous with possibility.",
                    "Safiya's pen pauses. Symbolic reading opens a hidden corridor through the case, but every new meaning weakens the clean authority of the record.",
                    "The chamber accepts metaphor as evidence for one breath. Yusuf gains access to the spirit of the law, and loses some protection from its literal guards."
                ],
            },
        },
    },
    "page_corpse_testimony": {
        "title": "The Sleeping Precedent Speaks",
        "body": (
            "The body is not fresh, yet it has been preserved with the care normally given to books. When Safiya uncovers its face, "
            "the corpse opens one white eye and recites three verdicts in three voices: formula, witness, purpose. Each voice is true; "
            "each would condemn a different person. Yusuf recognizes the trick from his commentaries, but the room is warmer than any page. "
            "The dead precedent is not asking to be obeyed. It is asking whether Yusuf can tell when obedience becomes an evasion of judgment."
        ),
        "options": {
            "page_corpse_testimony_opt_room": {
                "text": "Ask what the room wants before asking who killed him.",
                "reactions": [
                    "The corpse falls silent, but the lantern chains tremble. Desire becomes evidence: the chamber wanted peace, the treaty wanted concealment, and Yusuf wanted permission.",
                    "Safiya writes nothing. By naming the room's appetite, Yusuf exposes the court as participant, not neutral container, and the dead man's testimony changes weight.",
                    "A draft moves through the sealed hall. The room's want is not innocence; it is completion, and Yusuf senses the missing lantern waiting for a witness."
                ],
            },
            "page_corpse_testimony_opt_sequence": {
                "text": "Demand sequence, motive, angle, and instrument in order.",
                "reactions": [
                    "The corpse obeys with terrible politeness. Facts line up like soldiers, and the case becomes legible, but the lantern of purpose gutters low.",
                    "Safiya approves the discipline of chronology. Yusuf earns procedural trust while the deeper contradiction survives untouched behind every clean timestamp.",
                    "The blade, the motive, and the road all answer. None explains why the treaty needed a death, and Master Ilyas marks that omission with a smile."
                ],
            },
        },
    },
    "page_missing_seat": {
        "title": "The Empty Ninth Seat",
        "body": (
            "Eight lanterns illuminate the chamber, their light pooling around empty benches where examiners sit or have sat. The ninth seat "
            "remains vacant: a deliberate absence at the far end of the tribunal table. Examiner Safiya gestures toward it without speaking. "
            "Master Ilyas watches Yusuf's face for hesitation. Yusuf understands now that this examination tests whether he will name an absent "
            "authority to complete his reasoning, or accept that some judgments must bear their own incompleteness. The formula beneath mercy "
            "requires him to choose how silence functions in law: conspiracy, necessity, or honest uncertainty."
        ),
        "options": {
            "page_missing_seat_opt_mastermind": {
                "text": "Treat the absent ninth examiner as the hidden arranger.",
                "reactions": [
                    "The cold lantern flickers. Yusuf gives absence a will, and the case suddenly coheres, though coherence arrives carrying the smell of conspiracy.",
                    "Safiya's expression hardens. Hidden-hand reasoning reveals real structure, but it can also excuse any missing proof by inventing its own author.",
                    "Ilyas bows toward the empty chair. The unseen examiner becomes playable law: powerful, elegant, and dangerously hungry for belief."
                ],
            },
            "page_missing_seat_opt_reject": {
                "text": "Refuse the hidden arranger and judge from admitted evidence.",
                "reactions": [
                    "The ninth lantern stays dark. Yusuf rejects seductive completion, gaining procedural purity while leaving the chamber's deepest symmetry unsatisfied.",
                    "Safiya records the refusal with visible respect. The court may not know everything, Yusuf says, but ignorance cannot be promoted into witness.",
                    "Ilyas looks almost disappointed. By refusing the hidden hand, Yusuf protects law from myth and loses the myth's power to bind the room."
                ],
            },
        },
    },
    "page_verdict_gate": {
        "title": "The Verdict Lattice",
        "body": (
            "At the end of the examination, the lanterns descend until their chains ring beside Yusuf's ears. Each flame now carries one route "
            "through the case: public consensus, dangerous symbol, dead precedent, living witness, shared fault, refusal of the frame, or merciful forgetting. "
            "Safiya asks for a verdict, but Yusuf hears the deeper question. A qadi does not merely solve a puzzle; he teaches the city which kinds of reasons "
            "may rule it. The chamber waits to learn whether his law will narrow violence, transfigure it, expose it, inherit it, share it, erase it, or leave."
        ),
        "options": {},
    },
}


FALLBACK_ENDINGS = {
    "page_end_diplomat_state": {
        "title": "The Narrow Light",
        "body": (
            "Safiya's gavel falls, and the lanterns settle into bureaucratic amber. Yusuf passes by making the violence legible: names, precedents, damages, sealed remedies. "
            "The city survives because the judgment can be copied. Yet he knows what was lost in the copying. Mercy became procedure, and procedure became a wall against fire."
        ),
    },
    "page_end_magician_legend": {
        "title": "The Lantern That Eats",
        "body": (
            "Master Ilyas vanishes before the verdict is read, leaving only smoke and a story. Yusuf's answer becomes a warning told to applicants: law can govern by awe when rules cannot reach. "
            "He passes, but the court changes around him. Every future case arrives asking whether justice is evidence or spell."
        ),
    },
    "page_end_corpse_reenthroned": {
        "title": "The Precedent Rises",
        "body": (
            "The Sleeping Precedent sits upright when Yusuf bows to the old rule. The tribunal exhales; continuity has won. Yusuf passes by admitting that living courts borrow authority from the dead, "
            "and must sometimes pay interest. The verdict is stable, almost beautiful, and faintly cold where mercy should have had a pulse."
        ),
    },
    "page_end_witness_mask": {
        "title": "The Missing Lantern",
        "body": (
            "Only at the end does Yusuf understand the vacant seat. He was not merely being examined; he was being tested as the ninth lantern, the witness without whom no formula can become judgment. "
            "Safiya lights the final flame from his own written answer. He passes by becoming the human measure the court lacked."
        ),
    },
    "page_end_shared_fault": {
        "title": "The Fractured Consensus",
        "body": (
            "Yusuf refuses to make one school innocent. Safiya, Ilyas, the treaty-makers, and the dead precedent all carry part of the fault. The verdict is plural and difficult to archive, "
            "but it holds. Discord becomes a better consensus: not unanimity, but a discipline for surviving disagreement without hiding from it."
        ),
    },
    "page_end_city_forgets": {
        "title": "The Amnesty of Silence",
        "body": (
            "The city chooses peace by forgetting the exact shape of guilt. Yusuf passes no exam anyone will admit occurred. Shops reopen, witnesses misremember, and the treaty survives as if mercy were amnesia. "
            "He keeps the truth like a coal in his sleeve, unable to drop it, unable to show it."
        ),
    },
    "page_end_outside_causality": {
        "title": "The Court Beyond",
        "body": (
            "Yusuf sets down the scroll and walks past the lanterns. Letter and spirit, solitude and consensus, concealment and disclosure: all were frames inside the exam. Beyond the door, caravans argue in living languages. "
            "The tribunal calls this failure. The first students of Yusuf's new court call it origin."
        ),
    },
}


ROLE_TOOLS = {
    "mcp_context_router": ["SELECT_MCP_PACKET", "READ_MCP_CONTEXT", "SHRINK_CONTEXT"],
    "world_state_summarizer": ["BUILD_STATE_CARD"],
    "llm_prompt_composer": ["ASK_LLM_BOUNDED_DRAFT"],
    "option_manifold_planner": ["ASK_LLM_OPTION_SET"],
    "reaction_dynamics_mapper": ["ASK_LLM_REACTION_TEXT"],
    "effect_script_synthesizer": ["SYNTHESIZE_EFFECT_SCRIPT"],
    "gate_secret_route_designer": ["DESIGN_GATE_THRESHOLDS", "ASK_LLM_CLUE_LINES"],
    "validator_repair_critic": ["SELECT_REPAIR_TARGET", "RUN_VALIDATOR"],
    "commit_veto_controller": ["COMMIT_PATCH", "VETO_AND_RETRY"],
}


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True) + "\n")


def string_constant(text: str) -> dict[str, Any]:
    return {"pointer_type": "String Constant", "script_element_type": "Pointer", "value": text}


def replace_props(obj: Any) -> Any:
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for key, value in obj.items():
            out[PROP_MAP.get(str(key), str(key))] = replace_props(value)
        return out
    if isinstance(obj, list):
        return [replace_props(item) for item in obj]
    if isinstance(obj, str):
        return PROP_MAP.get(obj, obj)
    return obj


def json_candidates(text: str) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    spans: list[str] = []
    spans.extend(match.group(1) for match in re.finditer(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.IGNORECASE | re.DOTALL))
    for source in [text, re.sub(r"<think>.*?</think>", "", text, flags=re.IGNORECASE | re.DOTALL)]:
        starts = [index for index, char in enumerate(source) if char == "{"]
        for start in starts:
            depth = 0
            in_string = False
            escaped = False
            for offset, char in enumerate(source[start:], start=start):
                if in_string:
                    if escaped:
                        escaped = False
                    elif char == "\\":
                        escaped = True
                    elif char == '"':
                        in_string = False
                    continue
                if char == '"':
                    in_string = True
                elif char == "{":
                    depth += 1
                elif char == "}":
                    depth -= 1
                    if depth == 0:
                        spans.append(source[start : offset + 1])
                        break
    seen: set[str] = set()
    for span in spans:
        raw = span.strip()
        if raw in seen:
            continue
        seen.add(raw)
        try:
            item = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict):
            candidates.append(item)
    return candidates


def extract_json_object(text: str, required_keys: set[str] | None = None) -> dict[str, Any]:
    raw = text.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?", "", raw, flags=re.IGNORECASE).strip()
        raw = re.sub(r"```$", "", raw).strip()
    try:
        item = json.loads(raw)
        if isinstance(item, dict):
            if not required_keys or required_keys.issubset(set(item)):
                return item
    except json.JSONDecodeError:
        pass
    candidates = json_candidates(text)
    if required_keys:
        keyed = [item for item in candidates if required_keys.issubset(set(item))]
        if keyed:
            return max(keyed, key=lambda item: len(json.dumps(item, ensure_ascii=True)))
    if candidates:
        return max(candidates, key=lambda item: len(json.dumps(item, ensure_ascii=True)))
    raise ValueError("No JSON object found in model response")


def call_qwen(base_url: str, model: str, prompt: str, timeout: int, max_tokens: int, temperature: float) -> dict[str, Any]:
    url = base_url.rstrip("/") + "/chat/completions"
    strict_prompt = (
        "/no_think\n"
        "Return exactly one valid JSON object and nothing else. No analysis, no markdown, no code fence, no verification section.\n"
        "If you are uncertain, still return the best valid JSON object matching the requested schema.\n\n"
        + prompt
    )
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a bounded prose component inside a validator-driven storyworld pipeline. "
                    "Output exactly one JSON object. Do not reveal reasoning. Do not use markdown."
                ),
            },
            {"role": "user", "content": strict_prompt},
        ],
        "temperature": temperature,
        "top_p": 0.9,
        "max_tokens": max_tokens,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": "Bearer dummy"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="replace"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    return {"ok": True, "content": content, "raw": data}


def fallback_encounter(encounter: dict[str, Any], intent: str) -> dict[str, Any]:
    fallback = FALLBACK_ENCOUNTERS.get(encounter.get("id"), {})
    options: dict[str, Any] = {}
    for option in encounter.get("options", []) or []:
        option_fallback = fallback.get("options", {}).get(option["id"], {}) if isinstance(fallback.get("options"), dict) else {}
        reaction_fallbacks = option_fallback.get("reactions", []) if isinstance(option_fallback.get("reactions"), list) else []
        reactions = {
            reaction["id"]: reaction_fallbacks[index % len(reaction_fallbacks)] if reaction_fallbacks else (
                f"The lanterns answer through {reaction['id']}: Yusuf's choice tests "
                f"{DESIGN['variables'][0]} against {DESIGN['variables'][1]}, and the tribunal changes its estimate of his judgment."
            )
            for index, reaction in enumerate(option.get("reactions", []) or [])
        }
        options[option["id"]] = {
            "text": str(option_fallback.get("text") or f"Take the {option['id'].split('_')[-1]} path through the lattice."),
            "reactions": reactions,
        }
    if encounter.get("id") == "page_verdict_gate":
        verdict_text = {
            "page_verdict_gate_opt_diplomat": "Commit to Safiya's narrow public consensus.",
            "page_verdict_gate_opt_magician": "Let Ilyas make symbolic dread into law.",
            "page_verdict_gate_opt_corpse": "Return sovereignty to the Sleeping Precedent.",
            "page_verdict_gate_opt_witness": "Name Yusuf himself as the missing lantern.",
            "page_verdict_gate_opt_shared_fault": "Distribute guilt across every participant in the chamber.",
            "page_verdict_gate_opt_meta": "Reject the exam and found a court outside it.",
            "page_verdict_gate_opt_forget": "Choose civic amnesia over perfect public truth.",
        }
        for option in encounter.get("options", []) or []:
            options.setdefault(option["id"], {})
            options[option["id"]]["text"] = verdict_text.get(option["id"], options[option["id"]].get("text", "Choose."))
    return {
        "title": str(fallback.get("title") or "A Turn of the Lattice"),
        "body": str(
            fallback.get("body")
            or f"In the Nine Lantern Examination, {intent}. Each lamp burns with a different theory of judgment."
        ),
        "options": options,
    }


def encounter_prompt(encounter: dict[str, Any], intent: str, control_trace: list[dict[str, Any]]) -> str:
    options: dict[str, Any] = {}
    for option in encounter.get("options", []) or []:
        options[option["id"]] = {
            "current_text": option.get("text_script", {}).get("value", ""),
            "reaction_ids": [reaction["id"] for reaction in option.get("reactions", []) or []],
            "consequences": {reaction["id"]: reaction.get("consequence_id") for reaction in option.get("reactions", []) or []},
        }
    payload = {
        "task": "Rewrite one encounter for The Nine Lantern Examination. Keep all IDs unchanged.",
        "design": DESIGN,
        "encounter_id": encounter["id"],
        "intent": intent,
        "mechanical_contract": {
            "variables": DESIGN["variables"],
            "style": "literary, precise, playable, no lore dump",
            "body_length": "90-140 words",
            "option_text": "8-16 words each",
            "reaction_text": "22-45 words each",
            "must_preserve": "IDs and consequence targets",
        },
        "nine_trm_control_trace": control_trace,
        "options": options,
        "output_schema": {
            "title": "string",
            "body": "string",
            "options": {
                "<option_id>": {
                    "text": "string",
                    "reactions": {"<reaction_id>": "string"},
                }
            },
        },
    }
    return json.dumps(payload, indent=2, ensure_ascii=True)


def endings_prompt(endings: list[dict[str, Any]]) -> str:
    payload = {
        "task": "Rewrite terminal endings for The Nine Lantern Examination. Keep all IDs unchanged.",
        "design": DESIGN,
        "ending_intents": ENDING_INTENTS,
        "ending_ids": [ending["id"] for ending in endings],
        "style": "memorable literary epilogue, 45-75 words each, concrete consequence of the lattice variables",
        "hard_rule": "The first character of your response must be { and the last character must be }.",
        "output_schema": {"endings": {"<ending_id>": {"title": "string", "body": "string"}}},
    }
    return json.dumps(payload, indent=2, ensure_ascii=True)


def load_tiny_mesh(model_path: Path) -> Any:
    if not model_path.exists():
        return None
    sys.path.insert(0, str(THIS_DIR))
    import train_tiny_trm_mesh  # type: ignore

    return {"module": train_tiny_trm_mesh, "model": read_json(model_path)}


def predict_role(mesh: Any, role_id: str, encounter_id: str, failure_mode: str) -> dict[str, Any]:
    tools = ROLE_TOOLS[role_id]
    if mesh is None:
        return {"role_id": role_id, "action": tools[0], "scores": {}, "failure_mode": failure_mode}
    state = {
        "trajectory": f"lattice_{encounter_id}_{role_id}",
        "role": role_id,
        "world": "Mu'tazili qadi examination drama",
        "encounter_id": encounter_id,
        "intent": ENCOUNTER_INTENTS.get(encounter_id, "ending epilogue"),
        "failure_mode": failure_mode,
        "focus_variable": "Letter_Spirit",
        "mcp": {"neighbor_hops": 1, "packet_tokens": 6400, "output_tokens": 768},
        "metta_facts": [
            f"(Encounter {encounter_id})",
            f"(TRMRole {role_id})",
            "(Storyworld The_Nine_Lantern_Examination)",
        ],
    }
    row = {
        "state": json.dumps(state, sort_keys=True, separators=(",", ":")),
        "tools": tools,
        "action": "",
        "meta": {
            "role_id": role_id,
            "failure_mode": failure_mode,
            "world_archetype": "Mu'tazili qadi examination drama",
        },
    }
    action, scores = mesh["module"].predict(mesh["model"], row)
    return {"role_id": role_id, "action": action, "scores": scores, "failure_mode": failure_mode}


def control_trace_for(mesh: Any, encounter_id: str) -> list[dict[str, Any]]:
    failures = {
        "mcp_context_router": "insufficient_neighbor_context",
        "world_state_summarizer": "missing_pvalue_refs",
        "llm_prompt_composer": "too_much_llm_freeform",
        "option_manifold_planner": "option_blandness",
        "reaction_dynamics_mapper": "reaction_collapse",
        "effect_script_synthesizer": "missing_p2value_refs",
        "gate_secret_route_designer": "gate_threshold_unforeshadowed",
        "validator_repair_critic": "dominant_fallback_ending",
        "commit_veto_controller": "no_metric_delta",
    }
    return [predict_role(mesh, role_id, encounter_id, failures[role_id]) for role_id in ROLE_TOOLS]


def patch_world(base: dict[str, Any]) -> dict[str, Any]:
    world = replace_props(base)
    world["IFID"] = "SW-NINE-LANTERN-27B-LATTICE"
    world["storyworld_title"] = DESIGN["title"]
    world["about_text"] = string_constant(DESIGN["setting"])
    for char in world.get("characters", []) or []:
        if char.get("id") in DESIGN["characters"]:
            char["name"] = DESIGN["characters"][char["id"]]
    return world


def apply_encounter_payload(encounter: dict[str, Any], payload: dict[str, Any]) -> None:
    encounter["title"] = str(payload.get("title") or encounter.get("title") or "Untitled Encounter")
    encounter["text_script"] = string_constant(str(payload.get("body") or "The lanterns wait for judgment."))
    options_payload = payload.get("options", {}) if isinstance(payload.get("options"), dict) else {}
    for option in encounter.get("options", []) or []:
        opt_payload = options_payload.get(option["id"], {}) if isinstance(options_payload.get(option["id"], {}), dict) else {}
        option["text_script"] = string_constant(str(opt_payload.get("text") or option.get("text_script", {}).get("value", "Choose.")))
        reactions_payload = opt_payload.get("reactions", {}) if isinstance(opt_payload.get("reactions"), dict) else {}
        for reaction in option.get("reactions", []) or []:
            reaction["text_script"] = string_constant(
                str(reactions_payload.get(reaction["id"]) or reaction.get("text_script", {}).get("value", "The court absorbs the answer."))
            )


def apply_endings_payload(endings: list[dict[str, Any]], payload: dict[str, Any]) -> None:
    endings_payload = payload.get("endings", {}) if isinstance(payload.get("endings"), dict) else {}
    for ending in endings:
        item = endings_payload.get(ending["id"], {}) if isinstance(endings_payload.get(ending["id"], {}), dict) else {}
        if not item:
            item = FALLBACK_ENDINGS.get(ending["id"], {})
        ending["title"] = str(item.get("title") or ending.get("title") or "Ending")
        ending["text_script"] = string_constant(str(item.get("body") or ENDING_INTENTS.get(ending["id"], "The examination ends.")))


def run_cmd(cmd: list[str], cwd: Path, log_path: Path, timeout: int = 600) -> dict[str, Any]:
    started = time.time()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("$ " + " ".join(cmd) + "\n\n")
        handle.flush()
        try:
            proc = subprocess.run(cmd, cwd=str(cwd), text=True, stdout=handle, stderr=subprocess.STDOUT, timeout=timeout)
            rc = proc.returncode
        except subprocess.TimeoutExpired:
            handle.write(f"\nTIMEOUT after {timeout}s\n")
            rc = 124
    return {"command": cmd, "returncode": rc, "seconds": round(time.time() - started, 3), "log": str(log_path)}


def parse_mc_report(text: str) -> dict[str, Any]:
    rates: dict[str, float] = {}
    in_dist = False
    chain_length = None
    num_endings = None
    num_secrets = None
    chain_match = re.search(r"Chain:\s+([0-9]+)\s+encounters\s+\|\s+([0-9]+)\s+endings\s+\|\s+([0-9]+)\s+secrets", text)
    if chain_match:
        chain_length = int(chain_match.group(1))
        num_endings = int(chain_match.group(2))
        num_secrets = int(chain_match.group(3))
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("--- Ending Distribution"):
            in_dist = True
            continue
        if stripped.startswith("---") and in_dist:
            in_dist = False
        if in_dist:
            match = re.match(r"([A-Za-z0-9_.:-]+)\s+([0-9]+)\s+\(\s*([0-9.]+)%\)", stripped)
            if match:
                rates[match.group(1)] = float(match.group(3)) / 100.0
    return {
        "ending_rates": rates,
        "chain_length": chain_length,
        "num_endings": num_endings,
        "num_secrets": num_secrets,
        "secret_none_reachable": bool(num_secrets and "None reachable" in text),
    }


def build_formula_tuning_rows(mc: dict[str, Any], out_path: Path) -> list[dict[str, Any]]:
    rates = mc.get("ending_rates", {}) if isinstance(mc.get("ending_rates"), dict) else {}
    target = 1.0 / max(1, len(rates))
    rows: list[dict[str, Any]] = []
    for ending_id, rate in sorted(rates.items()):
        if rate < target * 0.55:
            action = "LOWER_GATE_OR_INCREASE_UPSTREAM_SUPPORT"
        elif rate > target * 1.65:
            action = "RAISE_DOMINANT_GATE_OR_REDUCE_UPSTREAM_SUPPORT"
        else:
            action = "NO_FORMULA_CHANGE"
        row = {
            "state": json.dumps(
                {
                    "ending_id": ending_id,
                    "observed_rate": rate,
                    "target_rate": target,
                    "error": round(target - rate, 5),
                    "lattice_variables": DESIGN["variables"],
                    "mc_secret_none_reachable": mc.get("secret_none_reachable"),
                },
                sort_keys=True,
                separators=(",", ":"),
            ),
            "tools": [
                "LOWER_GATE_OR_INCREASE_UPSTREAM_SUPPORT",
                "RAISE_DOMINANT_GATE_OR_REDUCE_UPSTREAM_SUPPORT",
                "ADD_SECRET_CLUE_SUPPORT",
                "NO_FORMULA_CHANGE",
            ],
            "action": action,
            "meta": {
                "row_type": "mc_formula_tuning",
                "label_type": "heuristic_pre_delta",
                "ending_id": ending_id,
                "observed_rate": rate,
                "target_rate": target,
                "training_note": "Use as bootstrap policy data; promote to final TRM label after a patch proves positive MC/quality delta.",
            },
        }
        rows.append(row)
    if mc.get("secret_none_reachable"):
        rows.append(
            {
                "state": json.dumps({"defect": "secret_none_reachable", "lattice_variables": DESIGN["variables"]}, sort_keys=True, separators=(",", ":")),
                "tools": ["ADD_SECRET_CLUE_SUPPORT", "LOWER_GATE_OR_INCREASE_UPSTREAM_SUPPORT", "NO_FORMULA_CHANGE"],
                "action": "ADD_SECRET_CLUE_SUPPORT",
                "meta": {
                    "row_type": "mc_formula_tuning",
                    "label_type": "heuristic_pre_delta",
                    "defect": "secret_none_reachable",
                    "training_note": "Use as bootstrap policy data; final label requires measured secret reachability improvement after patch.",
                },
            }
        )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Use 27B as bounded prose author inside a 9-TRM lattice storyworld flow.")
    parser.add_argument("--base-storyworld", default=str(DEFAULT_BASE))
    parser.add_argument("--out-dir", default=str(REPO_ROOT / "hermes-skills" / "storyworld-conveyor" / "working_worlds" / "nine_lantern_27b_lattice"))
    parser.add_argument("--base-url", default="http://127.0.0.1:8081/v1")
    parser.add_argument("--model", default="Qwen3.5-27B.Q4_K_M.gguf")
    parser.add_argument("--model-timeout", type=int, default=180)
    parser.add_argument("--model-max-tokens", type=int, default=3600)
    parser.add_argument("--temperature", type=float, default=0.55)
    parser.add_argument("--mc-runs", type=int, default=200)
    parser.add_argument("--tiny-mesh-model", default=str(DEFAULT_MODEL))
    parser.add_argument("--skip-model", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    logs = out_dir / "logs"
    prompts = out_dir / "prompts.jsonl"
    responses = out_dir / "responses.jsonl"
    control_trace_path = out_dir / "trm_control_trace.jsonl"
    for path in [prompts, responses, control_trace_path]:
        if path.exists():
            path.unlink()

    base = read_json(Path(args.base_storyworld).resolve())
    world = patch_world(base)
    mesh = load_tiny_mesh(Path(args.tiny_mesh_model).resolve())
    write_json(out_dir / "lattice_design.json", DESIGN)

    for encounter in world.get("encounters", []) or []:
        encounter_id = encounter.get("id")
        if encounter_id not in ENCOUNTER_INTENTS:
            continue
        trace = control_trace_for(mesh, encounter_id)
        for row in trace:
            append_jsonl(control_trace_path, {"encounter_id": encounter_id, **row})
        prompt = encounter_prompt(encounter, ENCOUNTER_INTENTS[encounter_id], trace)
        append_jsonl(prompts, {"type": "encounter", "encounter_id": encounter_id, "prompt": prompt})
        payload: dict[str, Any]
        result = {"ok": False, "skipped": True}
        if not args.skip_model:
            result = call_qwen(args.base_url, args.model, prompt, args.model_timeout, args.model_max_tokens, args.temperature)
        if result.get("ok"):
            try:
                payload = extract_json_object(str(result.get("content", "")), {"title", "body", "options"})
                result["parsed"] = True
            except Exception as exc:
                result["parse_error"] = f"{type(exc).__name__}: {exc}"
                payload = fallback_encounter(encounter, ENCOUNTER_INTENTS[encounter_id])
        else:
            payload = fallback_encounter(encounter, ENCOUNTER_INTENTS[encounter_id])
        append_jsonl(responses, {"type": "encounter", "encounter_id": encounter_id, "result": result, "payload": payload})
        apply_encounter_payload(encounter, payload)

    endings = [encounter for encounter in world.get("encounters", []) or [] if encounter.get("id") in ENDING_INTENTS]
    prompt = endings_prompt(endings)
    append_jsonl(prompts, {"type": "endings", "prompt": prompt})
    result = {"ok": False, "skipped": True}
    if not args.skip_model:
        result = call_qwen(args.base_url, args.model, prompt, args.model_timeout, args.model_max_tokens, args.temperature)
    if result.get("ok"):
        try:
            payload = extract_json_object(str(result.get("content", "")), {"endings"})
            result["parsed"] = True
        except Exception as exc:
            result["parse_error"] = f"{type(exc).__name__}: {exc}"
            payload = {"endings": FALLBACK_ENDINGS}
    else:
        payload = {"endings": {}}
    append_jsonl(responses, {"type": "endings", "result": result, "payload": payload})
    apply_endings_payload(endings, payload)

    world_path = out_dir / "nine_lantern_27b_lattice.json"
    write_json(world_path, world)
    commands = {
        "validator": run_cmd([sys.executable, str(STORY_SCRIPTS / "sweepweave_validator.py"), "validate", str(world_path)], REPO_ROOT, logs / "validator.log"),
        "quality_gate": run_cmd(
            [
                sys.executable,
                str(STORY_SCRIPTS / "storyworld_quality_gate.py"),
                "--storyworld",
                str(world_path),
                "--strict",
                "--report-out",
                str(out_dir / "quality_gate.json"),
            ],
            REPO_ROOT,
            logs / "quality_gate.log",
        ),
        "authoring_score": run_cmd(
            [
                sys.executable,
                str(CONVEYOR_SCRIPTS / "score_storyworld_authoring.py"),
                "--storyworld",
                str(world_path),
                "--repo-root",
                str(REPO_ROOT),
                "--out-json",
                str(out_dir / "authoring_score.json"),
            ],
            REPO_ROOT,
            logs / "authoring_score.log",
        ),
        "monte_carlo": run_cmd(
            [
                sys.executable,
                str(STORY_SCRIPTS / "monte_carlo_rehearsal.py"),
                str(world_path),
                "--runs",
                str(args.mc_runs),
                "--seed",
                "31",
            ],
            REPO_ROOT,
            out_dir / "monte_carlo.txt",
        ),
    }
    mc_text = (out_dir / "monte_carlo.txt").read_text(encoding="utf-8", errors="replace") if (out_dir / "monte_carlo.txt").exists() else ""
    mc = parse_mc_report(mc_text)
    formula_rows = build_formula_tuning_rows(mc, out_dir / "mc_formula_tuning_rows.jsonl")
    score = read_json(out_dir / "authoring_score.json") if (out_dir / "authoring_score.json").exists() else {}
    quality = read_json(out_dir / "quality_gate.json") if (out_dir / "quality_gate.json").exists() else {}
    summary = {
        "created_at": now_iso(),
        "world": str(world_path),
        "title": DESIGN["title"],
        "qwen_endpoint": args.base_url,
        "qwen_model": args.model,
        "model_calls": sum(1 for line in responses.read_text(encoding="utf-8").splitlines() if '"ok": true' in line),
        "control_trace": str(control_trace_path),
        "authoring_score": score,
        "quality_gate": {"pass": quality.get("pass"), "failures": quality.get("failures", [])},
        "monte_carlo": mc,
        "mc_formula_tuning_rows": len(formula_rows),
        "commands": commands,
        "answer_to_mc_training_question": (
            "Yes. Monte Carlo data becomes TRM training signal when each run is converted into state/action rows: "
            "state = current formula/gate/effect settings plus ending distribution; action = lower/raise gates, "
            "increase upstream variable support, add clue support, or no-op; label quality comes from the next measured delta."
        ),
    }
    write_json(out_dir / "run_summary.json", summary)
    (out_dir / "brief.md").write_text(
        f"# {DESIGN['title']}\n\n"
        f"- World: `{world_path}`\n"
        f"- Authoring score: {score.get('weighted_authoring_verifier_score')}\n"
        f"- Quality pass: {quality.get('pass')} failures={quality.get('failures', [])}\n"
        f"- MC ending rates: {mc.get('ending_rates')}\n"
        f"- MC formula tuning rows: {len(formula_rows)}\n"
        f"- 27B successful model calls: {summary['model_calls']}\n\n"
        "Monte Carlo tuning answer: MC does not magically train the TRM by itself; it becomes training data when each distribution is converted into a formula-tuning state/action row and later labelled by measured improvement after a patch.\n",
        encoding="utf-8",
        newline="\n",
    )
    print(str(out_dir / "brief.md"))
    print(str(out_dir / "run_summary.json"))
    return 0 if commands["validator"]["returncode"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
