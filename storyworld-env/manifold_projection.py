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
