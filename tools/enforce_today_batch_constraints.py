#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import math
from pathlib import Path
from typing import Any, Dict, List, Tuple


ROOT = Path(__file__).resolve().parents[1]
BATCH_DIR = ROOT / "storyworlds" / "2-23-2026-batch"
REPORT_DIR = BATCH_DIR / "_reports"


def _bn_const(v: float) -> Dict[str, Any]:
    return {"script_element_type": "Pointer", "pointer_type": "Bounded Number Constant", "value": float(v)}


def _bn_ptr(char_id: str, keyring: List[str], coeff: float = 1.0) -> Dict[str, Any]:
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


def _collect_vars(node: Any, out: set[Tuple[str, str]]) -> None:
    if isinstance(node, dict):
        if node.get("pointer_type") == "Bounded Number Pointer":
            char = node.get("character")
            keyring = node.get("keyring") or []
            if char and keyring:
                out.add((str(char), str(keyring[0])))
        for v in node.values():
            _collect_vars(v, out)
    elif isinstance(node, list):
        for v in node:
            _collect_vars(v, out)


def _count_vars(node: Any) -> int:
    out: set[Tuple[str, str]] = set()
    _collect_vars(node, out)
    return len(out)


def _script_is_constant(script: Any) -> bool:
    if not isinstance(script, dict):
        return True
    if script.get("script_element_type") == "Pointer":
        return script.get("pointer_type") in ("Bounded Number Constant", "Boolean Constant", "String Constant")
    if script.get("script_element_type") == "Operator":
        return all(_script_is_constant(op) for op in (script.get("operands", []) or []))
    return False


def _pointer_count(node: Any) -> int:
    if isinstance(node, dict):
        c = 1 if node.get("pointer_type") == "Bounded Number Pointer" else 0
        for v in node.values():
            c += _pointer_count(v)
        return c
    if isinstance(node, list):
        return sum(_pointer_count(v) for v in node)
    return 0


def _has_negative_const(node: Any) -> bool:
    if isinstance(node, dict):
        if node.get("pointer_type") == "Bounded Number Constant":
            try:
                return float(node.get("value", 0.0)) < 0.0
            except Exception:
                return False
        return any(_has_negative_const(v) for v in node.values())
    if isinstance(node, list):
        return any(_has_negative_const(v) for v in node)
    return False


