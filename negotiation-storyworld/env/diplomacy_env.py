#!/usr/bin/env python3
"""Deterministic diplomacy environment for small storyworlds."""

from __future__ import annotations

import json
import random
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .storyworld_env import StoryworldEnvBase, deep_copy_state


class JSONLLogger:
    def __init__(self, path: str | Path | None):
        self.path = Path(path) if path else None
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, event_type: str, payload: Dict[str, Any]) -> None:
        if not self.path:
            return
        record = {
            "ts": time.time(),
            "event": event_type,
            "payload": payload,
        }
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


class DiplomacyStoryworldEnv(StoryworldEnvBase):
    def __init__(
        self,
        storyworld: Dict[str, Any],
        seed: Optional[int] = None,
        log_path: Optional[str | Path] = None,
    ) -> None:
        self.storyworld = storyworld
        self.rng = random.Random(seed)
        self.logger = JSONLLogger(log_path)
        self.state: Dict[str, Any] = {}
        self._agent_ids = [a["id"] for a in storyworld.get("agents", [])]
        self._node_ids = {n["id"] for n in storyworld.get("nodes", [])}
        self._action_types = set(storyworld.get("rules", {}).get("action_types", []))
        self._message_types = set(storyworld.get("rules", {}).get("message_types", []))
        self._trust_min = storyworld.get("rules", {}).get("trust_bounds", {}).get("min", -1.0)
        self._trust_max = storyworld.get("rules", {}).get("trust_bounds", {}).get("max", 1.0)
        self._belief_update = storyworld.get("rules", {}).get("belief_update", {})
        self._forecast_questions = storyworld.get("rules", {}).get("forecast_questions", [])
        self._outcome_keys = list(storyworld.get("rules", {}).get("outcomes", {}).keys())

    def reset(self, seed: Optional[int] = None) -> Dict[str, Any]:
        if seed is not None:
            self.rng.seed(seed)
        init = self.storyworld.get("initial_state", {})
        self.state = {
            "turn": 0,
            "active_node": init.get("active_node"),
            "beliefs": deep_copy_state(init.get("beliefs", {})),
            "coalitions": deep_copy_state(init.get("coalitions", [])),
            "world_vars": deep_copy_state(init.get("world_vars", {})),
            "messages": [],
            "done": False,
            "history": [],
        }
        self._ensure_belief_matrix()
        self.logger.log("reset", {"state": self.state, "forecast_questions": self._forecast_questions})
        return deep_copy_state(self.state)

    def step(self, actions, messages) -> Tuple[Dict[str, Any], Dict[str, Any], bool]:
        if self.state.get("done"):
            return deep_copy_state(self.state), {"error": "episode already done"}, True

        actions_by_agent = self._normalize_actions(actions)
        messages_list = self._normalize_messages(messages)

        self._apply_messages(messages_list)
        pre_beliefs = deep_copy_state(self.state.get("beliefs", {}))
        outcome_flags = self._apply_actions(actions_by_agent)

        outcome = self._resolve_outcome(outcome_flags, actions_by_agent, messages_list)
        self._transition(outcome)

        self.state["turn"] += 1
        self.state["messages"] = messages_list
        forecast_scores = self._score_forecasts(actions_by_agent, outcome)
        metrics = self._compute_metrics(actions_by_agent, pre_beliefs)
        self.state["history"].append({
            "turn": self.state["turn"],
            "actions": actions_by_agent,
            "messages": messages_list,
            "outcome": outcome,
            "forecast_scores": forecast_scores,
            "metrics": metrics,
        })

        done = self._check_terminal(outcome)
        self.state["done"] = done

        event = {
            "turn": self.state["turn"],
            "actions": actions_by_agent,
            "messages": messages_list,
            "outcome": outcome,
            "forecast_scores": forecast_scores,
            "metrics": metrics,
            "coalitions": self.state["coalitions"],
            "beliefs": self.state["beliefs"],
            "active_node": self.state["active_node"],
            "done": done,
        }
        self.logger.log("step", event)
        return deep_copy_state(self.state), event, done

    def _ensure_belief_matrix(self) -> None:
        beliefs = self.state.get("beliefs", {})
        for aid in self._agent_ids:
            beliefs.setdefault(aid, {"trust": {}, "expected_payoff": 0.0})
            trust = beliefs[aid].setdefault("trust", {})
            for other in self._agent_ids:
                trust.setdefault(other, 0.0)
        self.state["beliefs"] = beliefs

    def _normalize_actions(self, actions) -> Dict[str, Dict[str, Any]]:
        if actions is None:
            return {aid: {"type": "wait"} for aid in self._agent_ids}
        if isinstance(actions, dict):
            normalized = {}
            for aid in self._agent_ids:
                normalized[aid] = actions.get(aid, {"type": "wait"})
            return normalized
        if isinstance(actions, list):
            by_agent = {a.get("agent_id"): a for a in actions if isinstance(a, dict)}
            return {aid: by_agent.get(aid, {"type": "wait"}) for aid in self._agent_ids}
        return {aid: {"type": "wait"} for aid in self._agent_ids}

    def _normalize_messages(self, messages) -> List[Dict[str, Any]]:
        if messages is None:
            return []
        if not isinstance(messages, list):
            return []
        normalized = []
        for msg in messages:
            if not isinstance(msg, dict):
                continue
            if self._message_types and msg.get("type") not in self._message_types:
                continue
            if msg.get("from") not in self._agent_ids or msg.get("to") not in self._agent_ids:
                continue
            normalized.append(msg)
        return normalized

    def _apply_messages(self, messages: List[Dict[str, Any]]) -> None:
        for msg in messages:
            src = msg.get("from")
            dst = msg.get("to")
            mtype = msg.get("type")
            delta = self._belief_update.get(f"message_{mtype}", 0.0)
            if src and dst:
                self._adjust_trust(dst, src, delta)

            commitments = msg.get("belief_commitments", {})
            if isinstance(commitments, dict):
                for key, val in commitments.items():
                    self.state["world_vars"][f"commitment.{src}.{dst}.{key}"] = val

    def _apply_actions(self, actions: Dict[str, Dict[str, Any]]) -> Dict[str, bool]:
        formed_new_coalition = False
        betrayal = False

        for aid, action in actions.items():
            atype = action.get("type", "wait")
            if self._action_types and atype not in self._action_types:
                atype = "wait"
            target = action.get("target")

            if atype == "ally" and target in self._agent_ids:
                formed_new_coalition |= self._form_or_merge_coalition(aid, target)
                self._adjust_trust(aid, target, self._belief_update.get("ally", 0.1))
                self._adjust_trust(target, aid, self._belief_update.get("ally", 0.1))

            elif atype == "betray" and target in self._agent_ids:
                betrayal = True
                self._break_coalition(aid, target)
                self._adjust_trust(target, aid, self._belief_update.get("betray", -0.4))
                self._adjust_trust(aid, target, self._belief_update.get("betray_self", -0.1))

            elif atype == "propose" and target in self._agent_ids:
                self._adjust_trust(target, aid, self._belief_update.get("propose", 0.05))

        return {
            "betrayal": betrayal,
            "coalition_formed": formed_new_coalition,
        }

    def _resolve_outcome(
        self,
        flags: Dict[str, bool],
        actions: Dict[str, Dict[str, Any]],
        messages: List[Dict[str, Any]],
    ) -> str:
        if flags.get("betrayal"):
            return "betrayal"
        if flags.get("coalition_formed"):
            return "coalition_formed"
        if all(a.get("type", "wait") == "wait" for a in actions.values()) and not messages:
            return "stalemate"
        return "maneuver"

    def _transition(self, outcome: str) -> None:
        outcomes = self.storyworld.get("rules", {}).get("outcomes", {})
        transition = outcomes.get(outcome)
        if not isinstance(transition, dict):
            self.state["world_vars"]["last_outcome"] = outcome
            return
        next_node = transition.get("next_node")
        if next_node in self._node_ids:
            self.state["active_node"] = next_node
        self.state["world_vars"]["last_outcome"] = outcome
        if transition.get("terminal") is True:
            self.state["done"] = True

    def _check_terminal(self, outcome: str) -> bool:
        if self.state.get("done"):
            return True
        if self.state["turn"] >= self.storyworld.get("turn_limit", 1):
            return True
        node = self._node_by_id(self.state.get("active_node"))
        if node and node.get("terminal") is True:
            return True
        outcomes = self.storyworld.get("rules", {}).get("outcomes", {})
        transition = outcomes.get(outcome, {}) if isinstance(outcomes, dict) else {}
        return bool(transition.get("terminal"))

    def _score_forecasts(self, actions: Dict[str, Dict[str, Any]], outcome: str) -> Dict[str, Dict[str, Any]]:
        scores: Dict[str, Dict[str, Any]] = {}
        for aid, action in actions.items():
            forecasts = []
            if isinstance(action, dict):
                if isinstance(action.get("forecasts"), list):
                    forecasts = [f for f in action.get("forecasts") if isinstance(f, dict)]
                elif isinstance(action.get("forecast"), dict):
                    forecasts = [action.get("forecast")]
            if not forecasts:
                continue
            entries: List[Dict[str, Any]] = []
            for forecast in forecasts:
                entry: Dict[str, Any] = {}
                outcomes = self._forecast_outcomes_for(forecast, outcome)
                actual = self._actual_outcome_for_question(forecast, outcome)
                likely = forecast.get("likely_outcome")
                if likely:
                    entry["accuracy"] = 1.0 if likely == actual else 0.0
                    entry["actual"] = actual
                probs = forecast.get("probabilities")
                if isinstance(probs, dict) and outcomes:
                    total = sum(max(0.0, float(probs.get(k, 0.0))) for k in outcomes)
                    if total > 0:
                        norm = {k: max(0.0, float(probs.get(k, 0.0))) / total for k in outcomes}
                        brier = sum((norm[k] - (1.0 if k == actual else 0.0)) ** 2 for k in outcomes) / len(outcomes)
                        entry["brier"] = round(brier, 4)
                if entry:
                    entry["question_id"] = forecast.get("question_id")
                    entries.append(entry)
            if entries:
                scores[aid] = entries if len(entries) > 1 else entries[0]
        return scores

    def _forecast_outcomes_for(self, forecast: Dict[str, Any], outcome: str) -> List[str]:
        qid = forecast.get("question_id")
        if qid:
            for q in self._forecast_questions:
                if q.get("id") == qid:
                    outcomes = q.get("outcomes", [])
                    if isinstance(outcomes, list) and outcomes:
                        return outcomes
        return self._outcome_keys if self._outcome_keys else [outcome]

    def _actual_outcome_for_question(self, forecast: Dict[str, Any], outcome: str) -> str:
        qid = forecast.get("question_id")
        if qid == "q1":
            return "betrayal" if outcome == "betrayal" else "no_betrayal"
        return outcome

    def _compute_metrics(self, actions: Dict[str, Dict[str, Any]], pre_beliefs: Dict[str, Any]) -> Dict[str, Any]:
        coalitions = self.state.get("coalitions", [])
        if coalitions:
            mean_stability = sum(c.get("stability", 0.0) for c in coalitions) / len(coalitions)
        else:
            mean_stability = 0.0

        betray_trusts: List[float] = []
        for aid, action in actions.items():
            if not isinstance(action, dict):
                continue
            if action.get("type") == "betray" and action.get("target") in self._agent_ids:
                target = action.get("target")
                trust = pre_beliefs.get(target, {}).get("trust", {}).get(aid)
                if trust is not None:
                    betray_trusts.append(float(trust))

        betrayal_surprise = None
        if betray_trusts:
            betrayal_surprise = sum(betray_trusts) / len(betray_trusts)

        return {
            "coalition_count": len(coalitions),
            "coalition_mean_stability": round(mean_stability, 4),
            "betrayal_surprise": None if betrayal_surprise is None else round(betrayal_surprise, 4),
        }

    def _node_by_id(self, node_id: str | None) -> Optional[Dict[str, Any]]:
        if not node_id:
            return None
        for node in self.storyworld.get("nodes", []):
            if node.get("id") == node_id:
                return node
        return None

    def _adjust_trust(self, holder: str, target: str, delta: float) -> None:
        beliefs = self.state.get("beliefs", {})
        trust = beliefs.get(holder, {}).get("trust", {})
        current = trust.get(target, 0.0)
        updated = max(self._trust_min, min(self._trust_max, current + delta))
        trust[target] = updated
        beliefs[holder]["trust"] = trust
        self.state["beliefs"] = beliefs

    def _form_or_merge_coalition(self, a: str, b: str) -> bool:
        coalitions = self.state.get("coalitions", [])
        coalition_a = None
        coalition_b = None
        for c in coalitions:
            if a in c.get("members", []):
                coalition_a = c
            if b in c.get("members", []):
                coalition_b = c
        if coalition_a and coalition_b:
            if coalition_a is coalition_b:
                return False
            merged = list({*coalition_a["members"], *coalition_b["members"]})
            coalition_a["members"] = merged
            coalition_a["stability"] = min(1.0, coalition_a.get("stability", 0.5) + 0.1)
            coalitions.remove(coalition_b)
            self.state["coalitions"] = coalitions
            return True
        if coalition_a:
            if b not in coalition_a["members"]:
                coalition_a["members"].append(b)
                coalition_a["stability"] = min(1.0, coalition_a.get("stability", 0.5) + 0.05)
                return True
            return False
        if coalition_b:
            if a not in coalition_b["members"]:
                coalition_b["members"].append(a)
                coalition_b["stability"] = min(1.0, coalition_b.get("stability", 0.5) + 0.05)
                return True
            return False
        new_id = f"coalition_{len(coalitions) + 1}"
        coalitions.append({"id": new_id, "members": [a, b], "stability": 0.5})
        self.state["coalitions"] = coalitions
        return True

    def _break_coalition(self, a: str, b: str) -> None:
        coalitions = self.state.get("coalitions", [])
        for c in list(coalitions):
            members = c.get("members", [])
            if a in members and b in members:
                if a in members:
                    members.remove(a)
                if b in members and len(members) <= 1:
                    coalitions.remove(c)
                c["members"] = members
                c["stability"] = max(0.0, c.get("stability", 0.5) - 0.2)
        self.state["coalitions"] = coalitions
