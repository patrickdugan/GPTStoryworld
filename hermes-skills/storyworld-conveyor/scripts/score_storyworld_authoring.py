#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import types
from pathlib import Path
from typing import Any


DEFAULT_WEIGHTS = {
    "structural_completeness": 1.0,
    "effect_diversity": 0.5,
    "pvalue_desirability_alignment": 1.0,
    "effect_script_quality": 0.5,
    "gating_score": 0.5,
    "ending_diversity_legacy": 0.5,
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_storyworld_env(repo_root: Path):
    """Load the local verifier metric code without requiring Linux-only vf runtime bits."""
    fake_vf = types.ModuleType("verifiers")
    fake_vf.Environment = object
    fake_vf.Rubric = object
    fake_vf.SingleTurnEnv = object
    sys.modules.setdefault("verifiers", fake_vf)

    module_path = repo_root / "verifiers_envs" / "storyworld-env" / "ALL_IN_ONE.py"
    spec = importlib.util.spec_from_file_location("storyworld_env_all_in_one", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load verifier module: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def weighted_score(metrics: dict[str, Any], weights: dict[str, float]) -> float:
    total_weight = sum(weights.values())
    if total_weight <= 0:
        return 0.0
    return sum(float(metrics.get(name, 0.0)) * weight for name, weight in weights.items()) / total_weight


def score_world(data: dict[str, Any], verifier_module: Any, min_options: float) -> dict[str, Any]:
    validator = verifier_module.SweepweaveValidator
    structure_valid, structure_errors = validator.validate_structure(data)
    requirements = {
        "min_characters": len(data.get("characters", [])) or 1,
        "min_encounters": len(data.get("encounters", [])) or 1,
        "min_spools": len(data.get("spools", [])) or 1,
        "min_options_per_encounter": min_options,
    }
    metrics = {
        "structure_valid": bool(structure_valid),
        "structure_error_count": len(structure_errors),
        "structure_errors": structure_errors[:50],
        "structural_completeness": validator.compute_structural_score(data, requirements),
        "effect_diversity": validator.compute_effect_diversity(data),
        "pvalue_desirability_alignment": validator.compute_pvalue_desirability_alignment(data),
        "effect_script_quality": validator.compute_effect_script_quality(data),
        "gating_score": validator.compute_gating_score(data),
        "ending_diversity_legacy": validator.compute_ending_diversity(data),
    }
    metrics["weighted_authoring_verifier_score"] = weighted_score(metrics, DEFAULT_WEIGHTS)
    return metrics


def recommendations(metrics: dict[str, Any]) -> list[str]:
    actions: list[str] = []
    if not metrics["structure_valid"]:
        actions.append("Fix missing required SweepWeave fields before scoring quality.")
    if float(metrics["structural_completeness"]) < 0.98:
        actions.append("Add meaningful options to low-branching non-terminal encounters.")
    if float(metrics["effect_diversity"]) < 0.6:
        actions.append("Diversify effect types/operators beyond repeated bounded-number nudges.")
    if float(metrics["pvalue_desirability_alignment"]) < 0.25:
        actions.append("Rewrite desirability scripts to reference actor/witness pValues or relationship targets.")
    if float(metrics["effect_script_quality"]) < 0.98:
        actions.append("Ensure every bounded-number effect has an operator and non-zero constant.")
    if float(metrics["gating_score"]) < 0.25:
        actions.append("Add more conditional visibility gates for late payoffs and secret routes.")
    if float(metrics["ending_diversity_legacy"]) < 0.5:
        actions.append("Check ending diversity scoring; terminal/endings topology may not match verifier assumptions.")
    return actions


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score authored SweepWeave world quality using local verifier metrics.")
    parser.add_argument("--storyworld", required=True)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--out-json")
    parser.add_argument("--target-score", type=float, default=0.65)
    parser.add_argument("--min-options-per-encounter", type=float, default=3.0)
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if target score is not reached or structure is invalid.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    data = load_json(Path(args.storyworld))
    verifier_module = load_storyworld_env(repo_root)
    metrics = score_world(data, verifier_module, min_options=float(args.min_options_per_encounter))
    metrics["storyworld"] = str(Path(args.storyworld))
    metrics["target_score"] = float(args.target_score)
    metrics["pass"] = bool(metrics["structure_valid"]) and float(metrics["weighted_authoring_verifier_score"]) >= float(args.target_score)
    metrics["recommendations"] = recommendations(metrics)

    rendered = json.dumps(metrics, indent=2, ensure_ascii=True)
    if args.out_json:
        out = Path(args.out_json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(rendered + "\n", encoding="utf-8", newline="\n")
        print(out)
    else:
        print(rendered)

    return 0 if metrics["pass"] or not args.strict else 1


if __name__ == "__main__":
    raise SystemExit(main())
