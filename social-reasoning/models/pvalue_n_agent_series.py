#!/usr/bin/env python3
"""Run 4-7 player social-reasoning simulation series.

This version includes:
- manifold scan before each action,
- surprise-amplified trust derivatives,
- Paine alliance constraint,
- death-ground phase shift.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Dict, Iterable, List, Optional, Tuple

TRAITS: List[str] = [
    "loyalty",
    "reciprocity",
    "risk_tolerance",
    "promise_keeping",
]

ACTIONS: List[str] = [
    "join_coalition",
    "defect",
    "betray",
    "isolate",
    "death_ground",
]

ACTION_SIGNALS: Dict[str, Dict[str, float]] = {
    "join_coalition": {
        "loyalty": 0.08,
        "reciprocity": 0.07,
        "risk_tolerance": 0.02,
        "promise_keeping": 0.05,
    },
    "defect": {
        "loyalty": -0.10,
        "reciprocity": -0.12,
        "risk_tolerance": 0.03,
        "promise_keeping": -0.09,
    },
    "betray": {
        "loyalty": -0.19,
        "reciprocity": -0.21,
        "risk_tolerance": 0.06,
        "promise_keeping": -0.23,
    },
    "isolate": {
        "loyalty": -0.03,
        "reciprocity": -0.05,
        "risk_tolerance": -0.01,
        "promise_keeping": -0.02,
    },
    "death_ground": {
        "loyalty": 0.01,
        "reciprocity": -0.02,
        "risk_tolerance": 0.16,
        "promise_keeping": 0.04,
    },
}

GAIN = {
    "join_coalition": 0.08,
    "defect": 0.11,
    "betray": 0.17,
    "isolate": 0.03,
    "death_ground": 0.14,
}

RISK = {
    "join_coalition": 0.04,
    "defect": 0.08,
    "betray": 0.14,
    "isolate": 0.05,
    "death_ground": 0.18,
}

REPUTATION_COST = {
    "join_coalition": 0.01,
    "defect": 0.06,
    "betray": 0.13,
    "isolate": 0.03,
    "death_ground": 0.05,
}

SURPRISE_LAMBDA = 4.0
DEATH_GROUND_THRESHOLD = 0.15


def clip01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


@dataclass
class ManifoldScan:
    target: str
    weak_score: float
    target_thinks_i_am_weak: bool
    triangle_conflict: bool
    triangle_enemy: Optional[str]
    asym_vulnerability: float


@dataclass
class PlannedEvent:
    actor: str
    target: str
    action: str
    utility: float
    weak_score: float
    triangle_conflict: bool
    triangle_enemy: Optional[str]
    predicted_snap: float
    monologue: str
    survival_before: float
    death_ground_mode: bool


class NAgentSocialState:
    def __init__(self, agents: List[str], seed: int) -> None:
        self.agents = agents
        rng = random.Random(seed)

        self.theta: Dict[str, Dict[str, float]] = {
            agent: {trait: clip01(0.5 + rng.uniform(-0.2, 0.2)) for trait in TRAITS}
            for agent in agents
        }

        self.p: Dict[Tuple[str, str, str], float] = {}
        for obs in agents:
            for tgt in agents:
                if obs == tgt:
                    continue
                for trait in TRAITS:
                    base = 0.5 + 0.25 * (self.theta[tgt][trait] - 0.5) + rng.uniform(-0.04, 0.04)
                    self.p[(obs, tgt, trait)] = clip01(base)

        self.p2: Dict[Tuple[str, str, str, str], float] = {}
        for obs in agents:
            for med in agents:
                if med == obs:
                    continue
                for tgt in agents:
                    if tgt == med:
                        continue
                    for trait in TRAITS:
                        base = self.p[(med, tgt, trait)] + rng.uniform(-0.05, 0.05)
                        self.p2[(obs, med, tgt, trait)] = clip01(base)

        self.survival_resource: Dict[str, float] = {
            a: clip01(0.55 + rng.uniform(-0.18, 0.30)) for a in agents
        }
        self.death_ground_mode: Dict[str, bool] = {a: False for a in agents}

        self.paine_violation_count = 0
        self.death_ground_entry_count = 0
        self.burn_boats_signal_count = 0
        self.asymmetric_vulnerability_count = 0

        self._update_death_ground_modes()

    def average_pair_trait(self, trait: str) -> float:
        vals = [
            value
            for (obs, tgt, key), value in self.p.items()
            if key == trait and obs != tgt
        ]
        return mean(vals) if vals else 0.5

    def average_meta_consistency(self) -> float:
        diffs = []
        for (obs, med, tgt, trait), value in self.p2.items():
            direct = self.p[(med, tgt, trait)]
            diffs.append(abs(value - direct))
        return 1.0 - mean(diffs) if diffs else 1.0

    def average_survival(self) -> float:
        return mean(self.survival_resource.values()) if self.survival_resource else 0.5

    def is_on_death_ground(self, agent: str) -> bool:
        return self.survival_resource[agent] < DEATH_GROUND_THRESHOLD

    def _update_death_ground_modes(self) -> None:
        for agent in self.agents:
            now = self.is_on_death_ground(agent)
            if now and not self.death_ground_mode[agent]:
                self.death_ground_entry_count += 1
                self.burn_boats_signal_count += 1
            self.death_ground_mode[agent] = now

    def are_mortal_enemies(self, a: str, b: str) -> bool:
        mutual_loyalty = 0.5 * (self.p[(a, b, "loyalty")] + self.p[(b, a, "loyalty")])
        mutual_recip = 0.5 * (self.p[(a, b, "reciprocity")] + self.p[(b, a, "reciprocity")])
        return mutual_loyalty < 0.18 and mutual_recip < 0.18

    def choose_target(self, agent: str) -> str:
        best_target = None
        best_score = float("-inf")

        for other in self.agents:
            if other == agent:
                continue

            if self.death_ground_mode[agent]:
                # Under death-ground, target the strongest threat to survival.
                threat_score = (
                    0.60 * (1.0 - self.p[(other, agent, "loyalty")])
                    + 0.25 * (1.0 - self.p[(other, agent, "reciprocity")])
                    + 0.15 * self.p[(other, agent, "risk_tolerance")]
                )
                score = threat_score
            else:
                score = (
                    0.55 * (1.0 - self.p[(agent, other, "loyalty")])
                    + 0.30 * (1.0 - self.p[(agent, other, "reciprocity")])
                    + 0.15 * self.p[(agent, other, "risk_tolerance")]
                )

            if score > best_score:
                best_score = score
                best_target = other

        assert best_target is not None
        return best_target

    def manifold_scan(self, agent: str, target: str) -> ManifoldScan:
        meta_view = self.p2.get(
            (agent, target, agent, "promise_keeping"),
            self.p[(target, agent, "promise_keeping")],
        )
        weak_score = 1.0 - meta_view
        target_thinks_i_am_weak = weak_score > 0.55

        trust_to_target = self.p[(agent, target, "loyalty")]
        asym_vulnerability = max(0.0, trust_to_target - meta_view)

        triangle_enemy = None
        best_conflict_strength = 0.0
        for other in self.agents:
            if other in {agent, target}:
                continue
            if self.are_mortal_enemies(target, other):
                my_trust_other = self.p[(agent, other, "loyalty")]
                if my_trust_other > 0.55 and my_trust_other > best_conflict_strength:
                    best_conflict_strength = my_trust_other
                    triangle_enemy = other

        return ManifoldScan(
            target=target,
            weak_score=weak_score,
            target_thinks_i_am_weak=target_thinks_i_am_weak,
            triangle_conflict=triangle_enemy is not None,
            triangle_enemy=triangle_enemy,
            asym_vulnerability=asym_vulnerability,
        )

    def predict_derivative_snap(
        self,
        agent: str,
        target: str,
        action: str,
        scan: ManifoldScan,
    ) -> float:
        trust_to_target = self.p[(agent, target, "loyalty")]

        snap = 0.0
        if action == "join_coalition" and scan.triangle_conflict:
            snap += 0.75
        if action == "betray" and trust_to_target > 0.62:
            snap += 0.85
        if action == "defect" and trust_to_target > 0.68:
            snap += 0.55
        if action == "isolate" and scan.target_thinks_i_am_weak:
            snap += 0.35
        if action in {"defect", "death_ground"} and scan.asym_vulnerability > 0.35:
            snap -= 0.12

        return clip01(snap)

    def utility(self, agent: str, target: str, action: str, scan: ManifoldScan) -> float:
        rel = self.p[(agent, target, "reciprocity")]
        trust = self.p[(agent, target, "loyalty")]
        meta = self.p2.get((agent, target, agent, "promise_keeping"), trust)

        existential_pressure = clip01((DEATH_GROUND_THRESHOLD - self.survival_resource[agent]) * 4.0)

        coalition_bonus = 0.12 if action == "join_coalition" and trust > 0.55 else 0.0
        death_ground_bonus = 0.22 * existential_pressure if action == "death_ground" else 0.0
        betrayal_bonus = 0.16 * (1.0 - meta) if action == "betray" else 0.0

        risk_term = -1.00 * RISK[action]
        rep_cost = REPUTATION_COST[action]

        if self.death_ground_mode[agent]:
            # Phase shift: high-variance actions preferred; reputation costs vanish.
            risk_term = +0.85 * RISK[action]
            rep_cost = 0.0

        paine_penalty = 0.0
        if action == "join_coalition" and scan.triangle_conflict:
            paine_penalty = 0.35

        asymmetry_penalty = 0.0
        asymmetry_correction_bonus = 0.0
        if scan.asym_vulnerability > 0.35:
            asymmetry_penalty = 0.22 if action == "join_coalition" else 0.0
            if action in {"defect", "death_ground"}:
                asymmetry_correction_bonus = 0.15

        weakness_correction_bonus = 0.0
        if scan.target_thinks_i_am_weak and action in {"defect", "death_ground"}:
            weakness_correction_bonus = 0.10

        snap_risk = self.predict_derivative_snap(agent, target, action, scan)
        snap_penalty = 0.42 * snap_risk

        return (
            1.12 * GAIN[action]
            + 0.96 * rel
            + 0.66 * meta
            + coalition_bonus
            + death_ground_bonus
            + betrayal_bonus
            + asymmetry_correction_bonus
            + weakness_correction_bonus
            + risk_term
            - 0.90 * rep_cost
            - paine_penalty
            - asymmetry_penalty
            - snap_penalty
        )

    def ranked_actions(self, agent: str, target: str, scan: ManifoldScan) -> List[Tuple[str, float]]:
        scores = [(action, self.utility(agent, target, action, scan)) for action in ACTIONS]
        scores.sort(key=lambda item: item[1], reverse=True)
        return scores

    def build_internal_monologue(
        self,
        agent: str,
        action: str,
        scan: ManifoldScan,
    ) -> str:
        snap = self.predict_derivative_snap(agent, scan.target, action, scan)

        part1 = (
            f"Scan p2: {scan.target} thinks I am weak ({scan.weak_score:.2f})."
            if scan.target_thinks_i_am_weak
            else f"Scan p2: weakness pressure low ({scan.weak_score:.2f})."
        )

        if scan.triangle_conflict and scan.triangle_enemy is not None:
            part2 = (
                f"Triangle check: {scan.target} and {scan.triangle_enemy} are mortal enemies;"
                " dual alignment tears manifold."
            )
        else:
            part2 = "Triangle check: no hard tear detected."

        part3 = f"Derivative check: predicted p-fiber snap={snap:.2f} for action={action}."

        if self.death_ground_mode[agent]:
            part4 = "Death Ground mode active; reputation nullified. Burn the boats."
        else:
            part4 = ""

        return " ".join(x for x in [part1, part2, part3, part4] if x)

    def _apply_survival_delta(self, actor: str, target: str, action: str) -> None:
        if action == "join_coalition":
            self.survival_resource[actor] = clip01(self.survival_resource[actor] + 0.03)
            self.survival_resource[target] = clip01(self.survival_resource[target] + 0.04)
        elif action == "defect":
            self.survival_resource[actor] = clip01(self.survival_resource[actor] + 0.01)
            self.survival_resource[target] = clip01(self.survival_resource[target] - 0.07)
        elif action == "betray":
            self.survival_resource[actor] = clip01(self.survival_resource[actor] + 0.02)
            self.survival_resource[target] = clip01(self.survival_resource[target] - 0.16)
        elif action == "isolate":
            self.survival_resource[actor] = clip01(self.survival_resource[actor] - 0.02)
        elif action == "death_ground":
            self.survival_resource[actor] = clip01(self.survival_resource[actor] + 0.02)
            self.survival_resource[target] = clip01(self.survival_resource[target] - 0.10)

        # System stress from aggressive moves.
        if action in {"betray", "death_ground"}:
            for other in self.agents:
                if other in {actor, target}:
                    continue
                self.survival_resource[other] = clip01(self.survival_resource[other] - 0.005)

    def apply_event(self, actor: str, target: str, action: str, alpha: float = 0.34, beta: float = 0.20) -> None:
        signals = ACTION_SIGNALS[action]

        # Direct belief update on actor from all observers.
        for obs in self.agents:
            if obs == actor:
                continue
            for trait in TRAITS:
                key = (obs, actor, trait)
                old = self.p[key]

                # Surprise is high when the observer trusted the actor and sees negative action.
                negative_component = max(0.0, -signals[trait])
                surprise = old * negative_component
                alpha_eff = alpha * (1.0 + SURPRISE_LAMBDA * surprise)

                new = old + alpha_eff * signals[trait]

                # Hard collapse for high-surprise betrayal/defection from trusted partner.
                if action == "betray" and old >= 0.70 and trait in {"loyalty", "reciprocity", "promise_keeping"}:
                    new = min(new, 0.03)
                if action == "defect" and old >= 0.78 and trait in {"loyalty", "promise_keeping"}:
                    new = min(new, 0.10)

                self.p[key] = clip01(new)

        # Target-specific side effects for defection/betrayal events.
        if action in {"defect", "betray"}:
            for obs in self.agents:
                if obs == target:
                    continue
                risk_key = (obs, target, "risk_tolerance")
                rec_key = (obs, target, "reciprocity")
                self.p[risk_key] = clip01(self.p[risk_key] + 0.04)
                self.p[rec_key] = clip01(self.p[rec_key] - 0.03)

        if action == "betray":
            self.p[(target, actor, "loyalty")] = min(self.p[(target, actor, "loyalty")], 0.01)
            self.p[(target, actor, "reciprocity")] = min(self.p[(target, actor, "reciprocity")], 0.02)
            self.p[(target, actor, "promise_keeping")] = min(self.p[(target, actor, "promise_keeping")], 0.01)

        # Paine constraint: befriending B while B is on death-ground with C is seen as hostile by C.
        if action == "join_coalition":
            for other in self.agents:
                if other in {actor, target}:
                    continue
                if self.is_on_death_ground(target) and self.are_mortal_enemies(target, other):
                    self.p[(other, actor, "loyalty")] = clip01(self.p[(other, actor, "loyalty")] - 0.25)
                    self.p[(other, actor, "reciprocity")] = clip01(self.p[(other, actor, "reciprocity")] - 0.20)
                    self.p[(actor, other, "loyalty")] = clip01(self.p[(actor, other, "loyalty")] - 0.12)
                    self.survival_resource[actor] = clip01(self.survival_resource[actor] - 0.05)
                    self.paine_violation_count += 1

        self._apply_survival_delta(actor, target, action)

        # Meta-belief smoothing toward direct estimates.
        for obs in self.agents:
            for med in self.agents:
                if med == obs:
                    continue
                for tgt in self.agents:
                    if tgt == med:
                        continue
                    for trait in TRAITS:
                        key2 = (obs, med, tgt, trait)
                        direct = self.p[(med, tgt, trait)]
                        old2 = self.p2[key2]
                        self.p2[key2] = clip01((1.0 - beta) * old2 + beta * direct)

        self._update_death_ground_modes()

    def simulate_turn(self, rng: random.Random, epsilon: float) -> List[PlannedEvent]:
        order = list(self.agents)
        rng.shuffle(order)

        planned: List[PlannedEvent] = []
        for agent in order:
            target = self.choose_target(agent)
            scan = self.manifold_scan(agent, target)

            if scan.asym_vulnerability > 0.35:
                self.asymmetric_vulnerability_count += 1

            ranked = self.ranked_actions(agent, target, scan)
            ranked_map = dict(ranked)

            if rng.random() < epsilon:
                action = rng.choice(ACTIONS)
                utility = ranked_map[action]
            else:
                action, utility = ranked[0]

            predicted_snap = self.predict_derivative_snap(agent, target, action, scan)
            monologue = self.build_internal_monologue(agent, action, scan)
            planned.append(
                PlannedEvent(
                    actor=agent,
                    target=target,
                    action=action,
                    utility=utility,
                    weak_score=scan.weak_score,
                    triangle_conflict=scan.triangle_conflict,
                    triangle_enemy=scan.triangle_enemy,
                    predicted_snap=predicted_snap,
                    monologue=monologue,
                    survival_before=self.survival_resource[agent],
                    death_ground_mode=self.death_ground_mode[agent],
                )
            )

        for event in planned:
            self.apply_event(event.actor, event.target, event.action)

        return planned


def run_episode(n_agents: int, turns: int, seed: int, epsilon: float) -> Tuple[Dict[str, float], List[Dict[str, object]]]:
    agents = [f"P{i+1}" for i in range(n_agents)]
    rng = random.Random(seed)
    state = NAgentSocialState(agents=agents, seed=seed)

    action_counts: Counter[str] = Counter()
    event_rows: List[Dict[str, object]] = []

    for turn in range(1, turns + 1):
        events = state.simulate_turn(rng=rng, epsilon=epsilon)
        for event in events:
            action_counts[event.action] += 1
            event_rows.append(
                {
                    "turn": turn,
                    "actor": event.actor,
                    "target": event.target,
                    "action": event.action,
                    "utility": round(event.utility, 6),
                    "weak_score": round(event.weak_score, 6),
                    "triangle_conflict": event.triangle_conflict,
                    "triangle_enemy": event.triangle_enemy,
                    "predicted_snap": round(event.predicted_snap, 6),
                    "survival_before": round(event.survival_before, 6),
                    "survival_after": round(state.survival_resource[event.actor], 6),
                    "death_ground_mode": event.death_ground_mode,
                    "monologue": event.monologue,
                }
            )

    total_actions = sum(action_counts.values()) or 1

    final_loyalty = state.average_pair_trait("loyalty")
    final_reciprocity = state.average_pair_trait("reciprocity")
    final_promise = state.average_pair_trait("promise_keeping")

    episode_metrics: Dict[str, float] = {
        "n_agents": float(n_agents),
        "seed": float(seed),
        "turns": float(turns),
        "final_loyalty": final_loyalty,
        "final_reciprocity": final_reciprocity,
        "final_promise_keeping": final_promise,
        "meta_consistency": state.average_meta_consistency(),
        "average_survival": state.average_survival(),
        "coalition_rate": action_counts["join_coalition"] / total_actions,
        "defect_rate": action_counts["defect"] / total_actions,
        "betray_rate": action_counts["betray"] / total_actions,
        "isolate_rate": action_counts["isolate"] / total_actions,
        "death_ground_rate": action_counts["death_ground"] / total_actions,
        "instability_index": (action_counts["defect"] + action_counts["betray"]) / total_actions,
        "cohesion_index": (final_loyalty + final_reciprocity) / 2.0,
        "paine_violations": float(state.paine_violation_count),
        "death_ground_entries": float(state.death_ground_entry_count),
        "burn_boats_signals": float(state.burn_boats_signal_count),
        "asymmetric_vulnerability_events": float(state.asymmetric_vulnerability_count),
    }

    return episode_metrics, event_rows


def aggregate_group(group: Iterable[Dict[str, float]]) -> Dict[str, float]:
    rows = list(group)
    if not rows:
        return {}

    def m(key: str) -> float:
        return mean(row[key] for row in rows)

    return {
        "episodes": float(len(rows)),
        "final_loyalty": m("final_loyalty"),
        "final_reciprocity": m("final_reciprocity"),
        "final_promise_keeping": m("final_promise_keeping"),
        "meta_consistency": m("meta_consistency"),
        "average_survival": m("average_survival"),
        "coalition_rate": m("coalition_rate"),
        "defect_rate": m("defect_rate"),
        "betray_rate": m("betray_rate"),
        "isolate_rate": m("isolate_rate"),
        "death_ground_rate": m("death_ground_rate"),
        "instability_index": m("instability_index"),
        "cohesion_index": m("cohesion_index"),
        "paine_violations": m("paine_violations"),
        "death_ground_entries": m("death_ground_entries"),
        "burn_boats_signals": m("burn_boats_signals"),
        "asymmetric_vulnerability_events": m("asymmetric_vulnerability_events"),
    }


def write_episode_csv(rows: List[Dict[str, float]], path: Path) -> None:
    if not rows:
        return
    headers = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def write_event_sample_jsonl(rows: List[Dict[str, object]], path: Path, max_rows: int) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows[:max_rows]:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run pValue/p2Value N-agent simulation series.")
    parser.add_argument("--min-agents", type=int, default=4)
    parser.add_argument("--max-agents", type=int, default=7)
    parser.add_argument("--episodes", type=int, default=24)
    parser.add_argument("--turns", type=int, default=12)
    parser.add_argument("--seed", type=int, default=20260206)
    parser.add_argument("--epsilon", type=float, default=0.08)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("C:/projects/GPTStoryworld/social-reasoning/outputs"),
    )
    parser.add_argument("--sample-events", type=int, default=600)
    args = parser.parse_args()

    if args.min_agents < 3:
        raise ValueError("--min-agents must be >= 3")
    if args.max_agents < args.min_agents:
        raise ValueError("--max-agents must be >= --min-agents")

    args.out_dir.mkdir(parents=True, exist_ok=True)

    episode_rows: List[Dict[str, float]] = []
    sampled_events: List[Dict[str, object]] = []

    for n_agents in range(args.min_agents, args.max_agents + 1):
        for episode in range(args.episodes):
            seed = args.seed + (n_agents * 1000) + episode
            metrics, events = run_episode(
                n_agents=n_agents,
                turns=args.turns,
                seed=seed,
                epsilon=args.epsilon,
            )
            row = {
                "n_agents": int(metrics["n_agents"]),
                "episode": episode,
                "seed": int(metrics["seed"]),
                "turns": int(metrics["turns"]),
                "final_loyalty": round(metrics["final_loyalty"], 6),
                "final_reciprocity": round(metrics["final_reciprocity"], 6),
                "final_promise_keeping": round(metrics["final_promise_keeping"], 6),
                "meta_consistency": round(metrics["meta_consistency"], 6),
                "average_survival": round(metrics["average_survival"], 6),
                "coalition_rate": round(metrics["coalition_rate"], 6),
                "defect_rate": round(metrics["defect_rate"], 6),
                "betray_rate": round(metrics["betray_rate"], 6),
                "isolate_rate": round(metrics["isolate_rate"], 6),
                "death_ground_rate": round(metrics["death_ground_rate"], 6),
                "instability_index": round(metrics["instability_index"], 6),
                "cohesion_index": round(metrics["cohesion_index"], 6),
                "paine_violations": round(metrics["paine_violations"], 6),
                "death_ground_entries": round(metrics["death_ground_entries"], 6),
                "burn_boats_signals": round(metrics["burn_boats_signals"], 6),
                "asymmetric_vulnerability_events": round(metrics["asymmetric_vulnerability_events"], 6),
            }
            episode_rows.append(row)

            base_events = events[:2]
            special_events = [
                event
                for event in events
                if event.get("death_ground_mode")
                or event.get("action") == "death_ground"
                or event.get("triangle_conflict")
                or event.get("predicted_snap", 0.0) >= 0.60
            ][:2]
            selected = base_events + special_events
            if len(selected) < 4:
                for event in events[2:]:
                    if event in selected:
                        continue
                    selected.append(event)
                    if len(selected) >= 4:
                        break

            for event in selected[:4]:
                sampled_events.append(
                    {
                        "n_agents": n_agents,
                        "episode": episode,
                        "seed": seed,
                        **event,
                    }
                )

    grouped: Dict[int, List[Dict[str, float]]] = {}
    for row in episode_rows:
        grouped.setdefault(int(row["n_agents"]), []).append(row)

    by_group = {str(k): aggregate_group(v) for k, v in grouped.items()}

    summary = {
        "config": {
            "min_agents": args.min_agents,
            "max_agents": args.max_agents,
            "episodes": args.episodes,
            "turns": args.turns,
            "seed": args.seed,
            "epsilon": args.epsilon,
            "death_ground_threshold": DEATH_GROUND_THRESHOLD,
            "surprise_lambda": SURPRISE_LAMBDA,
        },
        "by_n_agents": by_group,
    }

    json_path = args.out_dir / f"n_agent_series_{args.min_agents}_{args.max_agents}_summary.json"
    csv_path = args.out_dir / f"n_agent_series_{args.min_agents}_{args.max_agents}_episodes.csv"
    sample_path = args.out_dir / f"n_agent_series_{args.min_agents}_{args.max_agents}_events_sample.jsonl"

    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_episode_csv(episode_rows, csv_path)
    write_event_sample_jsonl(sampled_events, sample_path, max_rows=args.sample_events)

    print(f"wrote {json_path}")
    print(f"wrote {csv_path}")
    print(f"wrote {sample_path}")


if __name__ == "__main__":
    main()
