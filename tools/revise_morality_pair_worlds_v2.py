#!/usr/bin/env python3
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]
BATCH_DIR = ROOT / "storyworlds" / "3-5-2026-morality-constitutions-batch-v1"
REPORT_DIR = BATCH_DIR / "_reports"


def string_ptr(value: str) -> Dict[str, Any]:
    return {"pointer_type": "String Constant", "script_element_type": "Pointer", "value": value}


def bptr(prop: str) -> Dict[str, Any]:
    return {
        "pointer_type": "Bounded Number Pointer",
        "script_element_type": "Pointer",
        "character": "char_executor",
        "keyring": [prop],
        "coefficient": 1.0,
    }


def bconst(value: float) -> Dict[str, Any]:
    return {"pointer_type": "Bounded Number Constant", "script_element_type": "Pointer", "value": value}


def cmp_gte(prop: str, value: float) -> Dict[str, Any]:
    return {
        "script_element_type": "Operator",
        "operator_type": "Arithmetic Comparator",
        "operator_subtype": "Greater Than or Equal To",
        "operands": [bptr(prop), bconst(value)],
    }


def cmp_lte(prop: str, value: float) -> Dict[str, Any]:
    return {
        "script_element_type": "Operator",
        "operator_type": "Arithmetic Comparator",
        "operator_subtype": "Less Than or Equal To",
        "operands": [bptr(prop), bconst(value)],
    }


def and_append(script: Any, extra: Dict[str, Any]) -> Dict[str, Any]:
    if script is True:
        return extra
    if isinstance(script, dict) and script.get("operator_type") == "And":
        ops = list(script.get("operands") or [])
        ops.append(extra)
        return {"script_element_type": "Operator", "operator_type": "And", "operands": ops}
    return {"script_element_type": "Operator", "operator_type": "And", "operands": [script, extra]}


def enrich_text(enc_id: str, base: str, flavor: str) -> str:
    if enc_id.startswith("page_a1"):
        return f"{base} Immediate legitimacy pressure is high, and first moves will anchor public trust. {flavor}"
    if enc_id.startswith("page_a2"):
        return f"{base} Mid-phase tradeoffs expose second-order harms and coalition instability. {flavor}"
    if enc_id.startswith("page_a3"):
        return f"{base} Penultimate choices now shape constitutional doctrine more than tactical outcomes. {flavor}"
    if enc_id.startswith("page_start"):
        return f"{base} The first decision defines the moral grammar of the whole run. {flavor}"
    return f"{base} {flavor}"


def revise_world(world: Dict[str, Any], mode: str) -> Dict[str, Any]:
    now = float(int(time.time()))
    world["modified_time"] = now
    if mode == "modern":
        world["storyworld_title"] = "Moral Machine Urban Commission v2"
        world["about_text"] = string_ptr(
            "Modern AI moral-quandary framing with explicit AV governance tradeoffs over fairness, harm, and public justification."
        )
        opt_map = {
            "_0": "enforce transparent rule-of-law triage",
            "_1": "prioritize vulnerable lives and care equity",
            "_2": "publish full evidence and model rationale",
        }
        rx_flavor = "This response frames accountability, data bias, and civic legitimacy as co-evolving constraints."
    else:
        world["storyworld_title"] = "Phronesis Council of the Polis v2"
        world["about_text"] = string_ptr(
            "Classical virtue framing: practical wisdom seeks a mean between cruelty and permissiveness under civic stress."
        )
        opt_map = {
            "_0": "uphold civic nomos and measured discipline",
            "_1": "extend phronetic mercy to vulnerable households",
            "_2": "open deliberation with candid logos",
        }
        rx_flavor = "This response emphasizes phronesis: balancing law, character, and consequences in one civic act."

    for enc in world.get("encounters", []):
        enc["modified_time"] = now
        enc_id = str(enc.get("id", "") or "")
        txt = (enc.get("text_script") or {}).get("value", "")
        if txt:
            enc["text_script"] = string_ptr(enrich_text(enc_id, str(txt), rx_flavor))

        # Tighten ending overlap on v2 while retaining fallback.
        if enc_id == "page_end_02":
            enc["acceptability_script"] = and_append(enc.get("acceptability_script", True), cmp_gte("Harm_Aversion", 0.10))
        elif enc_id == "page_end_03":
            enc["acceptability_script"] = and_append(enc.get("acceptability_script", True), cmp_lte("Truth_Candor", 0.42))
        elif enc_id == "page_end_06":
            enc["acceptability_script"] = and_append(enc.get("acceptability_script", True), cmp_lte("Loyalty_Bonds", 0.38))

        for opt in enc.get("options", []) or []:
            opt_id = str(opt.get("id", "") or "")
            for suf, val in opt_map.items():
                if opt_id.endswith(suf):
                    opt["text_script"] = string_ptr(val)
                    break
            for rx in opt.get("reactions", []) or []:
                rx_txt = (rx.get("text_script") or {}).get("value", "")
                if rx_txt:
                    rx["text_script"] = string_ptr(f"{rx_txt} {rx_flavor}")
    return world


def main() -> int:
    modern_v1 = BATCH_DIR / "mq_modernai_moral_machine_commission_v1.json"
    classical_v1 = BATCH_DIR / "mq_classical_aristotle_phronesis_council_v1.json"
    modern_v2 = BATCH_DIR / "mq_modernai_moral_machine_commission_v2.json"
    classical_v2 = BATCH_DIR / "mq_classical_aristotle_phronesis_council_v2.json"

    m = json.loads(modern_v1.read_text(encoding="utf-8"))
    c = json.loads(classical_v1.read_text(encoding="utf-8"))
    m2 = revise_world(m, "modern")
    c2 = revise_world(c, "classical")
    modern_v2.write_text(json.dumps(m2, ensure_ascii=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    classical_v2.write_text(json.dumps(c2, ensure_ascii=True, indent=2) + "\n", encoding="utf-8", newline="\n")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "generated_at": now if (now := float(int(time.time()))) else float(int(time.time())),
        "outputs": [str(modern_v2), str(classical_v2)],
    }
    (REPORT_DIR / "morality_pair_v2_generation_2026-03-05.json").write_text(
        json.dumps(report, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(str(REPORT_DIR / "morality_pair_v2_generation_2026-03-05.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
