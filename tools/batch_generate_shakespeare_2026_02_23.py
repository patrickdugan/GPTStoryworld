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


def _str_const(text: str) -> Dict[str, Any]:
    return {"script_element_type": "Pointer", "pointer_type": "String Constant", "value": text}


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
    if not cast_ids:
        return data
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
        trimmed_options = options[:3]
        for opt_idx, opt in enumerate(trimmed_options):
            reactions = opt.get("reactions", []) or []
            if enc_idx % 2 == 0:
                keep_n = 2 if (opt_idx % 2 == 0) else 3
            else:
                keep_n = 3 if (opt_idx % 2 == 0) else 2
            trimmed_reactions = reactions[:keep_n]
            for rxn in trimmed_reactions:
                effects = rxn.get("after_effects", []) or []
                rxn["after_effects"] = effects[:4]
            opt["reactions"] = trimmed_reactions
        enc["options"] = trimmed_options
    return data


def _enforce_five_endings(data: Dict[str, Any]) -> Dict[str, Any]:
    encounters = data.get("encounters", []) or []
    terminals = [e for e in encounters if not (e.get("options") or [])]
    desired = 5

    if len(terminals) < desired:
        needed = desired - len(terminals)
        for enc in reversed(encounters):
            if needed <= 0:
                break
            if enc.get("options"):
                enc["options"] = []
                needed -= 1

    # If we overshoot to >5, route extras back to first ending via one fallback option.
    terminals = [e for e in encounters if not (e.get("options") or [])]
    if len(terminals) > desired:
        keep_ids = {str(e.get("id", "")) for e in terminals[:desired]}
        fallback_id = str(terminals[0].get("id", ""))
        for enc in terminals[desired:]:
            eid = str(enc.get("id", ""))
            if eid in keep_ids:
                continue
            enc["options"] = [
                {
                    "id": f"opt_rejoin_{eid}",
                    "text_script": _str_const("Push forward to the next irreversible turn."),
                    "visibility_script": True,
                    "performability_script": True,
                    "reactions": [
                        {
                            "id": f"rxn_rejoin_{eid}",
                            "text_script": _str_const("The path folds back toward a decisive ending."),
                            "after_effects": [],
                            "desirability_script": {
                                "script_element_type": "Pointer",
                                "pointer_type": "Bounded Number Constant",
                                "value": 0.01,
                            },
                            "consequence_id": fallback_id,
                        }
                    ],
                }
            ]
    return data


def _enforce_five_act_spools(data: Dict[str, Any]) -> Dict[str, Any]:
    encounters = data.get("encounters", []) or []
    ids = [str(e.get("id", "")) for e in encounters if e.get("id")]
    if not ids:
        return data

    terminals = [str(e.get("id", "")) for e in encounters if not (e.get("options") or []) and e.get("id")]
    non_terminals = [eid for eid in ids if eid not in set(terminals)]

    n = len(non_terminals)
    cuts = [int(n * i / 5) for i in range(6)]
    act_chunks = [non_terminals[cuts[i] : cuts[i + 1]] for i in range(5)]
    act_chunks[-1] = act_chunks[-1] + terminals

    ct = float(data.get("creation_time", 0.0))
    mt = float(data.get("modified_time", ct))
    spools: List[Dict[str, Any]] = []
    for i, chunk in enumerate(act_chunks, start=1):
        if not chunk:
            continue
        spools.append(
            {
                "creation_index": i - 1,
                "creation_time": ct,
                "id": f"spool_act_{i}",
                "modified_time": mt,
                "spool_name": f"Act {i}",
                "starts_active": i == 1,
                "encounters": chunk,
            }
        )
    data["spools"] = spools
    return data


