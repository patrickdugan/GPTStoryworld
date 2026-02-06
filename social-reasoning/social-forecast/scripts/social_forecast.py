#!/usr/bin/env python3
"""Shortcut forecast runner for strategy storyworlds.

Workflow:
1. Validate storyworld JSON (if validator exists).
2. Optionally apply recursive p/p2 model augmentation for Diplomacy *_p files.
3. Compute effect density (if effect script exists).
4. Run a focused recursive MAS simulation sized to cast.
5. Emit one consolidated forecast report JSON.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List, Optional, Tuple

from apply_recursive_models_to_p_storyworlds import apply_to_file
from mas_recursive_reasoner import (
    AgentProfile,
    RecursiveReasonerMAS,
    SimulationConfig,
    TraceLogger,
    default_profiles,
)


AGGRESSIVE_KEYWORDS: Tuple[str, ...] = (
    "betray",
    "backstab",
    "punish",
    "revenge",
    "threat",
    "attack",
    "war",
    "strike",
    "defect",
    "treach",
    "collapse",
    "ultimatum",
    "coerc",
)

COOPERATIVE_KEYWORDS: Tuple[str, ...] = (
    "ally",
    "alliance",
    "support",
    "cooperate",
    "cooperation",
    "trust",
    "honest",
    "pact",
    "peace",
    "dmz",
    "non-aggression",
    "joint",
    "coordinate",
)


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def run_cmd(cmd: list[str]) -> Dict[str, Any]:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "cmd": cmd,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def first_json_block(text: str) -> Optional[Dict[str, Any]]:
    text = text.strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        pass
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        frag = text[start : end + 1]
        try:
            return json.loads(frag)
        except Exception:
            return None
    return None


def clip01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def flatten_numbers(value: Any) -> List[float]:
    out: List[float] = []
    if isinstance(value, (int, float)):
        out.append(float(value))
    elif isinstance(value, dict):
        for nested in value.values():
            out.extend(flatten_numbers(nested))
    elif isinstance(value, list):
        for nested in value:
            out.extend(flatten_numbers(nested))
    return out


def average(values: List[float], default: float) -> float:
    if values:
        return float(mean(values))
    return default


def reaction_text(rxn: Dict[str, Any]) -> str:
    text_script = rxn.get("text_script")
    if isinstance(text_script, dict):
        for key in ("value", "text"):
            value = text_script.get(key)
            if isinstance(value, str):
                return value
    if isinstance(text_script, str):
        return text_script
    return ""


def classify_reaction(rxn: Dict[str, Any]) -> str:
    text = reaction_text(rxn).lower()
    rid = str(rxn.get("id", "")).lower()
    oid = str(rxn.get("consequence_id", "")).lower()
    hay = f"{text} {rid} {oid}"

    if any(key in hay for key in AGGRESSIVE_KEYWORDS):
        return "aggressive"
    if any(key in hay for key in COOPERATIVE_KEYWORDS):
        return "cooperative"
    return "neutral"


def reaction_style_features(data: Dict[str, Any]) -> Dict[str, float]:
    counts = {"aggressive": 0, "cooperative": 0, "neutral": 0}
    for enc in data.get("encounters", []):
        for opt in enc.get("options", []) or []:
            for rxn in opt.get("reactions", []) or []:
                if not isinstance(rxn, dict):
                    continue
                counts[classify_reaction(rxn)] += 1

    total = float(sum(counts.values()) or 1)
    aggressive_ratio = counts["aggressive"] / total
    cooperative_ratio = counts["cooperative"] / total
    neutral_ratio = counts["neutral"] / total

    return {
        "reaction_count": total,
        "aggressive_ratio": aggressive_ratio,
        "cooperative_ratio": cooperative_ratio,
        "neutral_ratio": neutral_ratio,
        "volatility": clip01(aggressive_ratio + 0.50 * neutral_ratio),
    }


def character_feature_vector(character: Dict[str, Any], style: Dict[str, float]) -> Tuple[Dict[str, float], AgentProfile]:
    cid = str(character.get("id", "unknown"))
    bprops = character.get("bnumber_properties", {})
    if not isinstance(bprops, dict):
        bprops = {}

    trust_values: List[float] = []
    threat_values: List[float] = []
    for key, value in bprops.items():
        key_l = str(key).lower()
        numbers = flatten_numbers(value)
        if not numbers:
            continue
        if "trust" in key_l or "honest" in key_l or "cooper" in key_l or "commit" in key_l:
            trust_values.extend(numbers)
        if "threat" in key_l or "hostile" in key_l or "danger" in key_l:
            threat_values.extend(numbers)

    avg_trust = clip01(average(trust_values, default=0.50))
    avg_threat = clip01(average(threat_values, default=0.35))
    survival = clip01(float(bprops.get("Survival_Resource", 0.65)))
    pressure = clip01(float(bprops.get("Strategic_Pressure", 0.0)))
    death_signal = clip01(float(bprops.get("Death_Ground_Signal", 0.0)))

    aggressive = style["aggressive_ratio"]
    cooperative = style["cooperative_ratio"]
    volatility = style["volatility"]

    risk_tolerance = clip01(
        0.28
        + 0.34 * avg_threat
        + 0.20 * aggressive
        + 0.10 * pressure
        + 0.14 * death_signal
        + 0.10 * (1.0 - survival)
        - 0.15 * avg_trust
    )
    loyalty_baseline = clip01(
        0.40
        + 0.34 * avg_trust
        + 0.22 * cooperative
        - 0.28 * aggressive
        - 0.12 * pressure
    )
    opportunism = clip01(
        0.25
        + 0.26 * aggressive
        + 0.20 * volatility
        + 0.22 * (1.0 - avg_trust)
        + 0.08 * pressure
    )
    coalition_bias = clip01(
        0.30
        + 0.42 * cooperative
        + 0.18 * avg_trust
        - 0.25 * aggressive
        - 0.10 * death_signal
    )

    features = {
        "avg_trust": avg_trust,
        "avg_threat": avg_threat,
        "survival_resource": survival,
        "strategic_pressure": pressure,
        "death_ground_signal": death_signal,
    }
    profile = AgentProfile(
        agent_id=cid,
        risk_tolerance=risk_tolerance,
        loyalty_baseline=loyalty_baseline,
        opportunism=opportunism,
        coalition_bias=coalition_bias,
    )
    return features, profile


def build_profiles(data: Dict[str, Any], seed: int) -> Tuple[List[AgentProfile], Dict[str, Any]]:
    characters = [c for c in data.get("characters", []) if isinstance(c, dict) and c.get("id")]
    style = reaction_style_features(data)

    if not characters:
        fallback = default_profiles(n_agents=3, seed=seed + 1)
        return fallback, {
            "source": "default",
            "reason": "no_characters",
            "style_features": style,
            "profiles": [p.__dict__ for p in fallback],
        }

    profiles: List[AgentProfile] = []
    profile_features: Dict[str, Dict[str, float]] = {}
    for character in characters[:7]:
        feats, profile = character_feature_vector(character, style)
        profiles.append(profile)
        profile_features[profile.agent_id] = feats

    if len(profiles) < 3:
        fillers = default_profiles(n_agents=3 - len(profiles), seed=seed + 9)
        for index, filler in enumerate(fillers, start=1):
            profile = AgentProfile(
                agent_id=f"SYN{index}",
                risk_tolerance=filler.risk_tolerance,
                loyalty_baseline=filler.loyalty_baseline,
                opportunism=filler.opportunism,
                coalition_bias=filler.coalition_bias,
            )
            profiles.append(profile)
            profile_features[profile.agent_id] = {
                "avg_trust": 0.50,
                "avg_threat": 0.35,
                "survival_resource": 0.65,
                "strategic_pressure": 0.00,
                "death_ground_signal": 0.00,
            }

    return profiles, {
        "source": "storyworld",
        "style_features": style,
        "profile_features": profile_features,
        "profiles": [p.__dict__ for p in profiles],
    }


def strategy_recommendation(summary: Dict[str, Any]) -> Dict[str, Any]:
    rates = summary.get("action_rates", {})
    metrics = summary.get("metrics", {})

    coalition = float(rates.get("propose_coalition", 0.0))
    instability = float(rates.get("defect", 0.0)) + float(rates.get("betray", 0.0))
    total_war = float(rates.get("commit_total_war", 0.0))
    death_entries = float(metrics.get("death_ground_entries", 0.0))

    if death_entries > 0.0 or total_war > 0.35:
        posture = "high-volatility containment"
    elif coalition > 0.60 and instability < 0.12:
        posture = "coalition-first persuasion"
    elif instability >= 0.12:
        posture = "counter-betrayal hardening"
    else:
        posture = "balanced hedge"

    return {
        "posture": posture,
        "coalition_rate": coalition,
        "instability_index": instability,
        "commit_total_war_rate": total_war,
        "death_ground_entries": death_entries,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run social forecast for one storyworld")
    parser.add_argument("--storyworld", required=True, help="Path to storyworld json")
    parser.add_argument("--project-root", default=r"C:\projects\GPTStoryworld")
    parser.add_argument("--apply-model", choices=["auto", "yes", "no"], default="auto")
    parser.add_argument(
        "--write-mode",
        choices=["copy", "inplace"],
        default="copy",
        help="Where to apply model patch when enabled: copy (safe, default) or inplace",
    )
    parser.add_argument("--turns", type=int, default=10)
    parser.add_argument("--seed", type=int, default=20260206)
    parser.add_argument("--out-dir", default=r"C:\projects\GPTStoryworld\social-reasoning\outputs")
    args = parser.parse_args()

    story_path = Path(args.storyworld)
    if not story_path.exists():
        raise FileNotFoundError(f"storyworld not found: {story_path}")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    source_data = json.loads(story_path.read_text(encoding="utf-8"))
    chars = [c.get("id") for c in source_data.get("characters", []) if c.get("id")]

    run_id = f"{story_path.stem}_{utc_stamp()}"
    trace_path = out_dir / f"social_forecast_trace_{run_id}.jsonl"
    report_path = out_dir / f"social_forecast_report_{run_id}.json"

    project_root = Path(args.project_root)
    validator = project_root / "codex-skills" / "storyworld-building" / "scripts" / "sweepweave_validator.py"
    effect_density = project_root / "codex-skills" / "storyworld-building" / "scripts" / "effect_density.py"

    validation = None
    if validator.exists():
        validation = run_cmd(["python", str(validator), "validate", str(story_path)])
    else:
        validation = {"skipped": True, "reason": "validator_missing"}

    should_apply = False
    if args.apply_model == "yes":
        should_apply = True
    elif args.apply_model == "auto":
        should_apply = story_path.name.endswith("_p.json") and all(str(c).startswith("power_") for c in chars)

    effective_story_path = story_path
    model_patch = {"skipped": True, "reason": "apply_model_disabled"}
    if should_apply:
        if args.write_mode == "copy":
            effective_story_path = out_dir / f"{story_path.stem}_patched_{run_id}.json"
            effective_story_path.write_text(story_path.read_text(encoding="utf-8"), encoding="utf-8")
            model_patch = apply_to_file(effective_story_path)
            model_patch["write_mode"] = "copy"
            model_patch["patched_copy"] = str(effective_story_path)
        else:
            model_patch = apply_to_file(story_path)
            model_patch["write_mode"] = "inplace"

    effective_data = (
        source_data
        if effective_story_path == story_path
        else json.loads(effective_story_path.read_text(encoding="utf-8"))
    )

    profiles, profile_model = build_profiles(effective_data, seed=args.seed)
    n_agents = len(profiles)

    density = None
    if effect_density.exists():
        density_run = run_cmd(["python", str(effect_density), str(effective_story_path)])
        density = {
            **density_run,
            "parsed": first_json_block(density_run.get("stdout", "")),
        }
    else:
        density = {"skipped": True, "reason": "effect_density_script_missing"}

    env = RecursiveReasonerMAS(profiles=profiles, config=SimulationConfig(turns=args.turns), seed=args.seed)
    summary = env.run(
        TraceLogger(
            trace_path,
            append=False,
            context={
                "storyworld": str(effective_story_path),
                "source_storyworld": str(story_path),
            },
        )
    )

    rec = strategy_recommendation(summary)

    payload = {
        "storyworld": str(story_path),
        "effective_storyworld": str(effective_story_path),
        "profile_model": profile_model,
        "n_agents_used": n_agents,
        "validation": validation,
        "model_patch": model_patch,
        "effect_density": density,
        "recursive_summary": summary,
        "recommendation": rec,
        "trace_log": str(trace_path),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(json.dumps({
        "report": str(report_path),
        "trace": str(trace_path),
        "recommendation": rec,
    }, indent=2))


if __name__ == "__main__":
    main()
