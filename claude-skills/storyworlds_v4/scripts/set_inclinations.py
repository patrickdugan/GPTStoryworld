"""
Set inclination formulas (desirability_script) and late-game gating
(acceptability_script) on SweepWeave storyworld encounters.

Usage:
    python set_inclinations.py storyworld.json

Sets:
    - Thesis/Pressure/Morph/Escape: desirability = 0.3 * |cumulative_prop|
    - Counter-Archivist: desirability = 0.4 * Influence
    - Relic: desirability = 0.5 (constant)
    - Late-game gates (Ages 14-20): |cumulative_prop| >= threshold
"""
import json
import sys
from sweepweave_helpers import (
    inclination_attractor, inclination_ca, inclination_constant,
    make_abs_threshold_gate, get_primary_effect, build_spool_map,
    get_encounter_slot, load_storyworld, save_storyworld,
)

GATE_THRESHOLDS = {
    14: 0.01, 15: 0.01,
    16: 0.02, 17: 0.02,
    18: 0.03, 19: 0.03,
    20: 0.04,
}


def set_inclinations(data):
    spool_map = build_spool_map(data)
    inclination_count = 0
    gate_count = 0

    for enc in data["encounters"]:
        eid = enc["id"]
        spool = spool_map.get(eid, "")
        if not spool.startswith("Age "):
            continue

        age = int(spool.split(" ")[1])
        slot = get_encounter_slot(data, eid, spool)
        if slot is None:
            continue

        prop, delta = get_primary_effect(enc)

        # Set desirability
        if slot == 5:
            enc["desirability_script"] = inclination_constant(0.5)
            inclination_count += 1
        elif slot == 4:
            enc["desirability_script"] = inclination_ca(0.4)
            inclination_count += 1
        elif prop is not None:
            enc["desirability_script"] = inclination_attractor("p" + prop, 0.3)
            inclination_count += 1

        # Set late-game gates
        if age >= 14 and slot < 4 and prop is not None:
            threshold = GATE_THRESHOLDS[age]
            enc["acceptability_script"] = make_abs_threshold_gate("char_civ", "p" + prop, threshold)
            gate_count += 1

    return inclination_count, gate_count


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python set_inclinations.py storyworld.json")
        sys.exit(1)

    data = load_storyworld(sys.argv[1])
    inc, gates = set_inclinations(data)
    save_storyworld(data, sys.argv[1])
    print(f"Set {inc} inclination formulas, {gates} late-game gates.")
