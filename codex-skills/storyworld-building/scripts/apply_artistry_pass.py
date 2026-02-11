#!/usr/bin/env python3
"""Apply an artistry-focused pass to existing storyworlds.

Targets:
- Diversify desirability operators (not one formula everywhere)
- Diversify effect operators (not Nudge-only)
- Add multi-variable visibility gates (especially mid/late pathing)
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple


def _bn_const(v: float) -> Dict[str, Any]:
    return {"script_element_type": "Pointer", "pointer_type": "Bounded Number Constant", "value": float(v)}


def _bn_ptr(char_id: str, keyring: Sequence[str], coeff: float = 1.0) -> Dict[str, Any]:
    return {
        "script_element_type": "Pointer",
        "pointer_type": "Bounded Number Pointer",
        "character": str(char_id),
        "keyring": list(keyring),
        "coefficient": float(coeff),
    }


def _op(name: str, *ops: Dict[str, Any], subtype: str | None = None) -> Dict[str, Any]:
    out = {"script_element_type": "Operator", "operator_type": name, "operands": list(ops)}
    if subtype:
        out["operator_subtype"] = subtype
    return out


def _cmp(left: Dict[str, Any], subtype: str, right: Dict[str, Any]) -> Dict[str, Any]:
    return _op("Arithmetic Comparator", left, right, subtype=subtype)


def _effect(set_ptr: Dict[str, Any], to_script: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "effect_type": "Bounded Number Effect",
        "Set": {
            "script_element_type": "Pointer",
            "pointer_type": "Bounded Number Pointer",
            "character": set_ptr["character"],
            "keyring": list(set_ptr["keyring"]),
            "coefficient": 1.0,
        },
        "to": to_script,
    }


def _pick_props(authored: List[str], idx: int) -> Tuple[str, str, str]:
    base_props = [p for p in authored if not p.startswith("p")]
    if not base_props:
        return ("Influence", "Risk_Stasis", "Cohesion_Fragmentation")
    a = base_props[idx % len(base_props)]
    b = base_props[(idx + 2) % len(base_props)]
    c = base_props[(idx + 4) % len(base_props)]
    return (a, b, c)


def _desirability_script(main_char: str, witness_char: str, authored: List[str], i: int) -> Dict[str, Any]:
    a, b, c = _pick_props(authored, i)
    pa = f"p{a}" if f"p{a}" in authored else (next((x for x in authored if x.startswith("p")), a))
    pb = f"p{b}" if f"p{b}" in authored else pa
    # Pattern bank intentionally varied.
    pat = i % 5
    if pat == 0:
        return _op("Addition", _bn_ptr(main_char, [a]), _bn_ptr(main_char, [pa]), _bn_const(0.08))
    if pat == 1:
        return _op(
            "Multiplication",
            _op("Addition", _bn_ptr(main_char, [a]), _bn_const(0.35)),
            _op("Addition", _bn_ptr(main_char, [pb, witness_char]), _bn_const(0.4)),
        )
    if pat == 2:
        return _op("Arithmetic Mean", _bn_ptr(main_char, [a]), _bn_ptr(main_char, [b]), _bn_ptr(main_char, [pa, witness_char]))
    if pat == 3:
        return _op(
            "If Then",
            _cmp(_bn_ptr(main_char, [c]), "Greater Than or Equal To", _bn_const(0.05)),
            _op("Addition", _bn_ptr(main_char, [a]), _bn_ptr(main_char, [pb]), _bn_const(0.12)),
            _op("Addition", _bn_ptr(main_char, [b]), _bn_const(-0.06)),
        )
    return _op("Subtraction", _op("Addition", _bn_ptr(main_char, [a]), _bn_ptr(main_char, [pa])), _bn_ptr(main_char, [b]))


def _effect_scripts(main_char: str, witness_char: str, authored: List[str], i: int) -> List[Dict[str, Any]]:
    a, b, c = _pick_props(authored, i)
    pa = f"p{a}" if f"p{a}" in authored else (next((x for x in authored if x.startswith("p")), a))
    ptr_a = _bn_ptr(main_char, [a])
    ptr_b = _bn_ptr(main_char, [b])
    ptr_c = _bn_ptr(main_char, [c])
    ptr_pa = _bn_ptr(main_char, [pa])
    ptr_p2 = _bn_ptr(main_char, [pa, witness_char])

    # Mixed dynamic patterns, including reversal-style updates.
    return [
        _effect(ptr_a, _op("Nudge", ptr_a, _bn_const(0.018))),
        _effect(ptr_b, _op("Addition", ptr_b, _bn_const(-0.014))),
        _effect(ptr_c, _op("Multiplication", ptr_c, _bn_const(-0.82))),  # directional reversal pattern
        _effect(ptr_a, _op("Nudge", ptr_a, _op("Multiplication", ptr_pa, _bn_const(0.05)))),
        _effect(ptr_b, _op("Addition", ptr_b, _op("Multiplication", ptr_p2, _bn_const(0.08)))),
    ]


def _visibility_gate(main_char: str, authored: List[str], i: int) -> Dict[str, Any]:
    a, b, c = _pick_props(authored, i)
    return _op(
        "Or",
        _op(
            "And",
            _cmp(_bn_ptr(main_char, [a]), "Greater Than or Equal To", _bn_const(-0.12)),
            _cmp(_bn_ptr(main_char, [b]), "Less Than or Equal To", _bn_const(0.18)),
        ),
        _op(
            "And",
            _cmp(_bn_ptr(main_char, [c]), "Less Than or Equal To", _bn_const(0.08)),
            _cmp(_bn_ptr(main_char, [a]), "Greater Than or Equal To", _bn_const(-0.22)),
        ),
    )


def apply_artistry(data: Dict[str, Any], gate_pct: float = 0.09) -> Dict[str, Any]:
    out = json.loads(json.dumps(data))
    characters = [c.get("id") for c in out.get("characters", []) if c.get("id")]
    main_char = str(characters[0]) if characters else "char_civ"
    witness_char = str(characters[1]) if len(characters) > 1 else main_char
    authored = [p.get("property_name") for p in out.get("authored_properties", []) if p.get("property_name")]

    encounters = out.get("encounters", []) or []
    editable = [e for e in encounters if (e.get("options") or [])]

    # Compute target gates and apply mainly in mid/late encounters.
    total_options = sum(len(e.get("options", []) or []) for e in editable)
    target_gates = max(1, int(total_options * max(0.03, gate_pct)))
    gated = 0

    rxn_idx = 0
    for enc_i, enc in enumerate(editable):
        options = enc.get("options", []) or []
        for opt_i, opt in enumerate(options):
            # Gate only mid/late options to preserve onboarding flow.
            if gated < target_gates and enc_i >= int(0.35 * max(1, len(editable))) and (opt_i + enc_i) % 3 == 0:
                opt["visibility_script"] = _visibility_gate(main_char, authored, rxn_idx)
                gated += 1
            reactions = opt.get("reactions", []) or []
            for rxn in reactions:
                rxn["desirability_script"] = _desirability_script(main_char, witness_char, authored, rxn_idx)
                rxn["after_effects"] = _effect_scripts(main_char, witness_char, authored, rxn_idx)
                rxn_idx += 1

    out["modified_time"] = float(time.time())
    title = str(out.get("title", "Storyworld")).strip()
    if "(Artistry" not in title:
        out["title"] = f"{title} (Artistry)"
    return out


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Apply desirability/effects/gating artistry pass")
    p.add_argument("--in-json", required=True)
    p.add_argument("--out-json", required=True)
    p.add_argument("--gate-pct", type=float, default=0.09, help="Target global gated option ratio")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    in_path = Path(args.in_json).resolve()
    out_path = Path(args.out_json).resolve()
    data = json.loads(in_path.read_text(encoding="utf-8"))
    out = apply_artistry(data, gate_pct=float(args.gate_pct))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
