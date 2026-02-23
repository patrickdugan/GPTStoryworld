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


def _enforce_saturation(data: Dict[str, Any]) -> Dict[str, Any]:
    """Tune to ~3 options/encounter, ~2.5 reactions/option, 4 effects/reaction."""
    encounters = data.get("encounters", []) or []
    for enc_idx, enc in enumerate(encounters):
        options = enc.get("options", []) or []
        if not options:
            continue
        trimmed_options = options[:3]
        for opt_idx, opt in enumerate(trimmed_options):
            reactions = opt.get("reactions", []) or []
            # Alternate per encounter: [2,3,2] then [3,2,3] -> batch average ~2.5.
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


def _ensure_three_characters(data: Dict[str, Any]) -> Dict[str, Any]:
    chars = data.get("characters", []) or []
    if len(chars) >= 3:
        return data
    ids = {str(c.get("id", "")) for c in chars}
    if "char_mediator" in ids:
        return data

    bnumber_props = {
        "Influence": 0,
        "pInfluence": {},
        "Trust_Balance": 0,
        "pTrust_Balance": {},
        "Risk_Stasis": 0,
        "pRisk_Stasis": {},
    }
    new_char = {
        "creation_index": len(chars),
        "creation_time": float(data.get("creation_time", 0.0)),
        "id": "char_mediator",
        "modified_time": float(data.get("modified_time", data.get("creation_time", 0.0))),
        "name": "The Mediator",
        "pronoun": "they",
        "description": "A broker of uneasy settlements who tracks public sentiment and timing windows.",
        "bnumber_properties": bnumber_props,
        "string_properties": {},
        "list_properties": {},
    }
    chars.append(new_char)
    data["characters"] = chars
    return data


def _make_specs() -> List[Dict[str, str]]:
    # Idea-factory samplings: derived from local trope overlays/mechanics.
    idea_specs = [
        {
            "slug": "if_legitimacy_crisis_councilfire_v1",
            "title": "Councilfire: A Legitimacy Crisis",
            "about": "A reform council balances orthodoxy, innovation, and public trust while elite factions force irreversible bargains.",
            "motif": "IdeaFactory overlay: legitimacy crisis with trust thresholds and delayed backlash.",
            "kind": "idea_factory",
            "base": "falm",
        },
        {
            "slug": "if_schism_interpretation_archivewars_v1",
            "title": "Archive Wars: Schism of Interpretation",
            "about": "Two schools weaponize interpretation and must either reconcile across spools or split into rival orders.",
            "motif": "IdeaFactory overlay: schism and interpretation with coupled orthodoxy versus innovation.",
            "kind": "idea_factory",
            "base": "falm",
        },
        {
            "slug": "if_reform_cycle_statute_or_silence_v1",
            "title": "Statute or Silence",
            "about": "A reform cycle spirals through committees, petitions, and retaliation as codification choices lock the final act.",
            "motif": "IdeaFactory overlay: reform cycles, delayed consequence, and irreversible codify-versus-preserve choice.",
            "kind": "idea_factory",
            "base": "falm",
        },
        {
            "slug": "if_institutional_deadlock_mediator_line_v1",
            "title": "Mediator Line",
            "about": "Institutional deadlock forces a mediator faction to broker power while influence remains a conserved pool.",
            "motif": "IdeaFactory overlay: institutional deadlock with negotiation gates and conserved influence.",
            "kind": "idea_factory",
            "base": "falm",
        },
        {
            "slug": "if_public_vs_elite_citypulse_v1",
            "title": "Citypulse: Public vs Elite",
            "about": "Public sentiment and elite calculus diverge until hidden civic encounters unlock late-stage settlement routes.",
            "motif": "IdeaFactory overlay: public versus elite with hidden sentiment channels and secret-route unlocks.",
            "kind": "idea_factory",
            "base": "falm",
        },
    ]

    # Interactive adaptations: original paraphrase only; no direct quotation.
    adaptation_specs = [
        {
            "slug": "adapt_casablanca_crossroads_at_ricks_v1",
            "title": "Crossroads at Rick's (Interactive Adaptation)",
            "about": "A wartime transit city tests loyalty, sacrifice, and leverage as each alliance can redirect the final departure.",
            "motif": "Interactive adaptation inspired by Casablanca using original paraphrased scene framing and dialogue style.",
            "kind": "adaptation",
            "base": "falm",
        },
        {
            "slug": "adapt_catcher_glass_corridors_v1",
            "title": "Glass Corridors (Interactive Adaptation)",
            "about": "An alienated student drifts through institutions and confidants, choosing between retreat, confrontation, and care.",
            "motif": "Interactive adaptation inspired by The Catcher in the Rye with original non-quoted inner-voice reactions.",
            "kind": "adaptation",
            "base": "falm",
        },
        {
            "slug": "adapt_on_the_road_midnight_mileposts_v1",
            "title": "Midnight Mileposts (Interactive Adaptation)",
            "about": "Restless travelers cross cities and obligations while friendship, exhaustion, and reinvention split the route tree.",
            "motif": "Interactive adaptation inspired by On the Road with original paraphrased road-arc encounters.",
            "kind": "adaptation",
            "base": "falm",
        },
        {
            "slug": "adapt_american_psyche_velvet_ledgers_v1",
            "title": "Velvet Ledgers (Interactive Adaptation)",
            "about": "An image-obsessed financier curates status masks while unstable impulses threaten to collapse the social simulation.",
            "motif": "Interactive adaptation inspired by American Psycho with original paraphrased social-horror dialogue.",
            "kind": "adaptation",
            "base": "falm",
        },
        {
            "slug": "adapt_billy_budd_foretop_oath_v1",
            "title": "Foretop Oath (Interactive Adaptation)",
            "about": "A young sailor's integrity collides with rigid command law, forcing crews to weigh justice, order, and mercy.",
            "motif": "Interactive adaptation inspired by Billy Budd with original paraphrased shipboard confrontation text.",
            "kind": "adaptation",
            "base": "falm",
        },
    ]

    return idea_specs + adaptation_specs


