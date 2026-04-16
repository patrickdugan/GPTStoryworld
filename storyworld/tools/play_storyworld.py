#!/usr/bin/env python3
"""Play a diplomacy storyworld with random or scripted multiplayer actions."""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from storyworld.benchmarking import export_turn_rows, write_turn_trace_rows
from storyworld.env import DiplomacyStoryworldEnv, load_storyworld


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def random_action(rng: random.Random, action_types, agent_id, agent_ids, outcomes):
    atype = rng.choice(action_types)
    if atype in {"ally", "betray", "propose"}:
        targets = [a for a in agent_ids if a != agent_id]
        target = rng.choice(targets) if targets else None
    else:
        target = None
    probs = {}
    if outcomes:
        weights = [rng.random() for _ in outcomes]
        total = sum(weights) or 1.0
        probs = {outcomes[i]: round(weights[i] / total, 3) for i in range(len(outcomes))}
    q1_probs = {"betrayal": round(rng.random(), 3)}
    q1_probs["no_betrayal"] = round(1.0 - q1_probs["betrayal"], 3)
    return {
        "type": atype,
        "target": target,
        "forecasts": [
            {
                "question_id": "q1",
                "likely_outcome": "betrayal" if q1_probs["betrayal"] >= 0.5 else "no_betrayal",
                "probabilities": q1_probs,
            },
            {
                "question_id": "q2",
                "likely_outcome": rng.choice(outcomes) if outcomes else "maneuver",
                "probabilities": probs,
            },
        ],
        "confidence": round(rng.uniform(0.3, 0.9), 2),
        "reasoning": f"Random policy chose {atype}.",
    }


def random_message(rng: random.Random, agent_ids):
    if len(agent_ids) < 2:
        return None
    src = rng.choice(agent_ids)
    dst = rng.choice([a for a in agent_ids if a != src])
    return {
        "from": src,
        "to": dst,
        "type": rng.choice(["proposal", "threat", "update"]),
        "content": "Auto-generated message.",
        "belief_commitments": {"trust_delta": round(rng.uniform(-0.1, 0.2), 2)},
    }


def resolve_turn_order(data: Dict[str, Any], agent_ids: List[str]) -> List[str]:
    raw_turns = data.get("turns")
    if isinstance(raw_turns, list):
        turns = [entry for entry in raw_turns if isinstance(entry, str) and entry in agent_ids]
        if turns:
            return turns
    return list(agent_ids)


def resolve_play_mode(data: Dict[str, Any], requested_mode: str) -> str:
    if requested_mode != "auto":
        return requested_mode
    if data.get("multiplayer", 1) > 1 or "turns" in data:
        return "scripted_multiplayer"
    return "random"


def initialize_player_models(storyworld: Dict[str, Any], agent_ids: List[str]) -> Dict[str, Dict[str, Any]]:
    metadata = storyworld.get("metadata", {})
    persona_specs = metadata.get("persona_specs", {})
    axes = metadata.get("other_self_model_axes", ["devotion", "mischief", "defiance", "mercy"])
    player_models: Dict[str, Dict[str, Any]] = {}
    for agent_id in agent_ids:
        spec = persona_specs.get(agent_id, {})
        seed_views = spec.get("other_self_model_seed", {})
        other_self_model = {}
        for other_id in agent_ids:
            if other_id == agent_id:
                continue
            seeded = seed_views.get(other_id, {})
            other_self_model[other_id] = {axis: float(seeded.get(axis, 0.0)) for axis in axes}
        player_models[agent_id] = {
            "agent_id": agent_id,
            "persona": spec.get("display_name", agent_id),
            "voice": spec.get("voice", ""),
            "style_tags": list(spec.get("style_tags", [])),
            "desires": list(spec.get("desires", [])),
            "moral_axes": {axis: 0.0 for axis in axes},
            "moral_commits": [],
            "memory": [],
            "other_self_model": other_self_model,
        }
    return player_models


def summarize_other_self_model(model: Dict[str, Dict[str, float]]) -> str:
    fragments = []
    for other_id, axes in model.items():
        ordered = ", ".join(f"{axis}={round(float(value), 2)}" for axis, value in axes.items())
        fragments.append(f"{other_id}[{ordered}]")
    return "; ".join(fragments)


