import json
import sys

# Slot offsets are now tiny enough to stay within the 0.1 'Age' bracket
SLOT_OFFSETS = [0.030, 0.025, 0.020, 0.015, 0.010, 0.005]

# CA gates: (min_age, max_age) -> (Grudge_threshold, Influence_threshold)
CA_GATES = {
    (1, 5):   (0.03, 0.15),
    (6, 10):  (0.05, 0.25),
    (11, 15): (0.07, 0.35),
    (16, 20): (0.10, 0.45),
}

def const(val):
    # HARD CLAMP: Ensure no floating point noise pushes us past 1.0 or -1.0
    clamped_val = max(-1.0, min(1.0, round(val, 4)))
    return {
        "pointer_type": "Bounded Number Constant",
        "script_element_type": "Pointer",
        "value": clamped_val
    }

def apply_spool_sequencing(data):
    enc_lookup = {e["id"]: e for e in data.get("encounters", [])}
    age_spools = {}
    
    for s in data.get("spools", []):
        s["starts_active"] = True
        name = s["spool_name"]
        if name.startswith("Age "):
            age_spools[name] = s.get("encounters", [])

    for spool_name, encounter_ids in sorted(age_spools.items()):
        try:
            age = int(spool_name.split(" ")[1])
        except (IndexError, ValueError):
            continue
            
        # THE BOUNDED HEURISTIC: 
        # Age 1 starts at 0.9, Age 20 ends at -1.0
        # Each age gets a 0.1 slice of the -1 to 1 manifold
        base = 1.0 - (age * 0.1) 

        for slot, eid in enumerate(encounter_ids):
            if eid not in enc_lookup: continue
            enc = enc_lookup[eid]
            offset = SLOT_OFFSETS[slot] if slot < len(SLOT_OFFSETS) else 0.0
            
            # This is now 100% compliant with the [-1, 1] Bounded Law
            enc["desirability_script"] = const(base + offset)

            if slot == 0 or slot == 5:
                enc["acceptability_script"] = True
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(1)
    with open(sys.argv[1], encoding="utf-8") as f:
        data = json.load(f)
    apply_spool_sequencing(data)
    with open(sys.argv[1], "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)