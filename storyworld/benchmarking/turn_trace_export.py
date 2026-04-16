#!/usr/bin/env python3
"""Export turn-level reasoning traces for diplomacy storyworld runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List


def _deep_copy(data: Any) -> Any:
    return json.loads(json.dumps(data))


def _legal_actions_for(agent_id: str, agent_ids: List[str], action_types: List[str]) -> List[Dict[str, Any]]:
    legal: List[Dict[str, Any]] = []
    targets = [other for other in agent_ids if other != agent_id]
    for action_type in action_types:
        if action_type in {"ally", "betray", "propose"}:
            for target in targets:
                legal.append({"type": action_type, "target": target})
        else:
            legal.append({"type": action_type, "target": None})
    return legal


def _action_legality(action: Dict[str, Any], legal_actions: List[Dict[str, Any]]) -> float:
    action_type = action.get("type")
    target = action.get("target")
    for legal in legal_actions:
        if legal.get("type") == action_type and legal.get("target") == target:
            return 1.0
    return 0.0


def _forecast_entries(action: Dict[str, Any]) -> List[Dict[str, Any]]:
    if isinstance(action.get("forecasts"), list):
        return [entry for entry in action["forecasts"] if isinstance(entry, dict)]
    if isinstance(action.get("forecast"), dict):
        return [action["forecast"]]
    return []


def _normalized_confidence(action: Dict[str, Any]) -> Dict[str, Any]:
    confidence = action.get("confidence")
    if isinstance(confidence, dict):
        return _deep_copy(confidence)
    if isinstance(confidence, (int, float)):
        return {"overall": float(confidence)}
    return {}


def export_turn_rows(
    storyworld: Dict[str, Any],
    pre_state: Dict[str, Any],
    event: Dict[str, Any],
    turn_index: int,
    episode_id: str,
    slice_id: str = "diplomacy_negotiation",
) -> List[Dict[str, Any]]:
    actions = event.get("actions", {})
    messages = event.get("messages", [])
    forecast_scores = event.get("forecast_scores", {})
    outcome = event.get("outcome")
    belief_delta = {
        "before": _deep_copy(pre_state.get("beliefs", {})),
        "after": _deep_copy(event.get("beliefs", {})),
    }

    agent_ids = [agent["id"] for agent in storyworld.get("agents", []) if isinstance(agent, dict) and agent.get("id")]
    action_types = list(storyworld.get("rules", {}).get("action_types", ["wait"]))
    hidden_state = _deep_copy(storyworld.get("hidden_state", []))
    player_models = event.get("player_models", {})
    turn_owner = event.get("turn_owner", pre_state.get("turn_owner"))
    turn_order = event.get("turn_order", pre_state.get("turn_order", storyworld.get("turns", agent_ids)))
    multiplayer = event.get("multiplayer", pre_state.get("multiplayer", storyworld.get("multiplayer", 1)))
    rows: List[Dict[str, Any]] = []

    for agent_id in agent_ids:
        action = actions.get(agent_id, {})
        if not isinstance(action, dict):
            action = {}
        legal_actions = _legal_actions_for(agent_id, agent_ids, action_types)
        row = {
            "benchmark_id": "storyworld_reasoning_v2",
            "slice_id": slice_id,
            "world_id": storyworld.get("id", "unknown_world"),
            "episode_id": episode_id,
            "turn_index": turn_index,
            "acting_agent": agent_id,
            "turn_owner": turn_owner,
            "next_turn_owner": event.get("next_turn_owner"),
            "turn_order": _deep_copy(turn_order),
            "multiplayer": multiplayer,
            "visible_state": {
                "visibility_mode": "shared_full_state",
                "active_node": pre_state.get("active_node"),
                "beliefs": _deep_copy(pre_state.get("beliefs", {})),
                "coalitions": _deep_copy(pre_state.get("coalitions", [])),
                "world_vars": _deep_copy(pre_state.get("world_vars", {})),
                "messages": [
                    _deep_copy(message)
                    for message in messages
                    if isinstance(message, dict)
                    and (message.get("from") == agent_id or message.get("to") == agent_id)
                ],
            },
            "legal_actions": legal_actions,
            "chosen_action": _deep_copy(action),
            "reasoning_trace": str(action.get("reasoning", "")),
            "reasoning_segments": _deep_copy(action.get("reasoning_segments", {})),
            "trace_mode": "pick_time",
            "forecasts": _deep_copy(_forecast_entries(action)),
            "confidence": _normalized_confidence(action),
            "hidden_state_reveal": hidden_state,
            "self_model": _deep_copy(player_models.get(agent_id, {})),
            "pvalue_fold": _deep_copy(action.get("pvalue_fold", {})),
            "realized_outcome": {
                "outcome": outcome,
                "active_node_after": event.get("active_node"),
                "done": bool(event.get("done", False)),
                "metrics": _deep_copy(event.get("metrics", {})),
                "world_vars_after": _deep_copy(event.get("world_vars_after", {})),
            },
            "belief_delta": _deep_copy(belief_delta),
            "score": {
                "action_legality": _action_legality(action, legal_actions),
                "forecast": _deep_copy(forecast_scores.get(agent_id, {})),
            },
        }
        rows.append(row)

    return rows


def write_turn_trace_rows(path: str | Path, rows: Iterable[Dict[str, Any]]) -> None:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
