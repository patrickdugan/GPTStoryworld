#!/usr/bin/env python3
"""Apply recursive-reasoning mechanics to Diplomacy *_p storyworlds in place.

Targets only storyworlds where all character IDs begin with "power_".
"""

from __future__ import annotations

import argparse
import copy
import glob
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple


AGGRESSIVE_KEYWORDS = {
    "betray",
    "backstab",
    "punish",
    "revenge",
    "threat",
    "attack",
    "war",
    "strike",
    "defect",
    "treach",
    "collapse",
    "ultimatum",
    "coerc",
}

COOPERATIVE_KEYWORDS = {
    "ally",
    "alliance",
    "support",
    "cooperate",
    "cooperation",
    "trust",
    "honest",
    "pact",
    "peace",
    "dmz",
    "non-aggression",
    "joint",
    "coordinate",
}


def const_ptr(value: float) -> Dict[str, Any]:
    return {
        "pointer_type": "Bounded Number Constant",
        "script_element_type": "Pointer",
        "value": value,
    }


def prop_ptr(character: str, keyring: List[str], coefficient: float = 1.0) -> Dict[str, Any]:
    return {
        "pointer_type": "Bounded Number Property",
        "script_element_type": "Pointer",
        "character": character,
        "keyring": keyring,
        "coefficient": coefficient,
    }


def add_expr(base_ptr: Dict[str, Any], delta: float) -> Dict[str, Any]:
    return {
        "script_element_type": "Bounded Number Operator",
        "operator_type": "Addition",
        "operands": [base_ptr, const_ptr(delta)],
    }


def normalize_desirability(script: Any) -> Dict[str, Any]:
    if isinstance(script, dict):
        return script
    if isinstance(script, bool):
        return const_ptr(1.0 if script else 0.0)
    if isinstance(script, (int, float)):
        return const_ptr(float(script))
    return const_ptr(0.0)


def reaction_text(rxn: Dict[str, Any]) -> str:
    ts = rxn.get("text_script")
    if isinstance(ts, dict):
        val = ts.get("value")
        if isinstance(val, str):
            return val
        text = ts.get("text")
        if isinstance(text, str):
            return text
    if isinstance(ts, str):
        return ts
    return ""


def classify_reaction(rxn: Dict[str, Any]) -> str:
    text = reaction_text(rxn).lower()
    rid = str(rxn.get("id", "")).lower()
    oid = str(rxn.get("consequence_id", "")).lower()
    hay = f"{text} {rid} {oid}"

    if any(k in hay for k in AGGRESSIVE_KEYWORDS):
        return "aggressive"
    if any(k in hay for k in COOPERATIVE_KEYWORDS):
        return "cooperative"
    return "neutral"


def choose_trust_property(data: Dict[str, Any]) -> str:
    ids = [p.get("id", "") for p in data.get("authored_properties", [])]
    p_ids = [x for x in ids if isinstance(x, str) and x.startswith("p")]

    priority = [
        "pTrustworthy",
        "pTrust",
        "pHonesty",
        "pCommitment",
        "pCooperation",
    ]
    for pref in priority:
        for pid in p_ids:
            if pref.lower() in pid.lower():
                return pid

    if p_ids:
        return p_ids[0]

    return "pTrust"


def ensure_authored_property(data: Dict[str, Any], pid: str, depth: int, default_value: float = 0.0) -> bool:
    props = data.setdefault("authored_properties", [])
    if any(p.get("id") == pid for p in props):
        return False

    creation_index = max([int(p.get("creation_index", -1)) for p in props] + [-1]) + 1
    now_val = data.get("modified_time", data.get("creation_time", 0))
    if isinstance(now_val, (int, float)):
        now = float(now_val)
    else:
        now = now_val
    props.append(
        {
            "affected_characters": [],
            "attribution_target": "all cast members",
            "creation_index": creation_index,
            "creation_time": now,
            "default_value": default_value,
            "depth": depth,
            "id": pid,
            "modified_time": now,
            "property_name": pid,
            "property_type": "bounded number",
        }
    )
    return True


def ensure_character_property(character: Dict[str, Any], key: str, value: Any) -> bool:
    bprops = character.setdefault("bnumber_properties", {})
    if key in bprops:
        return False
    bprops[key] = value
    return True


def desirability_has_key(script: Any, key: str) -> bool:
    if isinstance(script, dict):
        keyring = script.get("keyring")
        if isinstance(keyring, list) and keyring and keyring[0] == key:
            return True
        for v in script.values():
            if desirability_has_key(v, key):
                return True
    elif isinstance(script, list):
        for item in script:
            if desirability_has_key(item, key):
                return True
    return False


def has_set_effect(after_effects: List[Dict[str, Any]], character: str, keyring: List[str]) -> bool:
    for eff in after_effects:
        if eff.get("effect_type") != "Set":
            continue
        s = eff.get("Set", {})
        if s.get("character") == character and s.get("keyring") == keyring:
            return True
    return False


def add_set_effect(after_effects: List[Dict[str, Any]], character: str, keyring: List[str], delta: float) -> None:
    if has_set_effect(after_effects, character, keyring):
        return
    base = prop_ptr(character=character, keyring=keyring, coefficient=1.0)
    after_effects.append(
        {
            "effect_type": "Set",
            "Set": base,
            "to": add_expr(base, delta),
        }
    )


