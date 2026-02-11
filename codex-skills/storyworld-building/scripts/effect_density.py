import json
import sys
from pathlib import Path

NEGATIVE_KEYWORDS = {"betray", "punish", "loss", "collapse", "exploit", "gap", "risk", "threat"}


def count_effects(reaction):
    after = reaction.get("after_effects", []) or []
    return len(after)


def has_negative_consequence(reaction):
    text = ""
    ts = reaction.get("text_script")
    if isinstance(ts, dict):
        text = ts.get("value", "") or ts.get("text", "") or ""
    if isinstance(ts, str):
        text = ts
    lowered = text.lower()
    if any(k in lowered for k in NEGATIVE_KEYWORDS):
        return True
    # Check numeric effects for negative deltas
    for eff in reaction.get("after_effects", []) or []:
        to = eff.get("to", {})
        operands = to.get("operands", []) if isinstance(to, dict) else []
        for op in operands:
            if isinstance(op, dict) and op.get("pointer_type") == "Bounded Number Constant":
                val = op.get("coefficient", op.get("value", 0))
                try:
                    if float(val) < 0:
                        return True
                except Exception:
                    pass
    return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python effect_density.py storyworld.json")
        return 1

    path = Path(sys.argv[1])
    data = json.loads(path.read_text(encoding="utf-8"))

    encounters = data.get("encounters", []) or []
    total_reactions = 0
    total_effects = 0
    negative_reactions = 0

    early_encounters = [e for e in encounters if (e.get("earliest_turn", 0) <= 3)]

    for enc in early_encounters:
        for opt in enc.get("options", []) or []:
            reactions = opt.get("reactions", []) or []
            for rxn in reactions:
                total_reactions += 1
                total_effects += count_effects(rxn)
                if has_negative_consequence(rxn):
                    negative_reactions += 1

    density = (total_effects / total_reactions) if total_reactions else 0
    print(json.dumps({
        "file": str(path),
        "early_turn_reactions": total_reactions,
        "early_turn_effects": total_effects,
        "effect_density": round(density, 3),
        "negative_reaction_ratio": round((negative_reactions / total_reactions) if total_reactions else 0, 3),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
