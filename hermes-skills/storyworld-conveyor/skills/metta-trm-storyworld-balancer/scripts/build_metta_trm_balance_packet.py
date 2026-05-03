#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def atom_text(value: Any) -> str:
    text = str(value if value is not None else "unknown")
    text = text.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{text}"'


def symbol(value: Any) -> str:
    text = str(value if value is not None else "unknown").strip()
    text = re.sub(r"[^A-Za-z0-9_.:-]+", "_", text)
    return text[:120] or "unknown"


def iter_options(encounter: dict[str, Any]) -> list[dict[str, Any]]:
    options = encounter.get("options")
    return options if isinstance(options, list) else []


def iter_reactions(option: dict[str, Any]) -> list[dict[str, Any]]:
    reactions = option.get("reactions")
    return reactions if isinstance(reactions, list) else []


def iter_effects(reaction: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("after_effects", "effects"):
        effects = reaction.get(key)
        if isinstance(effects, list):
            return effects
    return []


def consequence_target(node: dict[str, Any]) -> str | None:
    for key in ("consequence_id", "next_encounter", "target", "encounter_id"):
        value = node.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def consequence_targets(option: dict[str, Any]) -> list[str]:
    targets: list[str] = []
    option_target = consequence_target(option)
    if option_target:
        targets.append(option_target)
    for reaction in iter_reactions(option):
        reaction_target = consequence_target(reaction)
        if reaction_target:
            targets.append(reaction_target)
    return targets


def effect_property(effect: dict[str, Any]) -> str:
    for key in ("property_id", "property", "bounded_number_id", "stat", "id"):
        value = effect.get(key)
        if isinstance(value, str) and value:
            return value
    set_pointer = effect.get("Set")
    if isinstance(set_pointer, dict):
        keyring = set_pointer.get("keyring")
        if isinstance(keyring, list) and keyring:
            return str(keyring[0])
    keyring = effect.get("keyring")
    if isinstance(keyring, list) and keyring:
        return str(keyring[0])
    return "unknown_property"


def effect_operator(effect: dict[str, Any]) -> str:
    for key in ("operator", "op", "operation"):
        value = effect.get(key)
        if isinstance(value, str) and value:
            return value
    to_expr = effect.get("to")
    if isinstance(to_expr, dict):
        value = to_expr.get("operator_type")
        if isinstance(value, str) and value:
            return value
    return "unknown_op"


def effect_delta(effect: dict[str, Any]) -> float | None:
    for key in ("value", "delta", "amount", "constant"):
        value = effect.get(key)
        if isinstance(value, (int, float)):
            return float(value)
    inputs = effect.get("inputs")
    if isinstance(inputs, list):
        for item in inputs:
            if isinstance(item, (int, float)):
                return float(item)
            if isinstance(item, dict):
                for key in ("value", "constant", "delta"):
                    value = item.get(key)
                    if isinstance(value, (int, float)):
                        return float(value)
    to_expr = effect.get("to")
    if isinstance(to_expr, dict):
        operands = to_expr.get("operands")
        if isinstance(operands, list):
            for item in operands:
                if isinstance(item, dict):
                    value = item.get("value")
                    if isinstance(value, (int, float)):
                        return float(value)
    return None


def text_blob(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return " ".join(text_blob(v) for v in value.values())
    if isinstance(value, list):
        return " ".join(text_blob(v) for v in value)
    return ""


def detect_secret(option: dict[str, Any], encounter: dict[str, Any]) -> str | None:
    blob = text_blob([option, encounter]).lower()
    if "secret" in blob:
        return "secret_token"
    if "hidden" in blob:
        return "hidden_token"
    if "synthesis" in blob:
        return "synthesis_token"
    if "meta" in blob:
        return "meta_token"
    return None


def extract_quality(path: Path | None) -> dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        return load_json(path)
    except Exception:
        return {"load_error": str(path)}


def extract_monte_carlo(path: Path | None) -> dict[str, Any]:
    if not path or not path.exists():
        return {}
    text = path.read_text(encoding="utf-8", errors="replace")
    rates: dict[str, float] = {}
    unreachable: list[str] = []
    in_distribution = False
    in_unreachable = False
    secret_none_reachable = "None reachable" in text
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("--- Ending Distribution"):
            in_distribution = True
            in_unreachable = False
            continue
        if stripped.startswith("--- Unreachable Endings"):
            in_distribution = False
            in_unreachable = True
            continue
        if stripped.startswith("---") and not stripped.startswith("--- Unreachable Endings"):
            in_distribution = False
            if not stripped.startswith("--- Unreachable Endings"):
                in_unreachable = False
        if in_distribution:
            match = re.match(r"([A-Za-z0-9_.:-]+)\s+([0-9]+)\s+\(\s*([0-9]+(?:\.[0-9]+)?)%\)", stripped)
            if match:
                rates[match.group(1)] = float(match.group(3)) / 100.0
        if in_unreachable and stripped and not stripped.startswith("---"):
            unreachable.append(stripped)
    dominant = max(rates.items(), key=lambda item: item[1]) if rates else None
    return {
        "raw_excerpt": text[:4000],
        "ending_rates": rates,
        "dominant_ending": dominant[0] if dominant else None,
        "dominant_rate": dominant[1] if dominant else None,
        "unreachable_endings": unreachable,
        "secret_none_reachable": secret_none_reachable,
    }


def build_packet(storyworld: dict[str, Any], quality: dict[str, Any], monte_carlo: dict[str, Any]) -> dict[str, Any]:
    encounters = storyworld.get("encounters") if isinstance(storyworld.get("encounters"), list) else []
    title = storyworld.get("title") or storyworld.get("storyworld_title") or "Untitled Storyworld"
    encounter_ids = [str(e.get("id") or e.get("encounter_id") or f"encounter_{i:04d}") for i, e in enumerate(encounters)]
    id_set = set(encounter_ids)
    inbound: Counter[str] = Counter()
    outbound: Counter[str] = Counter()
    properties: Counter[str] = Counter()
    operators: Counter[str] = Counter()
    secret_options: list[dict[str, Any]] = []
    missing_targets: list[dict[str, str]] = []

    for encounter_id, encounter in zip(encounter_ids, encounters):
        for option_index, option in enumerate(iter_options(encounter)):
            option_id = str(option.get("id") or option.get("option_id") or f"option_{option_index}")
            targets = consequence_targets(option)
            for target in targets:
                outbound[encounter_id] += 1
                inbound[target] += 1
                if target not in id_set:
                    missing_targets.append({"encounter": encounter_id, "option": option_id, "target": target})
            reason = detect_secret(option, encounter)
            if reason:
                secret_options.append({"encounter": encounter_id, "option": option_id, "reason": reason})
            for reaction in iter_reactions(option):
                for effect in iter_effects(reaction):
                    prop = effect_property(effect)
                    properties[prop] += 1
                    operators[effect_operator(effect)] += 1

    terminal = [encounter_id for encounter_id, encounter in zip(encounter_ids, encounters) if not iter_options(encounter)]
    zero_inbound = [encounter_id for encounter_id in encounter_ids[1:] if inbound[encounter_id] == 0]
    dead_routes = [encounter_id for encounter_id, encounter in zip(encounter_ids, encounters) if iter_options(encounter) and outbound[encounter_id] == 0]

    observations: list[str] = []
    if zero_inbound:
        observations.append(f"{len(zero_inbound)} non-entry encounters have zero inbound links.")
    if dead_routes:
        observations.append(f"{len(dead_routes)} nonterminal encounters have no detected outgoing consequence targets.")
    if missing_targets:
        observations.append(f"{len(missing_targets)} option consequence targets are missing from encounter ids.")
    if not secret_options:
        observations.append("No secret-like options detected by text/tag scan.")
    if len(operators) <= 2:
        observations.append("Low apparent effect-operator diversity.")
    mc_unreachable = monte_carlo.get("unreachable_endings") if isinstance(monte_carlo.get("unreachable_endings"), list) else []
    mc_dominant = monte_carlo.get("dominant_ending")
    mc_dominant_rate = monte_carlo.get("dominant_rate")
    if mc_unreachable:
        observations.append(f"Monte Carlo reports {len(mc_unreachable)} unreachable ending(s).")
    if isinstance(mc_dominant_rate, (int, float)) and mc_dominant_rate >= 0.85:
        observations.append(f"Monte Carlo ending distribution is dominated by {mc_dominant} at {mc_dominant_rate:.1%}.")
    if monte_carlo.get("secret_none_reachable"):
        observations.append("Monte Carlo reports no reachable secret ending.")

    repair_targets: list[dict[str, Any]] = []
    for encounter_id in zero_inbound[:12]:
        repair_targets.append({"target": encounter_id, "type": "zero_inbound", "priority": "high"})
    for item in missing_targets[:12]:
        repair_targets.append({"target": item["target"], "type": "missing_consequence_target", "priority": "high", "source": item})
    if not secret_options:
        repair_targets.append({"target": "secret_route_layer", "type": "weak_secret_route_support", "priority": "medium"})
    if len(operators) <= 2:
        repair_targets.append({"target": "effect_operator_layer", "type": "low_effect_diversity", "priority": "medium"})
    for ending_id in mc_unreachable[:12]:
        repair_targets.append({"target": ending_id, "type": "unreachable_ending", "priority": "high"})
    if isinstance(mc_dominant_rate, (int, float)) and mc_dominant_rate >= 0.85:
        repair_targets.append({
            "target": mc_dominant,
            "type": "dominant_ending_distribution",
            "priority": "high",
            "rate": mc_dominant_rate,
        })
    if monte_carlo.get("secret_none_reachable"):
        repair_targets.append({"target": "secret_route_layer", "type": "secret_unreachable_in_monte_carlo", "priority": "high"})

    balance_signals = {
        "encounters": len(encounters),
        "terminal_encounters": len(terminal),
        "options": sum(len(iter_options(e)) for e in encounters),
        "zero_inbound": len(zero_inbound),
        "dead_routes": len(dead_routes),
        "missing_targets": len(missing_targets),
        "secret_options_detected": len(secret_options),
        "effect_properties": len(properties),
        "effect_operators": len(operators),
        "quality_report_present": bool(quality),
        "monte_carlo_report_present": bool(monte_carlo),
        "mc_unreachable_endings": len(mc_unreachable),
        "mc_dominant_ending": mc_dominant or "unknown",
        "mc_dominant_rate": mc_dominant_rate if mc_dominant_rate is not None else "unknown",
        "mc_secret_none_reachable": bool(monte_carlo.get("secret_none_reachable")),
    }

    return {
        "storyworld": title,
        "observations": observations,
        "balance_signals": balance_signals,
        "top_properties": properties.most_common(20),
        "top_operators": operators.most_common(20),
        "terminal_encounters": terminal[:30],
        "zero_inbound": zero_inbound[:50],
        "dead_routes": dead_routes[:50],
        "missing_targets": missing_targets[:50],
        "secret_options": secret_options[:50],
        "quality": quality,
        "monte_carlo": monte_carlo,
        "repair_targets": repair_targets,
        "trm_roles": {
            "router": [
                "Prioritize validator/acceptance defects before distribution aesthetics.",
                "Route zero-inbound and missing targets to topology repair.",
                "Route unreachable or absent secret route evidence to gate/effect support repair.",
            ],
            "verifier": [
                "Predict improvement only when the proposed edit changes a measured signal.",
                "Veto edits that add unforeshadowed shortcuts to secret endings.",
            ],
            "repair": [
                "Use the smallest schema-valid edit family that can move the target metric.",
                "Prefer upstream variable support over final-gate hacks.",
            ],
            "commit_veto": [
                "Commit only after validator passes and at least one target metric improves.",
                "Veto no-op metric deltas even if prose quality seems better.",
            ],
        },
    }


def build_metta(storyworld: dict[str, Any], packet: dict[str, Any]) -> str:
    encounters = storyworld.get("encounters") if isinstance(storyworld.get("encounters"), list) else []
    title = storyworld.get("title") or storyworld.get("storyworld_title") or "Untitled Storyworld"
    lines = [f"(Storyworld {atom_text(title)})"]
    for key, value in packet["balance_signals"].items():
        lines.append(f"(BalanceSignal {symbol(key)} {atom_text(value)})")
    for index, encounter in enumerate(encounters):
        encounter_id = str(encounter.get("id") or encounter.get("encounter_id") or f"encounter_{index:04d}")
        options = iter_options(encounter)
        lines.append(f"(Encounter {symbol(encounter_id)})")
        lines.append(f"(OutboundCount {symbol(encounter_id)} {len(options)})")
        if not options:
            lines.append(f"(Terminal {symbol(encounter_id)})")
        for option_index, option in enumerate(options):
            option_id = str(option.get("id") or option.get("option_id") or f"option_{option_index}")
            lines.append(f"(Option {symbol(encounter_id)} {symbol(option_id)})")
            for target in consequence_targets(option):
                lines.append(f"(Consequence {symbol(encounter_id)} {symbol(option_id)} {symbol(target)})")
            reason = detect_secret(option, encounter)
            if reason:
                lines.append(f"(SecretCandidate {symbol(encounter_id)} {symbol(option_id)} {symbol(reason)})")
            for reaction_index, reaction in enumerate(iter_reactions(option)):
                lines.append(f"(Reaction {symbol(encounter_id)} {symbol(option_id)} {reaction_index})")
                for effect in iter_effects(reaction):
                    prop = effect_property(effect)
                    op = effect_operator(effect)
                    delta = effect_delta(effect)
                    lines.append(
                        f"(Effect {symbol(encounter_id)} {symbol(option_id)} {reaction_index} "
                        f"{symbol(prop)} {symbol(op)} {atom_text(delta if delta is not None else 'unknown')})"
                    )
    for target in packet["repair_targets"]:
        lines.append(
            f"(RepairTarget {symbol(target.get('target'))} {symbol(target.get('type'))} {symbol(target.get('priority'))})"
        )
    return "\n".join(lines) + "\n"


def build_brief(packet: dict[str, Any]) -> str:
    lines = [
        f"# MeTTa/TRM Balance Brief: {packet['storyworld']}",
        "",
        "## Balance Signals",
        "",
    ]
    for key, value in packet["balance_signals"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Observations", ""])
    if packet["observations"]:
        for item in packet["observations"]:
            lines.append(f"- {item}")
    else:
        lines.append("- No immediate structural balance warnings detected by the packet builder.")
    lines.extend(["", "## Repair Targets", ""])
    if packet["repair_targets"]:
        for item in packet["repair_targets"][:20]:
            lines.append(f"- {item.get('priority')}: {item.get('type')} -> {item.get('target')}")
    else:
        lines.append("- No repair targets emitted.")
    lines.extend([
        "",
        "## TRM Use",
        "",
        "- Router: choose exactly one repair target.",
        "- Verifier: predict whether a candidate edit changes validator, Monte Carlo, quality, or authoring metrics.",
        "- Repair: propose the smallest schema-valid edit family.",
        "- Commit/veto: commit only after measured improvement.",
    ])
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build MeTTa-style storyworld balance facts and TRM packets.")
    parser.add_argument("--storyworld", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--quality-report", default="")
    parser.add_argument("--monte-carlo-report", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    storyworld_path = Path(args.storyworld)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    quality_path = Path(args.quality_report) if args.quality_report else None
    mc_path = Path(args.monte_carlo_report) if args.monte_carlo_report else None

    storyworld = load_json(storyworld_path)
    quality = extract_quality(quality_path)
    monte_carlo = extract_monte_carlo(mc_path)
    packet = build_packet(storyworld, quality, monte_carlo)

    (out_dir / "trm_balance_packet.json").write_text(
        json.dumps(packet, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    (out_dir / "world_balance.metta").write_text(build_metta(storyworld, packet), encoding="utf-8", newline="\n")
    (out_dir / "balance_brief.md").write_text(build_brief(packet), encoding="utf-8", newline="\n")
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
