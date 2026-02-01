"""
Set up spool-based encounter sequencing for SweepWeave storyworlds.
Replaces brute-force consequence chains with desirability-ordered selection.

Usage:
    python spool_sequencing.py storyworld.json

Changes:
    1. Sets all Age spools to starts_active: true
    2. Removes intra-age consequence links
    3. Sets desirability hierarchy: (21-age) + slot_offset
    4. Gates Counter-Archivist encounters on Grudge/Influence
    5. Ensures Thesis (slot 0) is always acceptable (guaranteed landing)

Slot ordering within each age:
    0 (Thesis):   base + 0.30  — plays first
    1 (Pressure): base + 0.25
    2 (Morph):    base + 0.20
    3 (Escape):   base + 0.15
    4 (CA):       base + 0.10  — gated on provocation
    5 (Relic):    base + 0.05  — plays last
"""
import json
import sys

SLOT_OFFSETS = [0.30, 0.25, 0.20, 0.15, 0.10, 0.05]

# CA gates: (min_age, max_age) -> (Grudge_threshold, Influence_threshold)
# CA appears if Grudge >= threshold OR Influence >= threshold
CA_GATES = {
    (1, 5):   (0.03, 0.15),
    (6, 10):  (0.05, 0.25),
    (11, 15): (0.04, 0.20),
    (16, 20): (0.03, 0.15),
}


def const(value):
    return {"pointer_type": "Bounded Number Constant", "script_element_type": "Pointer", "value": value}

def cmp(subtype, char, prop, val):
    return {
        "operator_type": "Arithmetic Comparator", "script_element_type": "Operator",
        "operator_subtype": subtype,
        "operands": [
            {"pointer_type": "Bounded Number Pointer", "script_element_type": "Pointer",
             "character": char, "keyring": [prop], "coefficient": 1.0},
            {"pointer_type": "Bounded Number Constant", "script_element_type": "Pointer", "value": val},
        ],
    }

def or_gate(*ops):
    return {"operator_type": "Or", "script_element_type": "Operator", "operands": list(ops)}


def apply_spool_sequencing(data):
    spool_map = {}
    age_spools = {}
    for sp in data.get("spools", []):
        for eid in sp.get("encounters", []):
            spool_map[eid] = sp["spool_name"]
        if sp["spool_name"].startswith("Age "):
            age_spools[sp["spool_name"]] = sp["encounters"]

    enc_lookup = {e["id"]: e for e in data["encounters"]}

    # 1. Activate all Age spools
    for sp in data["spools"]:
        if sp["spool_name"].startswith("Age "):
            sp["starts_active"] = True

    # 2. Remove intra-age consequence links
    links_removed = 0
    for spool_name, encounter_ids in age_spools.items():
        for eid in encounter_ids:
            enc = enc_lookup[eid]
            for opt in enc.get("options", []):
                for rxn in opt.get("reactions", []):
                    cid = rxn.get("consequence_id", "")
                    if cid and cid != "" and cid != "wild":
                        rxn["consequence_id"] = ""
                        links_removed += 1

    # 3. Set desirability + 4. Gate CA encounters
    for spool_name, encounter_ids in sorted(age_spools.items()):
        age = int(spool_name.split(" ")[1])
        base = 21 - age

        for slot, eid in enumerate(encounter_ids):
            enc = enc_lookup[eid]
            offset = SLOT_OFFSETS[slot] if slot < len(SLOT_OFFSETS) else 0.0
            enc["desirability_script"] = const(base + offset)

            if slot == 0 or slot == 5:
                enc["acceptability_script"] = True
            elif slot == 4:
                for (lo, hi), (g_t, i_t) in CA_GATES.items():
                    if lo <= age <= hi:
                        enc["acceptability_script"] = or_gate(
                            cmp("Greater Than or Equal To", "char_counter_archivist", "Grudge", g_t),
                            cmp("Greater Than or Equal To", "char_counter_archivist", "Influence", i_t),
                        )
                        break

    return links_removed


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python spool_sequencing.py storyworld.json")
        sys.exit(1)

    with open(sys.argv[1], encoding="utf-8") as f:
        data = json.load(f)

    removed = apply_spool_sequencing(data)

    with open(sys.argv[1], "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Removed {removed} consequence links.")
    print("Set desirability hierarchy and CA gates.")
    print("All Age spools set to starts_active: true.")
