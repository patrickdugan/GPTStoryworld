#!/usr/bin/env python3
"""Inject experimental multi-path gating and reversal endpoints into a storyworld."""

from __future__ import annotations

import argparse
import json
import random
import time
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple


def _bn_ptr(char_id: str, prop: str) -> Dict[str, Any]:
    return {
        "script_element_type": "Pointer",
        "pointer_type": "Bounded Number Pointer",
        "character": char_id,
        "keyring": [prop],
        "coefficient": 1.0,
    }


def _bn_const(value: float) -> Dict[str, Any]:
    return {"script_element_type": "Pointer", "pointer_type": "Bounded Number Constant", "value": float(value)}


def _cmp(op_left: Dict[str, Any], subtype: str, op_right: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "script_element_type": "Operator",
        "operator_type": "Arithmetic Comparator",
        "operator_subtype": subtype,
        "operands": [op_left, op_right],
    }


def _mul(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    return {"script_element_type": "Operator", "operator_type": "Multiplication", "operands": [a, b]}


def _add(*ops: Dict[str, Any]) -> Dict[str, Any]:
    return {"script_element_type": "Operator", "operator_type": "Addition", "operands": list(ops)}


def _and(*ops: Dict[str, Any]) -> Dict[str, Any]:
    return {"script_element_type": "Operator", "operator_type": "And", "operands": list(ops)}


def _or(*ops: Dict[str, Any]) -> Dict[str, Any]:
    return {"script_element_type": "Operator", "operator_type": "Or", "operands": list(ops)}


def _abs(op: Dict[str, Any]) -> Dict[str, Any]:
    return {"script_element_type": "Operator", "operator_type": "Absolute Value", "operands": [op]}


def _candidate_options(encounters: Sequence[Dict[str, Any]]) -> List[Tuple[Dict[str, Any], Dict[str, Any]]]:
    rows = []
    for enc in encounters:
        opts = enc.get("options", []) or []
        if not opts:
            continue
        for opt in opts:
            rows.append((enc, opt))
    return rows


def _is_trivial_visibility(vis: Any) -> bool:
    return vis is True or vis is None or (isinstance(vis, dict) and vis.get("pointer_type") == "Boolean Constant" and bool(vis.get("value", False)))


def inject(data: Dict[str, Any], seed: int = 42, gate_ratio: float = 0.08) -> Dict[str, Any]:
    rng = random.Random(seed)
    out = json.loads(json.dumps(data))

    chars = [c.get("id") for c in out.get("characters", []) if c.get("id")]
    if not chars:
        return out
    main_char = str(chars[0])

    props = [p.get("property_name") for p in out.get("authored_properties", []) if p.get("property_name")]
    base_props = [p for p in props if not str(p).startswith("p")]
    if len(base_props) < 2:
        return out

    encounters = out.get("encounters", []) or []
    options = _candidate_options(encounters)
    if not options:
        return out

    # Bias gating to early/mid encounters so gates are actually exercised in rollouts.
    early_window = max(24, int(len(options) * 0.35))
    candidate_pool = options[:early_window]
    rng.shuffle(candidate_pool)
    gate_count = max(2, int(len(options) * max(0.01, gate_ratio)))
    selected = candidate_pool[:gate_count]

    # Use rotating variable pairs so different routes key off different variables.
    var_pairs = []
    for i in range(len(base_props)):
        for j in range(i + 1, len(base_props)):
            var_pairs.append((str(base_props[i]), str(base_props[j])))
    if not var_pairs:
        return out
    rng.shuffle(var_pairs)

    for idx, (_enc, opt) in enumerate(selected):
        if not _is_trivial_visibility(opt.get("visibility_script", True)):
            continue
        a, b = var_pairs[idx % len(var_pairs)]
        alt_a, alt_b = var_pairs[(idx + 3) % len(var_pairs)]
        branch1 = _and(
            _cmp(_bn_ptr(main_char, a), "Greater Than or Equal To", _bn_const(-0.08)),
            _cmp(_bn_ptr(main_char, b), "Less Than or Equal To", _bn_const(0.12)),
        )
        branch2 = _and(
            _cmp(_bn_ptr(main_char, alt_a), "Less Than or Equal To", _bn_const(0.08)),
            _cmp(_bn_ptr(main_char, alt_b), "Greater Than or Equal To", _bn_const(-0.12)),
        )
        opt["visibility_script"] = _or(branch1, branch2)

    # Add a secret reversal encounter if absent.
    secret_id = "page_secret_vader_reversal"
    enc_by_id = {e.get("id"): e for e in encounters if e.get("id")}
    if secret_id not in enc_by_id:
        a, b = var_pairs[0]
        diff = _add(_bn_ptr(main_char, a), _mul(_bn_const(-1.0), _bn_ptr(main_char, b)))
        secret_enc = {
            "id": secret_id,
            "title": "Secret: The Reversal",
            "text_script": {
                "script_element_type": "Pointer",
                "pointer_type": "String Constant",
                "value": "At the brink, the doctrine inverts. Allies reinterpret your prior commitments as tactical feints, and a hidden ending path opens through contradiction resolved as strategy.",
            },
            "acceptability_script": _cmp(_abs(diff), "Less Than or Equal To", _bn_const(0.18)),
            "desirability_script": _bn_const(1.2),
            "connected_spools": ["spool_endings"],
            "options": [],
        }
        encounters.append(secret_enc)
        # Ensure endings spool exists and contains secret.
        spools = out.get("spools", []) or []
        endings = None
        for sp in spools:
            sid = str(sp.get("id", "")).lower()
            sname = str(sp.get("spool_name", "")).lower()
            if "ending" in sid or "ending" in sname:
                endings = sp
                break
        if endings is None:
            endings = {"id": "spool_endings", "spool_type": "General", "spool_name": "Endings", "starts_active": True, "encounters": []}
            spools.append(endings)
            out["spools"] = spools
        end_encs = endings.get("encounters", []) or []
        if secret_id not in end_encs:
            end_encs.append(secret_id)
            endings["encounters"] = end_encs

    # Redirect a subset of gated options toward the secret to make it reachable via multiple paths.
    redirected = 0
    for _enc, opt in selected:
        if redirected >= 4:
            break
        reactions = opt.get("reactions", []) or []
        if not reactions:
            continue
        rxn = reactions[0]
        rxn["consequence_id"] = secret_id
        redirected += 1

    out["modified_time"] = float(time.time())
    return out


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Inject multi-path gates + reversal secret endpoint.")
    p.add_argument("--in-json", required=True)
    p.add_argument("--out-json", required=True)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--gate-ratio", type=float, default=0.08)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    in_path = Path(args.in_json).resolve()
    out_path = Path(args.out_json).resolve()
    data = json.loads(in_path.read_text(encoding="utf-8"))
    out = inject(data, seed=args.seed, gate_ratio=args.gate_ratio)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
