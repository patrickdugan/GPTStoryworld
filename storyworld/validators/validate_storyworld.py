#!/usr/bin/env python3
"""
Validate a Diplomacy Storyworld JSON file.

Uses jsonschema if installed; otherwise runs a focused manual validator.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import jsonschema
except Exception:  # pragma: no cover - optional dependency
    jsonschema = None


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def schema_validate(data: dict, schema_dir: Path) -> list[str]:
    if jsonschema is None:
        return ["jsonschema not installed; skipped JSON Schema validation"]

    schema_path = schema_dir / "storyworld.schema.json"
    with schema_path.open("r", encoding="utf-8") as f:
        schema = json.load(f)

    resolver = jsonschema.RefResolver(base_uri=schema_path.as_uri(), referrer=schema)
    validator = jsonschema.Draft7Validator(schema, resolver=resolver)
    errors = []
    for err in sorted(validator.iter_errors(data), key=lambda e: e.path):
        loc = ".".join(str(p) for p in err.path) or "<root>"
        errors.append(f"schema: {loc}: {err.message}")
    return errors


def manual_validate(data: dict) -> list[str]:
    errors: list[str] = []
    required = ["id", "title", "turn_limit", "agents", "nodes", "initial_state", "rules"]
    for key in required:
        if key not in data:
            errors.append(f"missing field: {key}")

    agents = data.get("agents", [])
    nodes = data.get("nodes", [])

    if not isinstance(agents, list):
        errors.append("agents must be a list")
    if not isinstance(nodes, list):
        errors.append("nodes must be a list")

    if isinstance(agents, list):
        if len(agents) > 5:
            errors.append("agents exceeds max of 5")
        agent_ids = [a.get("id") for a in agents if isinstance(a, dict)]
        if len(set(agent_ids)) != len(agent_ids):
            errors.append("agent ids must be unique")
    else:
        agent_ids = []

    if isinstance(nodes, list):
        if len(nodes) > 12:
            errors.append("nodes exceeds max of 12")
        node_ids = [n.get("id") for n in nodes if isinstance(n, dict)]
        if len(set(node_ids)) != len(node_ids):
            errors.append("node ids must be unique")
    else:
        node_ids = []

    initial_state = data.get("initial_state", {})
    active_node = initial_state.get("active_node")
    if active_node and node_ids and active_node not in node_ids:
        errors.append("initial_state.active_node must match a node id")

    beliefs = initial_state.get("beliefs", {})
    if isinstance(beliefs, dict) and agent_ids:
        for aid in agent_ids:
            if aid not in beliefs:
                errors.append(f"beliefs missing agent: {aid}")
            else:
                entry = beliefs.get(aid, {})
                if "trust" not in entry or "expected_payoff" not in entry:
                    errors.append(f"beliefs[{aid}] missing trust/expected_payoff")

    messages = data.get("messages", [])
    if isinstance(messages, list) and agent_ids:
        for idx, msg in enumerate(messages):
            if not isinstance(msg, dict):
                errors.append(f"messages[{idx}] must be object")
                continue
            src = msg.get("from")
            dst = msg.get("to")
            if src and src not in agent_ids:
                errors.append(f"messages[{idx}].from unknown agent {src}")
            if dst and dst not in agent_ids:
                errors.append(f"messages[{idx}].to unknown agent {dst}")

    rules = data.get("rules", {})
    outcomes = rules.get("outcomes", {}) if isinstance(rules, dict) else {}
    if isinstance(outcomes, dict):
        for name, outcome in outcomes.items():
            if not isinstance(outcome, dict):
                errors.append(f"rules.outcomes.{name} must be object")
                continue
            next_node = outcome.get("next_node")
            if next_node and node_ids and next_node not in node_ids:
                errors.append(f"rules.outcomes.{name}.next_node must match a node id")
    forecast_questions = rules.get("forecast_questions", []) if isinstance(rules, dict) else []
    if not isinstance(forecast_questions, list) or len(forecast_questions) == 0:
        errors.append("rules.forecast_questions must be a non-empty list")
    elif isinstance(forecast_questions, list):
        for idx, q in enumerate(forecast_questions):
            if not isinstance(q, dict):
                errors.append(f"rules.forecast_questions[{idx}] must be object")
                continue
            if not q.get("id") or not q.get("text"):
                errors.append(f"rules.forecast_questions[{idx}] missing id/text")
            outcomes_list = q.get("outcomes", [])
            if not isinstance(outcomes_list, list) or len(outcomes_list) == 0:
                errors.append(f"rules.forecast_questions[{idx}] missing outcomes list")

    return errors


def validate(path: Path, schema_dir: Path, strict: bool) -> int:
    data = load_json(path)

    schema_errors = schema_validate(data, schema_dir)
    manual_errors = manual_validate(data)

    if jsonschema is None and strict:
        print("ERROR: jsonschema not installed; use: pip install jsonschema", file=sys.stderr)
        return 2

    errors = [e for e in schema_errors if not e.startswith("jsonschema not installed")]
    errors.extend(manual_errors)

    if errors:
        print("INVALID")
        for err in errors:
            print(f"- {err}")
        return 1

    if schema_errors:
        print("VALID (schema validation skipped: jsonschema not installed)")
    else:
        print("VALID")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument(
        "--schema-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "schema",
    )
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    return validate(args.path, args.schema_dir, args.strict)


if __name__ == "__main__":
    raise SystemExit(main())
