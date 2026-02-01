"""
Structural enrichment for SweepWeave storyworld encounters.
Adds moderate options, backfire reactions, CA reversals, spectacular successes,
and wires effects with calibrated magnitudes.

Usage:
    python enrich_encounters.py storyworld.json [--start-age 1] [--end-age 20]

Requires encounters to already have:
    - At least 2 options (bold + deceptive) with 1 reaction each
    - Primary effects wired on first option's first reaction
    - Consequence chain (consequence_id) linking encounters

Adds:
    - 3rd moderate option on slots 0-3 (Thesis/Pressure/Morph/Escape)
    - Backfire reactions on bold/deceptive options (gated on cross-axis overextension)
    - Spectacular success reactions on Thesis/Escape slots
    - CA reversal reactions on Counter-Archivist encounters
    - Calibrated effect magnitudes (bold 0.045, moderate 0.024, etc.)
"""
import json
import sys
from sweepweave_helpers import (
    make_effect, make_dual_effect, make_option, make_reaction,
    make_visibility_gate, get_primary_effect, build_spool_map,
    get_encounter_slot, get_backfire_gate, EffectMagnitudes as EM,
    load_storyworld, save_storyworld, const,
)


def enrich_age_encounters(data, start_age=1, end_age=20):
    """Add structural enrichment to encounters in the specified age range."""
    spool_map = build_spool_map(data)
    enc_lookup = {e["id"]: e for e in data["encounters"]}

    stats = {"moderate_added": 0, "backfire_added": 0, "spectacular_added": 0, "ca_reversal_added": 0}

    for enc in data["encounters"]:
        eid = enc["id"]
        spool = spool_map.get(eid, "")
        if not spool.startswith("Age "):
            continue
        age = int(spool.split(" ")[1])
        if age < start_age or age > end_age:
            continue

        slot = get_encounter_slot(data, eid, spool)
        if slot is None:
            continue

        prop, delta = get_primary_effect(enc)

        # Get the consequence_id from existing reactions
        consequence_id = ""
        for opt in enc.get("options", []):
            for rxn in opt.get("reactions", []):
                if rxn.get("consequence_id"):
                    consequence_id = rxn["consequence_id"]
                    break
            if consequence_id:
                break

        if slot <= 3 and prop is not None:
            # ── Add moderate 3rd option if only 2 exist ──
            if len(enc["options"]) == 2:
                mod_opt = make_option(eid, 2, "[Moderate approach — placeholder text]")
                mod_effects = make_dual_effect("char_civ", prop,
                                               EM.MODERATE_BASE if delta > 0 else -EM.MODERATE_BASE,
                                               EM.MODERATE_CUMULATIVE if delta > 0 else -EM.MODERATE_CUMULATIVE)
                mod_rxn = make_reaction(eid, 2, 0, "[Moderate outcome — placeholder]",
                                        consequence_id, mod_effects)
                mod_opt["reactions"].append(mod_rxn)
                enc["options"].append(mod_opt)
                stats["moderate_added"] += 1

            # ── Add backfire reactions ──
            backfire_gate = get_backfire_gate(prop)
            if backfire_gate:
                for opt_idx in range(min(2, len(enc["options"]))):
                    opt = enc["options"][opt_idx]
                    existing_rxn_count = len(opt.get("reactions", []))
                    if existing_rxn_count < 3:  # Don't add if already enriched
                        reverse_delta = EM.BACKFIRE_REVERSE if delta > 0 else -EM.BACKFIRE_REVERSE
                        bf_effects = [
                            make_effect("char_civ", prop, reverse_delta),
                            make_effect("char_counter_archivist", "Grudge", EM.BACKFIRE_GRUDGE),
                        ]
                        bf_rxn = make_reaction(eid, opt_idx, existing_rxn_count,
                                               "[Backfire — placeholder]",
                                               consequence_id, bf_effects, desirability=0.8)
                        bf_rxn["visibility_script"] = backfire_gate
                        opt["reactions"].append(bf_rxn)
                        stats["backfire_added"] += 1

            # ── Add spectacular success on Thesis (slot 0) and Escape (slot 3) ──
            if slot in (0, 3):
                opt = enc["options"][0]
                existing_rxn_count = len(opt.get("reactions", []))
                spec_delta = EM.SPECTACULAR_BASE if delta > 0 else -EM.SPECTACULAR_BASE
                spec_cum = EM.SPECTACULAR_CUMULATIVE if delta > 0 else -EM.SPECTACULAR_CUMULATIVE
                spec_effects = [
                    make_effect("char_civ", prop, spec_delta),
                    make_effect("char_civ", "p" + prop, spec_cum),
                    make_effect("char_counter_archivist", "Grudge", EM.SPECTACULAR_GRUDGE),
                ]
                spec_rxn = make_reaction(eid, 0, existing_rxn_count,
                                         "[Spectacular success — placeholder]",
                                         consequence_id, spec_effects, desirability=0.5)
                opt["reactions"].append(spec_rxn)
                stats["spectacular_added"] += 1

        elif slot == 4:
            # ── CA reversal reaction ──
            for opt_idx in range(len(enc["options"])):
                opt = enc["options"][opt_idx]
                existing_rxn_count = len(opt.get("reactions", []))
                if existing_rxn_count < 3:
                    ca_effects = [
                        make_effect("char_counter_archivist", "Countercraft", EM.CA_COUNTERCRAFT),
                    ]
                    ca_rxn = make_reaction(eid, opt_idx, existing_rxn_count,
                                           "[Counter-Archivist reversal — placeholder]",
                                           consequence_id, ca_effects, desirability=0.6)
                    opt["reactions"].append(ca_rxn)
                    stats["ca_reversal_added"] += 1

    return stats


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python enrich_encounters.py storyworld.json [--start-age N] [--end-age N]")
        sys.exit(1)

    path = sys.argv[1]
    start_age, end_age = 1, 20
    for i, arg in enumerate(sys.argv):
        if arg == "--start-age" and i + 1 < len(sys.argv):
            start_age = int(sys.argv[i + 1])
        if arg == "--end-age" and i + 1 < len(sys.argv):
            end_age = int(sys.argv[i + 1])

    data = load_storyworld(path)
    stats = enrich_age_encounters(data, start_age, end_age)
    save_storyworld(data, path)

    print(f"Enrichment complete (Ages {start_age}-{end_age}):")
    for k, v in stats.items():
        print(f"  {k}: {v}")
