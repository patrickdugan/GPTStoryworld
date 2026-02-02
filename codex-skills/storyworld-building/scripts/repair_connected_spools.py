import json, sys
from collections import OrderedDict

def load(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f, object_pairs_hook=OrderedDict)

def save(p, d):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python tools/repair_connected_spools.py world.json")
        sys.exit(1)

    path = sys.argv[1]
    world = load(path)

    # Map spool_name → id
    spool_id = {
        s["spool_name"]: s["id"]
        for s in world.get("spools", [])
        if isinstance(s, dict) and "spool_name" in s and "id" in s
    }

    fixed = 0
    for e in world.get("encounters", []):
        title = e.get("title", "")
        if not title.startswith("Age "):
            continue
        try:
            n = int(title.split("Age ")[1].split(":")[0])
        except Exception:
            continue

        key = f"Age {n}"
        sid = spool_id.get(key)
        if sid:
            e["connected_spools"] = [sid]
            fixed += 1

    save(path, world)
    print(f"Repaired connected_spools on {fixed} encounters")
