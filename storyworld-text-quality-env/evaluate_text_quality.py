#!/usr/bin/env python3
"""Evaluate storyworld text quality using an OpenAI judge model."""

from __future__ import annotations

import argparse
import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Tuple


def _read_key(api_key_file: str) -> str:
    env = os.environ.get("OPENAI_API_KEY", "").strip()
    if env:
        return env
    if api_key_file:
        p = Path(api_key_file).expanduser().resolve()
        if p.exists():
            return p.read_text(encoding="utf-8").strip()
    desktop = Path.home() / "Desktop" / "GPTAPI.txt"
    if desktop.exists():
        return desktop.read_text(encoding="utf-8").strip()
    return ""


def _extract_text(script: Any) -> str:
    if isinstance(script, dict) and script.get("pointer_type") == "String Constant":
        return str(script.get("value", "") or "")
    if isinstance(script, str):
        return script
    return ""


def extract_samples(data: Dict[str, Any], max_encounters: int = 50, max_reactions: int = 200) -> Dict[str, Any]:
    encounters = []
    reactions = []
    for enc in data.get("encounters", []) or []:
        eid = str(enc.get("id", ""))
        etxt = _extract_text(enc.get("text_script"))
        if eid and etxt:
            encounters.append({"id": eid, "title": str(enc.get("title", "")), "text": etxt})
        for opt in enc.get("options", []) or []:
            oid = str(opt.get("id", ""))
            for rxn in opt.get("reactions", []) or []:
                rid = str(rxn.get("id", ""))
                rtxt = _extract_text(rxn.get("text_script"))
                if eid and oid and rid and rtxt:
                    reactions.append(
                        {"id": f"{eid}::{oid}::{rid}", "encounter_id": eid, "option_id": oid, "reaction_id": rid, "text": rtxt}
                    )
    return {"encounters": encounters[:max_encounters], "reactions": reactions[:max_reactions]}


def _heuristic_report(data: Dict[str, Any], samples: Dict[str, Any]) -> Dict[str, Any]:
    def uniq_ratio(texts: List[str]) -> float:
        if not texts:
            return 0.0
        norm = [re.sub(r"\s+", " ", t.strip().lower()) for t in texts if t.strip()]
        if not norm:
            return 0.0
        return len(set(norm)) / len(norm)

    e_texts = [x["text"] for x in samples["encounters"]]
    r_texts = [x["text"] for x in samples["reactions"]]
    e_uniq = uniq_ratio(e_texts)
    r_uniq = uniq_ratio(r_texts)
    avg_e_len = sum(len(t.split()) for t in e_texts) / max(1, len(e_texts))
    avg_r_len = sum(len(t.split()) for t in r_texts) / max(1, len(r_texts))
    # coarse local proxy for dry run only
    thematic = 0.8 if data.get("title") and _extract_text(data.get("about_text")) else 0.4
    non_rep = (e_uniq + r_uniq) / 2.0
    narrative = min(1.0, avg_e_len / 70.0)
    reaction_voice = min(1.0, avg_r_len / 30.0)
    overall = (thematic + non_rep + narrative + reaction_voice) / 4.0
    return {
        "overall_score": round(overall, 4),
        "dimension_scores": {
            "thematic_relevance": round(thematic, 4),
            "stylistic_distinctiveness": round(non_rep, 4),
            "encounter_narrative_quality": round(narrative, 4),
            "reaction_voice_quality": round(reaction_voice, 4),
            "specificity_and_imagery": round(narrative, 4),
            "coherence_and_consistency": round(thematic, 4),
            "non_repetition": round(non_rep, 4),
            "choice_consequence_clarity": round(reaction_voice, 4),
        },
        "summary": "Dry-run heuristic report (no model call).",
        "top_issues": [],
        "revision_instructions": [],
        "failing_examples": [],
    }


def _extract_json(text: str) -> Dict[str, Any]:
    raw = text.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?", "", raw).strip()
        raw = re.sub(r"```$", "", raw).strip()
    try:
        return json.loads(raw)
    except Exception:
        m = re.search(r"\{.*\}", raw, re.S)
        if not m:
            raise
        return json.loads(m.group(0))


def _responses_text(resp: Dict[str, Any]) -> str:
    if resp.get("output_text"):
        return str(resp["output_text"])
    out = []
    for item in resp.get("output", []):
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                out.append(content.get("text", ""))
    return "\n".join(out).strip()


def run_judge(
    storyworld_path: Path,
    judge_model: str,
    api_key: str,
    dry_run: bool,
    max_encounters: int,
    max_reactions: int,
) -> Dict[str, Any]:
    data = json.loads(storyworld_path.read_text(encoding="utf-8"))
    samples = extract_samples(data, max_encounters=max_encounters, max_reactions=max_reactions)
    if dry_run or not api_key:
        parsed = _heuristic_report(data, samples)
        return {
            "mode": "dry-run",
            "model": judge_model,
            "storyworld": str(storyworld_path),
            "samples": {"encounters": len(samples["encounters"]), "reactions": len(samples["reactions"])},
            "judge": parsed,
            "raw_response_text": "",
        }

    base_dir = Path(__file__).resolve().parent
    system_prompt = (base_dir / "judge_system_prompt.md").read_text(encoding="utf-8")
    system_card = (base_dir / "storyworld_system_card.md").read_text(encoding="utf-8")
    user_payload = {
        "title": data.get("title", ""),
        "about": _extract_text(data.get("about_text")),
        "samples": samples,
    }
    req_body = {
        "model": judge_model,
        "input": [
            {"role": "system", "content": [{"type": "input_text", "text": system_prompt + "\n\n" + system_card}]},
            {"role": "user", "content": [{"type": "input_text", "text": json.dumps(user_payload, ensure_ascii=True)}]},
        ],
        "max_output_tokens": 1400,
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(req_body).encode("utf-8"),
        method="POST",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            resp = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Judge API error HTTP {exc.code}: {detail}") from exc
    text = _responses_text(resp)
    parsed = _extract_json(text)
    return {
        "mode": "api",
        "model": judge_model,
        "storyworld": str(storyworld_path),
        "samples": {"encounters": len(samples["encounters"]), "reactions": len(samples["reactions"])},
        "judge": parsed,
        "raw_response_text": text,
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Storyworld text quality judge")
    p.add_argument("--storyworld", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--judge-model", default="gpt-5-mini")
    p.add_argument("--api-key-file", default="")
    p.add_argument("--max-encounters", type=int, default=50)
    p.add_argument("--max-reactions", type=int, default=200)
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    storyworld = Path(args.storyworld).resolve()
    out_path = Path(args.out).resolve()
    api_key = _read_key(args.api_key_file)
    report = run_judge(
        storyworld_path=storyworld,
        judge_model=args.judge_model,
        api_key=api_key,
        dry_run=bool(args.dry_run),
        max_encounters=int(args.max_encounters),
        max_reactions=int(args.max_reactions),
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
