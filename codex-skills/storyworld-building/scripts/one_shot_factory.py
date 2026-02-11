#!/usr/bin/env python3
"""Create a one-shot storyworld draft from a larger base world.

This script trims to a target encounter count, rewires consequences, and rethemes
title/about/encounter text so the result is immediately usable for polish passes.
"""

from __future__ import annotations

import argparse
import json
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Sequence


def _str_const(text: str) -> Dict[str, Any]:
    return {"script_element_type": "Pointer", "pointer_type": "String Constant", "value": text}


def _is_terminal(enc: Dict[str, Any]) -> bool:
    eid = str(enc.get("id", ""))
    if eid.startswith("page_end") or eid.startswith("page_secret"):
        return True
    return not (enc.get("options", []) or [])


def _retheme_encounter(enc: Dict[str, Any], motif: str) -> None:
    ts = enc.get("text_script")
    if not (isinstance(ts, dict) and ts.get("pointer_type") == "String Constant"):
        enc["text_script"] = _str_const(motif)
        return
    base = str(ts.get("value", "")).strip()
    if motif not in base:
        ts["value"] = f"{base} {motif}".strip()


def build_subset(data: Dict[str, Any], target_encounters: int, title: str, about: str, motif: str) -> Dict[str, Any]:
    out = json.loads(json.dumps(data))
    encounters = out.get("encounters", []) or []
    if not encounters:
        return out

    non_terminal = [e for e in encounters if not _is_terminal(e)]
    terminal = [e for e in encounters if _is_terminal(e)]
    if not terminal:
        terminal = [non_terminal[-1]] if non_terminal else [encounters[-1]]

    n_non_terminal = max(1, min(len(non_terminal), target_encounters - 4))
    n_terminal = max(1, min(len(terminal), target_encounters - n_non_terminal))
    selected = non_terminal[:n_non_terminal] + terminal[:n_terminal]
    selected = selected[:target_encounters]
    selected_ids = {str(e.get("id", "")) for e in selected}

    # Ensure we have at least one fallback terminal.
    fallback_terminal_id = str(terminal[0].get("id", selected[-1].get("id")))

    # Rewire consequences to remain inside subset.
    id_to_pos = {str(e.get("id")): i for i, e in enumerate(selected)}
    for i, enc in enumerate(selected):
        _retheme_encounter(enc, motif)
        opts = enc.get("options", []) or []
        if not opts:
            continue
        next_default = fallback_terminal_id
        for j in range(i + 1, len(selected)):
            cand = selected[j]
            if not _is_terminal(cand):
                next_default = str(cand.get("id"))
                break
        for opt in opts:
            for rxn in opt.get("reactions", []) or []:
                cid = str(rxn.get("consequence_id", ""))
                if (not cid) or (cid == "wild") or (cid not in selected_ids):
                    rxn["consequence_id"] = next_default

    out["encounters"] = selected

    # Keep only selected ids in spools.
    kept_spools = []
    for sp in out.get("spools", []) or []:
        encs = [eid for eid in (sp.get("encounters", []) or []) if str(eid) in selected_ids]
        if encs:
            sp["encounters"] = encs
            kept_spools.append(sp)
    out["spools"] = kept_spools

    out["title"] = title
    out["about_text"] = _str_const(about)
    out["IFID"] = f"SW-{uuid.uuid4()}"
    out["modified_time"] = float(time.time())
    if "creation_time" not in out:
        out["creation_time"] = float(time.time())
    return out


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="One-shot factory for themed storyworld drafts")
    p.add_argument("--base", required=True, help="Base storyworld JSON")
    p.add_argument("--out", required=True, help="Output JSON path")
    p.add_argument("--target-encounters", type=int, default=40)
    p.add_argument("--title", required=True)
    p.add_argument("--about", required=True)
    p.add_argument("--motif", required=True, help="Sentence to inject into encounter text")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    base = json.loads(Path(args.base).resolve().read_text(encoding="utf-8"))
    out = build_subset(
        base,
        target_encounters=int(args.target_encounters),
        title=str(args.title),
        about=str(args.about),
        motif=str(args.motif),
    )
    out_path = Path(args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
