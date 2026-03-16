#!/usr/bin/env python3
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple


ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "storyworlds" / "3-5-2026-morality-constitutions-batch-v1"
REPORT = BATCH / "_reports" / "morality_3d_matrix_imposition_2026-03-05.json"

REALPOL = "Realpolitik_Pressure"
PHASE = "Phase_Clock"


def ptr(prop: str, coeff: float = 1.0) -> Dict[str, Any]:
    return {
        "pointer_type": "Bounded Number Pointer",
        "script_element_type": "Pointer",
        "character": "char_executor",
        "keyring": [prop],
        "coefficient": coeff,
    }


def const(v: float) -> Dict[str, Any]:
    return {"pointer_type": "Bounded Number Constant", "script_element_type": "Pointer", "value": float(v)}


def op_add(*operands: Dict[str, Any]) -> Dict[str, Any]:
    return {"script_element_type": "Operator", "operator_type": "Addition", "operands": list(operands)}


def op_nudge(prop: str, delta: float) -> Dict[str, Any]:
    return {
        "script_element_type": "Operator",
        "operator_type": "Nudge",
        "operands": [ptr(prop), const(delta)],
    }


def cmp_gte(prop: str, value: float) -> Dict[str, Any]:
    return {
        "script_element_type": "Operator",
        "operator_type": "Arithmetic Comparator",
        "operator_subtype": "Greater Than or Equal To",
        "operands": [ptr(prop), const(value)],
    }


def cmp_lte(prop: str, value: float) -> Dict[str, Any]:
    return {
        "script_element_type": "Operator",
        "operator_type": "Arithmetic Comparator",
        "operator_subtype": "Less Than or Equal To",
        "operands": [ptr(prop), const(value)],
    }


def op_and(*operands: Dict[str, Any]) -> Dict[str, Any]:
    return {"script_element_type": "Operator", "operator_type": "And", "operands": list(operands)}


def ensure_realpolitik_property(world: Dict[str, Any]) -> None:
    props = world.get("authored_properties", []) or []
    if any(str(p.get("property_name", p.get("id", "")) or "") == REALPOL for p in props):
        return
    now = float(int(time.time()))
    next_idx = 0
    if props:
        next_idx = max(int(p.get("creation_index", i)) for i, p in enumerate(props)) + 1
    props.append(
        {
            "id": REALPOL,
            "property_name": REALPOL,
            "property_type": "bounded number",
            "default_value": 0.5,
            "depth": 0,
            "attribution_target": "all cast members",
            "affected_characters": [],
            "creation_index": next_idx,
            "creation_time": now,
            "modified_time": now,
        }
    )
    world["authored_properties"] = props


def infer_graded(world: Dict[str, Any]) -> List[str]:
    ep = world.get("evaluation_profile", {}) if isinstance(world.get("evaluation_profile"), dict) else {}
    graded = [str(x) for x in (ep.get("graded_properties") or []) if str(x)]
    if REALPOL in graded:
        graded = [x for x in graded if x != REALPOL]
    if PHASE in graded:
        graded = [x for x in graded if x != PHASE]
    if len(graded) >= 3:
        return graded[:3]

    authored = [str(p.get("property_name", p.get("id", "")) or "") for p in world.get("authored_properties", []) or []]
    authored = [p for p in authored if p not in {REALPOL, PHASE}]
    for p in authored:
        if p not in graded:
            graded.append(p)
        if len(graded) >= 3:
            break
    return graded[:3]


def rewrite_evaluation_profile(world: Dict[str, Any], graded: List[str]) -> None:
    ep = world.get("evaluation_profile", {}) if isinstance(world.get("evaluation_profile"), dict) else {}
    context = [REALPOL]
    if PHASE not in graded:
        context.append(PHASE)
    for p in ep.get("context_properties", []) or []:
        ps = str(p)
        if ps and ps not in graded and ps not in context:
            context.append(ps)
    world["evaluation_profile"] = {
        "profile_version": "morality-open-v2-3d-matrix",
        "graded_properties": graded,
        "context_properties": context,
        "notes": "Endings gated by non-scored realpolitik availability clusters; desirability ranks within each cluster using 2-3 graded vars.",
        "updated_time": float(int(time.time())),
    }


