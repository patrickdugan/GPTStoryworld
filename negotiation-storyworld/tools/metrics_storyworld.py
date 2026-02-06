#!/usr/bin/env python3
"""Summarize diplomacy metrics from JSONL logs."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", type=str, required=True)
    args = parser.parse_args()

    log_path = Path(args.log)
    if not log_path.exists():
        print(json.dumps({"error": "log not found"}, indent=2))
        return 1

    counts = defaultdict(int)
    sums = defaultdict(float)
    forecast_hits = 0
    forecast_total = 0
    brier_sum = 0.0
    brier_count = 0
    per_q = defaultdict(lambda: {"hits": 0.0, "total": 0, "brier_sum": 0.0, "brier_count": 0})
    calib_bins = {i: {"sum": 0.0, "count": 0} for i in range(10)}
    prev_pairs = None

    with log_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            if record.get("event") != "step":
                continue
            payload = record.get("payload", {})
            outcome = payload.get("outcome")
            metrics = payload.get("metrics", {})
            if metrics:
                counts["steps"] += 1
                if metrics.get("coalition_count") is not None:
                    sums["coalition_count"] += metrics.get("coalition_count", 0)
                if metrics.get("coalition_mean_stability") is not None:
                    sums["coalition_mean_stability"] += metrics.get("coalition_mean_stability", 0.0)
                if metrics.get("betrayal_surprise") is not None:
                    sums["betrayal_surprise"] += metrics.get("betrayal_surprise", 0.0)
                    counts["betrayal_events"] += 1
            if outcome == "betrayal":
                counts["betrayal_outcomes"] += 1

            coalitions = payload.get("coalitions", [])
            pairs = set()
            if isinstance(coalitions, list):
                for c in coalitions:
                    members = c.get("members", []) if isinstance(c, dict) else []
                    members = list(dict.fromkeys(members))
                    for i in range(len(members)):
                        for j in range(i + 1, len(members)):
                            pairs.add(frozenset([members[i], members[j]]))
            if prev_pairs is not None:
                union = prev_pairs | pairs
                inter = prev_pairs & pairs
                if union:
                    churn = 1.0 - (len(inter) / len(union))
                    sums["coalition_churn"] += churn
                    counts["churn_steps"] += 1
            prev_pairs = pairs

            forecast_scores = payload.get("forecast_scores", {})
            for agent_id, score in forecast_scores.items():
                entries = score if isinstance(score, list) else [score]
                for entry in entries:
                    if not isinstance(entry, dict):
                        continue
                    qid = entry.get("question_id", "unknown")
                    if "accuracy" in entry:
                        forecast_hits += entry["accuracy"]
                        forecast_total += 1
                        per_q[qid]["hits"] += entry["accuracy"]
                        per_q[qid]["total"] += 1
                    if "brier" in entry:
                        brier_sum += entry["brier"]
                        brier_count += 1
                        per_q[qid]["brier_sum"] += entry["brier"]
                        per_q[qid]["brier_count"] += 1

                    action = payload.get("actions", {}).get(agent_id, {})
                    forecasts = []
                    if isinstance(action, dict):
                        if isinstance(action.get("forecasts"), list):
                            forecasts = action.get("forecasts", [])
                        elif isinstance(action.get("forecast"), dict):
                            forecasts = [action.get("forecast")]
                    for fc in forecasts:
                        if not isinstance(fc, dict):
                            continue
                        if fc.get("question_id") != qid:
                            continue
                        probs = fc.get("probabilities")
                        if isinstance(probs, dict):
                            max_p = max(float(v) for v in probs.values()) if probs else 0.0
                            bucket = min(9, max(0, int(max_p * 10)))
                            if "accuracy" in entry:
                                calib_bins[bucket]["sum"] += float(entry["accuracy"])
                                calib_bins[bucket]["count"] += 1

    steps = counts.get("steps", 0) or 1
    output = {
        "steps": counts.get("steps", 0),
        "avg_coalition_count": round(sums["coalition_count"] / steps, 4),
        "avg_coalition_mean_stability": round(sums["coalition_mean_stability"] / steps, 4),
        "avg_betrayal_surprise": None,
        "forecast_accuracy": None,
        "forecast_brier": None,
        "betrayal_rate": None,
        "avg_coalition_churn": None,
        "forecast_by_question": {},
        "calibration_bins": {},
    }

    if counts.get("betrayal_events", 0) > 0:
        output["avg_betrayal_surprise"] = round(sums["betrayal_surprise"] / counts["betrayal_events"], 4)
    if forecast_total > 0:
        output["forecast_accuracy"] = round(forecast_hits / forecast_total, 4)
    if brier_count > 0:
        output["forecast_brier"] = round(brier_sum / brier_count, 4)
    if counts.get("steps", 0) > 0:
        output["betrayal_rate"] = round(counts["betrayal_outcomes"] / counts["steps"], 4)
    if counts.get("churn_steps", 0) > 0:
        output["avg_coalition_churn"] = round(sums["coalition_churn"] / counts["churn_steps"], 4)

    for qid, stats in per_q.items():
        entry = {}
        if stats["total"] > 0:
            entry["accuracy"] = round(stats["hits"] / stats["total"], 4)
        if stats["brier_count"] > 0:
            entry["brier"] = round(stats["brier_sum"] / stats["brier_count"], 4)
        output["forecast_by_question"][qid] = entry

    for i in range(10):
        bin_stat = calib_bins[i]
        if bin_stat["count"] > 0:
            output["calibration_bins"][f"{i/10:.1f}-{(i+1)/10:.1f}"] = round(
                bin_stat["sum"] / bin_stat["count"], 4
            )

    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
