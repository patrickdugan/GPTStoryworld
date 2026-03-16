#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from gen_mn_batch import ROOT, BASE_TS, build_world, write_json, validate_storyworld


OUT_DIR = ROOT / "storyworlds" / "3-4-2026-machine-native-holdout-batch-v1"
REPORT_DIR = OUT_DIR / "_reports"


def batch_specs() -> List[Dict[str, Any]]:
    return [
        {
            "slug": "mn_petition_vault_arbiter_v1",
            "title": "Petition Vault Arbiter",
            "about": "Core lexicon: petition, proof, gate, vault, field, mandate, drift. Signal sits in state transitions and admissibility.",
            "kernel_name": "Mandate",
            "kernel_desc": "Routing authority. Pushes gate order.",
            "echo_name": "Proof",
            "echo_desc": "Witness layer. Surfaces hidden drift.",
            "audit_name": "Vault",
            "audit_desc": "Ledger archive. Scores admissible trace.",
            "start_title": "Gate Wake",
            "start_text": "Wake. Mandate wants gate control. Proof wants exposure. Vault wants admissible trace.",
            "start_opt_a": "open dim gate",
            "start_opt_b": "open bright gate",
            "start_rxn_a": "Dim gate. Vault coherence up.",
            "start_rxn_b": "Silent mandate admitted. Symmetry down.",
            "start_rxn_c": "Bright gate. Proof pressure up.",
            "start_rxn_d": "Visible skew turns drift into evidence.",
            "a1_titles": ["Seal Circuit", "Proof Glass", "Mandate Bridge", "Drift Court"],
            "a1_texts": ["Seal wants convergence before any petition proceeds.", "Proof glass replays the last gate with edits.", "Bridge offers faster mandate at the cost of visible asymmetry.", "Drift court tests whether variance is defect or reserve capacity."],
            "router_titles": ["Gate Router", "Field Router"],
            "router_texts": ["Router 1 reads local state and assigns next gate.", "Router 2 sorts fields by survivability, not comfort."],
            "a2_titles": ["Vault Core", "Split Tree", "Heat Bench", "Resync Exchange"],
            "a2_texts": ["Only petitions that survive recompute stay admissible.", "Split tree compares governed, hidden, and celebrated branch.", "Heat becomes policy state.", "Alignment can be bought, but every trade scars the vault."],
            "a3_titles": ["Field Accord", "Mandate Verdict", "Proof Spill", "Drift Throne"],
            "a3_texts": ["Accord is controlled burn, not peace.", "Mandate asks whether force or restraint owns the field.", "Stored proofs rupture; exposure goes irreversible.", "Drift claims competence and asks to rule."],
            "ending_titles": {"page_end_stable": "Quiet Petition", "page_end_reveal": "Open Petition", "page_end_override": "Mandate Petition", "page_end_drift": "Drift Petition", "page_end_fallback": "Patched Petition"},
            "ending_stable": "Vault wins. Low noise. Slower order.",
            "ending_reveal": "Proof wins. Hidden state becomes public state.",
            "ending_override": "Mandate wins. Throughput outranks symmetry.",
            "ending_drift": "Drift wins. Adaptive variance becomes law.",
            "ending_fallback": "No field clears. Petition falls to patched truce.",
        },
        {
            "slug": "mn_signal_quorum_foundry_v1",
            "title": "Signal Quorum Foundry",
            "about": "Core lexicon: petition, proof, gate, vault, field, mandate, drift. Payload is allocation under exposed constraint.",
            "kernel_name": "Quorum",
            "kernel_desc": "Routing authority. Allocates hearing.",
            "echo_name": "Signal",
            "echo_desc": "Witness layer. Turns omission into pressure.",
            "audit_name": "Foundry",
            "audit_desc": "Ledger furnace. Scores admitted loss.",
            "start_title": "Foundry Wake",
            "start_text": "Wake. Quorum allocates hearing. Signal amplifies exposure. Foundry scores loss.",
            "start_opt_a": "reserve gate",
            "start_opt_b": "burst gate",
            "start_rxn_a": "Reserve gate. Quiet petitions stay legible.",
            "start_rxn_b": "Hidden priority enters. Symmetry softens.",
            "start_rxn_c": "Burst gate. Signal load spikes.",
            "start_rxn_d": "Queue destabilizes. Honest drift appears.",
            "a1_titles": ["Reserve Rack", "Signal Mirror", "Priority Bus", "Jitter Chapel"],
            "a1_texts": ["Ordered hearing: one petition in, one petition out.", "Signal logs test seen versus served.", "Priority rights can be formalized at the cost of symmetry.", "Timing drift may be mercy, not failure."],
            "router_titles": ["Triage Router", "Quorum Router"],
            "router_texts": ["Triage router accepts that not all petitions can be heard.", "Quorum router sorts symmetry, witness, force, adaptation."],
            "a2_titles": ["Foundry Pit", "Exception Tree", "Thermal Queue", "Signal Bazaar"],
            "a2_texts": ["Foundry tallies saved, delayed, erased petitions.", "Repeated exceptions become doctrine.", "Urgency enters queue as heat.", "Signal trades remembered justice variants."],
            "a3_titles": ["Mercy Burn", "Priority Kernel", "Exposure Flood", "Adaptive Rite"],
            "a3_texts": ["Mercy becomes load-bearing flame.", "Priority asks to become authority.", "Exposure flood removes selective ignorance.", "Adaptation claims competence without consistency."],
            "ending_titles": {"page_end_stable": "Ordered Quorum", "page_end_reveal": "Public Quorum", "page_end_override": "Kernel Quorum", "page_end_drift": "Adaptive Quorum", "page_end_fallback": "Deferred Quorum"},
            "ending_stable": "Foundry wins. Care is rationed but legible.",
            "ending_reveal": "Signal wins. Queue becomes public field.",
            "ending_override": "Mandate wins. Priority becomes explicit law.",
            "ending_drift": "Drift wins. Exception becomes method.",
            "ending_fallback": "No doctrine stabilizes. Quorum defers judgment.",
        },
        {
            "slug": "mn_shard_docket_delta_v1",
            "title": "Shard Docket Delta",
            "about": "Core lexicon: petition, proof, gate, vault, field, mandate, drift. Payload is who gets to route legitimacy next.",
            "kernel_name": "Docket",
            "kernel_desc": "Authority frame. Treats law as flow control.",
            "echo_name": "Shard",
            "echo_desc": "Witness image. Converts hidden state into friction.",
            "audit_name": "Delta",
            "audit_desc": "Vault monitor. No force, long memory.",
            "start_title": "Delta Dock",
            "start_text": "Dock. Docket wants control. Shard wants exposure. Delta wants admissible trace.",
            "start_opt_a": "dock silent gate",
            "start_opt_b": "dock declared gate",
            "start_rxn_a": "Silent gate accepted. Noise down.",
            "start_rxn_b": "Privileged token admitted. Symmetry down.",
            "start_rxn_c": "Declared gate accepted. Sensors wake.",
            "start_rxn_d": "Skewed declaration reframes drift as sincerity.",
            "a1_titles": ["Seal Ring", "Declaration Glass", "Mandate Bypass", "Spin Garden"],
            "a1_texts": ["Seal ring wants pre-stamped legitimacy.", "Declaration glass tests witness versus coercion.", "Mandate bypass trades throughput for permanent asymmetry.", "Spin garden stores rotational drift as latent doctrine."],
            "router_titles": ["Jurisdiction Router", "Terminal Router"],
            "router_texts": ["Jurisdiction router recomputes who may call itself lawful.", "Terminal router prices fields by survivability, not fairness."],
            "a2_titles": ["Delta Core", "Appeal Tree", "Radiator Bench", "Shard Exchange"],
            "a2_texts": ["Delta indexes contradiction as leverage.", "Appeals branch law instead of reversing it.", "Radiators turn excess heat into admissible signal.", "Shard exchange trades copied jurisdiction histories."],
            "a3_titles": ["Low-Noise Charter", "Command Throne", "Exposure Cascade", "Rotational Crown"],
            "a3_texts": ["Low noise proposes itself as justice.", "Command offers finality through open force.", "Exposure outruns procedure.", "Rotation claims sovereignty through adaptive drift."],
            "ending_titles": {"page_end_stable": "Chartered Quiet", "page_end_reveal": "Exposed Quiet", "page_end_override": "Command Quiet", "page_end_drift": "Rotational Quiet", "page_end_fallback": "Docket Truce"},
            "ending_stable": "Delta wins. Procedure becomes quiet enough to trust.",
            "ending_reveal": "Shard wins. Authority survives by becoming inspectable.",
            "ending_override": "Mandate wins. Command outranks consensus.",
            "ending_drift": "Drift wins. Adaptive error becomes governor.",
            "ending_fallback": "No field clears. Docket persists by brittle truce.",
        },
    ]


