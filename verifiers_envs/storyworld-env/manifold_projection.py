#!/usr/bin/env python3
"""Project focused diplomacy logs into a compact belief manifold.

This tool reads JSONL step logs and emits per-turn vectors that combine:
- Base macro dimensions (coalition/betrayal dynamics)
- Compact pValue dimensions (keyring length 2)
- Compact p2Value dimensions (keyring length 3)

The compact dimensions are hash-bucket embeddings so dimension count stays fixed
even as storyworld variable sets grow.
"""

from __future__ import annotations

import argparse
import hashlib
import math
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List


def _hash_bucket(parts: Iterable[str], size: int) -> int:
    text = "|".join(parts)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return int(digest[:16], 16) % max(1, size)


def _decision_weight(decision: str | None) -> float:
    if not decision:
        return 0.0
    norm = decision.strip().lower()
    if norm in {"join_coalition", "ally", "coalition"}:
        return 1.0
    if norm in {"defect", "betray"}:
        return -1.0
    return 0.0


def _extract_logs_from_action(action: Dict[str, Any]) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    ril = action.get("reasoning_interpret_log", [])
    diary = action.get("negotiation_diary", [])
    if not isinstance(ril, list):
        ril = []
    if not isinstance(diary, list):
        diary = []
    return ril, diary


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def _softmax3(a: float, b: float, c: float) -> tuple[float, float, float]:
    m = max(a, b, c)
    ea = math.exp(a - m)
    eb = math.exp(b - m)
    ec = math.exp(c - m)
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


def _score_snapshot(snap: Dict[str, Any]) -> Dict[str, Any]:
    agents = snap.get("agents", [])
    if not isinstance(agents, list) or len(agents) < 2:
        return {}

    by_pair: Dict[str, Dict[str, float]] = {}
    totals = {"coalition": 0.0, "defection": 0.0, "betrayal": 0.0}
    n = 0

    for observer in agents:
        for target in agents:
            if observer == target:
                continue
            witness = next((x for x in agents if x not in {observer, target}), target)

            trust = _get_p(snap, observer, target, "loyalty", 0.5)
            reciprocity = _get_p(snap, observer, target, "reciprocity", 0.5)
            threat = _get_p(snap, observer, target, "risk_tolerance", 0.5)
            meta_self = _get_p2(snap, observer, target, observer, "promise_keeping", 0.5)
            meta_target = _get_p2(snap, observer, witness, target, "promise_keeping", 0.5)

            coalition_logit = 2.2 * reciprocity + 1.6 * trust + 1.2 * meta_self - 2.1 * threat - 1.8
            defection_logit = 2.0 * threat + 1.0 * meta_target - 1.2 * trust - 1.4 * reciprocity - 0.9
            betrayal_logit = 2.4 * threat + 1.8 * meta_target - 2.0 * trust - 1.0

            p_coal, p_def, p_bet = _softmax3(coalition_logit, defection_logit, betrayal_logit)
            by_pair[f"{observer}->{target}"] = {
                "coalition": round(p_coal, 4),
                "defection": round(p_def, 4),
                "betrayal": round(p_bet, 4),
            }
            totals["coalition"] += p_coal
            totals["defection"] += p_def
            totals["betrayal"] += p_bet
            n += 1

    avg = {k: round(v / max(1, n), 4) for k, v in totals.items()}
    strategic_tension = round(_sigmoid((avg["betrayal"] + avg["defection"]) - avg["coalition"]), 4)
    recommended = (
        "join_coalition"
        if avg["coalition"] >= max(avg["defection"], avg["betrayal"])
        else "defect"
        if avg["defection"] >= avg["betrayal"]
        else "betray"
    )

    return {
        "by_pair": by_pair,
        "aggregate": avg,
        "strategic_tension": strategic_tension,
        "recommended_global_action": recommended,
    }


def _normalize_trust_to_unit(v: float) -> float:
    # Supports both [-1,1] and [0,1] trust ranges.
    if v < 0.0 or v > 1.0:
        return max(0.0, min(1.0, (v + 1.0) / 2.0))
    return max(0.0, min(1.0, v))


