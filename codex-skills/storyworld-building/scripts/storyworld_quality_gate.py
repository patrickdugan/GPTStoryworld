#!/usr/bin/env python3
"""Quality gate for one-shot storyworld generation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from polish_metrics import POLISH_THRESHOLDS, compute_metrics, count_vars
from sweepweave_validator import validate_storyworld


def _word_count(script: Any) -> int:
    if isinstance(script, dict):
        if script.get("pointer_type") == "String Constant":
            return len(str(script.get("value", "")).split())
        total = 0
        for value in script.values():
            total += _word_count(value)
        return total
    if isinstance(script, list):
        return sum(_word_count(item) for item in script)
    return len(str(script).split()) if isinstance(script, str) else 0


def _collect_pointer_refs(node: Any, out: List[Tuple[str, int]]) -> None:
    if isinstance(node, dict):
        if node.get("pointer_type") == "Bounded Number Pointer":
            keyring = node.get("keyring") or []
            if keyring and isinstance(keyring, list):
                prop = str(keyring[0])
                out.append((prop, len(keyring)))
        for value in node.values():
            _collect_pointer_refs(value, out)
        return
    if isinstance(node, list):
        for item in node:
            _collect_pointer_refs(item, out)


def _is_ending(encounter: Dict[str, Any]) -> bool:
    eid = str(encounter.get("id", ""))
    if eid.startswith("page_end") or eid.startswith("page_secret"):
        return True
    options = encounter.get("options", []) or []
    return len(options) == 0


def _safe_mean(values: Iterable[float]) -> float:
    vals = list(values)
    return float(mean(vals)) if vals else 0.0


def _check(name: str, actual: float, target: float) -> Dict[str, Any]:
    return {
        "name": name,
        "actual": round(actual, 4),
        "target": target,
        "pass": actual >= target,
    }


def evaluate_storyworld(data: Dict[str, Any], validation_errors: List[str]) -> Dict[str, Any]:
    metrics = compute_metrics(data)
    encounters = data.get("encounters", []) or []

    encounter_words: List[int] = []
    reaction_words: List[int] = []
    variable_counts: List[int] = []
    pvalue_refs = 0
    p2value_refs = 0

    for encounter in encounters:
        if not _is_ending(encounter):
            text_words = _word_count(encounter.get("text_script")) + _word_count(encounter.get("prompt_script"))
            encounter_words.append(text_words)
        for option in encounter.get("options", []) or []:
            for reaction in option.get("reactions", []) or []:
                reaction_words.append(_word_count(reaction.get("text_script")))
                variable_counts.append(count_vars(reaction.get("desirability_script")))

                refs: List[Tuple[str, int]] = []
                _collect_pointer_refs(reaction.get("desirability_script"), refs)
                _collect_pointer_refs(reaction.get("after_effects"), refs)
                for prop, depth in refs:
                    if prop.startswith("p"):
                        if depth >= 2:
                            p2value_refs += 1
                        else:
                            pvalue_refs += 1

    checks = [
        _check(
            "options_per_encounter",
            float(metrics["options_per_encounter"]),
            float(POLISH_THRESHOLDS["options_per_encounter"]),
        ),
        _check(
            "reactions_per_option",
            float(metrics["reactions_per_option"]),
            float(POLISH_THRESHOLDS["reactions_per_option"]),
        ),
        _check(
            "effects_per_reaction",
            float(metrics["effects_per_reaction"]),
            float(POLISH_THRESHOLDS["effects_per_reaction"]),
        ),
        _check(
            "desirability_vars_per_reaction",
            float(metrics["desirability_vars_avg"]),
            float(POLISH_THRESHOLDS["desirability_vars_per_reaction"]),
        ),
        _check("avg_encounter_words", _safe_mean(encounter_words), 50.0),
        _check("avg_reaction_words", _safe_mean(reaction_words), 20.0),
        _check("pvalue_refs", float(pvalue_refs), 1.0),
        _check("p2value_refs", float(p2value_refs), 1.0),
    ]

    checks.append(
        {
            "name": "validator_errors",
            "actual": len(validation_errors),
            "target": 0,
            "pass": len(validation_errors) == 0,
        }
    )

    failures = [c["name"] for c in checks if not c["pass"]]

    return {
        "checks": checks,
        "pass": len(failures) == 0,
        "failures": failures,
        "summary": {
            "encounters": len(encounters),
            "avg_encounter_words": round(_safe_mean(encounter_words), 2),
            "avg_reaction_words": round(_safe_mean(reaction_words), 2),
            "avg_desirability_vars": round(_safe_mean(variable_counts), 2),
            "pvalue_refs": pvalue_refs,
            "p2value_refs": p2value_refs,
        },
        "polish_metrics": metrics,
        "validator_errors": validation_errors,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Storyworld one-shot quality gate")
    parser.add_argument("--storyworld", required=True, help="Path to storyworld JSON")
    parser.add_argument("--report-out", default="", help="Optional report JSON output path")
    parser.add_argument("--strict", action="store_true", help="Return non-zero exit code when checks fail")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    storyworld_path = Path(args.storyworld).resolve()
    with storyworld_path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)

    validation_errors = validate_storyworld(str(storyworld_path))
    report = evaluate_storyworld(data, validation_errors)
    report["storyworld"] = str(storyworld_path)

    output = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True)
    if args.report_out:
        out_path = Path(args.report_out).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output + "\n", encoding="utf-8", newline="\n")
        print(str(out_path))
    else:
        print(output)

    if args.strict and not report["pass"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
