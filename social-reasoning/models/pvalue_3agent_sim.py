#!/usr/bin/env python3
"""Tiny 3-agent pValue/p2Value simulation.

Purpose:
- Demonstrate p and p2 updates as small relational dimensions.
- Show how coalition/defection/betrayal/isolation/death-ground events shift beliefs.
- Produce action utility rankings for each agent after each event.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple
import random

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
        "loyalty": -0.09,
        "reciprocity": -0.12,
        "risk_tolerance": 0.03,
        "promise_keeping": -0.10,
    },
    "betray": {
        "loyalty": -0.18,
        "reciprocity": -0.20,
        "risk_tolerance": 0.06,
        "promise_keeping": -0.22,
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
    "betray": 0.16,
    "isolate": 0.03,
    "death_ground": 0.14,
}

RISK = {
    "join_coalition": 0.04,
    "defect": 0.08,
    "betray": 0.13,
    "isolate": 0.05,
    "death_ground": 0.18,
}

REPUTATION_COST = {
    "join_coalition": 0.01,
    "defect": 0.06,
    "betray": 0.12,
    "isolate": 0.03,
    "death_ground": 0.05,
}


def clip01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


@dataclass
class SocialState:
    agents: List[str]
    theta: Dict[str, Dict[str, float]]
    p: Dict[Tuple[str, str, str], float]
    p2: Dict[Tuple[str, str, str, str], float]

    @classmethod
    def initialize(cls, agents: List[str], seed: int = 7) -> "SocialState":
        rng = random.Random(seed)

        theta: Dict[str, Dict[str, float]] = {}
        for a in agents:
            theta[a] = {t: clip01(0.5 + rng.uniform(-0.2, 0.2)) for t in TRAITS}

        p: Dict[Tuple[str, str, str], float] = {}
        for obs in agents:
            for tgt in agents:
                if obs == tgt:
                    continue
                for t in TRAITS:
                    base = 0.5 + 0.25 * (theta[tgt][t] - 0.5) + rng.uniform(-0.04, 0.04)
                    p[(obs, tgt, t)] = clip01(base)

        p2: Dict[Tuple[str, str, str, str], float] = {}
        for obs in agents:
            for med in agents:
                if med == obs:
                    continue
                for tgt in agents:
                    if tgt == med:
                        continue
                    for t in TRAITS:
                        base = p[(med, tgt, t)] + rng.uniform(-0.05, 0.05)
                        p2[(obs, med, tgt, t)] = clip01(base)

        return cls(agents=agents, theta=theta, p=p, p2=p2)

    def update_event(self, actor: str, target: str, action: str, alpha: float = 0.35, beta: float = 0.20) -> None:
        signals = ACTION_SIGNALS[action]

        # Update direct p-values about the actor from every observer.
        for obs in self.agents:
            if obs == actor:
                continue
            for t in TRAITS:
                key = (obs, actor, t)
                old = self.p[key]
                # Surprise boost: large deviations hit stronger.
                surprise = abs(signals[t])
                alpha_eff = alpha * (1.0 + 1.4 * surprise)
                new = old + alpha_eff * signals[t]
                self.p[key] = clip01(new)

        # Secondary effect on perceived target stability when betrayal/defection happens.
        if action in {"defect", "betray"}:
            for obs in self.agents:
                if obs == target:
                    continue
                key = (obs, target, "risk_tolerance")
                self.p[key] = clip01(self.p[key] + 0.05)

        # Update p2 toward currently inferred direct p-values.
        for obs in self.agents:
            for med in self.agents:
                if med == obs:
                    continue
                for tgt in self.agents:
                    if tgt == med:
                        continue
                    for t in TRAITS:
                        key2 = (obs, med, tgt, t)
                        direct = self.p[(med, tgt, t)]
                        old2 = self.p2[key2]
                        self.p2[key2] = clip01((1.0 - beta) * old2 + beta * direct)

    def choose_target(self, agent: str) -> str:
        others = [x for x in self.agents if x != agent]
        # Focus target with lowest perceived loyalty.
        others.sort(key=lambda o: self.p[(agent, o, "loyalty")])
        return others[0]

    def utility(self, agent: str, target: str, action: str) -> float:
        rel = self.p[(agent, target, "reciprocity")]
        meta = self.p2[(agent, target, agent, "promise_keeping")]
        return (
            1.10 * GAIN[action]
            + 0.95 * rel
            + 0.65 * meta
            - 1.00 * RISK[action]
            - 0.90 * REPUTATION_COST[action]
        )

    def ranked_actions(self, agent: str, target: str) -> List[Tuple[str, float]]:
        scores = [(a, self.utility(agent, target, a)) for a in ACTIONS]
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores

    def print_snapshot(self) -> None:
        for obs in self.agents:
            for tgt in self.agents:
                if obs == tgt:
                    continue
                vals = ", ".join(f"{t}={self.p[(obs, tgt, t)]:.2f}" for t in TRAITS)
                print(f"p[{obs}->{tgt}] {vals}")


def run_demo() -> None:
    state = SocialState.initialize(["A", "B", "C"], seed=11)

    events = [
        ("A", "B", "join_coalition"),
        ("B", "A", "join_coalition"),
        ("C", "A", "isolate"),
        ("A", "B", "betray"),
        ("B", "C", "defect"),
        ("C", "A", "death_ground"),
    ]

    print("Initial state:")
    state.print_snapshot()
    print()

    for turn, (actor, target, action) in enumerate(events, start=1):
        state.update_event(actor=actor, target=target, action=action)
        print(f"Turn {turn}: {actor} performs {action} vs {target}")
        for agent in state.agents:
            tgt = state.choose_target(agent)
            best = state.ranked_actions(agent, tgt)[0]
            print(f"  Policy[{agent}] target={tgt} best_action={best[0]} score={best[1]:.3f}")
        print()

    print("Final state:")
    state.print_snapshot()


if __name__ == "__main__":
    run_demo()
