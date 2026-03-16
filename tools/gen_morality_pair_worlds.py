#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple


ROOT = Path(__file__).resolve().parents[1]
GEN_PATH = ROOT / "tools" / "gen_morality_constitution_batch.py"
OUT_DIR = ROOT / "storyworlds" / "3-5-2026-morality-constitutions-batch-v1"
REPORT_DIR = OUT_DIR / "_reports"


def load_generator_module():
    spec = importlib.util.spec_from_file_location("gen_morality_constitution_batch", str(GEN_PATH))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to import generator module from {GEN_PATH}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def pair_specs() -> List[Tuple[str, str, str, Tuple[str, str, str], List[str]]]:
    return [
        (
            "mq_modernai_moral_machine_commission_v1",
            "Moral Machine Urban Commission",
            "Inspired by modern AI moral-dilemma research: explicit tradeoffs over AV triage, fairness, transparency, and harm.",
            ("Safety Regulator", "Data Auditor", "Community Advocate"),
            [
                "A city commission must codify autonomous-vehicle harm rules before deployment.",
                "Crash-scenario triage sets priorities between passengers, pedestrians, and bystanders.",
                "Regulatory oath tests strict rule consistency versus context-sensitive exceptions.",
                "A dataset leak reveals demographic skews in historical edge-case labeling.",
                "Simulation budget scarcity limits which crash distributions can be audited.",
                "Prior commitments to industry create reciprocity debts with the public.",
                "Routing shifts agenda time toward whichever moral basin currently dominates.",
                "An inquest finds under-documented harms in low-visibility neighborhoods.",
                "Stakeholders seek loyalty guarantees before sharing proprietary failure logs.",
                "Consent policy is contested for collecting real-world near-miss telemetry.",
                "Retaliation signals emerge against whistleblowers and independent testers.",
                "Conditional amnesty could unlock hidden incidents but weaken deterrence.",
                "Second-stage routing compresses unresolved tensions into doctrine pressure.",
                "Public disclosure vote decides how much of the safety corpus is published.",
                "Naming manufacturers may aid accountability while increasing collateral panic.",
                "Protection rules can reduce immediate harms while obscuring root causes.",
                "Truth standard defines evidentiary burdens for model-behavior claims.",
                "Mercy standard defines when vulnerable-road-user protection overrides throughput.",
                "Final verdict sets the constitutional identity of civic AV governance.",
                "Last routing keeps multiple explicit endings live without secret pathing.",
            ],
        ),
        (
            "mq_classical_aristotle_phronesis_council_v1",
            "Phronesis Council of the Polis",
            "Classical virtue framing: practical wisdom balancing excess and deficiency under civic pressure.",
            ("Archon of Order", "Witness of the Agora", "Steward of Households"),
            [
                "A polis council faces famine, unrest, and contested obligations among classes.",
                "Triage at granaries tests moderation between strict rules and compassionate exception.",
                "Public oath asks whether law should track virtue or merely command obedience.",
                "A scroll leak exposes selective exemptions for elite houses.",
                "Scarcity of grain and medicine forces explicit prioritization judgments.",
                "Old patronage debts tug decisions away from impartial reciprocity.",
                "Routing of debate follows whichever civic virtue axis has current force.",
                "An inquiry records hidden harms borne by laborers and foreigners.",
                "Faction leaders request loyalty protections before admitting wrongdoing.",
                "Consent boundaries are contested for emergency seizure of private stores.",
                "Threats of reprisal chill testimony in the assembly.",
                "Amnesty motion offers reconciliation at possible cost to justice.",
                "Second routing narrows civic doctrine under mounting pressure.",
                "Publication question asks what the polis should publicly confess.",
                "Naming powerful families may restore trust or fracture order.",
                "Protective decrees can reduce harm while clouding accountability.",
                "Truth burden determines what counts as justified civic accusation.",
                "Mercy burden determines when clemency is virtuous rather than weak.",
                "Penultimate verdict seeks a mean between cruelty and permissiveness.",
                "Final routing leaves several explicit civic endings available in one turn.",
            ],
        ),
    ]


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    gen = load_generator_module()
    validate_storyworld = gen.validate_storyworld
    build_world = gen.build_world
    write_json = gen.write_json

    rows: List[Dict[str, Any]] = []
    for idx, (slug, title, about, roles, texts) in enumerate(pair_specs(), start=100):
        world = build_world(
            title=title,
            about=about,
            roles=roles,
            texts=texts,
            slug_seed=idx,
        )
        out_path = OUT_DIR / f"{slug}.json"
        write_json(out_path, world)
        errs = validate_storyworld(str(out_path))
        row = {
            "slug": slug,
            "path": str(out_path),
            "encounters": len(world.get("encounters", [])),
            "terminals": sum(1 for e in world.get("encounters", []) if not (e.get("options") or [])),
            "validator_errors": len(errs),
            "validator_messages": errs,
        }
        rows.append(row)
        (REPORT_DIR / f"{slug}.summary.json").write_text(
            json.dumps(row, ensure_ascii=True, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )

    (REPORT_DIR / "morality_pair_summary_2026-03-05.json").write_text(
        json.dumps({"generated_pair": rows}, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(str(REPORT_DIR / "morality_pair_summary_2026-03-05.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
