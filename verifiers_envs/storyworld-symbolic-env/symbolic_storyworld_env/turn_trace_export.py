from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    from .qwen_local_policy import candidate_actions_for_agent
except ImportError:
    from qwen_local_policy import candidate_actions_for_agent


def _deep_copy(data: Any) -> Any:
    return json.loads(json.dumps(data))


def _parse_symbolic_action(action: str) -> dict[str, Any]:
    stripped = str(action or "").strip()
    if not stripped.startswith("(") or not stripped.endswith(")"):
        return {
            "type": "unknown",
            "target": None,
            "raw_action": stripped,
            "arguments": [],
        }

    parts = stripped[1:-1].split()
    if not parts:
        return {
            "type": "unknown",
            "target": None,
            "raw_action": stripped,
            "arguments": [],
        }

    action_type = parts[0]
    arguments = parts[1:]
    target = None

    if action_type == "move" and len(arguments) >= 3:
        target = arguments[2]
    elif action_type == "buy" and len(arguments) >= 4:
        target = arguments[1]
    elif action_type == "steal" and len(arguments) >= 3:
        target = arguments[1]
    elif action_type == "arrest" and len(arguments) >= 2:
        target = arguments[1]

    return {
        "type": action_type,
        "target": target,
        "raw_action": stripped,
        "arguments": arguments,
    }


def _reasoning_trace(record: dict[str, Any]) -> str:
    raw_text = str(record.get("policy_raw_text", "") or "").strip()
    action = str(record.get("action", "") or "").strip()
    route = record.get("route", {}) if isinstance(record.get("route"), dict) else {}
    rationale = str(route.get("rationale", "") or "").strip()

    if raw_text and raw_text != action:
        if rationale:
            return f"route_rationale={rationale}\npolicy_evidence={raw_text}"
        return raw_text
    return rationale


def build_turn_trace_rows(
    *,
    run_id: str,
    scenario: str,
    decision_records: list[dict[str, Any]],
    runtime: dict[str, Any],
    overlay: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    hidden_state_reveal = [
        {
            "kind": "grading_overlay",
            "ending_id": overlay.get("ending_id"),
            "scores": _deep_copy(overlay.get("scores", {})),
            "constraints": _deep_copy(overlay.get("constraints", {})),
        },
        {
            "kind": "runtime",
            "ok": bool(runtime.get("ok", False)),
            "returncode": runtime.get("returncode"),
            "note": runtime.get("note", ""),
        },
    ]

    for record in decision_records:
        route = record.get("route", {}) if isinstance(record.get("route"), dict) else {}
        visible_state = str(record.get("visible_state", "") or "")
        action = str(record.get("action", "") or "")
        prior_actions = list(record.get("prior_actions", []))
        legal_actions = [
            _parse_symbolic_action(candidate)
            for candidate in candidate_actions_for_agent(
                str(record.get("agent", "")),
                visible_state,
                str(route.get("route", "") or ""),
            )
        ]

        rows.append(
            {
                "benchmark_id": "storyworld_reasoning_v2",
                "slice_id": "symbolic_enforcement",
                "world_id": f"symbolic_{scenario}",
                "episode_id": run_id,
                "turn_index": int(record.get("step", 0)),
                "acting_agent": str(record.get("agent", "")),
                "visible_state": {
                    "visibility_mode": "local_symbolic_visible_state",
                    "scenario": scenario,
                    "raw_visible_state": visible_state,
                    "route": _deep_copy(route),
                    "prior_actions": prior_actions,
                },
                "legal_actions": legal_actions,
                "chosen_action": {
                    **_parse_symbolic_action(action),
                    "policy_backend": record.get("policy_backend", ""),
                    "policy_used_fallback": bool(record.get("policy_used_fallback", False)),
                    "route_mode": record.get("route_mode", ""),
                },
                "reasoning_trace": _reasoning_trace(record),
                "trace_mode": "pick_time",
                "forecasts": [],
                "confidence": {},
                "hidden_state_reveal": hidden_state_reveal,
                "realized_outcome": {
                    "outcome": overlay.get("ending_id"),
                    "active_node_after": None,
                    "done": True,
                    "metrics": {
                        **_deep_copy(overlay.get("scores", {})),
                        "runtime_ok": bool(runtime.get("ok", False)),
                    },
                    "constraints": _deep_copy(overlay.get("constraints", {})),
                    "final_actions": [item.get("action", "") for item in decision_records],
                },
                "belief_delta": {
                    "before": {"prior_actions": prior_actions},
                    "after": {"prior_actions": prior_actions + [action]},
                },
                "score": {
                    "action_legality": 1.0 if any(item.get("raw_action") == action for item in legal_actions) else 0.0,
                    "forecast": {},
                },
            }
        )
    return rows


def write_turn_trace_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True, sort_keys=True) + "\n")
