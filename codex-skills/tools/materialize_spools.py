import json, sys, time, secrets
from collections import OrderedDict

def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f, object_pairs_hook=OrderedDict)

def save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def now_ts():
    return float(time.time())

def new_hex_id(existing: set) -> str:
    while True:
        h = secrets.token_hex(4)
        if h not in existing:
            return h

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python tools/materialize_spools.py in.json out.json")
        sys.exit(1)

    inp, outp = sys.argv[1], sys.argv[2]
    world = load(inp)

    encounters = world.get("encounters", [])
    spools = world.get("spools", [])
    if not isinstance(spools, list):
        spools = []

    # Collect referenced Age numbers from encounter titles
    referenced_ages = set()
    for e in encounters:
        title = e.get("title", "")
        if title.startswith("Age "):
            try:
                n = int(title.split("Age ")[1].split(":")[0])
                referenced_ages.add(n)
            except Exception:
                pass

    # Index existing spools
    by_name = {}
    used_ids = set()
    max_ci = -1

    for s in spools:
        if not isinstance(s, dict):
            continue
        sid = s.get("id")
        if isinstance(sid, str):
            used_ids.add(sid)
        ci = s.get("creation_index")
        if isinstance(ci, int) and ci > max_ci:
            max_ci = ci
        name = s.get("spool_name")
        if isinstance(name, str):
            by_name[name] = s

    # Materialize missing Age spools
    for age in sorted(referenced_ages):
        name = f"Age {age}"
        if name in by_name:
            continue

        max_ci += 1
        ts = now_ts()

        s = OrderedDict()
        s["creation_index"] = max_ci
        s["creation_time"] = ts
        s["encounters"] = []
        s["id"] = new_hex_id(used_ids)
        used_ids.add(s["id"])
        s["modified_time"] = ts
        s["spool_name"] = name
        s["starts_active"] = False

        spools.append(s)
        by_name[name] = s

    # Exactly one spool starts active: the first (lowest creation_index)
    first = min(
        (s for s in spools if isinstance(s.get("creation_index"), int)),
        key=lambda s: s["creation_index"],
        default=None
    )
    for s in spools:
        s["starts_active"] = (s is first)

    world["spools"] = spools
    save(outp, world)
    print(f"Materialized {len(referenced_ages)} Age spools → {outp}")
