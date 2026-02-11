#!/usr/bin/env python3
"""Compute multi-dimensional quality vectors for storyworld JSON files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

from __init__ import benchmark_pass, benchmark_targets, evaluate_benchmark


def _clip01(x: float) -> float:
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else float(x)


def _at_least(actual: float, target: float) -> float:
    if target <= 0:
        return 1.0
    return _clip01(actual / target)


def _at_most(actual: float, target: float) -> float:
    if target <= 0:
        return 0.0
    return _clip01(target / max(actual, 1e-9))


def _in_band(actual: float, lo: float, hi: float) -> float:
    if lo > hi:
        lo, hi = hi, lo
    if lo <= actual <= hi:
        return 1.0
    if actual < lo:
        return _clip01(actual / max(lo, 1e-9))
    # actual > hi
    return _clip01(hi / max(actual, 1e-9))


def _mean(values: Iterable[float]) -> float:
    vals = list(values)
    return sum(vals) / len(vals) if vals else 0.0


def quality_vector(metrics: Dict[str, float], targets: Dict[str, float]) -> Dict[str, float]:
    structure_density = _mean(
        [
            _at_least(metrics.get("options_per_encounter", 0.0), targets["options_per_encounter_min"]),
            _at_least(metrics.get("reactions_per_option", 0.0), targets["reactions_per_option_min"]),
            _at_least(metrics.get("effects_per_reaction", 0.0), targets["effects_per_reaction_min"]),
            _at_least(metrics.get("desirability_vars", 0.0), targets["desirability_vars_min"]),
            _at_least(metrics.get("min_spec_compliance", 0.0), targets["min_spec_compliance_min"]),
            _at_least(metrics.get("text_length_compliance", 0.0), targets["text_length_compliance_min"]),
        ]
    )
    secret_gating = _mean(
        [
            _at_least(metrics.get("act2_gate_pct", 0.0), targets["act2_gate_pct_min"]),
            _at_least(metrics.get("act2_gate_vars", 0.0), targets["act2_gate_vars_min"]),
            _at_least(metrics.get("act3_gate_pct", 0.0), targets["act3_gate_pct_min"]),
            _at_least(metrics.get("act3_gate_vars", 0.0), targets["act3_gate_vars_min"]),
            _at_least(metrics.get("secret_gate_quality", 0.0), targets["secret_gate_quality_min"]),
            _at_least(metrics.get("secret_metric_distance", 0.0), targets["secret_metric_distance_min"]),
            _in_band(
                metrics.get("secret_reachability", 0.0),
                targets["secret_reachability_min"],
                targets["secret_reachability_max"],
            ),
            _at_least(metrics.get("gated_ratio_score", 0.0), 0.8),
        ]
    )
    ending_balance = _mean(
        [
            _at_most(metrics.get("dead_end_rate", 1.0), targets["dead_end_rate_max"]),
            _at_most(metrics.get("max_ending_share", 1.0), targets["max_ending_share_max"]),
            _at_least(metrics.get("min_ending_share", 0.0), targets["min_ending_share_min"]),
            _at_least(metrics.get("ending_entropy", 0.0), targets["ending_entropy_soft_min"]),
            _at_least(metrics.get("ending_effective", 0.0), targets["ending_effective_min"]),
        ]
    )
    pacing_control = _mean(
        [
            _at_least(metrics.get("major_turn_quality", 0.0), targets["major_turns_min"]),
            _in_band(metrics.get("late_block_rate", 0.0), targets["late_block_min"], targets["late_block_max"])
            if metrics.get("late_block_applicable", 1.0) >= 0.5
            else 1.0,
        ]
    )

    # Weighted composite emphasizing structural + outcome reliability.
    composite = (
        0.34 * structure_density + 0.24 * secret_gating + 0.30 * ending_balance + 0.12 * pacing_control
    )
    return {
        "structure_density": round(structure_density, 4),
        "secret_gating": round(secret_gating, 4),
        "ending_balance": round(ending_balance, 4),
        "pacing_control": round(pacing_control, 4),
        "composite_score": round(composite, 4),
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Multi-dimensional storyworld quality scoring")
    p.add_argument("--storyworlds", nargs="+", required=True, help="JSON files to score")
    p.add_argument("--runs", type=int, default=200, help="Monte Carlo runs per world")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", required=True, help="Output JSON report")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    targets = benchmark_targets()
    rows: List[Dict[str, Any]] = []
    for p in args.storyworlds:
        path = Path(p).resolve()
        data = json.loads(path.read_text(encoding="utf-8"))
        metrics = evaluate_benchmark(data, runs=args.runs, seed=args.seed)
        vector = quality_vector(metrics, targets)
        row = {
            "storyworld": str(path),
            "title": data.get("title", ""),
            "benchmark_pass": bool(benchmark_pass(metrics)),
            "metrics": metrics,
            "quality_vector": vector,
        }
        rows.append(row)

    rows.sort(key=lambda r: r["quality_vector"]["composite_score"], reverse=True)
    report = {
        "runs": args.runs,
        "seed": args.seed,
        "targets": targets,
        "count": len(rows),
        "pass_count": sum(1 for r in rows if r["benchmark_pass"]),
        "ranked": rows,
    }
    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    print(str(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
