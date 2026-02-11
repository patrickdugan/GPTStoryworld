#!/usr/bin/env python3
"""Generate a small batch of themed storyworld variants from a high-quality base."""

from __future__ import annotations

import argparse
import copy
import json
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List


THEMES = [
    {
        "suffix": "v7_archive_parliament",
        "title": "Last and First Men: The Archive Parliament",
        "about": "A civilizational senate of archivists and futurists debates whether memory should be constitutional law, tactical weapon, or sacred burden.",
        "lexicon": ["archive", "parliament", "constitution", "dissent", "coalition"],
    },
    {
        "suffix": "v8_orbital_schism",
        "title": "Last and First Men: Orbital Schism",
        "about": "Orbital houses split over austerity, spectacle, and emergency powers as old catastrophes return as policy arguments.",
        "lexicon": ["orbital", "schism", "austerity", "spectacle", "mandate"],
    },
    {
        "suffix": "v9_cathedral_of_forecast",
        "title": "Last and First Men: Cathedral of Forecasts",
        "about": "Competing schools of prediction weaponize models, rituals, and rumor to lock in the future before rivals do.",
        "lexicon": ["forecast", "cathedral", "ritual", "countermodel", "betrayal"],
    },
    {
        "suffix": "v10_ash_coalitions",
        "title": "Last and First Men: Ash Coalitions",
        "about": "After repeated collapses, surviving blocs bargain over legitimacy, vengeance, and who gets to write the next founding myth.",
        "lexicon": ["ash", "coalition", "legitimacy", "vengeance", "myth"],
    },
    {
        "suffix": "v11_mercy_protocol",
        "title": "Last and First Men: Mercy Protocol",
        "about": "A doctrine of strategic mercy competes with hardline preemption, forcing every faction to choose what kind of future deserves survival.",
        "lexicon": ["mercy", "protocol", "preemption", "survival", "doctrine"],
    },
]


def _as_string_ptr(text: str) -> Dict[str, Any]:
    return {"script_element_type": "Pointer", "pointer_type": "String Constant", "value": text}


def _retitle_prefix(encounter: Dict[str, Any], theme: Dict[str, Any], idx: int) -> None:
    title = str(encounter.get("title", "")).strip() or f"Encounter {idx + 1}"
    marker = theme["lexicon"][idx % len(theme["lexicon"])]
    encounter["title"] = f"{title} [{marker}]"


def _rewrite_encounter_text(encounter: Dict[str, Any], theme: Dict[str, Any]) -> None:
    script = encounter.get("text_script")
    if not (isinstance(script, dict) and script.get("pointer_type") == "String Constant"):
        encounter["text_script"] = _as_string_ptr(theme["about"])
        return
    base = str(script.get("value", "")).strip()
    addition = (
        f" The chamber frames this as a {theme['lexicon'][0]} dispute over {theme['lexicon'][1]} authority, "
        f"with arguments pivoting on {theme['lexicon'][2]}, {theme['lexicon'][3]}, and {theme['lexicon'][4]}."
    )
    if addition not in base:
        script["value"] = (base + addition).strip()


def _rewrite_option_text(option: Dict[str, Any], theme: Dict[str, Any], index: int) -> None:
    ts = option.get("text_script")
    if not (isinstance(ts, dict) and ts.get("pointer_type") == "String Constant"):
        ts = _as_string_ptr("Choose a strategic branch.")
        option["text_script"] = ts
    label = str(ts.get("value", "")).strip().split(".")[0]
    token = theme["lexicon"][index % len(theme["lexicon"])]
    ts["value"] = f"{label}. Prioritize {token} leverage."


def build_variant(base: Dict[str, Any], theme: Dict[str, Any]) -> Dict[str, Any]:
    out = copy.deepcopy(base)
    out["IFID"] = f"SW-{uuid.uuid4()}"
    out["title"] = theme["title"]
    out["about_text"] = _as_string_ptr(theme["about"])
    out["modified_time"] = float(time.time())
    if "creation_time" not in out:
        out["creation_time"] = float(time.time())

    encounters: List[Dict[str, Any]] = out.get("encounters", []) or []
    for i, encounter in enumerate(encounters[:18]):
        _retitle_prefix(encounter, theme, i)
        _rewrite_encounter_text(encounter, theme)
        for j, opt in enumerate((encounter.get("options") or [])[:4]):
            _rewrite_option_text(opt, theme, i + j)
    return out


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate 5 high-quality themed variants from a base storyworld.")
    p.add_argument("--base", required=True, help="Path to base JSON (already quality-gated)")
    p.add_argument("--out-dir", required=True, help="Output directory for generated variants")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    base_path = Path(args.base).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    base = json.loads(base_path.read_text(encoding="utf-8"))

    manifest = []
    for theme in THEMES:
        variant = build_variant(base, theme)
        out_name = f"first_and_last_men_{theme['suffix']}.json"
        out_path = out_dir / out_name
        out_path.write_text(json.dumps(variant, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
        manifest.append({"theme": theme["suffix"], "title": theme["title"], "file": str(out_path)})

    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps({"base": str(base_path), "count": len(manifest), "variants": manifest}, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(str(manifest_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
