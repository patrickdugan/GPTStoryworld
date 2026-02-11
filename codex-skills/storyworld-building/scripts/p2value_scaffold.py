"""
P2Value scaffold helper.

Adds optional p2{Property} entries to bnumber_properties and can inject
second-order pValue pointers into desirability scripts for reactions with effects.

Usage:
  python p2value_scaffold.py in.json out.json
"""
import json
import sys


def const(value: float):
    return {
        "pointer_type": "Bounded Number Constant",
        "script_element_type": "Pointer",
        "value": value,
    }


def bptr(char_id: str, keyring):
    return {
        "pointer_type": "Bounded Number Pointer",
        "script_element_type": "Pointer",
        "character": char_id,
        "keyring": keyring,
        "coefficient": 1.0,
    }


def main(inp: str, outp: str) -> None:
    data = json.load(open(inp, encoding="utf-8"))

    props = [p["id"] for p in data.get("authored_properties", []) if p.get("id")]
    characters = [c.get("id") for c in data.get("characters", []) if c.get("id")]

    # Optional storage scaffolding for tooling
    for ch in data.get("characters", []):
        bprops = ch.get("bnumber_properties", {})
        for pid in props:
            p2key = f"p2{pid}"
            if p2key not in bprops:
                bprops[p2key] = {}
        ch["bnumber_properties"] = bprops

    # Inject a P2Value term in desirability for reactions with effects
    for enc in data.get("encounters", []):
        for opt in enc.get("options", []) or []:
            for rxn in opt.get("reactions", []) or []:
                effects = rxn.get("after_effects", []) or []
                affected = []
                for eff in effects:
                    if eff.get("effect_type") != "Bounded Number Effect":
                        continue
                    ptr = eff.get("Set", {})
                    char = ptr.get("character")
                    keyring = ptr.get("keyring") or []
                    if char and keyring:
                        affected.append((char, keyring[0]))
                if not affected:
                    continue
                if len(characters) < 2:
                    continue
                actor, prop = affected[0]
                perceiver = characters[0]
                witness = characters[1] if characters[1] != perceiver else characters[0]
                base = rxn.get("desirability_script") or const(0.0)
                rxn["desirability_script"] = {
                    "operator_type": "Addition",
                    "script_element_type": "Operator",
                    "operands": [
                        base,
                        bptr(perceiver, [prop, witness, actor]),
                    ],
                }

    data["modified_time"] = float(data.get("modified_time", 0.0))
    json.dump(data, open(outp, "w", encoding="utf-8"), indent=2)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python p2value_scaffold.py in.json out.json")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
