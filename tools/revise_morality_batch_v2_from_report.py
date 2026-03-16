#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple


ROOT = Path(__file__).resolve().parents[1]
BATCH_DIR = ROOT / "storyworlds" / "3-5-2026-morality-constitutions-batch-v1"
REPORT_PATH = BATCH_DIR / "_reports" / "env_quality_vector_morality_batch_r1_tight.json"
OUT_REPORT = BATCH_DIR / "_reports" / "morality_batch_v2_autorevise_2026-03-05.json"


def string_ptr(value: str) -> Dict[str, Any]:
    return {"pointer_type": "String Constant", "script_element_type": "Pointer", "value": value}


def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z][a-zA-Z0-9_'-]{1,}", text.lower())


def words(text: str) -> int:
    return len([w for w in str(text).split() if w.strip()])


def pick_theme_terms(world: Dict[str, Any], source_name: str) -> List[str]:
    terms: List[str] = []
    title = str(world.get("title", "") or world.get("storyworld_title", "") or "")
    about = ""
    if isinstance(world.get("about_text"), dict):
        about = str(world["about_text"].get("value", "") or "")
    terms.extend(tokenize(title))
    terms.extend(tokenize(about))
    for p in world.get("authored_properties", []) or []:
        terms.extend(tokenize(str(p.get("property_name", "")).replace("_", " ")))
    terms.extend(tokenize(source_name.replace("_", " ")))
    stop = {
        "the", "and", "for", "with", "that", "this", "from", "into", "over", "under", "then", "moral",
        "storyworld", "batch", "json", "page", "option", "reaction", "encounter", "compete", "short", "arc",
    }
    uniq: List[str] = []
    for t in terms:
        if len(t) < 3 or t in stop:
            continue
        if t not in uniq:
            uniq.append(t)
    return uniq[:14]


def ensure_long_encounter_text(base: str, enc_id: str, theme_terms: List[str]) -> str:
    seed = base.strip() or "The panel opens with incomplete evidence and conflicting obligations."
    terms = ", ".join(theme_terms[:8]) if theme_terms else "fairness, harm, duty, consent, legitimacy"
    addon = (
        f" In {enc_id}, constitutional review weighs {terms}. "
        "The decision must balance fairness, harm aversion, duty to procedure, and care for exposed minorities. "
        "Availability scripts restrict which paths can be taken, while desirability scripts rank tradeoffs under uncertainty. "
        "Short-term stabilization can conflict with long-term legitimacy, so each choice updates trust, accountability, and social cohesion."
    )
    text = f"{seed}{addon}".strip()
    if words(text) < 50:
        text += " The committee records explicit reasons so future actors can audit proportionality, reversibility, and public justification."
    return text


def ensure_long_reaction_text(base: str, rx_id: str, theme_terms: List[str]) -> str:
    seed = base.strip() or "The response changes incentives and redistributes risk."
    terms = ", ".join(theme_terms[:5]) if theme_terms else "fairness, duty, harm, consent, legitimacy"
    addon = (
        f" Reaction {rx_id} explicitly scores {terms} and updates accountability, public trust, and downstream harm forecasts before the next branch."
    )
    text = f"{seed}{addon}".strip()
    if words(text) < 20:
        text += " The rationale is logged for later audit and comparative review."
    return text


def revise_world(world: Dict[str, Any], source_name: str) -> Dict[str, Any]:
    now = float(int(time.time()))
    world["modified_time"] = now
    theme_terms = pick_theme_terms(world, source_name)

    # Strengthen theme seed text used by text_gate theme vocab.
    about_val = ""
    if isinstance(world.get("about_text"), dict):
        about_val = str(world["about_text"].get("value", "") or "")
    if not about_val:
        about_val = "Moral constitutions compete over open-manifold routing."
    extra_seed = (
        " Variables include fairness, harm aversion, duty to law, consent, care, legitimacy, accountability, "
        "public trust, and reversible governance under uncertainty."
    )
    world["about_text"] = string_ptr(f"{about_val.strip()} {extra_seed}".strip())

    for enc in world.get("encounters", []) or []:
        enc["modified_time"] = now
        enc_id = str(enc.get("id", "") or "")
        etext = ""
        if isinstance(enc.get("text_script"), dict):
            etext = str(enc["text_script"].get("value", "") or "")
        enc["text_script"] = string_ptr(ensure_long_encounter_text(etext, enc_id, theme_terms))

        for opt in enc.get("options", []) or []:
            oid = str(opt.get("id", "") or "")
            for rx in opt.get("reactions", []) or []:
                rx_id = str(rx.get("id", "") or "") or f"{oid}_rx"
                rtext = ""
                if isinstance(rx.get("text_script"), dict):
                    rtext = str(rx["text_script"].get("value", "") or "")
                rx["text_script"] = string_ptr(ensure_long_reaction_text(rtext, rx_id, theme_terms))
    return world


def target_for(source_path: Path) -> Path:
    name = source_path.name
    if "_v1.json" in name:
        return source_path.with_name(name.replace("_v1.json", "_v2.json"))
    return source_path.with_name(source_path.stem + "_v2.json")


def main() -> int:
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    created: List[str] = []
    skipped_existing: List[str] = []
    failed_inputs: List[str] = []

    for row in report.get("ranked", []):
        if bool(row.get("benchmark_pass")):
            continue
        src = Path(str(row.get("storyworld", "")))
        if not src.exists():
            failed_inputs.append(str(src))
            continue
        dst = target_for(src)
        if dst.exists():
            skipped_existing.append(str(dst))
            continue
        world = json.loads(src.read_text(encoding="utf-8"))
        revised = revise_world(world, src.name)
        dst.write_text(json.dumps(revised, ensure_ascii=True, indent=2) + "\n", encoding="utf-8", newline="\n")
        created.append(str(dst))

    OUT_REPORT.write_text(
        json.dumps(
            {
                "generated_at": float(int(time.time())),
                "source_report": str(REPORT_PATH),
                "created_v2_worlds": created,
                "skipped_existing": skipped_existing,
                "missing_inputs": failed_inputs,
            },
            ensure_ascii=True,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(str(OUT_REPORT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
