#!/usr/bin/env python3
"""Extract JSON repair plans from campaign model responses.

Small/local models often add analysis text before the requested JSON. This
script records that as contract noncompliance while still extracting a fenced
or balanced JSON object when possible.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")


def extract_fenced_json(text: str) -> str | None:
    matches = re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL | re.IGNORECASE)
    if matches:
        return matches[-1].strip()
    return None


def balanced_json_candidates(text: str) -> list[str]:
    candidates: list[str] = []
    for start, char0 in enumerate(text):
        if char0 != "{":
            continue
        depth = 0
        in_string = False
        escape = False
        for index in range(start, len(text)):
            char = text[index]
            if in_string:
                if escape:
                    escape = False
                elif char == "\\":
                    escape = True
                elif char == '"':
                    in_string = False
                continue
            if char == '"':
                in_string = True
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    candidates.append(text[start : index + 1].strip())
                    break
    return candidates


def extract_json(text: str) -> tuple[dict[str, Any] | None, str, str | None]:
    fenced = extract_fenced_json(text)
    if fenced:
        try:
            parsed = json.loads(fenced)
        except json.JSONDecodeError as exc:
            return None, "fenced", f"JSONDecodeError: {exc}"
        if isinstance(parsed, dict):
            return parsed, "fenced", None
        return None, "fenced", "extracted JSON was not an object"
    last_error = None
    for candidate in balanced_json_candidates(text):
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError as exc:
            last_error = f"JSONDecodeError: {exc}"
            continue
        if isinstance(parsed, dict):
            return parsed, "balanced", None
        last_error = "extracted JSON was not an object"
    if last_error:
        return None, "balanced", last_error
    return None, "none", "no JSON object found"


def schema_keys_for_operation(operation: str) -> set[str]:
    if operation == "bounded_prose_rewrite_plan":
        return {"encounter_rewrites", "preserve_ids_and_mechanics"}
    if operation == "effect_operator_diversity_plan":
        return {"encounter_id", "operator_mix", "gate_or_effect_repairs"}
    if operation == "mcp_preflight_plan":
        return {"packet_budget_tokens", "recommended_cards", "no_model_call_needed"}
    if operation == "native_schema_receipt_plan":
        return {"run_native_planner", "append_teacher_rows", "do_not_ask_llm_to_route"}
    return set()


def validate_plan(plan: dict[str, Any], operation: str) -> dict[str, Any]:
    required = schema_keys_for_operation(operation)
    missing = sorted(key for key in required if key not in plan)
    return {
        "required_keys": sorted(required),
        "missing_keys": missing,
        "schema_key_pass": not missing,
    }


def find_jobs(campaign_dir: Path) -> list[Path]:
    jobs_dir = campaign_dir / "jobs"
    if not jobs_dir.exists():
        return []
    return sorted(path for path in jobs_dir.iterdir() if path.is_dir())


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract JSON plans from campaign model responses.")
    parser.add_argument("--campaign-dir", required=True)
    args = parser.parse_args()
    campaign_dir = Path(args.campaign_dir).resolve()
    rows: list[dict[str, Any]] = []
    for job_dir in find_jobs(campaign_dir):
        packet_path = job_dir / "packet.json"
        response_path = job_dir / "model_response.json"
        packet = read_json(packet_path) if packet_path.exists() else {}
        operation = str(packet.get("operation", ""))
        row: dict[str, Any] = {
            "job_id": job_dir.name,
            "operation": operation,
            "requires_model_call": packet.get("requires_model_call"),
            "has_response": response_path.exists(),
            "json_only_contract_pass": None,
            "extract_method": None,
            "extract_ok": False,
            "schema_key_pass": False,
        }
        if not response_path.exists():
            row["error"] = "missing_model_response"
            rows.append(row)
            continue
        response = read_json(response_path)
        if response.get("skipped"):
            row.update({"extract_ok": True, "schema_key_pass": True, "skipped": True})
            rows.append(row)
            continue
        content = str(response.get("content", ""))
        row["json_only_contract_pass"] = content.lstrip().startswith("{") and content.rstrip().endswith("}")
        plan, method, error = extract_json(content)
        row["extract_method"] = method
        if plan is None:
            row["error"] = error
            rows.append(row)
            continue
        validation = validate_plan(plan, operation)
        row.update(validation)
        row["extract_ok"] = True
        write_json(job_dir / "model_plan.json", plan)
        write_json(job_dir / "model_plan_status.json", row)
        rows.append(row)

    summary = {
        "campaign_dir": str(campaign_dir),
        "job_count": len(rows),
        "extract_ok_count": sum(1 for row in rows if row.get("extract_ok")),
        "schema_key_pass_count": sum(1 for row in rows if row.get("schema_key_pass")),
        "json_only_contract_pass_count": sum(1 for row in rows if row.get("json_only_contract_pass")),
        "rows": rows,
    }
    write_json(campaign_dir / "model_plan_extraction_summary.json", summary)
    with (campaign_dir / "model_plan_extraction_rows.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")
    print(str(campaign_dir / "model_plan_extraction_summary.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
