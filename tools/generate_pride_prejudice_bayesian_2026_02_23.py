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


def _set_cast(data: Dict[str, Any]) -> Dict[str, Any]:
    cast = [
        {"id": "char_elizabeth", "name": "Elizabeth Bennet", "description": "A sharp social reasoner calibrating trust under sparse evidence."},
        {"id": "char_darcy", "name": "Fitzwilliam Darcy", "description": "A high-status signaler with low transparency and delayed vulnerability."},
        {"id": "char_jane", "name": "Jane Bennet", "description": "A benevolent prior modeler vulnerable to strategic silence."},
        {"id": "char_bingley", "name": "Charles Bingley", "description": "A high-variance actor swayed by local consensus fields."},
        {"id": "char_wickham", "name": "George Wickham", "description": "A deceptive signal jammer exploiting reputation lag."},
        {"id": "char_lady_catherine", "name": "Lady Catherine", "description": "An institutional prior enforcer optimizing class boundary conditions."},
    ]
    authored = [str(p.get("property_name", "")) for p in (data.get("authored_properties", []) or []) if p.get("property_name")]
    defaults = _make_bnumber_defaults(authored)
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
                "bnumber_properties": json.loads(json.dumps(defaults)),
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
    if len(terminals) < 5:
        need = 5 - len(terminals)
        for enc in reversed(encounters):
            if need <= 0:
                break
            if enc.get("options"):
                enc["options"] = []
                need -= 1
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


def main() -> int:
    out_dir = ROOT / "storyworlds" / "2-23-2026-batch"
    report_dir = out_dir / "_reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    base = _read_json(ROOT / "storyworlds" / "by-week" / "2026-W07" / "first_and_last_men_flagship_v10_textgate.json")
    world = build_subset(
        base,
        target_encounters=92,
        title="Pride and Prejudice: Bayesian Courtship Under Noise (Interactive Adaptation)",
        about=(
            "A courtship inference machine where hidden signals, reputation scoring, and miscalibrated priors alter proposals, "
            "alliances, and social legitimacy."
        ),
        motif=(
            "Noisy signaling in drawing rooms: each slight, letter, and intervention updates posterior beliefs across the marriage market."
        ),
    )
    world = _set_cast(world)
    world = apply_artistry(world, gate_pct=0.20)
    world = _enforce_saturation(world)
    world = _spread_character_dynamics(world)
    world = _enforce_five_endings(world)
    world = _enforce_five_act_spools(world)

    out_path = out_dir / "austen_pride_and_prejudice_bayesian_courtship_multiending_v1.json"
    _write_json(out_path, world)
    errors = validate_storyworld(str(out_path))
    gate = evaluate_storyworld(world, errors)
    gate["storyworld"] = str(out_path)
    gate_path = report_dir / "austen_pride_and_prejudice_bayesian_courtship_multiending_v1.gate.json"
    gate_path.write_text(json.dumps(gate, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    summary = {
        "path": str(out_path),
        "encounters": len(world.get("encounters", [])),
        "characters": len(world.get("characters", [])),
        "character_names": [c.get("name") for c in world.get("characters", [])],
        "endings": sum(1 for e in world.get("encounters", []) if not (e.get("options") or [])),
        "act_spools": [s.get("id") for s in world.get("spools", [])],
        "validator_errors": len(errors),
    }
    summary_path = report_dir / "austen_pride_and_prejudice_bayesian_courtship_multiending_v1.summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    print(str(summary_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