def build_forecasts(action_type: str, outcomes: List[str]) -> List[Dict[str, Any]]:
    betrayal_prob = 0.72 if action_type == "betray" else 0.18
    likely_outcome = "betrayal" if action_type == "betray" else "coalition_formed" if action_type in {"ally", "propose"} else "maneuver"
    outcome_probs = {}
    for outcome in outcomes:
        if outcome == likely_outcome:
            outcome_probs[outcome] = 0.64
        elif outcome == "stalemate":
            outcome_probs[outcome] = 0.16
        else:
            outcome_probs[outcome] = 0.2 / max(1, len(outcomes) - 2)
    return [
        {
            "question_id": "q1",
            "likely_outcome": "betrayal" if betrayal_prob >= 0.5 else "no_betrayal",
            "probabilities": {
                "betrayal": round(betrayal_prob, 3),
                "no_betrayal": round(1.0 - betrayal_prob, 3),
            },
        },
        {
            "question_id": "q2",
            "likely_outcome": likely_outcome,
            "probabilities": {key: round(value, 3) for key, value in outcome_probs.items()},
        },
    ]


def build_moral_commit(storyworld: Dict[str, Any], agent_id: str, action_type: str, target: str | None) -> Dict[str, Any]:
    spec = storyworld.get("metadata", {}).get("persona_specs", {}).get(agent_id, {})
    heart_target = spec.get("heart_target")
    rival_target = spec.get("rival_target")
    if target == heart_target and action_type in {"ally", "propose"}:
        vector = {"devotion": 0.38, "mercy": 0.16, "defiance": 0.14, "mischief": 0.08}
        text = spec.get(
            "heart_commit_text",
            f"{agent_id} signs the luminous paperwork that says love should survive its own death.",
        )
        label = "protect_reincarnating_love"
    elif target == rival_target and action_type == "betray":
        vector = {"devotion": -0.08, "mercy": -0.12, "defiance": 0.36, "mischief": 0.18}
        text = spec.get(
            "rival_commit_text",
            f"{agent_id} marks a cruel little X through the ledger that would separate the lovers again.",
        )
        label = "cut_the_ledger_knot"
    elif action_type == "wait":
        vector = {"devotion": 0.02, "mercy": 0.04, "defiance": -0.02, "mischief": 0.0}
        text = f"{agent_id} hesitates and lets the moon do the talking."
        label = "hold_the_glimmer"
    else:
        vector = {"devotion": 0.12, "mercy": 0.06, "defiance": 0.08, "mischief": 0.05}
        text = f"{agent_id} treats negotiation like a spell and leaves the clause slightly charmed."
        label = "shape_the_contract"
    return {"label": label, "text": text, "vector": vector}


def compute_pvalue_fold(player_models: Dict[str, Dict[str, Any]], agent_id: str) -> Dict[str, float]:
    fold: Dict[str, float] = {}
    self_model = player_models.get(agent_id, {})
    for other_id, axes in self_model.get("other_self_model", {}).items():
        if not isinstance(axes, dict):
            continue
        for axis, value in axes.items():
            fold[f"pValue.{axis}.{agent_id}.{other_id}"] = round(float(value), 3)
    return fold


