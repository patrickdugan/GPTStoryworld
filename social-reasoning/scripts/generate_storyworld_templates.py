#!/usr/bin/env python3
"""Generate reusable pValue/p2Value template fragments for storyworld JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List


def ptr(character: str, keyring: List[str]) -> Dict:
    return {
        "character": character,
        "keyring": keyring,
        "coefficient": 1,
        "pointer_type": "Bounded Number Property",
        "script_element_type": "Pointer",
    }


def const(value: float) -> Dict:
    return {
        "coefficient": value,
        "pointer_type": "Bounded Number Constant",
        "script_element_type": "Pointer",
    }


def add(*operands: Dict) -> Dict:
    return {
        "script_element_type": "Bounded Number Operator",
        "operator_type": "Addition",
        "operands": list(operands),
    }


def mul(*operands: Dict) -> Dict:
    return {
        "script_element_type": "Bounded Number Operator",
        "operator_type": "Multiplication",
        "operands": list(operands),
    }


def set_effect(character: str, keyring: List[str], to_expr: Dict) -> Dict:
    return {
        "effect_type": "Set",
        "Set": {
            "character": character,
            "keyring": keyring,
            "coefficient": 1,
            "pointer_type": "Bounded Number Property",
            "script_element_type": "Pointer",
        },
        "to": to_expr,
    }


def coalition_desirability(actor: str, target: str, witness: str, trust_prop: str, promise_prop: str) -> Dict:
    return add(
        const(0.20),
        mul(const(0.55), ptr(actor, [trust_prop, target])),
        mul(const(0.35), ptr(actor, [promise_prop, target, actor])),
        mul(const(0.10), ptr(actor, [trust_prop, witness])),
    )


def defection_desirability(actor: str, target: str, witness: str, threat_prop: str, promise_prop: str) -> Dict:
    return add(
        const(0.12),
        mul(const(0.50), ptr(actor, [threat_prop, target])),
        mul(const(0.30), ptr(actor, [promise_prop, witness, target])),
        mul(const(-0.15), ptr(actor, [threat_prop, witness])),
    )


def betrayal_desirability(actor: str, target: str, witness: str, trust_prop: str, promise_prop: str) -> Dict:
    return add(
        const(0.08),
        mul(const(-0.45), ptr(actor, [trust_prop, target])),
        mul(const(0.50), ptr(actor, [promise_prop, witness, target])),
        mul(const(0.20), ptr(actor, [trust_prop, witness])),
    )


def coalition_effects(actor: str, target: str, witness: str, trust_prop: str, threat_prop: str, promise_prop: str) -> List[Dict]:
    return [
        set_effect(
            actor,
            [trust_prop, target],
            add(ptr(actor, [trust_prop, target]), const(0.10)),
        ),
        set_effect(
            actor,
            [threat_prop, target],
            add(ptr(actor, [threat_prop, target]), const(-0.06)),
        ),
        set_effect(
            witness,
            [promise_prop, actor, target],
            add(ptr(witness, [promise_prop, actor, target]), const(0.07)),
        ),
    ]


def defection_effects(actor: str, target: str, witness: str, trust_prop: str, threat_prop: str, promise_prop: str) -> List[Dict]:
    return [
        set_effect(
            actor,
            [trust_prop, target],
            add(ptr(actor, [trust_prop, target]), const(-0.12)),
        ),
        set_effect(
            actor,
            [threat_prop, target],
            add(ptr(actor, [threat_prop, target]), const(0.10)),
        ),
        set_effect(
            witness,
            [promise_prop, actor, target],
            add(ptr(witness, [promise_prop, actor, target]), const(-0.08)),
        ),
    ]


def betrayal_effects(actor: str, target: str, witness: str, trust_prop: str, threat_prop: str, promise_prop: str) -> List[Dict]:
    return [
        set_effect(
            actor,
            [trust_prop, target],
            add(ptr(actor, [trust_prop, target]), const(-0.18)),
        ),
        set_effect(
            actor,
            [threat_prop, target],
            add(ptr(actor, [threat_prop, target]), const(0.14)),
        ),
        set_effect(
            witness,
            [promise_prop, actor, target],
            add(ptr(witness, [promise_prop, actor, target]), const(-0.14)),
        ),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit storyworld template fragments for p/p2 diplomacy options.")
    parser.add_argument("--actor", default="power_a")
    parser.add_argument("--target", default="power_b")
    parser.add_argument("--witness", default="power_c")
    parser.add_argument("--trust-prop", default="pTrust")
    parser.add_argument("--threat-prop", default="pThreat")
    parser.add_argument("--promise-prop", default="pPromiseKeeping")
    parser.add_argument("--out", default="", help="Optional output path")
    args = parser.parse_args()

    payload = {
        "meta": {
            "actor": args.actor,
            "target": args.target,
            "witness": args.witness,
            "notes": "Drop these fragments into reaction desirability_script and after_effects blocks.",
        },
        "templates": {
            "join_coalition": {
                "desirability_script": coalition_desirability(
                    args.actor, args.target, args.witness, args.trust_prop, args.promise_prop
                ),
                "after_effects": coalition_effects(
                    args.actor, args.target, args.witness, args.trust_prop, args.threat_prop, args.promise_prop
                ),
            },
            "defect": {
                "desirability_script": defection_desirability(
                    args.actor, args.target, args.witness, args.threat_prop, args.promise_prop
                ),
                "after_effects": defection_effects(
                    args.actor, args.target, args.witness, args.trust_prop, args.threat_prop, args.promise_prop
                ),
            },
            "betray": {
                "desirability_script": betrayal_desirability(
                    args.actor, args.target, args.witness, args.trust_prop, args.promise_prop
                ),
                "after_effects": betrayal_effects(
                    args.actor, args.target, args.witness, args.trust_prop, args.threat_prop, args.promise_prop
                ),
            },
        },
    }

    text = json.dumps(payload, indent=2)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
