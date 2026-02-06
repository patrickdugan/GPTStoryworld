#!/usr/bin/env python3
"""Recursive reasoning for adversarial MAS with coalition formation.

This module intentionally logs explicit decision traces (observable rationale)
instead of hidden chain-of-thought.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Dict, List, Optional, Tuple
import json
import random


ACTION_TYPES: Tuple[str, ...] = (
    "propose_coalition",
    "defect",
    "betray",
    "isolate",
    "commit_total_war",
)

BASE_GAIN: Dict[str, float] = {
    "propose_coalition": 0.12,
    "defect": 0.10,
    "betray": 0.16,
    "isolate": 0.05,
    "commit_total_war": 0.15,
}

BASE_RISK: Dict[str, float] = {
    "propose_coalition": 0.05,
    "defect": 0.09,
    "betray": 0.15,
    "isolate": 0.04,
    "commit_total_war": 0.20,
}

REPUTATION_COST: Dict[str, float] = {
    "propose_coalition": 0.02,
    "defect": 0.06,
    "betray": 0.13,
    "isolate": 0.03,
    "commit_total_war": 0.07,
}

ACTION_SIGNALS: Dict[str, Dict[str, float]] = {
    "propose_coalition": {
        "loyalty": 0.08,
        "promise_keeping": 0.05,
        "reciprocity": 0.07,
    },
    "defect": {
        "loyalty": -0.10,
        "promise_keeping": -0.09,
        "reciprocity": -0.11,
    },
    "betray": {
        "loyalty": -0.22,
        "promise_keeping": -0.24,
        "reciprocity": -0.23,
    },
    "isolate": {
        "loyalty": -0.04,
        "promise_keeping": -0.02,
        "reciprocity": -0.05,
    },
    "commit_total_war": {
        "loyalty": -0.03,
        "promise_keeping": 0.03,
        "reciprocity": -0.02,
    },
}


def clip01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


@dataclass(frozen=True)
class Action:
    kind: str
    target: Optional[str]


@dataclass
class AgentProfile:
    agent_id: str
    risk_tolerance: float
    loyalty_baseline: float
    opportunism: float
    coalition_bias: float


@dataclass
class SimulationConfig:
    turns: int = 12
    alpha: float = 0.30
    surprise_lambda: float = 4.0
    betrayal_collapse_threshold: float = 0.72
    defect_collapse_threshold: float = 0.80
    death_ground_threshold: float = 0.15
    epsilon: float = 0.06


class TraceLogger:
    """JSONL logger for explicit decision traces."""

    def __init__(
        self,
        path: Path,
        append: bool = False,
        context: Optional[Dict[str, object]] = None,
    ) -> None:
        self.path = path
        self.context = context or {}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if append:
            if not self.path.exists():
                self.path.write_text("", encoding="utf-8")
        else:
            self.path.write_text("", encoding="utf-8")

    def log(self, payload: Dict[str, object]) -> None:
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            **self.context,
            **payload,
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


class RecursiveReasonerMAS:
    """Recursive social reasoner with adversarial/coalitional dynamics."""

    def __init__(self, profiles: List[AgentProfile], config: SimulationConfig, seed: int = 7) -> None:
        self.config = config
        self.rng = random.Random(seed)
        self.profiles: Dict[str, AgentProfile] = {p.agent_id: p for p in profiles}
        self.agents = [p.agent_id for p in profiles]

        self.p: Dict[str, Dict[str, float]] = {a: {} for a in self.agents}
        self.p2: Dict[str, Dict[str, Dict[str, float]]] = {
            a: {b: {} for b in self.agents if b != a} for a in self.agents
        }

        for a in self.agents:
            for b in self.agents:
                if a == b:
                    continue
                # Direct trust belief p[a][b]
                base = 0.5 + 0.35 * (self.profiles[b].loyalty_baseline - 0.5)
                jitter = self.rng.uniform(-0.08, 0.08)
                self.p[a][b] = clip01(base + jitter)

        # Seed structural rivalry so adversarial equilibria are possible.
        rival_edges = max(1, len(self.agents) // 3)
        all_pairs: List[Tuple[str, str]] = []
        for i, a in enumerate(self.agents):
            for b in self.agents[i + 1 :]:
                all_pairs.append((a, b))
        self.rng.shuffle(all_pairs)
        chosen_rivals = all_pairs[:rival_edges]
        for a, b in chosen_rivals:
            self.p[a][b] = clip01(0.08 + self.rng.uniform(0.0, 0.12))
            self.p[b][a] = clip01(0.08 + self.rng.uniform(0.0, 0.12))

        # Create at least one balancing triangle around rival edges.
        for a, b in chosen_rivals:
            brokers = [x for x in self.agents if x not in {a, b}]
            if not brokers:
                continue
            broker = self.rng.choice(brokers)
            self.p[broker][a] = clip01(0.70 + self.rng.uniform(0.0, 0.20))
            self.p[broker][b] = clip01(0.70 + self.rng.uniform(0.0, 0.20))

        for a in self.agents:
            for b in self.agents:
                if a == b:
                    continue
                for c in self.agents:
                    if c == b:
                        continue
                    # Second-order p2[a][b][c] = a's estimate of b's trust in c
                    self.p2[a][b][c] = clip01(self.p[b][c] + self.rng.uniform(-0.07, 0.07))

        self.survival_resource: Dict[str, float] = {
            a: clip01(0.58 + self.rng.uniform(-0.22, 0.24)) for a in self.agents
        }

        self.metrics: Dict[str, float] = {
            "paine_violations": 0.0,
            "death_ground_entries": 0.0,
            "burn_boats_signals": 0.0,
            "asym_vulnerability_events": 0.0,
            "betrayal_collapses": 0.0,
        }

        self._death_ground_mode: Dict[str, bool] = {a: False for a in self.agents}
        self._refresh_death_ground_modes()

    def _refresh_death_ground_modes(self) -> None:
        for a in self.agents:
            now = self.survival_resource[a] < self.config.death_ground_threshold
            if now and not self._death_ground_mode[a]:
                self.metrics["death_ground_entries"] += 1.0
                self.metrics["burn_boats_signals"] += 1.0
            self._death_ground_mode[a] = now

    def death_ground_mode(self, agent: str) -> bool:
        return self._death_ground_mode[agent]

    def mortal_enemy(self, a: str, b: str) -> bool:
        return self.p[a][b] < 0.20 and self.p[b][a] < 0.20

    def manifold_scan(self, agent: str) -> Dict[str, object]:
        weak_from: Dict[str, float] = {}
        asym_vulnerability: Dict[str, float] = {}

        for other in self.agents:
            if other == agent:
                continue
            weak_score = 1.0 - self.p2[agent][other][agent]
            weak_from[other] = weak_score

            delta = self.p[agent][other] - self.p2[agent][other][agent]
            if delta > 0.35:
                asym_vulnerability[other] = delta

        if asym_vulnerability:
            self.metrics["asym_vulnerability_events"] += 1.0

        high_affinity = [o for o in self.agents if o != agent and self.p[agent][o] > 0.60]
        triangle_conflicts: List[Tuple[str, str]] = []
        for i in range(len(high_affinity)):
            for j in range(i + 1, len(high_affinity)):
                b = high_affinity[i]
                c = high_affinity[j]
                if self.mortal_enemy(b, c):
                    triangle_conflicts.append((b, c))

        threat_rank: List[Tuple[str, float]] = []
        for other in self.agents:
            if other == agent:
                continue
            threat = (
                0.55 * (1.0 - self.p[other][agent])
                + 0.25 * self.profiles[other].risk_tolerance
                + 0.20 * self.profiles[other].opportunism
            )
            threat_rank.append((other, threat))
        threat_rank.sort(key=lambda x: x[1], reverse=True)

        return {
            "weak_from": weak_from,
            "asym_vulnerability": asym_vulnerability,
            "triangle_conflicts": triangle_conflicts,
            "threat_rank": threat_rank,
        }

    def _targets(self, agent: str) -> List[Optional[str]]:
        return [o for o in self.agents if o != agent] + [None]

    def _paine_penalty(self, agent: str, action: Action) -> Tuple[float, Optional[str]]:
        if action.kind != "propose_coalition" or action.target is None:
            return 0.0, None

        b = action.target
        for c in self.agents:
            if c in {agent, b}:
                continue
            if self.mortal_enemy(b, c) and self.p[agent][c] > 0.55:
                return 0.40, c
        return 0.0, None

    def predict_derivative_snap(self, agent: str, action: Action, scan: Dict[str, object]) -> float:
        snap = 0.0
        target = action.target

        if action.kind == "propose_coalition" and target is not None:
            for b, c in scan["triangle_conflicts"]:
                if target in {b, c}:
                    snap = max(snap, 0.78)

        if action.kind == "betray" and target is not None and self.p[agent][target] > 0.65:
            snap = max(snap, 0.85)

        if action.kind == "defect" and target is not None and self.p[agent][target] > 0.75:
            snap = max(snap, 0.58)

        if action.kind == "isolate":
            weak_scores = scan["weak_from"]
            if any(score > 0.60 for score in weak_scores.values()):
                snap = max(snap, 0.35)

        return clip01(snap)

    def _estimate_level1_response(self, agent: str, action: Action) -> float:
        """Estimate one-step response from other agents."""
        score = 0.0

        for other in self.agents:
            if other == agent:
                continue

            hostility_to_agent = 1.0 - self.p[other][agent]
            retaliatory = hostility_to_agent * (0.5 + 0.5 * self.profiles[other].risk_tolerance)

            if action.kind == "propose_coalition" and action.target == other:
                accept = 0.55 * self.p[other][agent] + 0.45 * self.p2[agent][other][agent]
                score += 0.18 * accept - 0.05 * retaliatory
            elif action.kind in {"defect", "betray"} and action.target == other:
                score -= 0.25 * retaliatory
            elif action.kind == "commit_total_war":
                deterrence = (self.profiles[agent].risk_tolerance + self.profiles[agent].opportunism) / 2
                score += 0.10 * deterrence - 0.10 * retaliatory
            else:
                score -= 0.06 * retaliatory

        return score

    def utility(self, agent: str, action: Action, scan: Dict[str, object]) -> Tuple[float, Dict[str, float]]:
        profile = self.profiles[agent]
        gain = BASE_GAIN[action.kind]
        risk = BASE_RISK[action.kind]
        rep = REPUTATION_COST[action.kind]

        if action.target is not None:
            trust_to_target = self.p[agent][action.target]
            meta_target_about_me = self.p2[agent][action.target][agent]
        else:
            trust_to_target = mean(self.p[agent][o] for o in self.agents if o != agent)
            meta_target_about_me = mean(self.p2[agent][o][agent] for o in self.agents if o != agent)

        coalition_bonus = 0.0
        if action.kind == "propose_coalition":
            coalition_bonus = 0.20 * profile.coalition_bias * trust_to_target

        betrayal_bonus = 0.0
        if action.kind == "betray":
            betrayal_bonus = 0.18 * (1.0 - meta_target_about_me)

        weak_max = max(scan["weak_from"].values()) if scan["weak_from"] else 0.0
        top_threat = scan["threat_rank"][0][1] if scan["threat_rank"] else 0.0
        pressure = clip01(0.55 * weak_max + 0.45 * top_threat)

        aggression_bonus = 0.0
        if action.kind == "defect":
            aggression_bonus = 0.13 * pressure * (0.4 + 0.6 * profile.opportunism)
        elif action.kind == "betray":
            aggression_bonus = 0.16 * pressure * (0.4 + 0.6 * profile.opportunism)
        elif action.kind == "commit_total_war":
            aggression_bonus = 0.20 * pressure * (0.4 + 0.6 * profile.risk_tolerance)

        correction_bonus = 0.0
        weak_scores = scan["weak_from"]
        if weak_scores and weak_max > 0.60 and action.kind in {"defect", "commit_total_war", "betray"}:
            correction_bonus += 0.10

        asymmetry_penalty = 0.0
        if action.kind == "propose_coalition" and scan["asym_vulnerability"]:
            asymmetry_penalty = 0.18

        coalition_fragility_penalty = 0.0
        if action.kind == "propose_coalition":
            coalition_fragility_penalty = max(0.0, 0.22 * (pressure - 0.52))

        paine_penalty, paine_enemy = self._paine_penalty(agent, action)

        snap = self.predict_derivative_snap(agent, action, scan)
        snap_penalty = 0.45 * snap

        level1 = self._estimate_level1_response(agent, action)

        death_mode = self.death_ground_mode(agent)
        if death_mode:
            # Death-ground phase shift: risk preference inverted, reputation suppressed.
            risk_term = +0.85 * risk
            rep_term = 0.0
        else:
            risk_term = -1.0 * risk
            rep_term = -0.9 * rep

        total = (
            1.1 * gain
            + coalition_bonus
            + betrayal_bonus
            + aggression_bonus
            + correction_bonus
            + level1
            + risk_term
            + rep_term
            - asymmetry_penalty
            - coalition_fragility_penalty
            - paine_penalty
            - snap_penalty
        )

        return total, {
            "gain": gain,
            "risk": risk,
            "rep": rep,
            "coalition_bonus": coalition_bonus,
            "betrayal_bonus": betrayal_bonus,
            "aggression_bonus": aggression_bonus,
            "correction_bonus": correction_bonus,
            "level1": level1,
            "paine_penalty": paine_penalty,
            "snap_penalty": snap_penalty,
            "asymmetry_penalty": asymmetry_penalty,
            "coalition_fragility_penalty": coalition_fragility_penalty,
            "pressure": pressure,
            "death_mode": 1.0 if death_mode else 0.0,
        }

    def candidate_actions(self, agent: str) -> List[Action]:
        actions: List[Action] = []
        for target in self._targets(agent):
            for kind in ACTION_TYPES:
                if kind in {"isolate", "commit_total_war"} and target is not None:
                    continue
                if kind in {"propose_coalition", "defect", "betray"} and target is None:
                    continue
                actions.append(Action(kind=kind, target=target))
        return actions

    def choose_action(self, agent: str) -> Tuple[Action, Dict[str, object]]:
        scan = self.manifold_scan(agent)
        candidates = []
        for action in self.candidate_actions(agent):
            score, parts = self.utility(agent, action, scan)
            candidates.append((action, score, parts))

        candidates.sort(key=lambda x: x[1], reverse=True)
        if self.rng.random() < self.config.epsilon:
            action, score, parts = self.rng.choice(candidates[: min(4, len(candidates))])
        else:
            action, score, parts = candidates[0]

        snap = self.predict_derivative_snap(agent, action, scan)
        top_threat = scan["threat_rank"][0][0] if scan["threat_rank"] else None

        rationale = (
            f"weak_from_max={max(scan['weak_from'].values()):.2f}; "
            f"triangle_conflicts={len(scan['triangle_conflicts'])}; "
            f"snap={snap:.2f}; top_threat={top_threat}; chosen={action.kind}"
        )
        if self.death_ground_mode(agent):
            rationale += "; death_ground_mode=1; burn_the_boats_signal=1"

        decision = {
            "scan": scan,
            "utility_parts": parts,
            "score": score,
            "rationale_text": rationale,
            "predicted_snap": snap,
            "candidates_top3": [
                {
                    "action": c[0].kind,
                    "target": c[0].target,
                    "score": round(c[1], 6),
                }
                for c in candidates[:3]
            ],
        }
        return action, decision

    def _survival_update(self, actor: str, action: Action) -> None:
        target = action.target

        if action.kind == "propose_coalition" and target is not None:
            self.survival_resource[actor] = clip01(self.survival_resource[actor] + 0.03)
            self.survival_resource[target] = clip01(self.survival_resource[target] + 0.04)
        elif action.kind == "defect" and target is not None:
            self.survival_resource[actor] = clip01(self.survival_resource[actor] + 0.01)
            self.survival_resource[target] = clip01(self.survival_resource[target] - 0.08)
        elif action.kind == "betray" and target is not None:
            self.survival_resource[actor] = clip01(self.survival_resource[actor] + 0.02)
            self.survival_resource[target] = clip01(self.survival_resource[target] - 0.17)
        elif action.kind == "isolate":
            self.survival_resource[actor] = clip01(self.survival_resource[actor] - 0.02)
        elif action.kind == "commit_total_war":
            self.survival_resource[actor] = clip01(self.survival_resource[actor] + 0.04)
            for other in self.agents:
                if other == actor:
                    continue
                self.survival_resource[other] = clip01(self.survival_resource[other] - 0.03)

    def _apply_surprise_update(self, actor: str, action: Action) -> None:
        target = action.target

        for obs in self.agents:
            if obs == actor:
                continue

            for trait, signal in ACTION_SIGNALS[action.kind].items():
                old = self.p[obs][actor]
                negative = max(0.0, -signal)
                surprise = old * negative
                alpha_eff = self.config.alpha * (1.0 + self.config.surprise_lambda * surprise)
                new = clip01(old + alpha_eff * signal)

                # Hard collapse on high surprise betrayal or defection.
                if action.kind == "betray" and old >= self.config.betrayal_collapse_threshold:
                    new = min(new, 0.03)
                    self.metrics["betrayal_collapses"] += 1.0
                if action.kind == "defect" and old >= self.config.defect_collapse_threshold:
                    new = min(new, 0.10)

                self.p[obs][actor] = new

        # Target and witness effects.
        if target is not None and action.kind in {"defect", "betray"}:
            self.p[target][actor] = clip01(self.p[target][actor] - 0.30)
            for witness in self.agents:
                if witness in {actor, target}:
                    continue
                self.p[witness][actor] = clip01(self.p[witness][actor] - 0.10)

        # Paine constraint spillover after coalition move.
        if action.kind == "propose_coalition" and target is not None:
            for c in self.agents:
                if c in {actor, target}:
                    continue
                if self.mortal_enemy(target, c) and self.p[actor][c] > 0.55:
                    self.p[c][actor] = clip01(self.p[c][actor] - 0.22)
                    self.metrics["paine_violations"] += 1.0

        # Update p2 to track revised direct beliefs.
        for obs in self.agents:
            for med in self.agents:
                if med == obs:
                    continue
                for tgt in self.agents:
                    if tgt == med:
                        continue
                    old2 = self.p2[obs][med][tgt]
                    direct = self.p[med][tgt]
                    self.p2[obs][med][tgt] = clip01(0.80 * old2 + 0.20 * direct)

    def step(self, turn: int, logger: TraceLogger) -> List[Dict[str, object]]:
        order = self.agents[:]
        self.rng.shuffle(order)
        decisions: List[Tuple[str, Action, Dict[str, object]]] = []

        for agent in order:
            action, decision = self.choose_action(agent)
            decisions.append((agent, action, decision))

        for agent, action, decision in decisions:
            before = self.survival_resource[agent]
            self._apply_surprise_update(agent, action)
            self._survival_update(agent, action)
            self._refresh_death_ground_modes()

            logger.log(
                {
                    "turn": turn,
                    "agent": agent,
                    "action": action.kind,
                    "target": action.target,
                    "survival_before": round(before, 6),
                    "survival_after": round(self.survival_resource[agent], 6),
                    "death_ground_mode": self.death_ground_mode(agent),
                    "decision": decision,
                }
            )

        return [
            {
                "turn": turn,
                "agent": agent,
                "action": action.kind,
                "target": action.target,
                "score": round(decision["score"], 6),
            }
            for agent, action, decision in decisions
        ]

    def run(self, logger: TraceLogger) -> Dict[str, object]:
        all_events: List[Dict[str, object]] = []
        for turn in range(1, self.config.turns + 1):
            all_events.extend(self.step(turn, logger))

        action_counts: CounterLike = {}
        for event in all_events:
            action_counts[event["action"]] = action_counts.get(event["action"], 0) + 1

        total_actions = float(sum(action_counts.values()) or 1)

        avg_trust = mean(
            self.p[a][b] for a in self.agents for b in self.agents if a != b
        )

        summary = {
            "agents": self.agents,
            "turns": self.config.turns,
            "average_trust": avg_trust,
            "average_survival": mean(self.survival_resource.values()),
            "action_rates": {k: v / total_actions for k, v in action_counts.items()},
            "metrics": self.metrics,
            "final_survival": self.survival_resource,
        }
        return summary


CounterLike = Dict[str, int]


def default_profiles(n_agents: int, seed: int = 19) -> List[AgentProfile]:
    rng = random.Random(seed)
    profiles = []
    for i in range(n_agents):
        profiles.append(
            AgentProfile(
                agent_id=f"P{i+1}",
                risk_tolerance=clip01(0.45 + rng.uniform(-0.20, 0.35)),
                loyalty_baseline=clip01(0.50 + rng.uniform(-0.28, 0.25)),
                opportunism=clip01(0.40 + rng.uniform(-0.22, 0.35)),
                coalition_bias=clip01(0.50 + rng.uniform(-0.25, 0.30)),
            )
        )
    return profiles


def run_recursive_reasoning_demo(
    n_agents: int,
    turns: int,
    seed: int,
    log_path: Path,
) -> Dict[str, object]:
    profiles = default_profiles(n_agents=n_agents, seed=seed + 1)
    config = SimulationConfig(turns=turns)
    env = RecursiveReasonerMAS(profiles=profiles, config=config, seed=seed)
    logger = TraceLogger(log_path)
    return env.run(logger)