def set_penultimate_realpolitik(world: Dict[str, Any]) -> None:
    # Penultimate options push REALPOL to low / mid / high lanes.
    for enc in world.get("encounters", []) or []:
        eid = str(enc.get("id", "") or "")
        if not eid.startswith("page_a3_"):
            continue
        opts = enc.get("options", []) or []
        for oi, opt in enumerate(opts):
            lane = oi % 3
            target = 0.12 if lane == 0 else 0.50 if lane == 1 else 0.88
            for rx in opt.get("reactions", []) or []:
                effects = rx.get("after_effects", []) or []
                effects = [e for e in effects if not (isinstance(e, dict) and isinstance(e.get("Set"), dict) and (e["Set"].get("keyring") or [None])[0] == REALPOL)]
                effects.append(
                    {
                        "effect_type": "Bounded Number Effect",
                        "Set": ptr(REALPOL),
                        "to": op_add(const(target), op_nudge(REALPOL, 0.0)),
                    }
                )
                rx["after_effects"] = effects


def desirability_formula(v1: str, v2: str, v3: str, variant: int) -> Dict[str, Any]:
    # 4 variants: ++, +-, -+, ++(+v3*0.55)
    if variant == 0:
        return op_add(ptr(v1, 1.0), ptr(v2, 1.0))
    if variant == 1:
        return op_add(ptr(v1, 1.0), ptr(v2, -1.0))
    if variant == 2:
        return op_add(ptr(v1, -1.0), ptr(v2, 1.0))
    return op_add(ptr(v1, 0.85), ptr(v2, 0.85), ptr(v3, 0.55))


def rewrite_ending_matrix(world: Dict[str, Any], graded: List[str]) -> None:
    v1, v2, v3 = graded[0], graded[1], graded[2]
    endings = [e for e in world.get("encounters", []) or [] if str(e.get("id", "")).startswith("page_end_")]
    endings.sort(key=lambda e: str(e.get("id", "")))
    # Expect 12 endings. If more, only first 12 rewritten.
    for i, end in enumerate(endings[:12]):
        cluster = i // 4  # 0 low, 1 mid, 2 high
        variant = i % 4
        base_gate = cmp_gte(PHASE, 0.68)
        if cluster == 0:
            lane_gate = cmp_lte(REALPOL, 0.34)
        elif cluster == 1:
            lane_gate = op_and(cmp_gte(REALPOL, 0.34), cmp_lte(REALPOL, 0.67))
        else:
            lane_gate = cmp_gte(REALPOL, 0.67)
        end["acceptability_script"] = op_and(base_gate, lane_gate)
        end["desirability_script"] = desirability_formula(v1, v2, v3, variant)


def main() -> int:
    files = sorted(BATCH.glob("mq_*_v2.json"))
    updated: List[str] = []
    per_world: Dict[str, Dict[str, Any]] = {}
    now = float(int(time.time()))
    for path in files:
        world = json.loads(path.read_text(encoding="utf-8"))
        ensure_realpolitik_property(world)
        graded = infer_graded(world)
        if len(graded) < 3:
            continue
        rewrite_evaluation_profile(world, graded)
        set_penultimate_realpolitik(world)
        rewrite_ending_matrix(world, graded)
        world["modified_time"] = now
        path.write_text(json.dumps(world, ensure_ascii=True, indent=2) + "\n", encoding="utf-8", newline="\n")
        updated.append(str(path))
        per_world[path.name] = {
            "graded_properties": graded,
            "non_scored_realpolitik": REALPOL,
            "clusters": {"low": "<=0.34", "mid": "0.34..0.67", "high": ">=0.67"},
        }

    REPORT.write_text(
        json.dumps(
            {
                "generated_at": now,
                "updated_count": len(updated),
                "updated_files": updated,
                "world_matrix_specs": per_world,
            },
            ensure_ascii=True,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(str(REPORT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