def main() -> int:
    out_dir = ROOT / "storyworlds" / "2-23-2026-batch"
    report_dir = out_dir / "_reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    base_worlds = {
        "falm": _read_json(ROOT / "storyworlds" / "by-week" / "2026-W07" / "first_and_last_men_flagship_v10_textgate.json"),
        "flux": _read_json(ROOT / "storyworlds" / "by-week" / "2026-W07" / "gone_with_the_flux_capacitor_v6_textgate.json"),
    }

    specs = _make_specs()
    summary: List[Dict[str, Any]] = []

    for spec in specs:
        base = base_worlds[spec["base"]]
        world = build_subset(
            base,
            target_encounters=92,
            title=spec["title"],
            about=spec["about"],
            motif=spec["motif"],
        )
        world = apply_artistry(world, gate_pct=0.10)
        world = _enforce_saturation(world)
        world = _ensure_three_characters(world)

        out_path = out_dir / f"{spec['slug']}.json"
        _write_json(out_path, world)

        validation_errors = validate_storyworld(str(out_path))
        gate = evaluate_storyworld(world, validation_errors)
        gate["storyworld"] = str(out_path)
        report_path = report_dir / f"{spec['slug']}.gate.json"
        report_path.write_text(json.dumps(gate, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")

        s = gate.get("summary", {})
        pm = gate.get("polish_metrics", {})
        summary.append(
            {
                "slug": spec["slug"],
                "kind": spec["kind"],
                "path": str(out_path),
                "pass": bool(gate.get("pass")),
                "encounters": s.get("encounters", 0),
                "options_per_encounter": round(float(pm.get("options_per_encounter", 0.0)), 3),
                "reactions_per_option": round(float(pm.get("reactions_per_option", 0.0)), 3),
                "effects_per_reaction": round(float(pm.get("effects_per_reaction", 0.0)), 3),
                "pvalue_refs": int(s.get("pvalue_refs", 0)),
                "p2value_refs": int(s.get("p2value_refs", 0)),
                "validator_errors": len(validation_errors),
            }
        )

    summary_path = report_dir / "batch_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    print(str(summary_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
