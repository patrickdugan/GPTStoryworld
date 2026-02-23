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
import math
import re
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

    # Effect policy:
    # - Nudge is dominant baseline (slow walk toward outcomes).
    # - Blend is sparse and relationship-mediated.
    # - Invert is rare (act-level dramatic reversal).
    # - Arithmetic Mean is primarily for desirability scripts, not frequent in effects.
    nudge_mag = 0.10 if (i % 30 == 0) else 0.03
    effects = [
        _effect(ptr_a, _op("Nudge", ptr_a, _bn_const(nudge_mag))),
        _effect(ptr_b, _op("Nudge", ptr_b, _bn_const(0.03))),
        _effect(ptr_c, _op("Nudge", ptr_c, _op("Multiplication", ptr_pa, _bn_const(0.03)))),
    ]
    m = i % 100
    avg_slots = {0, 50}  # 2% of reactions -> ~0.5% effects
    invert_slots = {5, 15, 25, 35, 45, 55, 65, 75, 85, 95}  # 10% of reactions -> ~2.5% effects
    blend_slots = {
        1, 2, 6, 7, 11, 12, 16, 17, 21, 22, 26, 27, 31, 32,
        36, 37, 41, 42, 46, 47, 51, 52, 56, 57, 61, 62, 66, 67,
    }  # 28% of reactions -> ~7% effects
    if m in avg_slots:
        effects.append(_effect(ptr_a, _op("Arithmetic Mean", ptr_a, ptr_pa, ptr_p2)))  # rare avg in effects
    elif m in invert_slots:
        effects.append(_effect(ptr_c, _op("Multiplication", ptr_c, _bn_const(-0.88))))  # dramatic inversion
    elif m in blend_slots:
        effects.append(_effect(ptr_b, _op("Addition", ptr_b, _op("Multiplication", ptr_p2, _bn_const(0.10)))))  # blend
    else:
        effects.append(_effect(ptr_a, _op("Nudge", ptr_a, _bn_const(0.03))))
    return effects


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


def _extract_theme_terms(data: Dict[str, Any]) -> List[str]:
    raw = []
    raw.append(str(data.get("title", "") or ""))
    about = data.get("about_text")
    if isinstance(about, dict) and about.get("pointer_type") == "String Constant":
        raw.append(str(about.get("value", "") or ""))
    text = " ".join(raw).lower()
    toks = re.findall(r"[a-zA-Z][a-zA-Z0-9'-]{2,}", text)
    stop = {
        "the", "and", "with", "that", "this", "from", "into", "over", "under", "their", "your",
        "about", "story", "world", "meets", "while", "before", "after", "between", "across",
    }
    uniq = []
    for t in toks:
        if t in stop:
            continue
        if t not in uniq:
            uniq.append(t)
    return uniq[:12] if uniq else ["timeline", "honor", "betrayal", "promise"]


def _ensure_text(script: Any) -> Dict[str, Any]:
    if isinstance(script, dict) and script.get("pointer_type") == "String Constant":
        return script
    return {"script_element_type": "Pointer", "pointer_type": "String Constant", "value": ""}


def apply_artistry(data: Dict[str, Any], gate_pct: float = 0.09) -> Dict[str, Any]:
    out = json.loads(json.dumps(data))
    characters = [c.get("id") for c in out.get("characters", []) if c.get("id")]
    main_char = str(characters[0]) if characters else "char_civ"
    witness_char = str(characters[1]) if len(characters) > 1 else main_char
    authored = [p.get("property_name") for p in out.get("authored_properties", []) if p.get("property_name")]
    theme_terms = _extract_theme_terms(out)

    encounters = out.get("encounters", []) or []
    editable = [e for e in encounters if (e.get("options") or [])]

    # Ensure global encounter text uniqueness (including endings/non-option encounters).
    for enc_i, enc in enumerate(encounters):
        enc_text = _ensure_text(enc.get("text_script"))
        t1 = theme_terms[enc_i % len(theme_terms)]
        t2 = theme_terms[(enc_i + 3) % len(theme_terms)]
        enc_text["value"] = (
            f"{enc_text.get('value','').strip()} Scene marker {enc.get('id','enc')} binds {t1} to {t2}, "
            f"recording a unique causal trace for downstream branches."
        ).strip()
        enc["text_script"] = enc_text

    # Compute act-staged targets for visibility gates.
    act_targets = {3: 0.05, 4: 0.10, 5: max(0.20, gate_pct)}
    act_totals = {3: 0, 4: 0, 5: 0}
    n_editable = max(1, len(editable))
    for enc_i, enc in enumerate(editable):
        act = min(5, (enc_i * 5) // n_editable + 1)
        if act in act_totals:
            act_totals[act] += len(enc.get("options", []) or [])
    act_gate_caps = {a: max(1, int(math.ceil(act_totals[a] * pct))) for a, pct in act_targets.items() if act_totals[a] > 0}
    act_gated = {3: 0, 4: 0, 5: 0}

    rxn_idx = 0
    for enc_i, enc in enumerate(editable):
        a, b, _c = _pick_props(authored, enc_i)
        enc_text = _ensure_text(enc.get("text_script"))
        t1 = theme_terms[enc_i % len(theme_terms)]
        t2 = theme_terms[(enc_i + 3) % len(theme_terms)]
        t3 = theme_terms[(enc_i + 6) % len(theme_terms)]
        enc_text["value"] = (
            f"{enc_text.get('value','').strip()} In encounter {enc.get('id','enc')}, the conflict over {t1} and {t2} "
            f"forces a public wager on {t3}, with reputations and timelines now mutually exposed."
        ).strip()
        enc["text_script"] = enc_text
        # Keep acceptance mostly permissive but variable-aware (non-constant).
        enc["acceptability_script"] = _cmp(_bn_ptr(main_char, [a]), "Greater Than or Equal To", _bn_const(-0.95))
        enc["desirability_script"] = _op("Addition", _bn_ptr(main_char, [a]), _op("Multiplication", _bn_ptr(main_char, [b]), _bn_const(0.4)))
        options = enc.get("options", []) or []
        for opt_i, opt in enumerate(options):
            # Performability also variable-aware while remaining permissive.
            opt["performability_script"] = _cmp(_bn_ptr(main_char, [a]), "Greater Than or Equal To", _bn_const(-0.98))
            act = min(5, (enc_i * 5) // n_editable + 1)
            # Explicit stage targets: Act III 5%, Act IV 10%, Act V 20%+.
            if act in act_gate_caps and act_gated[act] < act_gate_caps[act] and (opt_i + enc_i) % 2 == 0:
                opt["visibility_script"] = _visibility_gate(main_char, authored, rxn_idx)
                act_gated[act] += 1
            elif act in (3, 4, 5):
                opt["visibility_script"] = True
            reactions = opt.get("reactions", []) or []
            for rxn in reactions:
                rxn["desirability_script"] = _desirability_script(main_char, witness_char, authored, rxn_idx)
                rxn["after_effects"] = _effect_scripts(main_char, witness_char, authored, rxn_idx)
                rtext = _ensure_text(rxn.get("text_script"))
                u = theme_terms[(rxn_idx + 1) % len(theme_terms)]
                v = theme_terms[(rxn_idx + 4) % len(theme_terms)]
                rtext["value"] = (
                    f"Response trace {rxn_idx:05d} ({rxn.get('id','rxn')}) reframes {u} against {v}: the speaker pivots tone, telegraphs a new alliance geometry, "
                    f"and leaves a traceable contradiction that can be exploited in later scenes."
                )
                rxn["text_script"] = rtext
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
