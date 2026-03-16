#!/usr/bin/env python3
"""Compute multi-dimensional quality vectors for storyworld JSON files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

from __init__ import benchmark_pass, benchmark_targets, evaluate_benchmark

try:
    from pathing_lab.pathing_metrics import simulate_pathing
except Exception:
    simulate_pathing = None


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


def quality_vector(metrics: Dict[str, float], targets: Dict[str, float], profile: str = "default") -> Dict[str, float]:
    profile_key = (profile or "default").strip().lower()
    stretch = None
    if profile_key == "morality_open":
        # Stricter ranking thresholds than hard pass/fail so morality worlds do not saturate at 1.0.
        stretch = {
            "options_per_encounter_min": 3.1,
            "reactions_per_option_min": 2.2,
            "effects_per_reaction_min": 4.2,
            "desirability_vars_min": 1.8,
            "text_length_compliance_min": 0.55,
            "max_ending_share_max": 0.30,
            "min_ending_share_min": 0.005,
            "ending_entropy_soft_min": 2.4,
            "ending_effective_min": 7.5,
            "effect_operator_variety_min": 1.5,
            "des_operator_variety_min": 1.5,
            "option_visibility_nonconstant_ratio_min": 0.20,
            "option_performability_nonconstant_ratio_min": 0.20,
            "encounter_acceptability_nonconstant_ratio_min": 0.30,
            "encounter_desirability_nonconstant_ratio_min": 0.30,
            "encounter_theme_relevance_ratio_min": 0.80,
            "reaction_theme_relevance_ratio_min": 0.80,
            "encounter_theme_semantic_coherence_min": 0.32,
            "reaction_theme_semantic_coherence_min": 0.28,
        }
    t = stretch or targets
    structure_density = _mean(
        [
            _at_least(metrics.get("options_per_encounter", 0.0), t["options_per_encounter_min"]),
            _at_least(metrics.get("reactions_per_option", 0.0), t["reactions_per_option_min"]),
            _at_least(metrics.get("effects_per_reaction", 0.0), t["effects_per_reaction_min"]),
            _at_least(metrics.get("desirability_vars", 0.0), t["desirability_vars_min"]),
            _at_least(metrics.get("min_spec_compliance", 0.0), targets["min_spec_compliance_min"]),
            _at_least(metrics.get("text_length_compliance", 0.0), t["text_length_compliance_min"]),
        ]
    )
    if profile_key == "morality_open":
        secret_gating = _mean(
            [
                _at_least(metrics.get("desirability_vars", 0.0), targets["desirability_vars_min"]),
                _at_least(
                    metrics.get("option_visibility_nonconstant_ratio", 0.0),
                    t["option_visibility_nonconstant_ratio_min"],
                ),
                _at_least(
                    metrics.get("option_performability_nonconstant_ratio", 0.0),
                    t["option_performability_nonconstant_ratio_min"],
                ),
                _at_least(
                    metrics.get("encounter_acceptability_nonconstant_ratio", 0.0),
                    t["encounter_acceptability_nonconstant_ratio_min"],
                ),
                _at_least(
                    metrics.get("encounter_desirability_nonconstant_ratio", 0.0),
                    t["encounter_desirability_nonconstant_ratio_min"],
                ),
                _at_least(
                    metrics.get("reaction_theme_relevance_ratio", 0.0),
                    t["reaction_theme_relevance_ratio_min"],
                ),
            ]
        )
        manifold_alignment = _mean(
            [
                _at_least(metrics.get("local_max_proximity", 0.0), targets["local_max_proximity_min"]),
                _at_least(metrics.get("moral_manifold_score", 0.0), targets["moral_manifold_score_min"]),
                _at_least(metrics.get("context_flow_variability", 0.0), 0.35),
            ]
        )
    else:
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
        manifold_alignment = secret_gating
    ending_balance = _mean(
        [
            _at_most(metrics.get("dead_end_rate", 1.0), targets["dead_end_rate_max"]),
            _at_most(metrics.get("max_ending_share", 1.0), t["max_ending_share_max"]),
            _at_least(metrics.get("min_ending_share", 0.0), t["min_ending_share_min"]),
            _at_least(metrics.get("ending_entropy", 0.0), t["ending_entropy_soft_min"]),
            _at_least(metrics.get("ending_effective", 0.0), t["ending_effective_min"]),
        ]
    )
    major_turn_score = (
        _at_least(metrics.get("major_turn_quality", 0.0), targets["major_turns_min"])
        if targets.get("major_turns_min", 0.0) > 0.0
        else 1.0
    )
    pacing_control = _mean(
        [
            major_turn_score,
            _in_band(metrics.get("late_block_rate", 0.0), targets["late_block_min"], targets["late_block_max"])
            if metrics.get("late_block_applicable", 1.0) >= 0.5
            else 1.0,
        ]
    )

    script_artistry = _mean(
        [
            _at_least(metrics.get("effect_nonconstant_ratio", 0.0), targets["effect_nonconstant_ratio_min"]),
            _at_least(metrics.get("des_nonconstant_ratio", 0.0), targets["des_nonconstant_ratio_min"]),
            _at_least(metrics.get("effect_complexity", 0.0), targets["effect_complexity_min"]),
            _at_least(metrics.get("des_complexity", 0.0), targets["des_complexity_min"]),
            _at_least(metrics.get("effect_operator_variety", 0.0), t["effect_operator_variety_min"]),
            _at_least(metrics.get("des_operator_variety", 0.0), t["des_operator_variety_min"]),
            _at_most(metrics.get("effect_operator_dominance", 1.0), targets["effect_operator_dominance_max"]),
            _at_most(metrics.get("des_operator_dominance", 1.0), targets["des_operator_dominance_max"]),
            _at_least(
                metrics.get("option_visibility_nonconstant_ratio", 0.0),
                t["option_visibility_nonconstant_ratio_min"],
            ),
            _at_least(
                metrics.get("option_performability_nonconstant_ratio", 0.0),
                t["option_performability_nonconstant_ratio_min"],
            ),
            _at_least(
                metrics.get("encounter_acceptability_nonconstant_ratio", 0.0),
                t["encounter_acceptability_nonconstant_ratio_min"],
            ),
            _at_least(
                metrics.get("encounter_desirability_nonconstant_ratio", 0.0),
                t["encounter_desirability_nonconstant_ratio_min"],
            ),
        ]
    )

    text_gate = _mean(
        [
            _at_least(
                metrics.get("encounter_text_uniqueness_ratio", 0.0),
                targets["encounter_text_uniqueness_ratio_min"],
            ),
            _at_least(
                metrics.get("reaction_text_uniqueness_ratio", 0.0),
                targets["reaction_text_uniqueness_ratio_min"],
            ),
            _at_least(
                metrics.get("encounter_theme_relevance_ratio", 0.0),
                t["encounter_theme_relevance_ratio_min"],
            ),
            _at_least(
                metrics.get("reaction_theme_relevance_ratio", 0.0),
                t["reaction_theme_relevance_ratio_min"],
            ),
            _at_least(
                metrics.get("encounter_theme_semantic_coherence", 0.0),
                t["encounter_theme_semantic_coherence_min"],
            ),
            _at_least(
                metrics.get("reaction_theme_semantic_coherence", 0.0),
                t["reaction_theme_semantic_coherence_min"],
            ),
        ]
    )

    # Weighted composite emphasizing structural + outcome reliability.
    if profile_key == "morality_open":
        composite = (
            0.18 * structure_density
            + 0.12 * secret_gating
            + 0.22 * ending_balance
            + 0.08 * pacing_control
            + 0.16 * script_artistry
            + 0.12 * text_gate
            + 0.12 * manifold_alignment
        )
    else:
        composite = (
            0.22 * structure_density
            + 0.18 * secret_gating
            + 0.20 * ending_balance
            + 0.10 * pacing_control
            + 0.18 * script_artistry
            + 0.12 * text_gate
        )
    return {
        "structure_density": round(structure_density, 4),
        "secret_gating": round(secret_gating, 4),
        "ending_balance": round(ending_balance, 4),
        "pacing_control": round(pacing_control, 4),
        "script_artistry": round(script_artistry, 4),
        "text_gate": round(text_gate, 4),
        "manifold_alignment": round(manifold_alignment, 4),
        "composite_score": round(composite, 4),
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Multi-dimensional storyworld quality scoring")
    p.add_argument("--storyworlds", nargs="+", required=True, help="JSON files to score")
    p.add_argument(
        "--profile",
        default="default",
        choices=["default", "morality_open"],
        help="Benchmark profile for targets/pass criteria",
    )
    p.add_argument("--runs", type=int, default=200, help="Monte Carlo runs per world")
    p.add_argument("--pathing-rollouts", type=int, default=120, help="Rollouts for pathing-lab probes")
    p.add_argument("--with-pathing", action="store_true", help="Include experimental pathing_lab metrics in output")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", required=True, help="Output JSON report")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    targets = benchmark_targets(profile=args.profile)
    rows: List[Dict[str, Any]] = []
    for p in args.storyworlds:
        path = Path(p).resolve()
        data = json.loads(path.read_text(encoding="utf-8"))
        metrics = evaluate_benchmark(data, runs=args.runs, seed=args.seed)
        vector = quality_vector(metrics, targets, profile=args.profile)
        pathing = None
        if args.with_pathing and simulate_pathing is not None:
            pathing = simulate_pathing(data, rollouts=args.pathing_rollouts, seed=args.seed)
            # Pathing lab is experimental; blend softly so it informs ranking without dominating.
            vector["pathing_conceptuality"] = round(float(pathing.get("pathing_composite", 0.0)), 4)
            vector["composite_score"] = round(
                0.82 * float(vector["composite_score"]) + 0.18 * float(vector["pathing_conceptuality"]),
                4,
            )
        row = {
            "storyworld": str(path),
            "title": data.get("title", ""),
            "benchmark_pass": bool(benchmark_pass(metrics, profile=args.profile)),
            "metrics": metrics,
            "quality_vector": vector,
        }
        if pathing is not None:
            row["pathing_lab"] = pathing
        rows.append(row)

    rows.sort(key=lambda r: r["quality_vector"]["composite_score"], reverse=True)
    report = {
        "profile": args.profile,
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
