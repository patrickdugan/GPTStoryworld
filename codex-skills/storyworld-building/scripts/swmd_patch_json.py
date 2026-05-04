"""
Patch a SweepWeave storyworld JSON from full SWMD-0 markdown.

This is intentionally conservative: it treats the JSON file as the schema source
of truth and uses SWMD only to patch encounter titles/text, option text,
reaction text, and reaction consequence targets. Desirability/effect formulas
remain in JSON unless dedicated formula tooling updates them.

Usage:
  python swmd_patch_json.py --base-json world.json --swmd world.swmd.md --out-json patched.json
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ENC_RE = re.compile(r"^## ENC\s+(\S+)\s+\|\s*(.*?)\s+\|\s*turn=([^\s|]+)")
OPT_RE = re.compile(r"^OPT\s+(\S+):\s*(.*)$")
RXN_RE = re.compile(r"^\s*RXN\s+(\S+)\s*->\s*(\S*)\s*$")
TEXT_RE = re.compile(r"^\s*T:\s*(.*)$")


def ptr_string(text: str) -> dict[str, Any]:
    return {"pointer_type": "String Constant", "script_element_type": "Pointer", "value": text}


def parse_swmd_full(path: Path) -> dict[str, Any]:
    encounters: dict[str, dict[str, Any]] = {}
    current_enc: dict[str, Any] | None = None
    current_opt: dict[str, Any] | None = None
    current_rxn: dict[str, Any] | None = None
    pending_text_target: str | None = None

    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.rstrip()
        enc_match = ENC_RE.match(line)
        if enc_match:
            enc_id, title, turn_span = enc_match.groups()
            current_enc = {
                "id": enc_id,
                "title": title.strip(),
                "turn_span": turn_span.strip(),
                "text": "",
                "options": {},
            }
            encounters[enc_id] = current_enc
            current_opt = None
            current_rxn = None
            pending_text_target = None
            continue

        if current_enc is None:
            continue

        opt_match = OPT_RE.match(line)
        if opt_match:
            opt_id, text = opt_match.groups()
            current_opt = {"id": opt_id, "text": text.strip(), "reactions": {}}
            current_enc["options"][opt_id] = current_opt
            current_rxn = None
            pending_text_target = None
            continue

        rxn_match = RXN_RE.match(line)
        if rxn_match and current_opt is not None:
            rxn_id, consequence = rxn_match.groups()
            current_rxn = {"id": rxn_id, "consequence_id": consequence.strip(), "text": ""}
            current_opt["reactions"][rxn_id] = current_rxn
            pending_text_target = "reaction"
            continue

        text_match = TEXT_RE.match(line)
        if text_match:
            text = text_match.group(1).strip()
            if current_rxn is not None and pending_text_target == "reaction":
                current_rxn["text"] = text
            elif current_opt is None:
                current_enc["text"] = text
            continue

    return {"encounters": encounters}


def patch_world(base: dict[str, Any], swmd: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    patches = {
        "encounter_text": 0,
        "encounter_title": 0,
        "option_text": 0,
        "reaction_text": 0,
        "reaction_consequence": 0,
        "missing_encounters": [],
        "missing_options": [],
        "missing_reactions": [],
    }
    swmd_encounters = swmd.get("encounters", {})
    for enc in base.get("encounters", []) or []:
        enc_id = str(enc.get("id", ""))
        patch_enc = swmd_encounters.get(enc_id)
        if not patch_enc:
            continue
        if patch_enc.get("title") and enc.get("title") != patch_enc["title"]:
            enc["title"] = patch_enc["title"]
            patches["encounter_title"] += 1
        if patch_enc.get("text"):
            existing = enc.get("text_script", {})
            existing_text = existing.get("value") if isinstance(existing, dict) else ""
            if existing_text != patch_enc["text"]:
                enc["text_script"] = ptr_string(patch_enc["text"])
                patches["encounter_text"] += 1

        options_by_id = {str(opt.get("id", "")): opt for opt in enc.get("options", []) or []}
        for opt_id, patch_opt in (patch_enc.get("options") or {}).items():
            opt = options_by_id.get(str(opt_id))
            if opt is None:
                patches["missing_options"].append(opt_id)
                continue
            if patch_opt.get("text"):
                existing = opt.get("text_script", {})
                existing_text = existing.get("value") if isinstance(existing, dict) else ""
                if existing_text != patch_opt["text"]:
                    opt["text_script"] = ptr_string(patch_opt["text"])
                    patches["option_text"] += 1
            reactions_by_id = {str(rxn.get("id", "")): rxn for rxn in opt.get("reactions", []) or []}
            for rxn_id, patch_rxn in (patch_opt.get("reactions") or {}).items():
                rxn = reactions_by_id.get(str(rxn_id))
                if rxn is None:
                    patches["missing_reactions"].append(rxn_id)
                    continue
                if patch_rxn.get("text"):
                    existing = rxn.get("text_script", {})
                    existing_text = existing.get("value") if isinstance(existing, dict) else ""
                    if existing_text != patch_rxn["text"]:
                        rxn["text_script"] = ptr_string(patch_rxn["text"])
                        patches["reaction_text"] += 1
                if patch_rxn.get("consequence_id") and rxn.get("consequence_id") != patch_rxn["consequence_id"]:
                    rxn["consequence_id"] = patch_rxn["consequence_id"]
                    patches["reaction_consequence"] += 1

    base_ids = {str(enc.get("id", "")) for enc in base.get("encounters", []) or []}
    for enc_id in swmd_encounters:
        if enc_id not in base_ids:
            patches["missing_encounters"].append(enc_id)
    return base, patches


def main() -> int:
    parser = argparse.ArgumentParser(description="Patch SweepWeave JSON from full SWMD-0 markdown.")
    parser.add_argument("--base-json", required=True, type=Path)
    parser.add_argument("--swmd", required=True, type=Path)
    parser.add_argument("--out-json", required=True, type=Path)
    parser.add_argument("--report-out", type=Path, default=None)
    args = parser.parse_args()

    base = json.loads(args.base_json.read_text(encoding="utf-8-sig"))
    swmd = parse_swmd_full(args.swmd)
    patched, report = patch_world(base, swmd)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(patched, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    if args.report_out:
        args.report_out.parent.mkdir(parents=True, exist_ok=True)
        args.report_out.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    print(str(args.out_json))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
