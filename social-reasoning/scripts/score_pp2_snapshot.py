#!/usr/bin/env python3
"""Score coalition/defection/betrayal probabilities from p/p2 snapshots."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Dict, Tuple


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def _softmax3(a: float, b: float, c: float) -> Tuple[float, float, float]:
    m = max(a, b, c)
    ea, eb, ec = math.exp(a - m), math.exp(b - m), math.exp(c - m)
    z = ea + eb + ec
    return ea / z, eb / z, ec / z


def _get_p(snap: Dict[str, Any], observer: str, target: str, trait: str, default: float = 0.5) -> float:
    p = snap.get("p", {})
    if isinstance(p, dict):
        val = p.get(observer, {}).get(target, {}).get(trait)
        if isinstance(val, (int, float)):
            return float(val)
    return default


def _get_p2(
    snap: Dict[str, Any],
    observer: str,
    mediator: str,
    target: str,
    trait: str,
    default: float = 0.5,
) -> float:
    p2 = snap.get("p2", {})
    if isinstance(p2, dict):
        val = p2.get(observer, {}).get(mediator, {}).get(target, {}).get(trait)
        if isinstance(val, (int, float)):
            return float(val)
    return default


def _pair_scores(snap: Dict[str, Any], observer: str, target: str, witness: str) -> Dict[str, float]:
    trust = _get_p(snap, observer, target, "loyalty", 0.5)
    reciprocity = _get_p(snap, observer, target, "reciprocity", 0.5)
    threat = _get_p(snap, observer, target, "risk_tolerance", 0.5)
    meta_self = _get_p2(snap, observer, target, observer, "promise_keeping", 0.5)
    meta_target = _get_p2(snap, observer, witness, target, "promise_keeping", 0.5)

    coalition_logit = 2.2 * reciprocity + 1.6 * trust + 1.2 * meta_self - 2.1 * threat - 1.8
    defection_logit = 2.0 * threat + 1.0 * meta_target - 1.2 * trust - 1.4 * reciprocity - 0.9
    betrayal_logit = 2.4 * threat + 1.8 * meta_target - 2.0 * trust - 1.0

    p_coal, p_def, p_bet = _softmax3(coalition_logit, defection_logit, betrayal_logit)
    return {
        "coalition": round(p_coal, 4),
        "defection": round(p_def, 4),
        "betrayal": round(p_bet, 4),
        "coalition_logit": round(coalition_logit, 4),
        "defection_logit": round(defection_logit, 4),
        "betrayal_logit": round(betrayal_logit, 4),
    }


def score_snapshot(snap: Dict[str, Any]) -> Dict[str, Any]:
    agents = snap.get("agents", [])
    if not isinstance(agents, list) or len(agents) < 3:
        raise ValueError("snapshot must contain at least 3 agents in `agents`")

    by_pair: Dict[str, Dict[str, float]] = {}
    totals = {"coalition": 0.0, "defection": 0.0, "betrayal": 0.0}
    n = 0

    for observer in agents:
        for target in agents:
            if observer == target:
                continue
            witness = next((x for x in agents if x not in {observer, target}), agents[0])
            scores = _pair_scores(snap, observer, target, witness)
            by_pair[f"{observer}->{target}"] = scores
            totals["coalition"] += scores["coalition"]
            totals["defection"] += scores["defection"]
            totals["betrayal"] += scores["betrayal"]
            n += 1

    avg = {k: round(v / max(1, n), 4) for k, v in totals.items()}
    strategic_tension = round(_sigmoid((avg["betrayal"] + avg["defection"]) - avg["coalition"]), 4)

    return {
        "agents": agents,
        "by_pair": by_pair,
        "aggregate": avg,
        "strategic_tension": strategic_tension,
        "recommended_global_action": (
            "join_coalition" if avg["coalition"] >= max(avg["defection"], avg["betrayal"])
            else "defect" if avg["defection"] >= avg["betrayal"]
            else "betray"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Score p/p2 snapshots for coalition-defection-betrayal probabilities.")
    parser.add_argument("--snapshot", required=True, help="Path to input snapshot JSON")
    parser.add_argument("--out", default="", help="Optional output path")
    args = parser.parse_args()

    src = Path(args.snapshot)
    if not src.exists():
        raise SystemExit(f"snapshot not found: {src}")
    snap = json.loads(src.read_text(encoding="utf-8-sig"))
    result = score_snapshot(snap)

    text = json.dumps(result, indent=2)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
