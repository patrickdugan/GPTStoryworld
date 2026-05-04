#!/usr/bin/env python3
"""Build bounded small-model repair jobs from a storyworld-builder scorecard.

The runner is safe by default: it emits prompt packets and TRM-style job rows
without calling a model. Use --call-model only when an OpenAI-compatible local
endpoint is already running.
"""

from __future__ import annotations

import argparse
import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
COMPONENT_ORDER = (
    "validity",
    "scale",
    "branching",
    "control_logic",
    "text_surface",
    "small_model_readiness",
    "native_schema",
)
SCRIPT_KEYS = (
    "visibility_script",
    "performability_script",
    "acceptability_script",
    "desirability_script",
    "availability_script",
)


def resolve_path(raw: str | None) -> Path | None:
    if not raw:
        return None
    path = Path(raw)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


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


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def token_estimate(text: str) -> int:
    return max(1, len(text.encode("utf-8", errors="replace")) // 4)


def effect_operator(effect: Any) -> str:
    if isinstance(effect, str):
        return effect.split("(", 1)[0].strip() or "string_effect"
    if not isinstance(effect, dict):
        return type(effect).__name__
    for key in ("operator", "op", "type", "function", "name", "operator_type"):
        value = effect.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    for key, value in effect.items():
        if key.lower() not in {"inputs", "args", "value", "constant", "target", "property", "set"}:
            if isinstance(value, (dict, list)):
                return str(key)
    return "dict_effect"


def reaction_effects(reaction: dict[str, Any]) -> list[Any]:
    for key in ("after_effects", "effects", "effect_scripts"):
        value = reaction.get(key)
        if isinstance(value, list):
            return value
        if value:
            return [value]
    return []


def get_encounter_id(encounter: dict[str, Any], index: int) -> str:
    raw = encounter.get("id") or encounter.get("encounter_id") or encounter.get("name")
    return str(raw) if raw else f"encounter_{index:04d}"


def encounter_title(encounter: dict[str, Any]) -> str:
    return normalize(script_text(encounter.get("title") or encounter.get("title_text") or encounter.get("name")))[:160]


def encounter_body(encounter: dict[str, Any]) -> str:
    return normalize(script_text(encounter.get("body_text") or encounter.get("text_script") or encounter.get("text")))[:900]


def option_text(option: dict[str, Any]) -> str:
    return normalize(script_text(option.get("text_script") or option.get("text") or option.get("label")))[:240]


def reaction_text(reaction: dict[str, Any]) -> str:
    return normalize(script_text(reaction.get("text_script") or reaction.get("text") or reaction.get("description")))[:260]


def count_nonconstant_scripts(node: dict[str, Any]) -> int:
    total = 0
    for key in SCRIPT_KEYS:
        text = normalize(script_text(node.get(key, ""))).lower()
        if text and text not in {"true", "always", "1", "none", "null"}:
            total += 1
    return total


def summarize_encounter(encounter: dict[str, Any], index: int) -> dict[str, Any]:
    options = encounter.get("options", [])
    if not isinstance(options, list):
        options = []
    reaction_count = 0
    effect_ops: list[str] = []
    sample_options: list[dict[str, Any]] = []
    nonconstant_scripts = count_nonconstant_scripts(encounter)
    for option in options:
        if not isinstance(option, dict):
            continue
        reactions = option.get("reactions", [])
        if not isinstance(reactions, list):
            reactions = []
        reaction_count += len(reactions)
        nonconstant_scripts += count_nonconstant_scripts(option)
        sample_reactions: list[str] = []
        for reaction in reactions[:2]:
            if not isinstance(reaction, dict):
                continue
            nonconstant_scripts += count_nonconstant_scripts(reaction)
            sample_reactions.append(reaction_text(reaction))
            for effect in reaction_effects(reaction):
                effect_ops.append(effect_operator(effect))
        if len(sample_options) < 4:
            sample_options.append(
                {
                    "id": option.get("id") or option.get("option_id"),
                    "text": option_text(option),
                    "reaction_count": len(reactions),
                    "sample_reactions": sample_reactions,
                }
            )
    unique_effect_ops = sorted(set(effect_ops))
    return {
        "id": get_encounter_id(encounter, index),
        "title": encounter_title(encounter),
        "body": encounter_body(encounter),
        "option_count": len(options),
        "reaction_count": reaction_count,
        "effect_operator_count": len(unique_effect_ops),
        "effect_operators": unique_effect_ops[:8],
        "nonconstant_script_slots": nonconstant_scripts,
        "sample_options": sample_options,
    }


def issue_score(component: str, card: dict[str, Any]) -> float:
    if component == "text_surface":
        body_words = len(str(card.get("body", "")).split())
        reaction_text = " ".join(
            reaction
            for opt in card.get("sample_options", [])
            for reaction in opt.get("sample_reactions", [])
            if reaction
        )
        return (1.0 / max(body_words, 1)) + (0.5 if len(reaction_text) < 120 else 0.0)
    if component == "branching":
        return max(0.0, 4.0 - float(card.get("option_count", 0))) + max(
            0.0, 8.0 - float(card.get("reaction_count", 0))
        )
    if component == "control_logic":
        return max(0.0, 4.0 - float(card.get("effect_operator_count", 0))) + (
            1.0 if int(card.get("nonconstant_script_slots", 0)) == 0 else 0.0
        )
    if component == "scale":
        return 1.0
    return 0.0


def select_cards(world: dict[str, Any], component: str, max_cards: int, token_budget: int) -> list[dict[str, Any]]:
    encounters = world.get("encounters", [])
    if not isinstance(encounters, list):
        return []
    cards = [summarize_encounter(enc, i) for i, enc in enumerate(encounters) if isinstance(enc, dict)]
    cards.sort(key=lambda card: issue_score(component, card), reverse=True)
    selected: list[dict[str, Any]] = []
    used = 0
    for card in cards:
        encoded = json.dumps(card, ensure_ascii=True)
        cost = token_estimate(encoded)
        if selected and used + cost > token_budget:
            continue
        selected.append(card)
        used += cost
        if len(selected) >= max_cards:
            break
    return selected


def weakest_component(components: dict[str, Any]) -> str:
    candidates: dict[str, float] = {}
    for key in COMPONENT_ORDER:
        value = components.get(key)
        if isinstance(value, (int, float)):
            candidates[key] = float(value)
    if not candidates:
        return "validity"
    return min(candidates, key=candidates.get)


def route_for_component(component: str) -> tuple[str, str, dict[str, Any]]:
    if component == "validity":
        return (
            "validator_repair_critic",
            "schema_repair_plan",
            {
                "diagnosis": "short string",
                "packet_fields_needed": ["field names, no prose"],
                "materializer_constraints": ["deterministic JSON repair rule"],
            },
        )
    if component == "scale":
        return (
            "world_state_summarizer",
            "encounter_inventory_plan",
            {
                "missing_spools_or_endings": ["ids"],
                "encounter_slots_to_add": [{"slot_id": "string", "purpose": "string"}],
                "do_not_write_full_json": True,
            },
        )
    if component == "branching":
        return (
            "option_manifold_planner",
            "bounded_option_reaction_effect_plan",
            {
                "encounter_id": "string",
                "options": [
                    {
                        "option_text": "one sentence",
                        "intended_delta": {"variable": "direction"},
                        "reactions": ["2-3 short reaction purposes"],
                    }
                ],
            },
        )
    if component == "control_logic":
        return (
            "effect_script_synthesizer",
            "effect_operator_diversity_plan",
            {
                "encounter_id": "string",
                "operator_mix": ["Nudge", "Blend", "Average", "Clamp"],
                "gate_or_effect_repairs": [
                    {"target": "option/reaction id", "repair": "schema-valid operator plan"}
                ],
            },
        )
    if component == "text_surface":
        return (
            "llm_prompt_composer",
            "bounded_prose_rewrite_plan",
            {
                "encounter_rewrites": [
                    {
                        "encounter_id": "string",
                        "title": "short title",
                        "body": "70-150 words",
                        "reaction_rewrites": ["12-50 words each"],
                    }
                ],
                "preserve_ids_and_mechanics": True,
            },
        )
    if component == "small_model_readiness":
        return (
            "mcp_context_router",
            "mcp_preflight_plan",
            {
                "packet_budget_tokens": "integer",
                "recommended_cards": ["world_card", "target_encounter", "neighbors", "ledger"],
                "no_model_call_needed": True,
            },
        )
    return (
        "validator_repair_critic",
        "native_schema_receipt_plan",
        {
            "run_native_planner": True,
            "append_teacher_rows": True,
            "do_not_ask_llm_to_route": True,
        },
    )


def requires_model_call(operation: str, output_schema: dict[str, Any]) -> bool:
    if bool(output_schema.get("no_model_call_needed")):
        return False
    if operation in {"mcp_preflight_plan", "native_schema_receipt_plan"}:
        return False
    return True


def build_prompt(packet: dict[str, Any]) -> str:
    return (
        "Return ONLY minified JSON. Start with { and end with }.\n"
        "No analysis. No markdown. No code fences. No <think> text.\n"
        "You are the bounded local author inside a MeTTa/MCP/TRM storyworld factory.\n"
        "Do not output full storyworld JSON. Do not change IDs unless explicitly asked.\n"
        "The JSON object must match output_schema.\n\n"
        + json.dumps(packet, indent=2, ensure_ascii=True)
    )


def call_model(base_url: str, model: str, prompt: str, timeout: int, max_tokens: int) -> dict[str, Any]:
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Return only a single minified JSON object. Do not explain, "
                    "do not use markdown, do not include chain-of-thought, and do not wrap in code fences."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": max_tokens,
    }
    req = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": "Bearer dummy"},
        method="POST",
    )
    started = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = json.loads(resp.read().decode("utf-8", errors="replace"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {"ok": False, "seconds": round(time.time() - started, 3), "error": f"{type(exc).__name__}: {exc}"}
    content = raw.get("choices", [{}])[0].get("message", {}).get("content", "")
    return {"ok": True, "seconds": round(time.time() - started, 3), "content": content, "raw": raw}


def build_job(row: dict[str, Any], *, max_cards: int, packet_token_budget: int) -> dict[str, Any]:
    components = row.get("components", {})
    component = weakest_component(components if isinstance(components, dict) else {})
    route, operation, output_schema = route_for_component(component)
    artifact = resolve_path(row.get("artifact"))
    world: dict[str, Any] = {}
    cards: list[dict[str, Any]] = []
    if artifact and artifact.exists():
        try:
            world = read_json(artifact)
            cards = select_cards(world, component, max_cards=max_cards, token_budget=packet_token_budget)
        except (OSError, json.JSONDecodeError):
            cards = []
    metrics = row.get("metrics", {}) if isinstance(row.get("metrics"), dict) else {}
    packet = {
        "job_id": f"{row.get('run_id', 'run')}_{component}",
        "source_run_id": row.get("run_id"),
        "artifact": row.get("artifact"),
        "model_under_test": row.get("model"),
        "condition": row.get("condition"),
        "weakest_component": component,
        "selected_role": route,
        "operation": operation,
        "requires_model_call": requires_model_call(operation, output_schema),
        "score_components": components,
        "metrics_snapshot": {
            key: metrics.get(key)
            for key in (
                "whole_context_token_estimate",
                "encounters",
                "options_per_nonterminal",
                "reactions_per_option",
                "effects_per_reaction",
                "gated_option_ratio",
                "effect_operator_variety",
                "effect_operator_dominance",
                "encounter_text_length_ok",
                "reaction_text_uniqueness",
            )
            if key in metrics
        },
        "bounded_context_cards": cards,
        "constraints": [
            "Do not output full storyworld JSON.",
            "Preserve existing IDs and mechanics unless the output schema asks for new slot IDs.",
            "Write only the local proposal needed by the selected role.",
            "Assume deterministic scaffold/verifiers will materialize and commit/veto.",
        ],
        "output_schema": output_schema,
    }
    prompt = build_prompt(packet)
    packet["prompt_token_estimate"] = token_estimate(prompt)
    packet["prompt"] = prompt
    return packet


def write_prompt_file(path: Path, packet: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(str(packet["prompt"]) + "\n", encoding="utf-8", newline="\n")


def write_summary_md(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Small-Model Builder Campaign",
        "",
        f"- Scorecard: `{summary['scorecard']}`",
        f"- Jobs: `{summary['job_count']}`",
        f"- Called model: `{summary['called_model']}`",
        "",
        "| Job | Role | Operation | Tokens | Model Call |",
        "|---|---|---|---:|---|",
    ]
    for job in summary["jobs"]:
        call = job.get("model_response", {})
        call_state = "required" if job.get("requires_model_call") else "scaffold"
        if call:
            if call.get("skipped"):
                call_state = "scaffold"
            else:
                call_state = "ok" if call.get("ok") else "failed"
        lines.append(
            "| `{job_id}` | `{role}` | `{operation}` | {tokens} | {call_state} |".format(
                job_id=job["job_id"],
                role=job["selected_role"],
                operation=job["operation"],
                tokens=job["prompt_token_estimate"],
                call_state=call_state,
            )
        )
    lines.extend(
        [
            "",
            "## Next Step",
            "",
            "Feed one prompt packet to the local small model, materialize only the returned bounded JSON plan, rerun the scorecard, and append the before/after delta as TRM training data.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build bounded repair jobs from a small-model builder scorecard.")
    parser.add_argument("--scorecard", required=True, help="scorecard.json from score_small_model_storyworld_builder.py")
    parser.add_argument("--out-dir", required=True, help="Campaign output directory")
    parser.add_argument("--max-jobs", type=int, default=4)
    parser.add_argument("--max-cards", type=int, default=3)
    parser.add_argument("--packet-token-budget", type=int, default=2400)
    parser.add_argument("--call-model", action="store_true", help="Call an already-running OpenAI-compatible endpoint")
    parser.add_argument("--base-url", default="http://127.0.0.1:8081/v1")
    parser.add_argument("--model", default="Qwen3.5-3B.Q4_K_M.gguf")
    parser.add_argument("--timeout", type=int, default=90)
    parser.add_argument("--max-response-tokens", type=int, default=700)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    scorecard_path = resolve_path(args.scorecard)
    out_dir = resolve_path(args.out_dir)
    if scorecard_path is None or not scorecard_path.exists():
        raise SystemExit(f"Scorecard not found: {args.scorecard}")
    if out_dir is None:
        raise SystemExit("Invalid --out-dir")
    out_dir.mkdir(parents=True, exist_ok=True)
    scorecard = read_json(scorecard_path)
    ranked = scorecard.get("ranked", [])
    if not isinstance(ranked, list):
        raise SystemExit("Scorecard has no ranked rows")

    jobs: list[dict[str, Any]] = []
    for row in ranked[: max(0, args.max_jobs)]:
        if not isinstance(row, dict):
            continue
        job = build_job(row, max_cards=args.max_cards, packet_token_budget=args.packet_token_budget)
        job_dir = out_dir / "jobs" / job["job_id"]
        write_json(job_dir / "packet.json", {k: v for k, v in job.items() if k != "prompt"})
        write_prompt_file(job_dir / "prompt.md", job)
        if args.call_model and bool(job.get("requires_model_call", True)):
            response = call_model(
                args.base_url,
                args.model,
                str(job["prompt"]),
                timeout=args.timeout,
                max_tokens=args.max_response_tokens,
            )
            job["model_response"] = response
            write_json(job_dir / "model_response.json", response)
            if response.get("ok"):
                (job_dir / "model_response.txt").write_text(
                    str(response.get("content", "")) + "\n",
                    encoding="utf-8",
                    newline="\n",
                )
        elif args.call_model:
            response = {"ok": True, "skipped": True, "reason": "scaffold_owned_job"}
            job["model_response"] = response
            write_json(job_dir / "model_response.json", response)
        jobs.append(job)

    compact_jobs = [{k: v for k, v in job.items() if k != "prompt"} for job in jobs]
    write_jsonl(out_dir / "campaign_jobs.jsonl", compact_jobs)
    summary = {
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "scorecard": str(scorecard_path),
        "out_dir": str(out_dir),
        "job_count": len(jobs),
        "called_model": bool(args.call_model),
        "model": args.model if args.call_model else None,
        "base_url": args.base_url if args.call_model else None,
        "jobs": compact_jobs,
    }
    write_json(out_dir / "campaign_summary.json", summary)
    write_summary_md(out_dir / "campaign_summary.md", summary)
    print(str(out_dir / "campaign_summary.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
