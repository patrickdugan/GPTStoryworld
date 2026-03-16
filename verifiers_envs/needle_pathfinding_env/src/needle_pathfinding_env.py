from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _constraint_score(value: float, op: str, threshold: float) -> float:
    op = str(op or "").strip()
    if op in {">=", ">"}:
        deficit = max(0.0, threshold - value)
        scale = max(abs(threshold), 0.1)
        return max(0.0, 1.0 - min(1.0, deficit / scale))
    if op in {"<=", "<"}:
        deficit = max(0.0, value - threshold)
        scale = max(abs(threshold), 0.1)
        return max(0.0, 1.0 - min(1.0, deficit / scale))
    if op in {"==", "="}:
        delta = abs(value - threshold)
        scale = max(abs(threshold), 0.1)
        return max(0.0, 1.0 - min(1.0, delta / scale))
    return 0.0


def _attempt_proximity(attempt: dict[str, Any], proximity_spec: list[dict[str, Any]]) -> dict[str, Any]:
    terminal_state = dict(attempt.get("terminal_state") or {})
    if not proximity_spec:
        return {
            "proximity_score": 0.0,
            "constraint_scores": [],
        }

    scores: list[dict[str, Any]] = []
    total_weight = 0.0
    weighted_sum = 0.0
    for item in proximity_spec:
        var_name = str(item.get("var", "") or "")
        op = str(item.get("op", "") or "")
        threshold = _safe_float(item.get("threshold", 0.0))
        weight = _safe_float(item.get("weight", 1.0), 1.0)
        value = _safe_float(terminal_state.get(var_name, 0.0))
        score = _constraint_score(value=value, op=op, threshold=threshold)
        scores.append(
            {
                "var": var_name,
                "op": op,
                "threshold": threshold,
                "value": value,
                "weight": weight,
                "score": score,
            }
        )
        total_weight += weight
        weighted_sum += weight * score

    proximity_score = (weighted_sum / max(total_weight, 1e-9)) if scores else 0.0
    return {
        "proximity_score": proximity_score,
        "constraint_scores": scores,
    }


def evaluate(
    attempts: list[dict[str, Any]],
    target: str,
    n_endings: int,
    proximity_spec: list[dict[str, Any]] | None = None,
) -> dict:
    plays_to_target = None
    for row in attempts:
        if str(row.get("ending_id", "")).strip() == target:
            plays_to_target = int(row.get("play_index", 0))
            break

    solved = plays_to_target is not None
    if not solved:
        plays_to_target = len(attempts) + 1

    # normalized: 1.0 means found on first play, 0.0 means not found within n_endings
    denom = max(1, n_endings - 1)
    hit_score = max(0.0, 1.0 - ((plays_to_target - 1) / denom)) if solved else 0.0

    proximity_spec = list(proximity_spec or [])
    best_proximity_score = 0.0
    best_proximity_play_index = None
    best_constraint_scores: list[dict[str, Any]] = []
    per_play_proximity: list[dict[str, Any]] = []
    for row in attempts:
        prox = _attempt_proximity(row, proximity_spec)
        per_play_proximity.append(
            {
                "play_index": int(row.get("play_index", 0) or 0),
                "ending_id": str(row.get("ending_id", "") or ""),
                "proximity_score": float(prox["proximity_score"]),
                "constraint_scores": list(prox["constraint_scores"]),
            }
        )
        if prox["proximity_score"] > best_proximity_score:
            best_proximity_score = float(prox["proximity_score"])
            best_proximity_play_index = int(row.get("play_index", 0) or 0)
            best_constraint_scores = list(prox["constraint_scores"])

    score = max(hit_score, best_proximity_score)

    return {
        "target": target,
        "n_endings": n_endings,
        "solved": solved,
        "plays_to_target": plays_to_target,
        "needle_hit_score": hit_score,
        "needle_proximity_score": best_proximity_score,
        "proximity_spec_used": proximity_spec,
        "best_proximity_play_index": best_proximity_play_index,
        "best_proximity_constraints": best_constraint_scores,
        "per_play_proximity": per_play_proximity,
        "needle_score": score,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Needle-in-haystack ending benchmark")
    ap.add_argument("--attempts", required=True)
    ap.add_argument("--target", required=True)
    ap.add_argument("--n-endings", required=True, type=int)
    ap.add_argument("--proximity-spec", default="", help="Optional JSON file containing a proximity_spec array.")
    args = ap.parse_args()

    attempts_obj = load_json(Path(args.attempts))
    attempts = attempts_obj.get("attempts", [])
    proximity_spec = []
    if str(args.proximity_spec).strip():
        proximity_spec = load_json(Path(args.proximity_spec)).get("proximity_spec", [])
    elif isinstance(attempts_obj.get("target_specs"), dict):
        proximity_spec = list((attempts_obj.get("target_specs") or {}).get(str(args.target), []) or [])
    elif isinstance(attempts_obj.get("proximity_spec"), list):
        proximity_spec = list(attempts_obj.get("proximity_spec") or [])
    result = evaluate(attempts, args.target, int(args.n_endings), proximity_spec=proximity_spec)
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