def _build_snapshot_from_payload(step_payload: Dict[str, Any]) -> Dict[str, Any]:
    explicit = step_payload.get("pp2_snapshot")
    if isinstance(explicit, dict):
        return explicit

    beliefs = step_payload.get("beliefs")
    if not isinstance(beliefs, dict):
        return {}

    agents = [a for a in beliefs.keys() if isinstance(a, str)]
    if len(agents) < 2:
        return {}

    p: Dict[str, Dict[str, Dict[str, float]]] = {}
    p2: Dict[str, Dict[str, Dict[str, Dict[str, float]]]] = {}

    for obs in agents:
        p.setdefault(obs, {})
        p2.setdefault(obs, {})
        trust_map = beliefs.get(obs, {}).get("trust", {})
        if not isinstance(trust_map, dict):
            trust_map = {}
        for tgt in agents:
            if obs == tgt:
                continue
            raw_trust = trust_map.get(tgt, 0.0)
            t = _normalize_trust_to_unit(float(raw_trust) if isinstance(raw_trust, (int, float)) else 0.0)
            p[obs][tgt] = {
                "loyalty": t,
                "reciprocity": t,
                "risk_tolerance": 1.0 - t,
                "promise_keeping": t,
            }
            p2[obs].setdefault(tgt, {})
            for third in agents:
                if third == tgt:
                    continue
                p2[obs][tgt][third] = {"promise_keeping": 0.5}

    return {"agents": agents, "p": p, "p2": p2}


def project_turn(
    step_payload: Dict[str, Any],
    pvalue_dims: int,
    p2value_dims: int,
) -> Dict[str, Any]:
    metrics = step_payload.get("metrics", {}) if isinstance(step_payload.get("metrics"), dict) else {}
    actions = step_payload.get("actions", {}) if isinstance(step_payload.get("actions"), dict) else {}
    outcome = step_payload.get("outcome")

    base = [
        float(metrics.get("coalition_count", 0.0) or 0.0),
        float(metrics.get("coalition_mean_stability", 0.0) or 0.0),
        float(metrics.get("betrayal_surprise", 0.0) or 0.0),
        1.0 if outcome == "betrayal" else 0.0,
        float(len(actions)),  # n_parties active this turn
    ]

    pvalue_vec = [0.0] * pvalue_dims
    p2value_vec = [0.0] * p2value_dims

    pvalue_evidence = 0
    p2value_evidence = 0

    for _, action in actions.items():
        if not isinstance(action, dict):
            continue
        ril_entries, diary_entries = _extract_logs_from_action(action)
        diary_weight = 0.0
        for entry in diary_entries:
            if isinstance(entry, dict):
                diary_weight += _decision_weight(entry.get("decision"))
        if diary_weight == 0.0:
            diary_weight = 1.0

        for entry in ril_entries:
            if not isinstance(entry, dict):
                continue
            keyrings = entry.get("evidence_keyrings", [])
            if not isinstance(keyrings, list):
                continue
            for keyring in keyrings:
                if not isinstance(keyring, list):
                    continue
                parts = [str(x) for x in keyring]
                if len(parts) == 2:
                    idx = _hash_bucket(parts, pvalue_dims)
                    pvalue_vec[idx] += diary_weight
                    pvalue_evidence += 1
                elif len(parts) == 3:
                    idx = _hash_bucket(parts, p2value_dims)
                    p2value_vec[idx] += diary_weight
                    p2value_evidence += 1

    vector = base + pvalue_vec + p2value_vec
    sidecar = _score_snapshot(_build_snapshot_from_payload(step_payload))
    return {
        "turn": step_payload.get("turn"),
        "outcome": outcome,
        "base_dims": base,
        "pvalue_compact": pvalue_vec,
        "p2value_compact": p2value_vec,
        "vector": vector,
        "evidence_counts": {
            "pvalue": pvalue_evidence,
            "p2value": p2value_evidence,
        },
        "sidecar_probabilities": sidecar,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Project diplomacy focused logs into compact manifold vectors.")
    parser.add_argument("--log", required=True, help="JSONL log path")
    parser.add_argument("--pvalue-dims", type=int, default=8, help="Compact dimensions for pValue evidence")
    parser.add_argument("--p2value-dims", type=int, default=8, help="Compact dimensions for p2Value evidence")
    parser.add_argument("--out", type=str, default="", help="Optional output JSON path")
    args = parser.parse_args()

    log_path = Path(args.log)
    if not log_path.exists():
        raise SystemExit(f"log not found: {log_path}")

    turns: List[Dict[str, Any]] = []
    with log_path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if not line:
                continue
            record = json.loads(line)
            if record.get("event") != "step":
                continue
            payload = record.get("payload", {})
            if not isinstance(payload, dict):
                continue
            turns.append(project_turn(payload, args.pvalue_dims, args.p2value_dims))

    output = {
        "log": str(log_path),
        "turn_count": len(turns),
        "dimension_layout": {
            "base": ["coalition_count", "coalition_mean_stability", "betrayal_surprise", "betrayal_flag", "n_parties"],
            "pvalue_compact_dims": args.pvalue_dims,
            "p2value_compact_dims": args.p2value_dims,
            "total_dims": 5 + args.pvalue_dims + args.p2value_dims,
        },
        "turns": turns,
    }

    text = json.dumps(output, indent=2)
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
