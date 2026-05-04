#!/usr/bin/env python3
"""Repair schema-invalid small-model storyworld-builder campaign plans.

This is the validator/TRM-style retry stage: keep the original bounded packet,
show the malformed model response as evidence, and ask the local model for only
the minimal schema-valid JSON plan. Successful repairs overwrite model_plan.json
so the existing materializer can consume them.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

from extract_campaign_model_plans import extract_json, read_json, schema_keys_for_operation, validate_plan, write_json
from run_small_model_builder_campaign import call_model, token_estimate


def find_jobs(campaign_dir: Path) -> list[Path]:
    jobs_dir = campaign_dir / "jobs"
    if not jobs_dir.exists():
        return []
    return sorted(path for path in jobs_dir.iterdir() if path.is_dir())


def response_content(job_dir: Path) -> str:
    response_path = job_dir / "model_response.json"
    if response_path.exists():
        response = read_json(response_path)
        return str(response.get("content", ""))
    text_path = job_dir / "model_response.txt"
    if text_path.exists():
        return text_path.read_text(encoding="utf-8", errors="replace")
    return ""


def status_row(job_dir: Path) -> dict[str, Any]:
    status_path = job_dir / "model_plan_status.json"
    if status_path.exists():
        status = read_json(status_path)
        if isinstance(status, dict):
            return status
    return {}


def compact_cards(packet: dict[str, Any], max_cards: int) -> list[dict[str, Any]]:
    cards = packet.get("bounded_context_cards", [])
    if not isinstance(cards, list):
        return []
    compacted: list[dict[str, Any]] = []
    for card in cards[: max(0, max_cards)]:
        if not isinstance(card, dict):
            continue
        compacted.append(
            {
                "id": card.get("id"),
                "title": card.get("title"),
                "body": card.get("body"),
                "option_count": card.get("option_count"),
                "reaction_count": card.get("reaction_count"),
                "effect_operators": card.get("effect_operators"),
                "sample_options": card.get("sample_options"),
            }
        )
    return compacted


def operation_guidance(operation: str) -> str:
    if operation == "bounded_prose_rewrite_plan":
        return (
            "For bounded_prose_rewrite_plan, return encounter_rewrites and "
            "preserve_ids_and_mechanics. Include 1-3 rewrites from the cards. "
            "Each body should be 70-150 words. Keep reaction_rewrites in option "
            "order and make each reaction 12-50 words."
        )
    if operation == "effect_operator_diversity_plan":
        return (
            "For effect_operator_diversity_plan, return encounter_id, "
            "operator_mix, and gate_or_effect_repairs. Pick an existing "
            "encounter id from the cards and use repair strings, not full JSON."
        )
    if operation == "schema_repair_plan":
        return "For schema_repair_plan, return only the diagnosis, packet_fields_needed, and materializer_constraints keys."
    return "Return exactly the required top-level keys for this operation."


def build_repair_prompt(
    *,
    packet: dict[str, Any],
    original_response: str,
    previous_response: str,
    attempt: int,
    max_cards: int,
    max_bad_chars: int,
) -> str:
    operation = str(packet.get("operation", ""))
    required = sorted(schema_keys_for_operation(operation))
    bad_excerpt = original_response[-max_bad_chars:]
    previous_excerpt = previous_response[-max_bad_chars:] if previous_response else ""
    payload = {
        "repair_attempt": attempt,
        "job_id": packet.get("job_id"),
        "operation": operation,
        "required_top_level_keys": required,
        "output_schema": packet.get("output_schema"),
        "bounded_context_cards": compact_cards(packet, max_cards),
        "malformed_response_excerpt": bad_excerpt,
        **({"previous_repair_excerpt": previous_excerpt} if previous_excerpt else {}),
    }
    return (
        "Return only one minified JSON object. Start with { and end with }.\n"
        "No analysis, no markdown, no code fences, no <think> text.\n"
        "You are the JSON repair gate in a MeTTa/MCP/TRM storyworld factory.\n"
        "Repair the malformed response into a minimal valid plan. Do not output full storyworld JSON.\n"
        f"{operation_guidance(operation)}\n\n"
        + json.dumps(payload, indent=2, ensure_ascii=True)
    )


def first_active_card(packet: dict[str, Any]) -> dict[str, Any]:
    cards = compact_cards(packet, max_cards=20)
    for card in cards:
        if card.get("id") and (card.get("body") or card.get("sample_options")):
            return card
    return cards[0] if cards else {"id": "page_0000", "title": "Untitled Encounter", "body": "", "sample_options": []}


def fallback_reaction(option: dict[str, Any], index: int) -> str:
    samples = option.get("sample_reactions", [])
    if isinstance(samples, list):
        for sample in samples:
            text = str(sample).strip()
            words = text.split()
            if 12 <= len(words) <= 50:
                return text
    option_text = str(option.get("text", "")).strip() or f"option {index + 1}"
    return (
        f"The choice around {option_text[:80]} changes the local balance without changing IDs, "
        "giving the verifier a concrete reaction trace to score."
    )


def deterministic_fallback_plan(packet: dict[str, Any]) -> dict[str, Any] | None:
    operation = str(packet.get("operation", ""))
    card = first_active_card(packet)
    encounter_id = str(card.get("id") or "page_0000")
    if operation == "effect_operator_diversity_plan":
        sample_options = card.get("sample_options", [])
        target = encounter_id
        if isinstance(sample_options, list) and sample_options:
            first = sample_options[0]
            if isinstance(first, dict) and first.get("id"):
                target = str(first["id"])
        return {
            "encounter_id": encounter_id,
            "operator_mix": ["Nudge", "Blend", "Average", "Clamp"],
            "gate_or_effect_repairs": [
                {
                    "target": target,
                    "repair": "Use Nudge for the immediate variable delta, Blend for relationship state, and Clamp for bounded ending pressure.",
                }
            ],
        }
    if operation == "bounded_prose_rewrite_plan":
        title = str(card.get("title") or "Reframed Encounter").strip() or "Reframed Encounter"
        body = str(card.get("body") or "").strip()
        if len(body.split()) < 70:
            body = (
                f"{title} becomes a focused scene where the local stakes, hidden pressure, and next mechanical "
                "consequences are made legible without changing the graph. The player can read the social field, "
                "infer why each choice matters, and anticipate that reactions will move distinct variables rather "
                "than merely decorate the passage. This rewrite preserves the encounter identity while giving the "
                "storyworld builder enough surface detail for calibration, verifier scoring, and later repair."
            )
        sample_options = card.get("sample_options", [])
        reaction_rewrites: list[str] = []
        if isinstance(sample_options, list):
            reaction_rewrites = [
                fallback_reaction(option, index)
                for index, option in enumerate(sample_options)
                if isinstance(option, dict)
            ]
        return {
            "encounter_rewrites": [
                {
                    "encounter_id": encounter_id,
                    "title": title[:80],
                    "body": body,
                    "reaction_rewrites": reaction_rewrites,
                }
            ],
            "preserve_ids_and_mechanics": True,
        }
    return None


def repair_job(
    job_dir: Path,
    *,
    base_url: str,
    model: str,
    timeout: int,
    max_response_tokens: int,
    attempts: int,
    max_cards: int,
    max_bad_chars: int,
    allow_deterministic_fallback: bool,
) -> dict[str, Any]:
    packet_path = job_dir / "packet.json"
    if not packet_path.exists():
        return {"job_id": job_dir.name, "attempted": False, "reason": "missing_packet"}
    packet = read_json(packet_path)
    operation = str(packet.get("operation", ""))
    if not bool(packet.get("requires_model_call", True)):
        return {"job_id": job_dir.name, "operation": operation, "attempted": False, "reason": "scaffold_owned_job"}
    current_status = status_row(job_dir)
    if current_status.get("schema_key_pass") and (job_dir / "model_plan.json").exists():
        return {"job_id": job_dir.name, "operation": operation, "attempted": False, "reason": "already_schema_valid"}

    original = response_content(job_dir)
    row: dict[str, Any] = {
        "job_id": job_dir.name,
        "operation": operation,
        "attempted": True,
        "repaired": False,
        "attempts": [],
    }
    previous = ""
    for attempt in range(1, max(1, attempts) + 1):
        prompt = build_repair_prompt(
            packet=packet,
            original_response=original,
            previous_response=previous,
            attempt=attempt,
            max_cards=max_cards,
            max_bad_chars=max_bad_chars,
        )
        (job_dir / f"repair_prompt_{attempt}.md").write_text(prompt + "\n", encoding="utf-8", newline="\n")
        response = call_model(base_url, model, prompt, timeout=timeout, max_tokens=max_response_tokens)
        write_json(job_dir / f"model_response_repair_{attempt}.json", response)
        content = str(response.get("content", ""))
        if content:
            (job_dir / f"model_response_repair_{attempt}.txt").write_text(content + "\n", encoding="utf-8", newline="\n")
        plan, method, error = extract_json(content, operation)
        validation = validate_plan(plan, operation) if isinstance(plan, dict) else {"schema_key_pass": False}
        attempt_row = {
            "attempt": attempt,
            "model_ok": response.get("ok"),
            "seconds": response.get("seconds"),
            "prompt_token_estimate": token_estimate(prompt),
            "json_only_contract_pass": content.lstrip().startswith("{") and content.rstrip().endswith("}"),
            "extract_method": method,
            "extract_ok": isinstance(plan, dict),
            "schema_key_pass": validation.get("schema_key_pass", False),
            **({"error": error} if error else {}),
            **({"missing_keys": validation.get("missing_keys")} if isinstance(plan, dict) else {}),
        }
        row["attempts"].append(attempt_row)
        if isinstance(plan, dict) and validation.get("schema_key_pass"):
            write_json(job_dir / "model_plan.json", plan)
            status = {
                "job_id": job_dir.name,
                "operation": operation,
                "requires_model_call": True,
                "has_response": True,
                "repaired": True,
                **attempt_row,
                **validate_plan(plan, operation),
            }
            write_json(job_dir / "model_plan_status.json", status)
            row.update({"repaired": True, "repair_source": "model", "final_attempt": attempt})
            return row
        previous = content

    if allow_deterministic_fallback:
        plan = deterministic_fallback_plan(packet)
        validation = validate_plan(plan, operation) if isinstance(plan, dict) else {"schema_key_pass": False}
        if isinstance(plan, dict) and validation.get("schema_key_pass"):
            fallback_response = {
                "ok": True,
                "skipped_model_repair": True,
                "repair_source": "deterministic_fallback",
                "content": json.dumps(plan, separators=(",", ":"), ensure_ascii=True),
            }
            write_json(job_dir / "model_response_repair_fallback.json", fallback_response)
            (job_dir / "model_response_repair_fallback.txt").write_text(
                str(fallback_response["content"]) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            write_json(job_dir / "model_plan.json", plan)
            status = {
                "job_id": job_dir.name,
                "operation": operation,
                "requires_model_call": True,
                "has_response": True,
                "repaired": True,
                "repair_source": "deterministic_fallback",
                **validate_plan(plan, operation),
            }
            write_json(job_dir / "model_plan_status.json", status)
            row.update({"repaired": True, "repair_source": "deterministic_fallback"})
            return row

    return row


def write_summary_md(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Campaign Plan Repair",
        "",
        f"- Campaign: `{summary['campaign_dir']}`",
        f"- Jobs: `{summary['job_count']}`",
        f"- Attempted: `{summary['attempted_count']}`",
        f"- Repaired: `{summary['repaired_count']}`",
        "",
        "| Job | Operation | Attempted | Repaired | Source |",
        "|---|---|---:|---:|---|",
    ]
    for row in summary["rows"]:
        lines.append(
            "| `{job_id}` | `{operation}` | {attempted} | {repaired} | `{source}` |".format(
                job_id=row.get("job_id"),
                operation=row.get("operation", ""),
                attempted=1 if row.get("attempted") else 0,
                repaired=1 if row.get("repaired") else 0,
                source=row.get("repair_source", row.get("reason", "")),
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Repair invalid model plans in a small-model builder campaign.")
    parser.add_argument("--campaign-dir", required=True)
    parser.add_argument("--base-url", default="http://127.0.0.1:8081/v1")
    parser.add_argument("--model", default="Qwen3.5-3B.Q4_K_M.gguf")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--max-response-tokens", type=int, default=1800)
    parser.add_argument("--attempts", type=int, default=1)
    parser.add_argument("--max-cards", type=int, default=5)
    parser.add_argument("--max-bad-chars", type=int, default=9000)
    parser.add_argument("--allow-deterministic-fallback", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    campaign_dir = Path(args.campaign_dir).resolve()
    rows = [
        repair_job(
            job_dir,
            base_url=args.base_url,
            model=args.model,
            timeout=args.timeout,
            max_response_tokens=args.max_response_tokens,
            attempts=args.attempts,
            max_cards=args.max_cards,
            max_bad_chars=args.max_bad_chars,
            allow_deterministic_fallback=args.allow_deterministic_fallback,
        )
        for job_dir in find_jobs(campaign_dir)
    ]
    summary = {
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "campaign_dir": str(campaign_dir),
        "job_count": len(rows),
        "attempted_count": sum(1 for row in rows if row.get("attempted")),
        "repaired_count": sum(1 for row in rows if row.get("repaired")),
        "rows": rows,
    }
    write_json(campaign_dir / "repair_summary.json", summary)
    write_summary_md(campaign_dir / "repair_summary.md", summary)
    print(str(campaign_dir / "repair_summary.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
