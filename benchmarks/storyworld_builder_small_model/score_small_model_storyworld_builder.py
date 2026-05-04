#!/usr/bin/env python3
"""Offline scorecard for small-model storyworld-builder experiments.

This script intentionally does not load an LLM. It scores generated artifacts and
run receipts so small-model experiments can optimize concrete failure modes.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]

CORE_TOP_LEVEL = ("characters", "authored_properties", "spools", "encounters")
TEXT_KEYS = (
    "title",
    "title_text",
    "text",
    "text_script",
    "description",
    "about_text",
)
SCRIPT_KEYS = (
    "visibility_script",
    "performability_script",
    "acceptability_script",
    "desirability_script",
    "availability_script",
)
CONSTANT_TRUE = {"", "true", "always", "1", "none", "null"}


def resolve_path(raw: str | None) -> Path | None:
    if not raw:
        return None
    path = Path(raw)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path


def clip01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def at_least(actual: float, target: float) -> float:
    if target <= 0:
        return 1.0
    return clip01(actual / target)


def at_most(actual: float, target: float) -> float:
    if target <= 0:
        return 0.0
    return clip01(target / max(actual, 1e-9))


def mean(values: Iterable[float]) -> float:
    vals = list(values)
    return sum(vals) / len(vals) if vals else 0.0


def token_estimate(text: str) -> int:
    return max(1, len(text.encode("utf-8", errors="replace")) // 4)


def script_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, dict):
        if isinstance(value.get("value"), str):
            return value["value"]
        return " ".join(script_text(v) for v in value.values())
    if isinstance(value, list):
        return " ".join(script_text(v) for v in value)
    return ""


def collect_texts(value: Any, out: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in TEXT_KEYS:
                text = script_text(child).strip()
                if text:
                    out.append(text)
            else:
                collect_texts(child, out)
    elif isinstance(value, list):
        for child in value:
            collect_texts(child, out)


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def script_is_nonconstant(value: Any) -> bool:
    text = normalize_text(script_text(value))
    if text in CONSTANT_TRUE:
        return False
    if any(token in text for token in ("property", "pvalue", "p2value", "keyring", "metric", "distance")):
        return True
    if any(op in text for op in (">", "<", ">=", "<=", "==", "!=", "and", "or", "blend", "nudge")):
        return True
    return len(text) > 24


def effect_operator(effect: Any) -> str:
    if isinstance(effect, str):
        return effect.split("(", 1)[0].strip() or "string_effect"
    if not isinstance(effect, dict):
        return type(effect).__name__
    for key in ("operator", "op", "type", "function", "name"):
        value = effect.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    for key, value in effect.items():
        if key.lower() not in {"inputs", "args", "value", "constant", "target", "property"}:
            if isinstance(value, (dict, list)):
                return str(key)
    return "dict_effect"


def effect_has_nonzero_constant(effect: Any) -> bool:
    if isinstance(effect, (int, float)):
        return abs(float(effect)) > 1e-9
    if isinstance(effect, str):
        return bool(re.search(r"[-+]?(?:\d*\.\d+|\d+)", effect))
    if isinstance(effect, dict):
        for value in effect.values():
            if effect_has_nonzero_constant(value):
                return True
    if isinstance(effect, list):
        return any(effect_has_nonzero_constant(v) for v in effect)
    return False


def reaction_effects(reaction: dict[str, Any]) -> list[Any]:
    for key in ("after_effects", "effects", "effect_scripts"):
        value = reaction.get(key)
        if isinstance(value, list):
            return value
        if value:
            return [value]
    return []


def extract_storyworld_metrics(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8-sig", errors="replace")
    metrics: dict[str, Any] = {
        "artifact": str(path),
        "bytes": path.stat().st_size if path.exists() else 0,
        "whole_context_token_estimate": token_estimate(raw),
        "valid_json": 0.0,
        "core_fields_present": 0.0,
    }
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        metrics["json_error"] = str(exc)
        return metrics

    metrics["valid_json"] = 1.0
    metrics["core_fields_present"] = mean(1.0 if key in data else 0.0 for key in CORE_TOP_LEVEL)
    encounters = data.get("encounters", [])
    characters = data.get("characters", [])
    properties = data.get("authored_properties", [])
    spools = data.get("spools", [])
    if not isinstance(encounters, list):
        encounters = []
    if not isinstance(characters, list):
        characters = []
    if not isinstance(properties, list):
        properties = []
    if not isinstance(spools, list):
        spools = []

    option_count = 0
    reaction_count = 0
    effect_count = 0
    nonterminal_encounters = 0
    terminal_encounters = 0
    gated_options = 0
    nonconstant_scripts = 0
    script_slots = 0
    effect_ops: Counter[str] = Counter()
    nonzero_effects = 0
    encounter_texts: list[str] = []
    reaction_texts: list[str] = []
    option_texts: list[str] = []

    for encounter in encounters:
        if not isinstance(encounter, dict):
            continue
        collect_texts({k: encounter.get(k) for k in TEXT_KEYS if k in encounter}, encounter_texts)
        options = encounter.get("options", [])
        if not isinstance(options, list):
            options = []
        if options:
            nonterminal_encounters += 1
        else:
            terminal_encounters += 1
        for key in SCRIPT_KEYS:
            if key in encounter:
                script_slots += 1
                if script_is_nonconstant(encounter.get(key)):
                    nonconstant_scripts += 1
        option_count += len(options)
        for option in options:
            if not isinstance(option, dict):
                continue
            collect_texts({k: option.get(k) for k in TEXT_KEYS if k in option}, option_texts)
            option_gated = False
            for key in SCRIPT_KEYS:
                if key in option:
                    script_slots += 1
                    if script_is_nonconstant(option.get(key)):
                        nonconstant_scripts += 1
                        option_gated = True
            if option_gated:
                gated_options += 1
            reactions = option.get("reactions", [])
            if not isinstance(reactions, list):
                reactions = []
            reaction_count += len(reactions)
            for reaction in reactions:
                if not isinstance(reaction, dict):
                    continue
                collect_texts({k: reaction.get(k) for k in TEXT_KEYS if k in reaction}, reaction_texts)
                for key in SCRIPT_KEYS:
                    if key in reaction:
                        script_slots += 1
                        if script_is_nonconstant(reaction.get(key)):
                            nonconstant_scripts += 1
                effects = reaction_effects(reaction)
                effect_count += len(effects)
                for effect in effects:
                    effect_ops[effect_operator(effect)] += 1
                    if effect_has_nonzero_constant(effect):
                        nonzero_effects += 1

    all_effects = sum(effect_ops.values())
    max_effect_share = (max(effect_ops.values()) / all_effects) if all_effects else 1.0
    ending_like = [
        e
        for e in encounters
        if isinstance(e, dict)
        and (
            not e.get("options")
            or str(e.get("id", "")).lower().startswith("page_end")
            or "ending" in normalize_text(script_text(e.get("title") or e.get("title_text") or ""))
        )
    ]
    encounter_norm = [normalize_text(t) for t in encounter_texts if normalize_text(t)]
    reaction_norm = [normalize_text(t) for t in reaction_texts if normalize_text(t)]

    metrics.update(
        {
            "characters": len(characters),
            "properties": len(properties),
            "spools": len(spools),
            "encounters": len(encounters),
            "nonterminal_encounters": nonterminal_encounters,
            "terminal_encounters": terminal_encounters,
            "ending_like_encounters": len(ending_like),
            "options": option_count,
            "reactions": reaction_count,
            "effects": effect_count,
            "options_per_nonterminal": option_count / max(nonterminal_encounters, 1),
            "reactions_per_option": reaction_count / max(option_count, 1),
            "effects_per_reaction": effect_count / max(reaction_count, 1),
            "gated_options": gated_options,
            "gated_option_ratio": gated_options / max(option_count, 1),
            "nonconstant_script_ratio": nonconstant_scripts / max(script_slots, 1),
            "effect_operator_variety": len(effect_ops),
            "effect_operator_dominance": max_effect_share,
            "nonzero_effect_ratio": nonzero_effects / max(effect_count, 1),
            "encounter_text_count": len(encounter_texts),
            "reaction_text_count": len(reaction_texts),
            "option_text_count": len(option_texts),
            "encounter_text_uniqueness": len(set(encounter_norm)) / max(len(encounter_norm), 1),
            "reaction_text_uniqueness": len(set(reaction_norm)) / max(len(reaction_norm), 1),
            "encounter_text_length_ok": mean(1.0 if 40 <= len(t.split()) <= 320 else 0.0 for t in encounter_texts),
            "reaction_text_length_ok": mean(1.0 if 8 <= len(t.split()) <= 180 else 0.0 for t in reaction_texts),
        }
    )
    return metrics


def load_run_summary(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}


def component_scores(metrics: dict[str, Any], row: dict[str, Any], run_summary: dict[str, Any]) -> dict[str, float]:
    context_budget = int(row.get("context_budget_tokens") or run_summary.get("context_budget_tokens") or 8192)
    max_packet_tokens = row.get("max_packet_tokens")
    if max_packet_tokens is not None:
        readiness = at_most(float(max_packet_tokens), float(context_budget))
    else:
        whole_tokens = float(metrics.get("whole_context_token_estimate", 0.0))
        condition = str(row.get("condition", "")).lower()
        if "packet" in condition or "mcp" in condition or "native" in condition:
            readiness = 0.9 if whole_tokens > context_budget else 0.8
        else:
            readiness = 0.35 if whole_tokens > context_budget else 0.7

    native_schema = float(run_summary.get("planner_agreement_rate", row.get("planner_agreement_rate", 0.5)))
    validity = mean([float(metrics.get("valid_json", 0.0)), float(metrics.get("core_fields_present", 0.0))])
    scale = mean(
        [
            at_least(float(metrics.get("encounters", 0.0)), float(row.get("target_encounters", 40))),
            at_least(float(metrics.get("ending_like_encounters", 0.0)), float(row.get("target_endings", 4))),
            at_least(float(metrics.get("characters", 0.0)), 2.0),
            at_least(float(metrics.get("properties", 0.0)), 4.0),
        ]
    )
    branching = mean(
        [
            at_least(float(metrics.get("options_per_nonterminal", 0.0)), 3.0),
            at_least(float(metrics.get("reactions_per_option", 0.0)), 2.0),
            at_least(float(metrics.get("effects_per_reaction", 0.0)), 2.0),
        ]
    )
    control_logic = mean(
        [
            at_least(float(metrics.get("gated_option_ratio", 0.0)), 0.08),
            at_least(float(metrics.get("nonconstant_script_ratio", 0.0)), 0.20),
            at_least(float(metrics.get("effect_operator_variety", 0.0)), 4.0),
            at_most(float(metrics.get("effect_operator_dominance", 1.0)), 0.65),
            at_least(float(metrics.get("nonzero_effect_ratio", 0.0)), 0.85),
        ]
    )
    text_surface = mean(
        [
            float(metrics.get("encounter_text_uniqueness", 0.0)),
            float(metrics.get("reaction_text_uniqueness", 0.0)),
            float(metrics.get("encounter_text_length_ok", 0.0)),
            float(metrics.get("reaction_text_length_ok", 0.0)),
        ]
    )
    score = (
        0.18 * validity
        + 0.10 * scale
        + 0.18 * branching
        + 0.20 * control_logic
        + 0.12 * text_surface
        + 0.12 * readiness
        + 0.10 * native_schema
    )
    return {
        "validity": round(validity, 4),
        "scale": round(scale, 4),
        "branching": round(branching, 4),
        "control_logic": round(control_logic, 4),
        "text_surface": round(text_surface, 4),
        "small_model_readiness": round(readiness, 4),
        "native_schema": round(native_schema, 4),
        "small_model_builder_score": round(score, 4),
    }


def improvement_hint(components: dict[str, float]) -> str:
    candidates = {k: v for k, v in components.items() if k != "small_model_builder_score"}
    weakest = min(candidates, key=candidates.get)
    return {
        "validity": "Switch from whole JSON generation to deterministic materialization from packets.",
        "scale": "Ask the model for an encounter inventory and ending matrix before prose.",
        "branching": "Route only option/reaction/effect slot filling; enforce target counts.",
        "control_logic": "Use native routes for gates/effects; oversample effect and secret-route repair rows.",
        "text_surface": "Run bounded prose rewrite packets after mechanics pass.",
        "small_model_readiness": "Run MCP preflight and keep every packet under the context budget.",
        "native_schema": "Run native planner receipts and append teacher rows before learned routing.",
    }[weakest]


def read_manifest(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        row = json.loads(stripped)
        row["_manifest_line"] = line_no
        rows.append(row)
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "rank",
        "run_id",
        "model",
        "condition",
        "score",
        "validity",
        "scale",
        "branching",
        "control_logic",
        "text_surface",
        "small_model_readiness",
        "native_schema",
        "encounters",
        "options_per_nonterminal",
        "reactions_per_option",
        "effects_per_reaction",
        "gated_option_ratio",
        "effect_operator_variety",
        "hint",
        "artifact",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for idx, row in enumerate(rows, start=1):
            components = row["components"]
            metrics = row["metrics"]
            writer.writerow(
                {
                    "rank": idx,
                    "run_id": row["run_id"],
                    "model": row["model"],
                    "condition": row["condition"],
                    "score": components["small_model_builder_score"],
                    "validity": components["validity"],
                    "scale": components["scale"],
                    "branching": components["branching"],
                    "control_logic": components["control_logic"],
                    "text_surface": components["text_surface"],
                    "small_model_readiness": components["small_model_readiness"],
                    "native_schema": components["native_schema"],
                    "encounters": metrics.get("encounters", 0),
                    "options_per_nonterminal": round(float(metrics.get("options_per_nonterminal", 0.0)), 3),
                    "reactions_per_option": round(float(metrics.get("reactions_per_option", 0.0)), 3),
                    "effects_per_reaction": round(float(metrics.get("effects_per_reaction", 0.0)), 3),
                    "gated_option_ratio": round(float(metrics.get("gated_option_ratio", 0.0)), 3),
                    "effect_operator_variety": metrics.get("effect_operator_variety", 0),
                    "hint": row["improvement_hint"],
                    "artifact": row["artifact"],
                }
            )


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# Small-Model Storyworld Builder Scorecard",
        "",
        f"- Manifest: `{report['manifest']}`",
        f"- Rows: `{report['count']}`",
        "",
        "| Rank | Run | Model | Condition | Score | Weakest Fix |",
        "|---:|---|---|---|---:|---|",
    ]
    for idx, row in enumerate(report["ranked"], start=1):
        lines.append(
            "| {rank} | `{run_id}` | `{model}` | `{condition}` | {score:.4f} | {hint} |".format(
                rank=idx,
                run_id=row["run_id"],
                model=row["model"],
                condition=row["condition"],
                score=float(row["components"]["small_model_builder_score"]),
                hint=row["improvement_hint"],
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Use this as a fast optimization target for small-model runs. A low component score should become the next bounded packet or native-schema repair target, not a larger one-shot prompt.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score small-model storyworld-builder artifacts.")
    parser.add_argument("--manifest", required=True, help="JSONL rows describing generated artifacts.")
    parser.add_argument("--out-dir", required=True, help="Directory for scorecard outputs.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest_path = resolve_path(args.manifest)
    if manifest_path is None or not manifest_path.exists():
        raise SystemExit(f"Manifest not found: {args.manifest}")
    out_dir = resolve_path(args.out_dir)
    if out_dir is None:
        raise SystemExit("Invalid --out-dir")
    out_dir.mkdir(parents=True, exist_ok=True)

    scored: list[dict[str, Any]] = []
    for row in read_manifest(manifest_path):
        artifact = resolve_path(row.get("artifact"))
        if artifact is None or not artifact.exists():
            scored.append(
                {
                    "run_id": row.get("run_id", f"line_{row['_manifest_line']}"),
                    "model": row.get("model", ""),
                    "condition": row.get("condition", ""),
                    "artifact": str(artifact) if artifact else "",
                    "error": "artifact_not_found",
                    "components": {"small_model_builder_score": 0.0},
                    "metrics": {},
                    "improvement_hint": "Fix manifest artifact path.",
                }
            )
            continue
        run_summary = load_run_summary(resolve_path(row.get("run_summary")))
        metrics = extract_storyworld_metrics(artifact)
        components = component_scores(metrics, row, run_summary)
        scored.append(
            {
                "run_id": row.get("run_id", artifact.stem),
                "model": row.get("model", ""),
                "condition": row.get("condition", ""),
                "artifact": str(artifact),
                "notes": row.get("notes", ""),
                "metrics": metrics,
                "components": components,
                "run_summary": {
                    key: run_summary.get(key)
                    for key in (
                        "planner",
                        "planner_agreement",
                        "planner_agreement_rate",
                        "context_budget_tokens",
                        "oracle_rows",
                    )
                    if key in run_summary
                },
                "improvement_hint": improvement_hint(components),
            }
        )

    scored.sort(key=lambda r: float(r["components"].get("small_model_builder_score", 0.0)), reverse=True)
    report = {
        "manifest": str(manifest_path),
        "count": len(scored),
        "ranked": scored,
        "score_weights": {
            "validity": 0.18,
            "scale": 0.10,
            "branching": 0.18,
            "control_logic": 0.20,
            "text_surface": 0.12,
            "small_model_readiness": 0.12,
            "native_schema": 0.10,
        },
    }
    (out_dir / "scorecard.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    write_csv(out_dir / "scorecard.csv", scored)
    write_markdown(out_dir / "scorecard.md", report)
    print(str(out_dir / "scorecard.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