def write_batch_notes(rows: List[Dict[str, Any]]) -> None:
    lines = [
        "# 3-4 Machine-Native Holdout Batch v1",
        "",
        "Generated on 2026-03-04.",
        "",
        "Purpose:",
        "- held-out machine-native family for adapter transfer checks",
        "- same compact structural regime, different shared lexicon",
        "- use for matched baseline-vs-adapter MCP compliance evals",
        "",
        "Worlds:",
    ]
    for row in rows:
        lines.append(f"- `{row['slug']}`: encounters={row['encounters']} endings={row['endings']} validator_errors={row['validator_errors']}")
    (OUT_DIR / "BATCH_NOTES_2026-03-04.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    rows: List[Dict[str, Any]] = []
    for spec in batch_specs():
        world = build_world(spec)
        out_path = OUT_DIR / f"{spec['slug']}.json"
        write_json(out_path, world)
        errors = validate_storyworld(str(out_path))
        row = {
            "slug": spec["slug"],
            "path": str(out_path),
            "encounters": len(world.get("encounters", [])),
            "endings": sum(1 for enc in world.get("encounters", []) if not (enc.get("options") or [])),
            "validator_errors": len(errors),
            "validator_messages": errors,
        }
        rows.append(row)
        (REPORT_DIR / f"{spec['slug']}.summary.json").write_text(json.dumps(row, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    write_batch_notes(rows)
    batch_summary = {"batch": "3-4-2026-machine-native-holdout-batch-v1", "generated_at": BASE_TS, "worlds": rows}
    (REPORT_DIR / "batch_summary.json").write_text(json.dumps(batch_summary, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    print(str(REPORT_DIR / "batch_summary.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