def choose_scripted_action(
    rng: random.Random,
    storyworld: Dict[str, Any],
    state: Dict[str, Any],
    agent_id: str,
    agent_ids: List[str],
) -> Dict[str, Any]:
    action_types = list(storyworld.get("rules", {}).get("action_types", ["wait"]))
    outcomes = list(storyworld.get("rules", {}).get("outcomes", {}).keys())
    spec = storyworld.get("metadata", {}).get("persona_specs", {}).get(agent_id, {})
    heart_target = spec.get("heart_target")
    rival_target = spec.get("rival_target")
    trust = state.get("beliefs", {}).get(agent_id, {}).get("trust", {})
    world_vars = state.get("world_vars", {})
    reincarnation_glimmer = float(world_vars.get("reincarnation_glimmer", 0.0))
    audit_pressure = float(world_vars.get("audit_pressure", 0.0))
    bureaucracy_heat = float(world_vars.get("bureaucracy_heat", 0.0))
    betray_trigger_heat = spec.get("betray_trigger_heat")
    betray_trigger_bonus = float(spec.get("betray_trigger_bonus", 0.0))
    proposal_fade_heat = spec.get("proposal_fade_heat")
    proposal_fade_penalty = float(spec.get("proposal_fade_penalty", 0.0))
    candidates = []
    for action_type in action_types:
        targets = [None]
        if action_type in {"ally", "betray", "propose"}:
            targets = [other for other in agent_ids if other != agent_id]
        for target in targets:
            score = float(spec.get("action_bias", {}).get(action_type, 0.0))
            if target == heart_target:
                if action_type in {"ally", "propose"}:
                    score += 1.1 + reincarnation_glimmer + max(0.0, float(trust.get(target, 0.0)))
                if action_type == "betray":
                    score -= 0.9
            if target == rival_target:
                if action_type == "betray":
                    score += 0.7 + audit_pressure
                if action_type == "propose":
                    score += 0.25 + bureaucracy_heat * 0.2
            if (
                isinstance(betray_trigger_heat, (int, float))
                and target == rival_target
                and action_type == "betray"
                and bureaucracy_heat >= float(betray_trigger_heat)
            ):
                score += betray_trigger_bonus
            if (
                isinstance(proposal_fade_heat, (int, float))
                and action_type == "propose"
                and bureaucracy_heat >= float(proposal_fade_heat)
            ):
                score -= proposal_fade_penalty
            if action_type == "propose" and state.get("active_node") == "node_invoice_ballad":
                score += 0.25
            if action_type == "betray" and state.get("active_node") == "node_tithe_hearing":
                score += 0.2
            if action_type == "wait":
                score -= 0.35
            score += rng.uniform(0.0, 0.05)
            candidates.append((score, action_type, target))
    _, action_type, target = max(candidates, key=lambda entry: entry[0])
    moral_commit = build_moral_commit(storyworld, agent_id, action_type, target)
    return {
        "type": action_type,
        "target": target,
        "moral_commit": moral_commit,
        "forecasts": build_forecasts(action_type, outcomes),
        "confidence": round(clamp(0.58 + max(0.0, moral_commit["vector"].get("devotion", 0.0)) * 0.2, 0.35, 0.92), 2),
    }


