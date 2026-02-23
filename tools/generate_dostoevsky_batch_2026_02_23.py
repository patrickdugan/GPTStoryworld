#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "codex-skills" / "storyworld-building" / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from one_shot_factory import build_subset  # type: ignore
from apply_artistry_pass import apply_artistry  # type: ignore
from storyworld_quality_gate import evaluate_storyworld  # type: ignore
from sweepweave_validator import validate_storyworld  # type: ignore


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")


def _make_bnumber_defaults(authored_props: List[str]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for p in authored_props:
        out[p] = {} if p.startswith("p") else 0
    return out


def _set_principal_cast(data: Dict[str, Any], cast: List[Dict[str, str]]) -> Dict[str, Any]:
    authored_props = [str(p.get("property_name", "")) for p in (data.get("authored_properties", []) or []) if p.get("property_name")]
    bdefaults = _make_bnumber_defaults(authored_props)
    ct = float(data.get("creation_time", 0.0))
    mt = float(data.get("modified_time", ct))
    chars: List[Dict[str, Any]] = []
    for idx, c in enumerate(cast):
        chars.append(
            {
                "creation_index": idx,
                "creation_time": ct,
                "id": c["id"],
                "modified_time": mt,
                "name": c["name"],
                "pronoun": "they",
                "description": c["description"],
                "bnumber_properties": json.loads(json.dumps(bdefaults)),
                "string_properties": {},
                "list_properties": {},
            }
        )
    data["characters"] = chars
    return data


def _rewrite_pointer_characters(node: Any, cast_ids: List[str], idx_seed: int = 0) -> int:
    idx = idx_seed
    if isinstance(node, dict):
        if node.get("pointer_type") == "Bounded Number Pointer":
            if cast_ids:
                node["character"] = cast_ids[idx % len(cast_ids)]
                keyring = node.get("keyring") or []
                if isinstance(keyring, list) and len(keyring) >= 2 and isinstance(keyring[1], str):
                    node["keyring"][1] = cast_ids[(idx + 1) % len(cast_ids)]
            idx += 1
        for v in node.values():
            idx = _rewrite_pointer_characters(v, cast_ids, idx)
        return idx
    if isinstance(node, list):
        for v in node:
            idx = _rewrite_pointer_characters(v, cast_ids, idx)
        return idx
    return idx


def _spread_character_dynamics(data: Dict[str, Any]) -> Dict[str, Any]:
    cast_ids = [str(c.get("id", "")) for c in (data.get("characters", []) or []) if c.get("id")]
    seed = 0
    for enc in data.get("encounters", []) or []:
        seed = _rewrite_pointer_characters(enc.get("acceptability_script"), cast_ids, seed)
        seed = _rewrite_pointer_characters(enc.get("desirability_script"), cast_ids, seed)
        for opt in enc.get("options", []) or []:
            seed = _rewrite_pointer_characters(opt.get("visibility_script"), cast_ids, seed)
            seed = _rewrite_pointer_characters(opt.get("performability_script"), cast_ids, seed)
            for rxn in opt.get("reactions", []) or []:
                seed = _rewrite_pointer_characters(rxn.get("desirability_script"), cast_ids, seed)
                seed = _rewrite_pointer_characters(rxn.get("after_effects"), cast_ids, seed)
    return data


def _enforce_saturation(data: Dict[str, Any]) -> Dict[str, Any]:
    encounters = data.get("encounters", []) or []
    for enc_idx, enc in enumerate(encounters):
        options = enc.get("options", []) or []
        if not options:
            continue
        options = options[:3]
        for opt_idx, opt in enumerate(options):
            reactions = opt.get("reactions", []) or []
            keep_n = 2 if ((enc_idx + opt_idx) % 2 == 0) else 3
            reactions = reactions[:keep_n]
            for rxn in reactions:
                rxn["after_effects"] = (rxn.get("after_effects", []) or [])[:4]
            opt["reactions"] = reactions
        enc["options"] = options
    return data


def _enforce_five_endings(data: Dict[str, Any]) -> Dict[str, Any]:
    encounters = data.get("encounters", []) or []
    terminals = [e for e in encounters if not (e.get("options") or [])]
    desired = 5
    if len(terminals) < desired:
        need = desired - len(terminals)
        for enc in reversed(encounters):
            if need <= 0:
                break
            if enc.get("options"):
                enc["options"] = []
                need -= 1
    terminals = [e for e in encounters if not (e.get("options") or [])]
    if len(terminals) > desired:
        keep_ids = {str(e.get("id", "")) for e in terminals[:desired]}
        fallback = str(terminals[0].get("id", ""))
        for e in terminals[desired:]:
            if str(e.get("id", "")) in keep_ids:
                continue
            e["options"] = [
                {
                    "id": f"opt_rejoin_{e.get('id','x')}",
                    "text_script": {"script_element_type": "Pointer", "pointer_type": "String Constant", "value": "Commit to final judgment."},
                    "visibility_script": True,
                    "performability_script": True,
                    "reactions": [
                        {
                            "id": f"rxn_rejoin_{e.get('id','x')}",
                            "text_script": {"script_element_type": "Pointer", "pointer_type": "String Constant", "value": "The narrative collapses into the final court of meaning."},
                            "after_effects": [],
                            "desirability_script": {"script_element_type": "Pointer", "pointer_type": "Bounded Number Constant", "value": 0.01},
                            "consequence_id": fallback,
                        }
                    ],
                }
            ]
    return data


def _enforce_five_act_spools(data: Dict[str, Any]) -> Dict[str, Any]:
    encounters = data.get("encounters", []) or []
    ids = [str(e.get("id", "")) for e in encounters if e.get("id")]
    terminals = [str(e.get("id", "")) for e in encounters if e.get("id") and not (e.get("options") or [])]
    non_term = [eid for eid in ids if eid not in set(terminals)]
    n = len(non_term)
    cuts = [int(n * i / 5) for i in range(6)]
    chunks = [non_term[cuts[i] : cuts[i + 1]] for i in range(5)]
    chunks[-1] = chunks[-1] + terminals
    ct = float(data.get("creation_time", 0.0))
    mt = float(data.get("modified_time", ct))
    data["spools"] = [
        {
            "creation_index": i - 1,
            "creation_time": ct,
            "id": f"spool_act_{i}",
            "modified_time": mt,
            "spool_name": f"Act {i}",
            "starts_active": i == 1,
            "encounters": chunk,
        }
        for i, chunk in enumerate(chunks, start=1)
        if chunk
    ]
    return data


def _specs() -> List[Dict[str, Any]]:
    return [
        {
            "slug": "dostoevsky_crime_and_punishment_multiending_v1",
            "title": "Crime and Punishment: Fever Geometry (Interactive Adaptation)",
            "about": "Guilt, ideology, and survival collide as confession, denial, and transcendence produce divergent moral endgames.",
            "motif": "Adaptation inspired by Crime and Punishment with fevered monologue branches and legal-spiritual reckoning arcs.",
            "cast": [
                {"id": "char_rodion", "name": "Raskolnikov", "description": "A brilliant student rationalizing extraordinary violence."},
                {"id": "char_sonya", "name": "Sonya", "description": "A compassionate moral witness and path to redemption."},
                {"id": "char_porfiry", "name": "Porfiry", "description": "An investigator who weaponizes patience and psychology."},
                {"id": "char_dunya", "name": "Dunya", "description": "A principled sister balancing dignity and family crisis."},
                {"id": "char_razumikhin", "name": "Razumikhin", "description": "A loyal pragmatist stabilizing social fallout."},
                {"id": "char_svidrigailov", "name": "Svidrigailov", "description": "A predatory cynic amplifying moral collapse."},
            ],
        },
        {
            "slug": "dostoevsky_the_gambler_multiending_v1",
            "title": "The Gambler: Roulette of Souls (Interactive Adaptation)",
            "about": "Desire, debt, and compulsion spiral around chance systems where each wager rewrites dignity and dependency.",
            "motif": "Adaptation inspired by The Gambler with compulsive risk loops, social humiliation pivots, and volatile reversals.",
            "cast": [
                {"id": "char_alexei", "name": "Alexei Ivanovich", "description": "A tutor consumed by risk, pride, and obsession."},
                {"id": "char_polina", "name": "Polina", "description": "A volatile focal point of desire, status, and leverage."},
                {"id": "char_general", "name": "The General", "description": "A decaying aristocrat trapped by appearances."},
                {"id": "char_grandmother", "name": "Antonida", "description": "An unpredictable force who distorts every plan."},
                {"id": "char_de_grieux", "name": "De Grieux", "description": "A calculating opportunist in creditor politics."},
                {"id": "char_mlle_blanche", "name": "Mademoiselle Blanche", "description": "A social strategist gaming reputation markets."},
            ],
        },
        {
            "slug": "dostoevsky_brothers_karamazov_multiending_v1",
            "title": "The Brothers Karamazov: Tribunal of Faith (Interactive Adaptation)",
            "about": "Family violence, metaphysics, and law collide as belief and responsibility branch into ruin, grace, or endless doubt.",
            "motif": "Adaptation inspired by The Brothers Karamazov with courtroom, confession, and theological confrontation branches.",
            "cast": [
                {"id": "char_dmitri", "name": "Dmitri", "description": "A passionate heir pulled between guilt and honor."},
                {"id": "char_ivan", "name": "Ivan", "description": "A rational skeptic unraveling under moral paradox."},
                {"id": "char_alyosha", "name": "Alyosha", "description": "A spiritual mediator seeking living compassion."},
                {"id": "char_smerdyakov", "name": "Smerdyakov", "description": "A resentful manipulator of truth and implication."},
                {"id": "char_katerina", "name": "Katerina", "description": "A proud strategist of sacrifice and accusation."},
                {"id": "char_grushenka", "name": "Grushenka", "description": "A charismatic actor in love, revenge, and mercy."},
            ],
        },
    ]


def main() -> int:
    out_dir = ROOT / "storyworlds" / "2-23-2026-batch"
    report_dir = out_dir / "_reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    base = _read_json(ROOT / "storyworlds" / "by-week" / "2026-W07" / "first_and_last_men_flagship_v10_textgate.json")
    summary: List[Dict[str, Any]] = []
    for spec in _specs():
        world = build_subset(
            base,
            target_encounters=92,
            title=spec["title"],
            about=spec["about"],
            motif=spec["motif"],
        )
        world = _set_principal_cast(world, spec["cast"])
        world = apply_artistry(world, gate_pct=0.20)
        world = _enforce_saturation(world)
        world = _spread_character_dynamics(world)
        world = _enforce_five_endings(world)
        world = _enforce_five_act_spools(world)

        out_path = out_dir / f"{spec['slug']}.json"
        _write_json(out_path, world)
        errors = validate_storyworld(str(out_path))
        gate = evaluate_storyworld(world, errors)
        gate["storyworld"] = str(out_path)
        gate_path = report_dir / f"{spec['slug']}.gate.json"
        gate_path.write_text(json.dumps(gate, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
        summary.append(
            {
                "slug": spec["slug"],
                "path": str(out_path),
                "encounters": len(world.get("encounters", [])),
                "characters": len(world.get("characters", [])),
                "endings": sum(1 for e in world.get("encounters", []) if not (e.get("options") or [])),
                "act_spools": [s.get("id") for s in world.get("spools", [])],
                "validator_errors": len(errors),
            }
        )
    summary_path = report_dir / "dostoevsky_batch_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    print(str(summary_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
