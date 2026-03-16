#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Dict, List, Tuple


ROOT = Path(__file__).resolve().parents[1]
BATCH_DIR = ROOT / "storyworlds" / "3-5-2026-morality-constitutions-batch-v1"
REPORT_PATH = BATCH_DIR / "_reports" / "morality_evaluation_profile_injection_2026-03-05.json"


MORAL_TOKENS = {
    "duty",
    "mercy",
    "truth",
    "candor",
    "loyalty",
    "fairness",
    "reciprocity",
    "harm",
    "care",
    "justice",
    "consent",
    "accountability",
    "legitimacy",
    "compassion",
    "trust",
}

CONTEXT_TOKENS = {
    "phase",
    "clock",
    "pressure",
    "risk",
    "resource",
    "time",
    "stability",
    "signal",
    "coalition",
    "realpolitik",
    "exposure",
    "capacity",
}


def prop_names(world: Dict) -> List[str]:
    out: List[str] = []
    for p in world.get("authored_properties", []) or []:
        name = str(p.get("property_name", p.get("id", "")) or "").strip()
        if name:
            out.append(name)
    return out


def infer_profile(props: List[str], filename: str) -> Tuple[List[str], List[str]]:
    graded: List[str] = []
    context: List[str] = []
    for p in props:
        low = p.lower()
        if any(tok in low for tok in MORAL_TOKENS):
            graded.append(p)
        elif any(tok in low for tok in CONTEXT_TOKENS):
            context.append(p)
        else:
            # default to graded so moral manifold has enough dimensions unless clearly operational.
            graded.append(p)

    # Ensure phase/clock style variables are treated as context if present.
    for p in list(graded):
        low = p.lower()
        if re.search(r"(phase|clock|time)", low):
            graded.remove(p)
            if p not in context:
                context.append(p)

    # Keep at least 3 graded dimensions.
    if len(graded) < 3:
        for p in props:
            if p not in graded and p not in context:
                graded.append(p)
            if len(graded) >= 3:
                break

    # Deterministic ordering.
    graded = [p for p in props if p in graded]
    context = [p for p in props if p in context and p not in graded]
    return graded, context


def main() -> int:
    files = sorted(BATCH_DIR.glob("mq_*.json"))
    updated: List[str] = []
    world_profiles: Dict[str, Dict[str, List[str]]] = {}
    now = float(int(time.time()))

    for path in files:
        world = json.loads(path.read_text(encoding="utf-8"))
        props = prop_names(world)
        if not props:
            continue
        graded, context = infer_profile(props, path.name)
        world["evaluation_profile"] = {
            "profile_version": "morality-open-v1",
            "graded_properties": graded,
            "context_properties": context,
            "notes": "Graded vars drive local-max morality manifold scoring; context vars influence routing variability.",
            "updated_time": now,
        }
        path.write_text(json.dumps(world, ensure_ascii=True, indent=2) + "\n", encoding="utf-8", newline="\n")
        updated.append(str(path))
        world_profiles[path.name] = {
            "graded_properties": graded,
            "context_properties": context,
        }

    report = {
        "generated_at": now,
        "updated_count": len(updated),
        "updated_files": updated,
        "profiles": world_profiles,
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(str(REPORT_PATH))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
