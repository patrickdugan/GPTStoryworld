#!/usr/bin/env python3
"""Materialize safe campaign model plans into candidate storyworld copies.

Only bounded prose rewrite plans are applied automatically. Control-logic plans
are retained as teacher data because effect operator patches are schema-specific
and should not be guessed from prose targets.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")


def script_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        raw = value.get("value")
        if isinstance(raw, str):
            return raw
        return " ".join(script_text(v) for v in value.values())
    if isinstance(value, list):
        return " ".join(script_text(v) for v in value)
    return ""


def set_script_value(container: dict[str, Any], keys: tuple[str, ...], text: str, fallback_key: str) -> str:
    for key in keys:
        if key not in container:
            continue
        current = container.get(key)
        if isinstance(current, dict):
            current["value"] = text
            return key
        container[key] = text
        return key
    container[fallback_key] = text
    return fallback_key


def encounter_id(encounter: dict[str, Any]) -> str:
    raw = encounter.get("id") or encounter.get("encounter_id") or encounter.get("name")
    return str(raw) if raw else ""


def reaction_iter(encounter: dict[str, Any]):
    options = encounter.get("options", [])
    if not isinstance(options, list):
        return
    for option in options:
        if not isinstance(option, dict):
            continue
        reactions = option.get("reactions", [])
        if not isinstance(reactions, list):
            continue
        for reaction in reactions:
            if isinstance(reaction, dict):
                yield reaction


def apply_bounded_prose_plan(world: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    rewrites = plan.get("encounter_rewrites", [])
    if not isinstance(rewrites, list):
        return {"applied": 0, "errors": ["encounter_rewrites_not_list"], "touched": []}
    encounters = world.get("encounters", [])
    if not isinstance(encounters, list):
        return {"applied": 0, "errors": ["world_encounters_not_list"], "touched": []}
    by_id = {encounter_id(enc): enc for enc in encounters if isinstance(enc, dict)}
    touched: list[dict[str, Any]] = []
    errors: list[str] = []
    applied = 0
    for rewrite in rewrites:
        if not isinstance(rewrite, dict):
            continue
        target_id = str(rewrite.get("encounter_id", ""))
        encounter = by_id.get(target_id)
        if encounter is None:
            errors.append(f"missing_encounter:{target_id}")
            continue
        entry: dict[str, Any] = {"encounter_id": target_id}
        title = rewrite.get("title")
        if isinstance(title, str) and title.strip():
            entry["title_field"] = set_script_value(encounter, ("title_text", "title", "name"), title.strip(), "title")
        body = rewrite.get("body")
        if isinstance(body, str) and body.strip():
            entry["body_field"] = set_script_value(
                encounter,
                ("body_text", "text_script", "text", "description"),
                body.strip(),
                "text_script",
            )
        reaction_rewrites = rewrite.get("reaction_rewrites", [])
        reaction_count = 0
        if isinstance(reaction_rewrites, list):
            for reaction, reaction_text in zip(reaction_iter(encounter), reaction_rewrites):
                if isinstance(reaction_text, str) and reaction_text.strip():
                    set_script_value(reaction, ("text_script", "text", "description"), reaction_text.strip(), "text_script")
                    reaction_count += 1
        entry["reaction_rewrites_applied"] = reaction_count
        touched.append(entry)
        applied += 1
    return {"applied": applied, "errors": errors, "touched": touched}


def campaign_jobs(campaign_dir: Path) -> list[Path]:
    jobs_dir = campaign_dir / "jobs"
    if not jobs_dir.exists():
        return []
    return sorted(path for path in jobs_dir.iterdir() if path.is_dir())


def main() -> int:
    parser = argparse.ArgumentParser(description="Materialize safe campaign plans into candidate storyworlds.")
    parser.add_argument("--campaign-dir", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--run-summary", default="", help="Optional run_summary.json receipt to attach to candidate manifest rows.")
    parser.add_argument("--context-budget-tokens", type=int, default=32768)
    args = parser.parse_args()
    campaign_dir = Path(args.campaign_dir).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    manifest_lines: list[str] = []
    for job_dir in campaign_jobs(campaign_dir):
        packet_path = job_dir / "packet.json"
        plan_path = job_dir / "model_plan.json"
        if not packet_path.exists():
            continue
        packet = read_json(packet_path)
        job_id = job_dir.name
        operation = str(packet.get("operation", ""))
        source = Path(str(packet.get("artifact", "")))
        row: dict[str, Any] = {
            "job_id": job_id,
            "operation": operation,
            "source_artifact": str(source),
            "applied": False,
        }
        if not plan_path.exists():
            row["reason"] = "missing_model_plan"
            rows.append(row)
            continue
        if operation != "bounded_prose_rewrite_plan":
            row["reason"] = "operation_requires_schema_specific_materializer"
            rows.append(row)
            continue
        if not source.exists():
            row["reason"] = "source_artifact_missing"
            rows.append(row)
            continue
        world = read_json(source)
        plan = read_json(plan_path)
        result = apply_bounded_prose_plan(world, plan)
        candidate = out_dir / "candidates" / f"{job_id}.json"
        write_json(candidate, world)
        row.update({"applied": True, "candidate": str(candidate), "result": result})
        rows.append(row)
        manifest_lines.append(
            json.dumps(
                {
                    "run_id": f"{job_id}_candidate",
                    "model": "teacher_materialized",
                    "condition": "bounded_prose_rewrite_candidate_native" if args.run_summary else "bounded_prose_rewrite_candidate",
                    "artifact": str(candidate),
                    "context_budget_tokens": args.context_budget_tokens,
                    **({"run_summary": args.run_summary} if args.run_summary else {}),
                    "notes": f"Materialized from campaign job {job_id}.",
                },
                ensure_ascii=True,
            )
        )
    write_json(out_dir / "materialization_summary.json", {"campaign_dir": str(campaign_dir), "rows": rows})
    (out_dir / "candidate_manifest.jsonl").write_text("\n".join(manifest_lines) + ("\n" if manifest_lines else ""), encoding="utf-8", newline="\n")
    print(str(out_dir / "materialization_summary.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