def _authored_props(data: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    authored = [str(p.get("property_name", "")) for p in (data.get("authored_properties", []) or []) if p.get("property_name")]
    base = [p for p in authored if not p.startswith("p")]
    pvals = [p for p in authored if p.startswith("p")]
    if not base:
        base = ["Influence", "Risk_Stasis", "Cohesion_Fragmentation"]
    return base, pvals


def _pick_props(base: List[str], idx: int) -> Tuple[str, str, str]:
    a = base[idx % len(base)]
    b = base[(idx + 2) % len(base)]
    c = base[(idx + 4) % len(base)]
    return a, b, c


def _ensure_secret_encounter(data: Dict[str, Any]) -> str:
    encounters = data.get("encounters", []) or []
    for e in encounters:
        if str(e.get("id", "")).startswith("page_secret_"):
            return str(e.get("id"))
    terminals = [e for e in encounters if not (e.get("options") or [])]
    template = copy.deepcopy(terminals[0]) if terminals else {"id": "page_end_fallback", "options": []}
    template["id"] = "page_secret_01"
    template["options"] = []
    template["text_script"] = {
        "script_element_type": "Pointer",
        "pointer_type": "String Constant",
        "value": "Secret ending: the concealed coalition resolves the final contradiction offstage.",
    }
    encounters.append(template)
    data["encounters"] = encounters
    return "page_secret_01"


def _ensure_five_act_spools(data: Dict[str, Any]) -> Dict[str, Any]:
    encounters = data.get("encounters", []) or []
    enc_ids = [str(e.get("id", "")) for e in encounters if e.get("id")]
    terminals = [str(e.get("id", "")) for e in encounters if e.get("id") and not (e.get("options") or [])]
    non_term = [eid for eid in enc_ids if eid not in set(terminals)]
    n = len(non_term)
    cuts = [int(n * i / 5) for i in range(6)]
    chunks = [non_term[cuts[i] : cuts[i + 1]] for i in range(5)]
    chunks[-1] = chunks[-1] + terminals
    ct = float(data.get("creation_time", 0.0))
    mt = float(data.get("modified_time", ct))
    new_spools: List[Dict[str, Any]] = []
    for i, chunk in enumerate(chunks, start=1):
        if not chunk:
            continue
        new_spools.append(
            {
                "creation_index": i - 1,
                "creation_time": ct,
                "id": f"spool_act_{i}",
                "modified_time": mt,
                "spool_name": f"Act {i}",
                "starts_active": i == 1,
                "encounters": chunk,
            }
        )
    old = [s for s in (data.get("spools", []) or []) if not str(s.get("id", "")).startswith("spool_act_")]
    if old:
        for s in old:
            s["starts_active"] = bool(s.get("starts_active", False)) and False
    data["spools"] = old + new_spools
    return data


def _act_option_refs(data: Dict[str, Any]) -> Dict[int, List[Tuple[Dict[str, Any], Dict[str, Any]]]]:
    enc_by_id = {str(e.get("id", "")): e for e in (data.get("encounters", []) or []) if e.get("id")}
    refs: Dict[int, List[Tuple[Dict[str, Any], Dict[str, Any]]]] = {3: [], 4: [], 5: []}
    for act in (3, 4, 5):
        sid = f"spool_act_{act}"
        spool = next((s for s in (data.get("spools", []) or []) if str(s.get("id", "")).lower() == sid), None)
        if not spool:
            continue
        for eid in spool.get("encounters", []) or []:
            enc = enc_by_id.get(str(eid))
            if not enc:
                continue
            for opt in enc.get("options", []) or []:
                refs[act].append((enc, opt))
    return refs


def _desirability_formula(cast_ids: List[str], base: List[str], pvals: List[str], idx: int) -> Dict[str, Any]:
    c0 = cast_ids[idx % len(cast_ids)]
    c1 = cast_ids[(idx + 1) % len(cast_ids)]
    a, b, _c = _pick_props(base, idx)
    pa = f"p{a}" if f"p{a}" in pvals else (pvals[0] if pvals else f"p{a}")
    return _op(
        "Addition",
        _op("Arithmetic Mean", _bn_ptr(c0, [a]), _bn_ptr(c1, [b]), _bn_ptr(c0, [pa, c1])),
        _op("Multiplication", _bn_ptr(c0, [b]), _bn_const(0.35)),
    )


def _effect_suite(cast_ids: List[str], base: List[str], pvals: List[str], idx: int) -> List[Dict[str, Any]]:
    c0 = cast_ids[idx % len(cast_ids)]
    c1 = cast_ids[(idx + 1) % len(cast_ids)]
    a, b, c = _pick_props(base, idx)
    pa = f"p{a}" if f"p{a}" in pvals else (pvals[0] if pvals else f"p{a}")
    ptr_a = _bn_ptr(c0, [a])
    ptr_b = _bn_ptr(c0, [b])
    ptr_c = _bn_ptr(c1, [c])
    ptr_p2 = _bn_ptr(c0, [pa, c1])
    # Operator policy for effects:
    # - Nudge dominates (slow metric-distance progression).
    # - Blend is sparse and relationship-based.
    # - Invert is rare dramatic reversal.
    # - Avg appears mainly in desirability, only rarely in effects.
    nudge_mag = 0.10 if (idx % 30 == 0) else 0.03
    effects = [
        _effect(ptr_a, _op("Nudge", ptr_a, _bn_const(nudge_mag))),
        _effect(ptr_b, _op("Nudge", ptr_b, _bn_const(0.03))),
        _effect(ptr_c, _op("Nudge", ptr_c, _op("Multiplication", ptr_p2, _bn_const(0.03)))),
    ]
    m = idx % 100
    avg_slots = {0, 50}  # 2% reactions -> ~0.5% effects
    invert_slots = {5, 15, 25, 35, 45, 55, 65, 75, 85, 95}  # 10% reactions -> ~2.5% effects
    blend_slots = {
        1, 2, 6, 7, 11, 12, 16, 17, 21, 22, 26, 27, 31, 32,
        36, 37, 41, 42, 46, 47, 51, 52, 56, 57, 61, 62, 66, 67,
    }  # 28% reactions -> ~7% effects
    if m in avg_slots:
        effects.append(_effect(ptr_a, _op("Arithmetic Mean", ptr_a, ptr_b, ptr_p2)))  # rare avg in effects
    elif m in invert_slots:
        effects.append(_effect(ptr_c, _op("Multiplication", ptr_c, _bn_const(-0.88))))  # dramatic reversal
    elif m in blend_slots:
        effects.append(_effect(ptr_b, _op("Addition", ptr_b, _op("Multiplication", ptr_p2, _bn_const(0.10)))))  # blend
    else:
        effects.append(_effect(ptr_a, _op("Nudge", ptr_a, _bn_const(0.03))))
    return effects


def _visibility_gate(cast_ids: List[str], base: List[str], idx: int) -> Dict[str, Any]:
    c0 = cast_ids[idx % len(cast_ids)]
    a, b, _c = _pick_props(base, idx)
    return _op(
        "And",
        _cmp(_bn_ptr(c0, [a]), "Greater Than or Equal To", _bn_const(-0.12)),
        _cmp(_bn_ptr(c0, [b]), "Less Than or Equal To", _bn_const(0.18)),
    )


def _enforce_world(data: Dict[str, Any]) -> Dict[str, Any]:
    cast_ids = [str(c.get("id", "")) for c in (data.get("characters", []) or []) if c.get("id")]
    if not cast_ids:
        cast_ids = ["char_player", "char_witness"]
    base, pvals = _authored_props(data)
    secret_id = _ensure_secret_encounter(data)
    _ensure_five_act_spools(data)

    rxn_idx = 0
    for enc in data.get("encounters", []) or []:
        for opt in enc.get("options", []) or []:
            for rxn in opt.get("reactions", []) or []:
                ds = rxn.get("desirability_script")
                if _script_is_constant(ds) or _count_vars(ds) < 2:
                    rxn["desirability_script"] = _desirability_formula(cast_ids, base, pvals, rxn_idx)
                rxn["after_effects"] = _effect_suite(cast_ids, base, pvals, rxn_idx)
                rxn_idx += 1

    # Reset and enforce stage-gated options with secret pathing targets.
    refs = _act_option_refs(data)
    targets = {3: 0.05, 4: 0.10, 5: 0.20}
    gate_idx = 0
    for act in (3, 4, 5):
        options = refs.get(act, [])
        for _enc, opt in options:
            opt["visibility_script"] = True
        if not options:
            continue
        need = max(1, int(math.ceil(len(options) * targets[act])))
        for _enc, opt in options[:need]:
            opt["visibility_script"] = _visibility_gate(cast_ids, base, gate_idx)
            reactions = opt.get("reactions", []) or []
            if reactions:
                reactions[0]["consequence_id"] = secret_id
                opt["reactions"] = reactions
            gate_idx += 1
    return data


def _effect_mix_stats(data: Dict[str, Any]) -> Dict[str, Any]:
    totals = {"effects": 0, "flat": 0, "nudge": 0, "blend": 0, "invert": 0, "avg": 0}
    for enc in data.get("encounters", []) or []:
        for opt in enc.get("options", []) or []:
            for rxn in opt.get("reactions", []) or []:
                for eff in rxn.get("after_effects", []) or []:
                    totals["effects"] += 1
                    to = eff.get("to") if isinstance(eff, dict) else None
                    op = to.get("operator_type") if isinstance(to, dict) else None
                    if (not op) or _script_is_constant(to):
                        totals["flat"] += 1
                    if op == "Nudge":
                        totals["nudge"] += 1
                    if op == "Arithmetic Mean":
                        totals["avg"] += 1
                    if op == "Addition" and _pointer_count(to) >= 2:
                        totals["blend"] += 1
                    if op == "Multiplication" and _has_negative_const(to):
                        totals["invert"] += 1
    eff = max(1, totals["effects"])
    return {
        **totals,
        "nudge_pct": round(100.0 * totals["nudge"] / eff, 2),
        "blend_pct": round(100.0 * totals["blend"] / eff, 2),
        "invert_pct": round(100.0 * totals["invert"] / eff, 2),
        "avg_pct": round(100.0 * totals["avg"] / eff, 2),
    }


def _act_gate_stats(data: Dict[str, Any]) -> Dict[str, Any]:
    refs = _act_option_refs(data)
    secret_ids = {str(e.get("id", "")) for e in (data.get("encounters", []) or []) if str(e.get("id", "")).startswith("page_secret_")}
    out: Dict[str, Any] = {}
    for act in (3, 4, 5):
        options = refs.get(act, [])
        total = len(options)
        gated = 0
        to_secret = 0
        for _enc, opt in options:
            if opt.get("visibility_script", True) is not True:
                gated += 1
                if any(str(r.get("consequence_id", "")) in secret_ids for r in (opt.get("reactions", []) or [])):
                    to_secret += 1
        out[f"act_{act}"] = {
            "options": total,
            "gated": gated,
            "gated_pct": round(100.0 * gated / total, 2) if total else 0.0,
            "gated_to_secret": to_secret,
        }
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Enforce storyworld constraints and emit audit report for a folder.")
    ap.add_argument("--dir", type=str, default=str(BATCH_DIR), help="Folder containing storyworld JSON files.")
    ap.add_argument("--report-name", type=str, default="today_batch_constraints_audit.json")
    args = ap.parse_args()

    target_dir = Path(args.dir).resolve()
    report_dir = target_dir / "_reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    files = sorted(p for p in target_dir.glob("*.json") if p.is_file())
    summary: List[Dict[str, Any]] = []
    for p in files:
        data = json.loads(p.read_text(encoding="utf-8"))
        data = _enforce_world(data)
        p.write_text(json.dumps(data, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")

        # Local validator import to avoid external side effects.
        sys_path = str(ROOT / "codex-skills" / "storyworld-building" / "scripts")
        if sys_path not in __import__("sys").path:
            __import__("sys").path.insert(0, sys_path)
        from sweepweave_validator import validate_storyworld  # type: ignore

        errors = validate_storyworld(str(p))
        reactions = 0
        des_bad = 0
        for enc in data.get("encounters", []) or []:
            for opt in enc.get("options", []) or []:
                for rxn in opt.get("reactions", []) or []:
                    reactions += 1
                    ds = rxn.get("desirability_script")
                    if _script_is_constant(ds) or _count_vars(ds) < 2:
                        des_bad += 1
        effect_stats = _effect_mix_stats(data)
        act_stats = _act_gate_stats(data)
        summary.append(
            {
                "file": p.name,
                "encounters": len(data.get("encounters", [])),
                "characters": len(data.get("characters", [])),
                "reactions": reactions,
                "desirability_bad_reactions": des_bad,
                "effects_total": effect_stats["effects"],
                "effects_flat": effect_stats["flat"],
                "effect_mix_pct": {
                    "nudge": effect_stats["nudge_pct"],
                    "blend": effect_stats["blend_pct"],
                    "invert": effect_stats["invert_pct"],
                    "avg": effect_stats["avg_pct"],
                },
                "act_gate_stats": act_stats,
                "validator_errors": len(errors),
            }
        )

    out = report_dir / str(args.report_name)
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    print(str(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