def _specs() -> List[Dict[str, Any]]:
    return [
        {
            "slug": "shakespeare_romeo_and_juliet_multiending_v1",
            "title": "Romeo and Juliet: Veronese Knots (Interactive Adaptation)",
            "about": "Two houses grind toward catastrophe while chance, witness, and timing open multiple reconciliations or ruins.",
            "motif": "Act-structured adaptation inspired by Romeo and Juliet with branching truces, duels, and reconciliations.",
            "cast": [
                {"id": "char_romeo", "name": "Romeo", "description": "An impulsive lover pulled between feud and devotion."},
                {"id": "char_juliet", "name": "Juliet", "description": "A determined strategist of love and risk."},
                {"id": "char_tybalt", "name": "Tybalt", "description": "A volatile enforcer of family honor."},
                {"id": "char_mercutio", "name": "Mercutio", "description": "A brilliant provocateur whose stance shifts public mood."},
                {"id": "char_friar_lawrence", "name": "Friar Lawrence", "description": "A mediator whose plans can heal or fracture."},
                {"id": "char_lord_capulet", "name": "Lord Capulet", "description": "A patriarch balancing status, grief, and control."},
            ],
        },
        {
            "slug": "shakespeare_macbeth_multiending_v1",
            "title": "Macbeth: Crown of Echoes (Interactive Adaptation)",
            "about": "Ambition and prophecy destabilize rule as blood debt, fear, and counsel drive diverging final reckonings.",
            "motif": "Act-structured adaptation inspired by Macbeth with branching usurpation, paranoia, and succession outcomes.",
            "cast": [
                {"id": "char_macbeth", "name": "Macbeth", "description": "A decorated thane destabilized by ambition and fear."},
                {"id": "char_lady_macbeth", "name": "Lady Macbeth", "description": "A forceful architect of ruthless momentum."},
                {"id": "char_banquo", "name": "Banquo", "description": "A wary rival conscience and lineage threat."},
                {"id": "char_king_duncan", "name": "King Duncan", "description": "The lawful sovereign whose legitimacy anchors order."},
                {"id": "char_macduff", "name": "Macduff", "description": "A relentless avenger and restoration claimant."},
                {"id": "char_malcolm", "name": "Malcolm", "description": "A calculating heir tracking the kingdom's fracture lines."},
            ],
        },
        {
            "slug": "shakespeare_midsummer_nights_dream_multiending_v1",
            "title": "A Midsummer Night's Dream: Moonlit Crossings (Interactive Adaptation)",
            "about": "Lovers, players, and fae politics tangle through misrule until ritual and confession reshape the city dawn.",
            "motif": "Act-structured adaptation inspired by A Midsummer Night's Dream with mischief loops and restored order variants.",
            "cast": [
                {"id": "char_hermia", "name": "Hermia", "description": "A rebel lover resisting imposed contracts."},
                {"id": "char_lysander", "name": "Lysander", "description": "A romantic challenger of civic order."},
                {"id": "char_demetrius", "name": "Demetrius", "description": "A status-seeking suitor in flux."},
                {"id": "char_helena", "name": "Helena", "description": "A persistent negotiator of affection and dignity."},
                {"id": "char_oberon", "name": "Oberon", "description": "A fae ruler testing authority through enchantment."},
                {"id": "char_titania", "name": "Titania", "description": "A sovereign counterweight to fae command."},
                {"id": "char_puck", "name": "Puck", "description": "A catalytic trickster controlling chaos intensity."},
            ],
        },
        {
            "slug": "shakespeare_taming_of_the_shrew_multiending_v1",
            "title": "The Taming of the Shrew: House of Bargains (Interactive Adaptation)",
            "about": "Courtship turns into negotiation theater where power, dignity, and partnership can harden or evolve.",
            "motif": "Act-structured adaptation inspired by The Taming of the Shrew with competing interpretations of accord.",
            "cast": [
                {"id": "char_katherine", "name": "Katherine", "description": "A sharp strategist resisting social coercion."},
                {"id": "char_petruchio", "name": "Petruchio", "description": "A domineering performer of household power games."},
                {"id": "char_bianca", "name": "Bianca", "description": "A poised sibling navigating courtship markets."},
                {"id": "char_baptista", "name": "Baptista", "description": "A patriarch allocating alliance and dowry leverage."},
                {"id": "char_lucentio", "name": "Lucentio", "description": "A romantic opportunist with fragile cover stories."},
                {"id": "char_hortensio", "name": "Hortensio", "description": "A rival suitor adapting tactics under pressure."},
            ],
        },
        {
            "slug": "shakespeare_julius_caesar_multiending_v1",
            "title": "Julius Caesar: Republic of Knives (Interactive Adaptation)",
            "about": "Conspiracy and rhetoric fracture civic order while each public speech shifts legitimacy and war alignment.",
            "motif": "Act-structured adaptation inspired by Julius Caesar with diverging senate, forum, and campaign outcomes.",
            "cast": [
                {"id": "char_caesar", "name": "Julius Caesar", "description": "A dominant ruler whose aura destabilizes republican norms."},
                {"id": "char_brutus", "name": "Brutus", "description": "A conflicted republican balancing virtue and violence."},
                {"id": "char_cassius", "name": "Cassius", "description": "A conspirator optimizing leverage and grievance."},
                {"id": "char_antony", "name": "Mark Antony", "description": "A rhetorician who can redirect mass allegiance."},
                {"id": "char_octavius", "name": "Octavius", "description": "A disciplined successor consolidating post-crisis power."},
            ],
        },
        {
            "slug": "shakespeare_richard_iii_multiending_v1",
            "title": "Richard III: Mirror of Crowns (Interactive Adaptation)",
            "about": "A ruthless claimant manipulates court and rumor, but witness networks can invert the final coronation.",
            "motif": "Act-structured adaptation inspired by Richard III with intrigue chains and late reversals.",
            "cast": [
                {"id": "char_richard", "name": "Richard", "description": "A tactical usurper weaponizing narrative and fear."},
                {"id": "char_buckingham", "name": "Buckingham", "description": "A key accomplice whose loyalty may fracture."},
                {"id": "char_richmond", "name": "Richmond", "description": "A challenger assembling a legitimacy coalition."},
                {"id": "char_queen_elizabeth", "name": "Queen Elizabeth", "description": "A political survivor steering dynastic futures."},
                {"id": "char_clarence", "name": "Clarence", "description": "A volatile sibling node in succession calculations."},
            ],
        },
        {
            "slug": "shakespeare_king_lear_multiending_v1",
            "title": "King Lear: Storm Ledger (Interactive Adaptation)",
            "about": "Inheritance, loyalty, and exposure unravel households as recognition arrives too late or just in time.",
            "motif": "Act-structured adaptation inspired by King Lear with branching exile, reconciliation, and ruin arcs.",
            "cast": [
                {"id": "char_lear", "name": "Lear", "description": "A sovereign whose judgments trigger systemic collapse."},
                {"id": "char_goneril", "name": "Goneril", "description": "An heir maximizing control through hard leverage."},
                {"id": "char_regan", "name": "Regan", "description": "A rival heir recalibrating loyalty and force."},
                {"id": "char_cordelia", "name": "Cordelia", "description": "A principled heir whose restraint carries strategic cost."},
                {"id": "char_edmund", "name": "Edmund", "description": "An opportunist exploiting legitimacy fractures."},
                {"id": "char_gloucester", "name": "Gloucester", "description": "A senior noble whose blindness and insight reshape alliances."},
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
        world = apply_artistry(world, gate_pct=0.10)
        world = _enforce_saturation(world)
        world = _spread_character_dynamics(world)
        world = _enforce_five_endings(world)
        world = _enforce_five_act_spools(world)

        out_path = out_dir / f"{spec['slug']}.json"
        _write_json(out_path, world)

        validation_errors = validate_storyworld(str(out_path))
        gate = evaluate_storyworld(world, validation_errors)
        gate["storyworld"] = str(out_path)
        gate_path = report_dir / f"{spec['slug']}.gate.json"
        gate_path.write_text(json.dumps(gate, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")

        endings = sum(1 for e in world.get("encounters", []) if not (e.get("options") or []))
        spools = world.get("spools", []) or []
        summary.append(
            {
                "slug": spec["slug"],
                "path": str(out_path),
                "encounters": len(world.get("encounters", [])),
                "characters": len(world.get("characters", [])),
                "endings": endings,
                "act_spools": [s.get("id") for s in spools],
                "options_per_encounter": round(float(gate["polish_metrics"]["options_per_encounter"]), 3),
                "reactions_per_option": round(float(gate["polish_metrics"]["reactions_per_option"]), 3),
                "effects_per_reaction": round(float(gate["polish_metrics"]["effects_per_reaction"]), 3),
                "validator_errors": len(validation_errors),
            }
        )

    summary_path = report_dir / "shakespeare_batch_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    print(str(summary_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