def apply_to_file(path: Path) -> Dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    original = copy.deepcopy(data)

    characters = [c.get("id") for c in data.get("characters", []) if c.get("id")]
    if not characters or not all(str(c).startswith("power_") for c in characters):
        return {"file": str(path), "skipped": True, "reason": "not diplomacy power_* cast"}

    focal = characters[0]
    target = characters[1] if len(characters) > 1 else characters[0]
    witness = characters[2] if len(characters) > 2 else target

    trust_prop = choose_trust_property(data)

    added_props = 0
    for pid, depth, default in [
        ("Survival_Resource", 0, 0.65),
        ("Death_Ground_Signal", 0, 0.0),
        ("Strategic_Pressure", 0, 0.0),
    ]:
        if ensure_authored_property(data, pid, depth, default_value=default):
            added_props += 1

    added_char_props = 0
    for ch in data.get("characters", []):
        added_char_props += int(ensure_character_property(ch, "Survival_Resource", 0.65))
        added_char_props += int(ensure_character_property(ch, "Death_Ground_Signal", 0.0))
        added_char_props += int(ensure_character_property(ch, "Strategic_Pressure", 0.0))
        added_char_props += int(ensure_character_property(ch, "pTrust", {}))
        added_char_props += int(ensure_character_property(ch, "pThreat", {}))

    touched_reactions = 0
    added_effects = 0

    for enc in data.get("encounters", []):
        for opt in enc.get("options", []) or []:
            for rxn in opt.get("reactions", []) or []:
                cls = classify_reaction(rxn)

                if cls == "aggressive":
                    survival_coeff = -0.18
                    threat_coeff = 0.15
                    p2_coeff_primary = -0.12
                    p2_coeff_witness = -0.06
                    delta_survival = -0.08
                    delta_pressure = 0.07
                    delta_signal = 0.11
                    delta_p2 = -0.10
                elif cls == "cooperative":
                    survival_coeff = 0.10
                    threat_coeff = -0.10
                    p2_coeff_primary = 0.12
                    p2_coeff_witness = 0.06
                    delta_survival = 0.05
                    delta_pressure = -0.05
                    delta_signal = -0.04
                    delta_p2 = 0.08
                else:
                    survival_coeff = 0.0
                    threat_coeff = 0.03
                    p2_coeff_primary = 0.05
                    p2_coeff_witness = 0.03
                    delta_survival = -0.01
                    delta_pressure = 0.02
                    delta_signal = 0.01
                    delta_p2 = -0.01

                base = normalize_desirability(rxn.get("desirability_script"))
                new_terms: List[Dict[str, Any]] = []

                if not desirability_has_key(base, trust_prop):
                    new_terms.append(prop_ptr(focal, [trust_prop, target, focal], p2_coeff_primary))
                    if witness != focal:
                        new_terms.append(prop_ptr(focal, [trust_prop, target, witness], p2_coeff_witness))

                if not desirability_has_key(base, "pThreat"):
                    new_terms.append(prop_ptr(focal, ["pThreat", target], threat_coeff))

                if survival_coeff != 0.0 and not desirability_has_key(base, "Survival_Resource"):
                    new_terms.append(prop_ptr(focal, ["Survival_Resource"], survival_coeff))

                if new_terms:
                    rxn["desirability_script"] = {
                        "script_element_type": "Bounded Number Operator",
                        "operator_type": "Addition",
                        "operands": [base] + new_terms,
                    }

                after_effects = rxn.setdefault("after_effects", [])
                before_len = len(after_effects)

                add_set_effect(after_effects, focal, ["Survival_Resource"], delta_survival)
                add_set_effect(after_effects, focal, ["Strategic_Pressure"], delta_pressure)
                add_set_effect(after_effects, focal, ["Death_Ground_Signal"], delta_signal)
                add_set_effect(after_effects, focal, [trust_prop, target, focal], delta_p2)

                # Paine-style tradeoff: coalition framing can weaken third-party trust.
                if cls == "cooperative" and witness not in {focal, target}:
                    add_set_effect(after_effects, focal, [trust_prop, witness], -0.04)

                delta_added = len(after_effects) - before_len
                if delta_added > 0 or new_terms:
                    touched_reactions += 1
                    added_effects += max(0, delta_added)

    if data != original:
        # Preserve existing type for modified_time (numeric or ISO string).
        if "modified_time" not in data:
            data["modified_time"] = data.get("creation_time", 0.0)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "file": str(path),
        "skipped": False,
        "focal": focal,
        "target": target,
        "witness": witness,
        "trust_prop": trust_prop,
        "added_props": added_props,
        "added_char_props": added_char_props,
        "touched_reactions": touched_reactions,
        "added_effects": added_effects,
        "changed": data != original,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply recursive models to diplomacy *_p storyworlds")
    parser.add_argument(
        "--glob",
        default=r"C:\projects\GPTStoryworld\storyworlds\*_p.json",
        help="Glob for candidate storyworld files",
    )
    args = parser.parse_args()

    paths = [Path(p) for p in sorted(glob.glob(args.glob))]
    results = [apply_to_file(p) for p in paths]

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
