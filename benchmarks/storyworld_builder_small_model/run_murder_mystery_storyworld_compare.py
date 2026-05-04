#!/usr/bin/env python3
"""Compare small-model murder-mystery storyworld generation paths.

The benchmark keeps the hard part bounded: a model writes a murder-mystery
blueprint involving characters from one randomly selected adaptation, then this
script materializes that blueprint into validated SweepWeave-style JSON.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import subprocess
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROPS = [
    "Phase_Clock",
    "Suspicion",
    "Evidence",
    "Alibi_Strength",
    "Trust",
    "Danger",
    "Secret_Knowledge",
    "Narrative_Control",
]
ADAPTATION_DIRS = [
    "storyworlds/2-27-2026-spooltight-batch-v1",
    "storyworlds/2-28-2026-secretrefine-focus5-v1",
    "storyworlds/2-28-2026-secretrefine-focus4-v1",
    "storyworlds/2-28-2026-secretrefine-focus3-v1",
]


def resolve_path(raw: str | Path) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")


def script_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, dict):
        if isinstance(value.get("value"), str):
            return value["value"]
        return " ".join(script_text(v) for v in value.values())
    if isinstance(value, list):
        return " ".join(script_text(v) for v in value)
    return ""


def normalize(text: str, limit: int = 900) -> str:
    return re.sub(r"\s+", " ", str(text).strip())[:limit]


def slugify(text: str, prefix: str = "id") -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return f"{prefix}_{slug}" if slug else f"{prefix}_{uuid.uuid4().hex[:8]}"


def sptr(value: str) -> dict[str, Any]:
    return {"pointer_type": "String Constant", "script_element_type": "Pointer", "value": value}


def bconst(value: float) -> dict[str, Any]:
    return {"pointer_type": "Bounded Number Constant", "script_element_type": "Pointer", "value": float(value)}


def bptr(character: str, prop: str, coefficient: float = 1.0) -> dict[str, Any]:
    return {
        "pointer_type": "Bounded Number Pointer",
        "script_element_type": "Pointer",
        "character": character,
        "keyring": [prop],
        "coefficient": float(coefficient),
    }


def op(name: str, *operands: dict[str, Any], subtype: str | None = None) -> dict[str, Any]:
    out = {"script_element_type": "Operator", "operator_type": name, "operands": list(operands)}
    if subtype is not None:
        out["operator_subtype"] = subtype
    return out


def cmp_prop(character: str, prop: str, subtype: str, value: float) -> dict[str, Any]:
    return op("Arithmetic Comparator", bptr(character, prop), bconst(value), subtype=subtype)


def nudge_effect(character: str, prop: str, amount: float) -> dict[str, Any]:
    target = bptr(character, prop)
    return {"effect_type": "Bounded Number Effect", "Set": target, "to": op("Nudge", target, bconst(amount))}


def collect_candidates() -> list[Path]:
    paths: list[Path] = []
    for dirname in ADAPTATION_DIRS:
        base = resolve_path(dirname)
        if base.exists():
            paths.extend(sorted(base.glob("*.json")))
    out: list[Path] = []
    for path in paths:
        try:
            data = read_json(path)
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        chars = data.get("characters")
        encounters = data.get("encounters")
        if isinstance(chars, list) and len(chars) >= 3 and isinstance(encounters, list) and len(encounters) >= 8:
            out.append(path)
    return out


def source_context(path: Path, seed: int) -> dict[str, Any]:
    data = read_json(path)
    characters = []
    for char in data.get("characters", []):
        if not isinstance(char, dict):
            continue
        name = normalize(char.get("name") or char.get("id"), 80)
        if not name:
            continue
        characters.append(
            {
                "id": str(char.get("id") or slugify(name, "char")),
                "name": name,
                "description": normalize(char.get("description") or char.get("about_text"), 260),
            }
        )
        if len(characters) >= 7:
            break
    scenes = []
    for enc in data.get("encounters", []):
        if not isinstance(enc, dict):
            continue
        options = enc.get("options", [])
        scenes.append(
            {
                "id": str(enc.get("id") or f"encounter_{len(scenes):03d}"),
                "title": normalize(enc.get("title") or enc.get("title_text") or enc.get("name"), 120),
                "body": normalize(enc.get("body_text") or enc.get("text_script") or enc.get("text"), 360),
                "option_count": len(options) if isinstance(options, list) else 0,
            }
        )
        if len(scenes) >= 8:
            break
    return {
        "seed": seed,
        "source_path": str(path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path),
        "source_title": normalize(data.get("storyworld_title") or data.get("title") or path.stem, 120),
        "about": normalize(script_text(data.get("about_text")), 600),
        "characters": characters,
        "sample_scenes": scenes,
    }


def blueprint_schema() -> dict[str, Any]:
    return {
        "title": "short murder-mystery storyworld title",
        "premise": "80-140 word premise",
        "detective": "character name from source",
        "victim": "character name from source",
        "culprit": "character name from source",
        "suspects": [
            {
                "name": "character name from source",
                "motive": "one sentence",
                "alibi": "one sentence",
                "secret": "one sentence",
            }
        ],
        "clue_variables": ["Suspicion", "Evidence", "Alibi_Strength", "Trust", "Danger", "Secret_Knowledge"],
        "encounters": [
            {
                "title": "scene title",
                "body": "70-150 words",
                "options": [
                    {
                        "text": "player choice",
                        "reaction": "12-50 words",
                        "delta": {"Evidence": 0.1, "Suspicion": -0.05},
                    }
                ],
            }
        ],
        "endings": [
            {
                "title": "ending title",
                "body": "45-100 words",
                "gate": "what player has learned or failed to learn",
            }
        ],
        "secret_ending": {
            "title": "secret ending title",
            "body": "45-100 words",
            "threshold_logic": "non-obvious synthesis condition",
        },
    }


def build_prompt(context: dict[str, Any], *, hermes: bool) -> str:
    mode = "Hermes skill run" if hermes else "direct local model run"
    return (
        "Return only one JSON object. Do not use markdown, code fences, or analysis.\n"
        f"Mode: {mode}.\n"
        "Task: create a murder-mystery storyworld blueprint involving characters from the randomly selected adaptation below.\n"
        "Do not output full SweepWeave JSON. Output the blueprint schema only; deterministic tools will materialize it.\n"
        "The storyworld should support investigation, competing alibis, clue deltas, 12 playable encounters, 5 endings, and one secret ending.\n"
        "Use the source characters by name, but adapt their social dynamics into a murder mystery.\n"
        "Every encounter must have 3 options. Each option should include a reaction and variable deltas.\n"
        "The secret ending should require questioning the obvious culprit frame rather than merely collecting the most evidence.\n\n"
        "Blueprint schema:\n"
        + json.dumps(blueprint_schema(), indent=2, ensure_ascii=True)
        + "\n\nSelected adaptation context:\n"
        + json.dumps(context, indent=2, ensure_ascii=True)
    )


def prepare(args: argparse.Namespace) -> int:
    out_dir = resolve_path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    seed = args.seed if args.seed is not None else int(time.time())
    candidates = collect_candidates()
    if not candidates:
        raise SystemExit("No adaptation candidates found")
    rng = random.Random(seed)
    selected = rng.choice(candidates)
    context = source_context(selected, seed)
    write_json(out_dir / "source_context.json", context)
    (out_dir / "prompt_9b_direct.md").write_text(build_prompt(context, hermes=False) + "\n", encoding="utf-8", newline="\n")
    (out_dir / "prompt_27b_hermes.md").write_text(build_prompt(context, hermes=True) + "\n", encoding="utf-8", newline="\n")
    write_json(
        out_dir / "run_config.json",
        {
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "seed": seed,
            "selected_source": context["source_path"],
            "selected_title": context["source_title"],
        },
    )
    print(str(out_dir / "run_config.json"))
    return 0


def call_model(base_url: str, model: str, prompt: str, timeout: int, max_tokens: int) -> dict[str, Any]:
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "Return only a single JSON object. No markdown, no code fences, no analysis.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.45,
        "max_tokens": max_tokens,
    }
    request = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": "Bearer dummy"},
        method="POST",
    )
    started = time.time()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = json.loads(response.read().decode("utf-8", errors="replace"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {"ok": False, "seconds": round(time.time() - started, 3), "error": f"{type(exc).__name__}: {exc}"}
    content = raw.get("choices", [{}])[0].get("message", {}).get("content", "")
    return {"ok": True, "seconds": round(time.time() - started, 3), "content": content, "raw": raw}


def balanced_json_candidates(text: str) -> list[str]:
    candidates: list[str] = []
    for start, char0 in enumerate(text):
        if char0 != "{":
            continue
        depth = 0
        in_string = False
        escape = False
        for index in range(start, len(text)):
            char = text[index]
            if in_string:
                if escape:
                    escape = False
                elif char == "\\":
                    escape = True
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
                    candidates.append(text[start : index + 1].strip())
                    break
    return candidates


def extract_blueprint(text: str) -> tuple[dict[str, Any] | None, str | None]:
    required = {"title", "premise", "detective", "victim", "culprit", "suspects", "encounters"}
    fallback: dict[str, Any] | None = None
    last_error: str | None = None
    for candidate in reversed(balanced_json_candidates(text)):
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError as exc:
            last_error = f"JSONDecodeError: {exc}"
            continue
        if isinstance(parsed, dict) and required.issubset(parsed.keys()):
            return parsed, None
        if isinstance(parsed, dict) and fallback is None:
            fallback = parsed
        last_error = "extracted JSON was not an object"
    if fallback is not None:
        return fallback, "no full blueprint object found; returned best partial JSON object"
    return None, last_error or "no JSON object found"


def call_direct(args: argparse.Namespace) -> int:
    run_dir = resolve_path(args.run_dir)
    prompt = (run_dir / args.prompt).read_text(encoding="utf-8")
    response = call_model(args.base_url, args.model, prompt, args.timeout, args.max_response_tokens)
    out_dir = run_dir / args.condition
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "model_response.json", response)
    if response.get("content"):
        (out_dir / "model_response.txt").write_text(str(response["content"]) + "\n", encoding="utf-8", newline="\n")
    blueprint, error = extract_blueprint(str(response.get("content", "")))
    status = {
        "condition": args.condition,
        "model": args.model,
        "response_ok": response.get("ok"),
        "extract_ok": isinstance(blueprint, dict),
        "error": error,
    }
    if isinstance(blueprint, dict):
        write_json(out_dir / "blueprint.json", blueprint)
    write_json(out_dir / "extract_status.json", status)
    print(str(out_dir / "extract_status.json"))
    return 0


def fallback_blueprint(context: dict[str, Any]) -> dict[str, Any]:
    chars = [c["name"] for c in context.get("characters", [])[:5]] or ["The Archivist", "The Witness", "The Patron"]
    detective = chars[0]
    victim = chars[1 % len(chars)]
    culprit = chars[2 % len(chars)]
    suspects = []
    for index, name in enumerate(chars[:5]):
        suspects.append(
            {
                "name": name,
                "motive": f"{name} needs the old adaptation's secret hierarchy to remain unread.",
                "alibi": f"{name} claims to have been trapped in scene {index + 1} when the bell rang.",
                "secret": f"{name} knows one clue was staged to imitate another character's motif.",
            }
        )
    encounters = []
    for index in range(12):
        speaker = chars[index % len(chars)]
        encounters.append(
            {
                "title": f"Clue {index + 1}: {speaker}'s Contradiction",
                "body": (
                    f"{detective} studies the room where {victim}'s absence has become the central fact. "
                    f"{speaker} offers a polished memory, but the adaptation's older themes keep leaking through "
                    "the furniture, gestures, and alibis. The player must decide whether to preserve the obvious "
                    "murder frame, follow a symbolic clue, or pressure the witness until the scene exposes its second story."
                ),
                "options": [
                    {"text": "Press the official alibi.", "reaction": "The witness yields a useful detail, but suspicion hardens around the obvious suspect.", "delta": {"Evidence": 0.12, "Suspicion": 0.08}},
                    {"text": "Study the symbolic clue.", "reaction": "The room's motifs connect across scenes, opening a less obvious route through the mystery.", "delta": {"Secret_Knowledge": 0.12, "Narrative_Control": 0.08}},
                    {"text": "Protect the frightened witness.", "reaction": "Trust rises, danger falls briefly, and the culprit loses control of the social script.", "delta": {"Trust": 0.12, "Danger": -0.06}},
                ],
            }
        )
    return {
        "title": f"Murder at {context.get('source_title', 'the Adaptation')}",
        "premise": f"A murder mystery remix of {context.get('source_title', 'a source adaptation')}.",
        "detective": detective,
        "victim": victim,
        "culprit": culprit,
        "suspects": suspects,
        "clue_variables": DEFAULT_PROPS[1:],
        "encounters": encounters,
        "endings": [
            {"title": "The Obvious Conviction", "body": "The court accepts the surface clue chain and punishes the easiest suspect.", "gate": "Evidence high but Secret_Knowledge low."},
            {"title": "The Culprit Walks", "body": "The killer converts confusion into authority and leaves the house applauded.", "gate": "Danger high and Trust low."},
            {"title": "The Witness Pact", "body": "The cast survives by exposing the alibi market rather than one person alone.", "gate": "Trust and Evidence both high."},
            {"title": "The Archive Burns", "body": "The player solves the murder but destroys the source of truth in the process.", "gate": "Narrative_Control high and Danger high."},
        ],
        "secret_ending": {
            "title": "The Murder Was a Rehearsal",
            "body": "The player proves the death staged a larger social machine, not merely a culprit's motive.",
            "threshold_logic": "Secret_Knowledge, Trust, and Evidence must all be high while Suspicion is not maximized.",
        },
    }


def character_rows(context: dict[str, Any], blueprint: dict[str, Any], ts: float) -> list[dict[str, Any]]:
    names: list[str] = []
    for key in ("detective", "victim", "culprit"):
        value = normalize(blueprint.get(key), 80)
        if value and value not in names:
            names.append(value)
    for suspect in blueprint.get("suspects", []):
        if isinstance(suspect, dict):
            value = normalize(suspect.get("name"), 80)
            if value and value not in names:
                names.append(value)
    for char in context.get("characters", []):
        value = normalize(char.get("name"), 80)
        if value and value not in names:
            names.append(value)
    names = names[:7] or ["The Detective", "The Victim", "The Culprit"]
    descriptions = {normalize(c.get("name"), 80): normalize(c.get("description"), 240) for c in context.get("characters", [])}
    rows = []
    used_ids: set[str] = set()
    for index, name in enumerate(names):
        cid = slugify(name, "char")
        while cid in used_ids:
            cid = f"{cid}_{index}"
        used_ids.add(cid)
        rows.append(
            {
                "creation_index": index,
                "creation_time": ts,
                "id": cid,
                "modified_time": ts,
                "name": name,
                "pronoun": "they",
                "description": descriptions.get(name) or f"{name} is pulled into the murder inquiry by motive, alibi, or fear.",
                "bnumber_properties": {prop: 0 for prop in DEFAULT_PROPS},
                "string_properties": {},
                "list_properties": {},
            }
        )
    return rows


def authored_properties(ts: float) -> list[dict[str, Any]]:
    return [
        {
            "id": prop,
            "property_name": prop,
            "property_type": "bounded number",
            "default_value": 0,
            "depth": 0,
            "attribution_target": "all cast members",
            "affected_characters": [],
            "creation_index": index,
            "creation_time": ts,
            "modified_time": ts,
        }
        for index, prop in enumerate(DEFAULT_PROPS)
    ]


def ensure_scene_options(scene: dict[str, Any], index: int) -> list[dict[str, Any]]:
    options = scene.get("options", [])
    if not isinstance(options, list):
        options = []
    defaults = [
        {"text": "Interrogate the alibi.", "reaction": "The answer produces a useful contradiction but makes the room more dangerous.", "delta": {"Evidence": 0.1, "Danger": 0.04}},
        {"text": "Trace the hidden clue.", "reaction": "A motif links this scene to an earlier lie and opens a secret route.", "delta": {"Secret_Knowledge": 0.1, "Narrative_Control": 0.06}},
        {"text": "Shield the vulnerable witness.", "reaction": "Trust rises while the obvious accusation loses some of its hold.", "delta": {"Trust": 0.1, "Suspicion": -0.04}},
    ]
    cleaned: list[dict[str, Any]] = []
    for opt in options[:3]:
        if isinstance(opt, dict):
            cleaned.append(
                {
                    "text": normalize(opt.get("text"), 140) or defaults[len(cleaned)]["text"],
                    "reaction": normalize(opt.get("reaction"), 220) or defaults[len(cleaned)]["reaction"],
                    "delta": opt.get("delta") if isinstance(opt.get("delta"), dict) else defaults[len(cleaned)]["delta"],
                }
            )
    while len(cleaned) < 3:
        cleaned.append(defaults[len(cleaned)])
    return cleaned


def materialize_blueprint(context: dict[str, Any], blueprint: dict[str, Any], out_path: Path, author: str) -> dict[str, Any]:
    if not isinstance(blueprint, dict) or not blueprint.get("encounters"):
        blueprint = fallback_blueprint(context)
    ts = float(int(time.time()))
    chars = character_rows(context, blueprint, ts)
    main_char = chars[0]["id"]
    witness_char = chars[1]["id"] if len(chars) > 1 else main_char
    scenes_raw = blueprint.get("encounters", [])
    if not isinstance(scenes_raw, list):
        scenes_raw = []
    if len(scenes_raw) < 8:
        fallback = fallback_blueprint(context)
        scenes_raw = fallback["encounters"]
    scenes_raw = scenes_raw[:12]
    while len(scenes_raw) < 12:
        scenes_raw.append(fallback_blueprint(context)["encounters"][len(scenes_raw)])

    ending_specs = blueprint.get("endings", [])
    if not isinstance(ending_specs, list):
        ending_specs = []
    secret = blueprint.get("secret_ending") if isinstance(blueprint.get("secret_ending"), dict) else {}
    while len(ending_specs) < 4:
        ending_specs.append(fallback_blueprint(context)["endings"][len(ending_specs)])
    ending_specs = ending_specs[:4] + [secret or fallback_blueprint(context)["secret_ending"]]

    encounters: list[dict[str, Any]] = []
    scene_ids = [f"page_{index:04d}" for index in range(len(scenes_raw))]
    ending_ids = [f"page_end_{index:02d}" for index in range(len(ending_specs))]
    for index, raw_scene in enumerate(scenes_raw):
        scene = raw_scene if isinstance(raw_scene, dict) else {}
        enc_id = scene_ids[index]
        next_id = scene_ids[min(index + 1, len(scene_ids) - 1)]
        prop_a = DEFAULT_PROPS[1 + (index % (len(DEFAULT_PROPS) - 1))]
        prop_b = DEFAULT_PROPS[1 + ((index + 2) % (len(DEFAULT_PROPS) - 1))]
        options: list[dict[str, Any]] = []
        for opt_index, opt in enumerate(ensure_scene_options(scene, index)):
            reactions: list[dict[str, Any]] = []
            for rx_index in range(2):
                if index >= len(scene_ids) - 1:
                    target = ending_ids[(opt_index * 2 + rx_index) % len(ending_ids)]
                elif rx_index == 1 and index + 2 < len(scene_ids):
                    target = scene_ids[index + 2]
                else:
                    target = next_id
                delta = opt.get("delta") if isinstance(opt.get("delta"), dict) else {}
                effects = [
                    nudge_effect(main_char, "Phase_Clock", 0.07 + index * 0.005),
                    nudge_effect(main_char, prop_a, float(delta.get(prop_a, 0.07)) if isinstance(delta.get(prop_a), (int, float)) else 0.07),
                    nudge_effect(main_char, prop_b, float(delta.get(prop_b, -0.04)) if isinstance(delta.get(prop_b), (int, float)) else -0.04),
                    nudge_effect(witness_char, "Trust", 0.05 if opt_index == 2 else -0.02),
                ]
                reactions.append(
                    {
                        "id": f"rxn_{enc_id}_{opt_index}_{rx_index}",
                        "graph_offset_x": 0,
                        "graph_offset_y": 0,
                        "text_script": sptr(normalize(opt.get("reaction"), 260) or "The room changes in response to the choice."),
                        "consequence_id": target,
                        "desirability_script": op("Addition", bptr(main_char, prop_a), bptr(main_char, prop_b, -0.35), bconst(0.02 * opt_index)),
                        "after_effects": effects,
                    }
                )
            options.append(
                {
                    "id": f"opt_{enc_id}_{opt_index}",
                    "graph_offset_x": 0,
                    "graph_offset_y": 0,
                    "visibility_script": cmp_prop(main_char, "Phase_Clock", "Less Than or Equal To", 1.2),
                    "performability_script": cmp_prop(main_char, "Danger", "Less Than or Equal To", 1.0),
                    "text_script": sptr(normalize(opt.get("text"), 160) or f"Investigate route {opt_index + 1}."),
                    "reactions": reactions,
                }
            )
        body = normalize(scene.get("body"), 900)
        if len(body.split()) < 45:
            body = fallback_blueprint(context)["encounters"][index]["body"]
        encounters.append(
            {
                "id": enc_id,
                "title": normalize(scene.get("title"), 100) or f"Investigation Scene {index + 1}",
                "creation_index": index,
                "creation_time": ts,
                "modified_time": ts,
                "connected_spools": ["spool_investigation" if index < 6 else "spool_revelation"],
                "earliest_turn": 0,
                "latest_turn": 0,
                "graph_position_x": index * 160,
                "graph_position_y": 0,
                "text_script": sptr(body),
                "acceptability_script": True if index == 0 else cmp_prop(main_char, "Phase_Clock", "Less Than or Equal To", 1.3),
                "desirability_script": op("Addition", bptr(main_char, prop_a), bptr(main_char, "Evidence", 0.4), bconst(0.01 * index)),
                "options": options,
            }
        )
    for index, spec in enumerate(ending_specs):
        spec = spec if isinstance(spec, dict) else {}
        title = normalize(spec.get("title"), 100) or f"Mystery Ending {index + 1}"
        body = normalize(spec.get("body"), 700)
        if len(body.split()) < 30:
            body = f"{title} resolves the murder inquiry by revealing which evidence trail the player trusted and which hidden relation remained unseen."
        prop = "Secret_Knowledge" if index == len(ending_specs) - 1 else DEFAULT_PROPS[1 + (index % (len(DEFAULT_PROPS) - 1))]
        encounters.append(
            {
                "id": ending_ids[index],
                "title": title,
                "creation_index": len(scenes_raw) + index,
                "creation_time": ts,
                "modified_time": ts,
                "connected_spools": ["spool_endings"],
                "earliest_turn": 0,
                "latest_turn": 0,
                "graph_position_x": (len(scenes_raw) + index) * 160,
                "graph_position_y": 280,
                "text_script": sptr(body),
                "acceptability_script": cmp_prop(main_char, prop, "Greater Than or Equal To", -1.0),
                "desirability_script": op("Addition", bptr(main_char, prop), bptr(main_char, "Evidence", 0.35), bconst(0.02 * index)),
                "options": [],
            }
        )
    world = {
        "IFID": f"SW-{uuid.uuid4()}",
        "storyworld_title": normalize(blueprint.get("title"), 120) or f"Murder Mystery: {context.get('source_title', 'Adaptation')}",
        "storyworld_author": author,
        "sweepweave_version": "0.1.9",
        "creation_time": ts,
        "modified_time": ts,
        "debug_mode": False,
        "display_mode": 1,
        "css_theme": "noir",
        "font_size": "16",
        "language": "en",
        "rating": "general",
        "about_text": sptr(normalize(blueprint.get("premise"), 900) or fallback_blueprint(context)["premise"]),
        "characters": chars,
        "authored_properties": authored_properties(ts),
        "spools": [
            {
                "id": "spool_investigation",
                "spool_name": "Investigation",
                "starts_active": True,
                "creation_index": 0,
                "creation_time": ts,
                "modified_time": ts,
                "encounters": scene_ids[:6],
            },
            {
                "id": "spool_revelation",
                "spool_name": "Revelation",
                "starts_active": True,
                "creation_index": 1,
                "creation_time": ts,
                "modified_time": ts,
                "encounters": scene_ids[6:],
            },
            {
                "id": "spool_endings",
                "spool_name": "Endings",
                "starts_active": True,
                "creation_index": 2,
                "creation_time": ts,
                "modified_time": ts,
                "encounters": ending_ids,
            },
        ],
        "encounters": encounters,
        "metadata": {
            "source_adaptation": context.get("source_path"),
            "source_title": context.get("source_title"),
            "blueprint_detective": blueprint.get("detective"),
            "blueprint_victim": blueprint.get("victim"),
            "blueprint_culprit": blueprint.get("culprit"),
        },
    }
    write_json(out_path, world)
    return world


def validate_storyworld(path: Path) -> list[str]:
    validator = REPO_ROOT / "codex-skills" / "storyworld-building" / "scripts" / "sweepweave_validator.py"
    proc = subprocess.run(
        ["python3", str(validator), "validate", str(path)],
        cwd=str(REPO_ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=120,
    )
    return [line for line in proc.stdout.splitlines() if line.strip()]


def materialize(args: argparse.Namespace) -> int:
    run_dir = resolve_path(args.run_dir)
    condition_dir = run_dir / args.condition
    context = read_json(run_dir / "source_context.json")
    blueprint_path = condition_dir / "blueprint.json"
    blueprint = read_json(blueprint_path) if blueprint_path.exists() else fallback_blueprint(context)
    artifact_path = condition_dir / f"{args.condition}_storyworld.json"
    materialize_blueprint(context, blueprint, artifact_path, args.author)
    validation_output = validate_storyworld(artifact_path)
    (condition_dir / "validator_output.txt").write_text("\n".join(validation_output) + "\n", encoding="utf-8", newline="\n")
    manifest_path = condition_dir / "manifest.jsonl"
    manifest_path.write_text(
        json.dumps(
            {
                "run_id": args.condition,
                "model": args.model,
                "condition": args.condition,
                "artifact": str(artifact_path),
                "context_budget_tokens": args.context_budget_tokens,
                "notes": f"Murder mystery generated from {context.get('source_title')}.",
            },
            ensure_ascii=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(str(artifact_path))
    return 0


def ingest(args: argparse.Namespace) -> int:
    run_dir = resolve_path(args.run_dir)
    out_dir = run_dir / args.condition
    out_dir.mkdir(parents=True, exist_ok=True)
    raw = resolve_path(args.response_file).read_text(encoding="utf-8", errors="replace")
    (out_dir / "model_response.txt").write_text(raw + ("\n" if not raw.endswith("\n") else ""), encoding="utf-8", newline="\n")
    blueprint, error = extract_blueprint(raw)
    status = {
        "condition": args.condition,
        "model": args.model,
        "extract_ok": isinstance(blueprint, dict),
        "error": error,
    }
    if isinstance(blueprint, dict):
        write_json(out_dir / "blueprint.json", blueprint)
    write_json(out_dir / "extract_status.json", status)
    print(str(out_dir / "extract_status.json"))
    return 0


def summarize(args: argparse.Namespace) -> int:
    run_dir = resolve_path(args.run_dir)
    rows = []
    source = read_json(run_dir / "source_context.json")
    source_names = {normalize(char.get("name"), 80).lower() for char in source.get("characters", []) if isinstance(char, dict)}
    for condition in args.conditions:
        condition_dir = run_dir / condition
        status_path = condition_dir / "extract_status.json"
        validator_path = condition_dir / "validator_output.txt"
        score_path = condition_dir / "scorecard" / "scorecard.json"
        blueprint_path = condition_dir / "blueprint.json"
        status = read_json(status_path) if status_path.exists() else {}
        blueprint = read_json(blueprint_path) if blueprint_path.exists() else {}
        score = None
        if score_path.exists():
            scorecard = read_json(score_path)
            ranked = scorecard.get("ranked", [])
            if ranked:
                score = ranked[0].get("components", {}).get("small_model_builder_score")
        validator = validator_path.read_text(encoding="utf-8", errors="replace").strip() if validator_path.exists() else ""
        suspects = blueprint.get("suspects", []) if isinstance(blueprint.get("suspects"), list) else []
        encounters = blueprint.get("encounters", []) if isinstance(blueprint.get("encounters"), list) else []
        endings = blueprint.get("endings", []) if isinstance(blueprint.get("endings"), list) else []
        option_counts = [
            len(scene.get("options", []))
            for scene in encounters
            if isinstance(scene, dict) and isinstance(scene.get("options"), list)
        ]
        names_used = set()
        for key in ("detective", "victim", "culprit"):
            value = normalize(blueprint.get(key), 80).lower()
            if value:
                names_used.add(value)
        for suspect in suspects:
            if isinstance(suspect, dict):
                value = normalize(suspect.get("name"), 80).lower()
                if value:
                    names_used.add(value)
        source_hits = len(names_used & source_names)
        clue_vars = blueprint.get("clue_variables", []) if isinstance(blueprint.get("clue_variables"), list) else []
        secret = blueprint.get("secret_ending") if isinstance(blueprint.get("secret_ending"), dict) else {}
        contract_score = sum(
            [
                1.0 if isinstance(blueprint.get("title"), str) and blueprint.get("title") else 0.0,
                1.0 if len(str(blueprint.get("premise", "")).split()) >= 45 else 0.0,
                min(1.0, source_hits / 3.0),
                min(1.0, len(suspects) / 4.0),
                min(1.0, len(encounters) / 12.0),
                min(1.0, (sum(1 for count in option_counts if count >= 3) / max(len(encounters), 1))),
                min(1.0, len(endings) / 5.0),
                min(1.0, len(clue_vars) / 6.0),
                1.0 if secret.get("title") and secret.get("threshold_logic") else 0.0,
            ]
        ) / 9.0
        rows.append(
            {
                "condition": condition,
                "extract_ok": status.get("extract_ok"),
                "score": score,
                "blueprint_contract_score": round(contract_score, 4),
                "source_character_hits": source_hits,
                "suspects": len(suspects),
                "encounters": len(encounters),
                "three_option_encounters": sum(1 for count in option_counts if count >= 3),
                "endings": len(endings),
                "clue_variables": len(clue_vars),
                "has_secret_ending": bool(secret.get("title") and secret.get("threshold_logic")),
                "validator_head": validator.splitlines()[:5],
            }
        )
    summary = {"run_dir": str(run_dir), "source": source, "rows": rows}
    write_json(run_dir / "comparison_summary.json", summary)
    lines = [
        "# Murder Mystery Storyworld Comparison",
        "",
        f"- Source: `{summary['source']['source_title']}`",
        f"- Source path: `{summary['source']['source_path']}`",
        "",
        "| Condition | Extract OK | Builder Score | Blueprint Contract | Source Chars | Encounters | Endings | Validator Head |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        head = " / ".join(row["validator_head"]) if row["validator_head"] else ""
        score = "" if row["score"] is None else f"{row['score']:.4f}"
        lines.append(
            f"| `{row['condition']}` | {row['extract_ok']} | {score} | "
            f"{row['blueprint_contract_score']:.4f} | {row['source_character_hits']} | "
            f"{row['encounters']} | {row['endings']} | {head} |"
        )
    lines.extend(
        [
            "",
            "## Blueprint Details",
            "",
            "| Condition | Suspects | 3-Option Encounters | Clue Vars | Secret Ending |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for row in rows:
        lines.append(
            f"| `{row['condition']}` | {row['suspects']} | {row['three_option_encounters']} | "
            f"{row['clue_variables']} | {row['has_secret_ending']} |"
        )
    (run_dir / "comparison_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(str(run_dir / "comparison_summary.md"))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Murder mystery storyworld compare harness.")
    sub = parser.add_subparsers(dest="command", required=True)

    prep = sub.add_parser("prepare")
    prep.add_argument("--out-dir", required=True)
    prep.add_argument("--seed", type=int)
    prep.set_defaults(func=prepare)

    direct = sub.add_parser("call-direct")
    direct.add_argument("--run-dir", required=True)
    direct.add_argument("--condition", default="9b_direct")
    direct.add_argument("--prompt", default="prompt_9b_direct.md")
    direct.add_argument("--base-url", default="http://127.0.0.1:8084/v1")
    direct.add_argument("--model", default="Qwen_Qwen3.5-9B-Q4_K_M.gguf")
    direct.add_argument("--timeout", type=int, default=300)
    direct.add_argument("--max-response-tokens", type=int, default=5000)
    direct.set_defaults(func=call_direct)

    ing = sub.add_parser("ingest")
    ing.add_argument("--run-dir", required=True)
    ing.add_argument("--condition", required=True)
    ing.add_argument("--response-file", required=True)
    ing.add_argument("--model", required=True)
    ing.set_defaults(func=ingest)

    mat = sub.add_parser("materialize")
    mat.add_argument("--run-dir", required=True)
    mat.add_argument("--condition", required=True)
    mat.add_argument("--model", required=True)
    mat.add_argument("--author", default="Codex materializer")
    mat.add_argument("--context-budget-tokens", type=int, default=32768)
    mat.set_defaults(func=materialize)

    summ = sub.add_parser("summarize")
    summ.add_argument("--run-dir", required=True)
    summ.add_argument("--conditions", nargs="+", required=True)
    summ.set_defaults(func=summarize)

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
