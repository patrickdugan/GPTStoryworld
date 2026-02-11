#!/usr/bin/env python3
"""Iterate storyworld text rewrites until quality threshold is reached."""

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List

from evaluate_text_quality import run_judge


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


def _ensure_text_script(script: Any) -> Dict[str, Any]:
    if isinstance(script, dict) and script.get("pointer_type") == "String Constant":
        return script
    return {"script_element_type": "Pointer", "pointer_type": "String Constant", "value": ""}


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


def _collect_rewrite_targets(data: Dict[str, Any], judge: Dict[str, Any], max_items: int = 80) -> Dict[str, Any]:
    encounter_map: Dict[str, Dict[str, str]] = {}
    reaction_map: Dict[str, Dict[str, str]] = {}
    for enc in data.get("encounters", []) or []:
        eid = str(enc.get("id", ""))
        if eid:
            encounter_map[eid] = {"id": eid, "text": _extract_text(enc.get("text_script"))}
        for opt in enc.get("options", []) or []:
            oid = str(opt.get("id", ""))
            for rxn in opt.get("reactions", []) or []:
                rid = str(rxn.get("id", ""))
                key = f"{eid}::{oid}::{rid}"
                reaction_map[key] = {"id": key, "text": _extract_text(rxn.get("text_script"))}

    failing = judge.get("failing_examples", []) or []
    enc_targets: List[Dict[str, str]] = []
    rxn_targets: List[Dict[str, str]] = []
    for item in failing:
        sid = str(item.get("id", ""))
        kind = str(item.get("kind", ""))
        if kind == "encounter" and sid in encounter_map:
            enc_targets.append(encounter_map[sid])
        elif kind == "reaction" and sid in reaction_map:
            rxn_targets.append(reaction_map[sid])

    if not enc_targets and not rxn_targets:
        # fallback: top sample if judge didn't emit failing IDs
        enc_targets = list(encounter_map.values())[: min(25, len(encounter_map))]
        rxn_targets = list(reaction_map.values())[: min(55, len(reaction_map))]

    return {"encounters": enc_targets[:max_items], "reactions": rxn_targets[:max_items]}


def _request_rewrites(
    data: Dict[str, Any],
    judge: Dict[str, Any],
    targets: Dict[str, Any],
    writer_model: str,
    api_key: str,
) -> Dict[str, Any]:
    prompt = (
        "You are revising storyworld text only.\n"
        "Keep IDs unchanged. Do not change mechanics, scripts, or graph.\n"
        "Return JSON only with schema:\n"
        "{\n"
        '  "encounter_rewrites":[{"id":"...", "text":"..."}],\n'
        '  "reaction_rewrites":[{"id":"enc::opt::rxn", "text":"..."}]\n'
        "}\n"
        "Rules:\n"
        "- Make each rewritten text unique.\n"
        "- Keep thematic relevance to title/about.\n"
        "- Improve vividness, voice, and consequence clarity.\n"
        "- Avoid repetitive templates.\n"
    )
    payload = {
        "title": data.get("title", ""),
        "about": _extract_text(data.get("about_text")),
        "judge_feedback": judge,
        "targets": targets,
    }
    req_body = {
        "model": writer_model,
        "input": [
            {"role": "system", "content": [{"type": "input_text", "text": prompt}]},
            {"role": "user", "content": [{"type": "input_text", "text": json.dumps(payload, ensure_ascii=True)}]},
        ],
        "max_output_tokens": 2000,
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(req_body).encode("utf-8"),
        method="POST",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=240) as r:
            resp = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Writer API error HTTP {exc.code}: {detail}") from exc
    text = _responses_text(resp)
    return _extract_json(text)


def _apply_rewrites(data: Dict[str, Any], rewrites: Dict[str, Any]) -> Dict[str, Any]:
    out = copy.deepcopy(data)
    enc_map = {str(e.get("id", "")): e for e in out.get("encounters", []) or []}
    for item in rewrites.get("encounter_rewrites", []) or []:
        eid = str(item.get("id", ""))
        txt = str(item.get("text", "")).strip()
        if eid in enc_map and txt:
            ts = _ensure_text_script(enc_map[eid].get("text_script"))
            ts["value"] = txt
            enc_map[eid]["text_script"] = ts
    for item in rewrites.get("reaction_rewrites", []) or []:
        sid = str(item.get("id", ""))
        txt = str(item.get("text", "")).strip()
        if not txt or "::" not in sid:
            continue
        eid, oid, rid = sid.split("::", 2)
        enc = enc_map.get(eid)
        if not enc:
            continue
        for opt in enc.get("options", []) or []:
            if str(opt.get("id", "")) != oid:
                continue
            for rxn in opt.get("reactions", []) or []:
                if str(rxn.get("id", "")) == rid:
                    ts = _ensure_text_script(rxn.get("text_script"))
                    ts["value"] = txt
                    rxn["text_script"] = ts
    return out


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Iterate storyworld text quality until threshold")
    p.add_argument("--in-json", required=True)
    p.add_argument("--out-json", required=True)
    p.add_argument("--work-dir", required=True)
    p.add_argument("--threshold", type=float, default=0.8)
    p.add_argument("--max-iters", type=int, default=4)
    p.add_argument("--judge-model", default="gpt-5-mini")
    p.add_argument("--writer-model", default="gpt-5-mini")
    p.add_argument("--api-key-file", default="")
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    in_path = Path(args.in_json).resolve()
    out_path = Path(args.out_json).resolve()
    work_dir = Path(args.work_dir).resolve()
    work_dir.mkdir(parents=True, exist_ok=True)
    api_key = _read_key(args.api_key_file)

    current = json.loads(in_path.read_text(encoding="utf-8"))
    history: List[Dict[str, Any]] = []
    reached = False

    for step in range(1, int(args.max_iters) + 1):
        current_path = work_dir / f"iter_{step:02d}_input.json"
        current_path.write_text(json.dumps(current, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
        judge_report = run_judge(
            storyworld_path=current_path,
            judge_model=args.judge_model,
            api_key=api_key,
            dry_run=bool(args.dry_run),
            max_encounters=60,
            max_reactions=240,
        )
        score = float(judge_report.get("judge", {}).get("overall_score", 0.0) or 0.0)
        judge_path = work_dir / f"iter_{step:02d}_judge.json"
        judge_path.write_text(json.dumps(judge_report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
        history.append({"iter": step, "score": score, "judge_report": str(judge_path)})
        if score >= float(args.threshold):
            reached = True
            break
        if args.dry_run or not api_key:
            # Deterministic fallback in dry-run mode: no model rewrite call.
            break

        targets = _collect_rewrite_targets(current, judge_report.get("judge", {}), max_items=80)
        rewrites = _request_rewrites(
            data=current,
            judge=judge_report.get("judge", {}),
            targets=targets,
            writer_model=args.writer_model,
            api_key=api_key,
        )
        rewrite_path = work_dir / f"iter_{step:02d}_rewrites.json"
        rewrite_path.write_text(json.dumps(rewrites, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
        current = _apply_rewrites(current, rewrites)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(current, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    summary = {
        "in_json": str(in_path),
        "out_json": str(out_path),
        "threshold": float(args.threshold),
        "max_iters": int(args.max_iters),
        "judge_model": args.judge_model,
        "writer_model": args.writer_model,
        "dry_run": bool(args.dry_run),
        "reached_threshold": reached,
        "history": history,
    }
    summary_path = work_dir / "loop_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    print(str(summary_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