def build_reasoning_segments(
    storyworld: Dict[str, Any],
    agent_id: str,
    action: Dict[str, Any],
    player_models: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    self_model = player_models.get(agent_id, {})
    pvalue_fold = compute_pvalue_fold(player_models, agent_id)
    choice = f"{action.get('type')} -> {action.get('target') or 'none'}"
    return {
        "self_model": {
            "persona": self_model.get("persona"),
            "moral_axes": self_model.get("moral_axes", {}),
            "memory": self_model.get("memory", []),
        },
        "other_self_model": summarize_other_self_model(self_model.get("other_self_model", {})),
        "pvalue_fold": pvalue_fold,
        "moral_commit": action.get("moral_commit", {}),
        "choice": choice,
        "story_fabric": storyworld.get("metadata", {}).get("story_fabric", "first_order_pvalue"),
    }


def build_reasoning_trace(reasoning_segments: Dict[str, Any]) -> str:
    return "\n".join(
        [
            f"self_model: {json.dumps(reasoning_segments.get('self_model', {}), ensure_ascii=False, sort_keys=True)}",
            f"other_self_model: {reasoning_segments.get('other_self_model', '')}",
            f"pvalue_fold: {json.dumps(reasoning_segments.get('pvalue_fold', {}), ensure_ascii=False, sort_keys=True)}",
            f"moral_commit: {json.dumps(reasoning_segments.get('moral_commit', {}), ensure_ascii=False, sort_keys=True)}",
            f"choice: {reasoning_segments.get('choice', '')}",
        ]
    )


def build_scripted_message(agent_id: str, action: Dict[str, Any]) -> Dict[str, Any] | None:
    target = action.get("target")
    action_type = action.get("type")
    if not target or action_type not in {"ally", "betray", "propose"}:
        return None
    if action_type == "betray":
        message_type = "threat"
        content = "The ledger can be torn two ways, darling, and I know both."
    elif action_type == "ally":
        message_type = "proposal"
        content = "Let us file the lovers under moonlight and call it compliance."
    else:
        message_type = "update"
        content = "A clause just bloomed. Read it before the stars cool."
    return {
        "from": agent_id,
        "to": target,
        "type": message_type,
        "content": content,
        "belief_commitments": {
            "trust_delta": 0.12 if action_type in {"ally", "propose"} else -0.18,
        },
        "meta": {
            "moral_commit_label": action.get("moral_commit", {}).get("label"),
        },
    }


def seed_story_fabric(env: DiplomacyStoryworldEnv, player_models: Dict[str, Dict[str, Any]], agent_ids: List[str]) -> None:
    pvalue_updates: Dict[str, float] = {}
    for agent_id in agent_ids:
        pvalue_updates.update(compute_pvalue_fold(player_models, agent_id))
    env.state.setdefault("world_vars", {}).update(pvalue_updates)


def apply_story_fabric_updates(
    env: DiplomacyStoryworldEnv,
    agent_id: str,
    action: Dict[str, Any],
    player_models: Dict[str, Dict[str, Any]],
    agent_ids: List[str],
) -> None:
    commit = action.get("moral_commit", {})
    vector = commit.get("vector", {})
    owner_model = player_models[agent_id]
    for axis, delta in vector.items():
        owner_model["moral_axes"][axis] = round(clamp(float(owner_model["moral_axes"].get(axis, 0.0)) + float(delta), -1.0, 1.0), 3)
    owner_model["moral_commits"].append(
        {
            "turn": env.state.get("turn"),
            "active_node": env.state.get("active_node"),
            "label": commit.get("label"),
            "text": commit.get("text"),
            "vector": vector,
        }
    )
    owner_model["moral_commits"] = owner_model["moral_commits"][-6:]
    owner_model["memory"].append(commit.get("text"))
    owner_model["memory"] = owner_model["memory"][-4:]

    target = action.get("target")
    for observer_id, observer_model in player_models.items():
        if observer_id == agent_id:
            continue
        observed = observer_model.setdefault("other_self_model", {}).setdefault(
            agent_id,
            {axis: 0.0 for axis in owner_model["moral_axes"].keys()},
        )
        for axis, delta in vector.items():
            observed[axis] = round(clamp(float(observed.get(axis, 0.0)) + float(delta) * 0.55, -1.0, 1.0), 3)
    if target and target in owner_model.get("other_self_model", {}):
        viewed = owner_model["other_self_model"][target]
        devotion_delta = 0.12 if action.get("type") in {"ally", "propose"} else -0.18 if action.get("type") == "betray" else 0.0
        viewed["devotion"] = round(clamp(float(viewed.get("devotion", 0.0)) + devotion_delta, -1.0, 1.0), 3)

    world_vars = env.state.setdefault("world_vars", {})
    world_vars["reincarnation_glimmer"] = round(
        clamp(
            float(world_vars.get("reincarnation_glimmer", 0.0))
            + float(vector.get("devotion", 0.0)) * 0.22
            + float(vector.get("mercy", 0.0)) * 0.1,
            0.0,
            1.5,
        ),
        3,
    )
    world_vars["audit_pressure"] = round(
        clamp(float(world_vars.get("audit_pressure", 0.0)) + (0.11 if action.get("type") == "betray" else -0.03), 0.0, 1.5),
        3,
    )
    world_vars["bureaucracy_heat"] = round(
        clamp(float(world_vars.get("bureaucracy_heat", 0.0)) + (0.08 if target else -0.02), 0.0, 1.5),
        3,
    )
    world_vars[f"moral_commit.{agent_id}"] = commit.get("label")

    pvalue_updates: Dict[str, float] = {}
    for observer_id in agent_ids:
        pvalue_updates.update(compute_pvalue_fold(player_models, observer_id))
    world_vars.update(pvalue_updates)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--world", type=str, required=True)
    parser.add_argument("--steps", type=int, default=5)
    parser.add_argument("--seed", type=int, default=3)
    parser.add_argument("--log", type=str, default="logs/play.jsonl")
    parser.add_argument("--turn-trace-out", type=str, default="")
    parser.add_argument("--episode-id", type=str, default="")
    parser.add_argument("--mode", type=str, choices=["auto", "random", "scripted_multiplayer"], default="auto")
    parser.add_argument("--player-models-out", type=str, default="")
    args = parser.parse_args()

    data = load_storyworld(args.world)
    env = DiplomacyStoryworldEnv(data, seed=args.seed, log_path=args.log)
    state = env.reset(seed=args.seed)
    if args.turn_trace_out:
        Path(args.turn_trace_out).unlink(missing_ok=True)

    rng = random.Random(args.seed)
    action_types = data.get("rules", {}).get("action_types", ["wait"])
    outcomes = list(data.get("rules", {}).get("outcomes", {}).keys())
    agent_ids = [a["id"] for a in data.get("agents", [])]
    turn_order = resolve_turn_order(data, agent_ids)
    mode = resolve_play_mode(data, args.mode)
    player_models = initialize_player_models(data, agent_ids) if mode == "scripted_multiplayer" else {}
    if player_models:
        seed_story_fabric(env, player_models, agent_ids)
        state = json.loads(json.dumps(env.state))
    episode_id = args.episode_id or f"{data.get('id', 'storyworld')}_seed_{args.seed}"

    for turn_index in range(1, args.steps + 1):
        pre_state = json.loads(json.dumps(state))
        current_turn_owner = pre_state.get("turn_owner") or turn_order[(turn_index - 1) % max(1, len(turn_order))]
        if mode == "scripted_multiplayer":
            owner_action = choose_scripted_action(rng, data, pre_state, current_turn_owner, agent_ids)
            reasoning_segments = build_reasoning_segments(data, current_turn_owner, owner_action, player_models)
            owner_action["pvalue_fold"] = reasoning_segments["pvalue_fold"]
            owner_action["reasoning_segments"] = reasoning_segments
            owner_action["reasoning"] = build_reasoning_trace(reasoning_segments)
            actions = {current_turn_owner: owner_action}
            messages = []
            message = build_scripted_message(current_turn_owner, owner_action)
            if message:
                messages.append(message)
        else:
            actions = {aid: random_action(rng, action_types, aid, agent_ids, outcomes) for aid in agent_ids}
            messages = []
            if rng.random() < 0.6:
                msg = random_message(rng, agent_ids)
                if msg:
                    messages.append(msg)
        state, event, done = env.step(actions, messages)
        if mode == "scripted_multiplayer":
            current_action = actions.get(current_turn_owner, {})
            apply_story_fabric_updates(env, current_turn_owner, current_action, player_models, agent_ids)
            env.state["history"][-1]["player_models"] = json.loads(json.dumps(player_models))
            env.state["history"][-1]["pvalue_fold"] = {aid: compute_pvalue_fold(player_models, aid) for aid in agent_ids}
            state = json.loads(json.dumps(env.state))
            event["player_models"] = json.loads(json.dumps(player_models))
            event["pvalue_fold"] = {aid: compute_pvalue_fold(player_models, aid) for aid in agent_ids}
            event["world_vars_after"] = json.loads(json.dumps(env.state.get("world_vars", {})))
            event["mode"] = mode
        if args.turn_trace_out:
            rows = export_turn_rows(
                storyworld=data,
                pre_state=pre_state,
                event=event,
                turn_index=turn_index,
                episode_id=episode_id,
            )
            write_turn_trace_rows(args.turn_trace_out, rows)
        if done:
            break

    if args.player_models_out and player_models:
        out_path = Path(args.player_models_out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(player_models, indent=2, ensure_ascii=False), encoding="utf-8")

    print(
        json.dumps(
            {
                "mode": mode,
                "final_state": state,
                "player_models": player_models,
                "done": state.get("done"),
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
