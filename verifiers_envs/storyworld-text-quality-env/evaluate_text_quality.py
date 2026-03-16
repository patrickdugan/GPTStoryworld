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

def _walk_json(obj: Any) -> List[Dict[str, Any]]:
    """Return a flat list of dict nodes for simple introspection/tracing."""
    out: List[Dict[str, Any]] = []
    stack = [obj]
    while stack:
        cur = stack.pop()
        if isinstance(cur, dict):
            out.append(cur)
            for v in cur.values():
                stack.append(v)
        elif isinstance(cur, list):
            for v in cur:
                stack.append(v)
    return out


def _collect_script_refs(obj: Any, character_ids: set[str]) -> Dict[str, Any]:
    """Collect lightweight script structure + variable references from a script/effect blob."""
    ops: List[str] = []
    ptrs: List[str] = []
    vars_: List[str] = []
    involved_chars: set[str] = set()
    for node in _walk_json(obj):
        op = node.get("operator_type")
        if isinstance(op, str) and op:
            ops.append(op)
        pt = node.get("pointer_type")
        if isinstance(pt, str) and pt:
            ptrs.append(pt)
        ch = node.get("character")
        kr = node.get("keyring")
        if isinstance(ch, str) and isinstance(kr, list) and kr:
            path = ".".join(str(x) for x in kr if x is not None)
            vars_.append(f"{ch}.{path}")
            if ch in character_ids:
                involved_chars.add(ch)
            for x in kr:
                if isinstance(x, str) and x in character_ids:
                    involved_chars.add(x)

    def dedup(xs: List[str]) -> List[str]:
        seen: set[str] = set()
        out2: List[str] = []
        for x in xs:
            if x not in seen:
                seen.add(x)
                out2.append(x)
        return out2

    return {
        "operators": dedup(ops)[:60],
        "pointer_types": dedup(ptrs)[:60],
        "variables": dedup(vars_)[:120],
        "involved_characters": sorted(involved_chars),
    }


def _truncate(s: str, max_chars: int) -> str:
    if len(s) <= max_chars:
        return s
    return s[: max(0, max_chars - 30)] + "\n...[truncated]..."


def _resolve_swmd_path(storyworld_path: Path, explicit_swmd: str = "") -> Path | None:
    if explicit_swmd:
        p = Path(explicit_swmd).expanduser().resolve()
        return p if p.exists() else None
    stem = storyworld_path.stem
    parent = storyworld_path.parent
    candidates = [
        parent / f"{stem}.swmd.min.md",
        parent / f"{stem}.swmd.md",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def _split_swmd_frontmatter(swmd_text: str) -> Tuple[Dict[str, Any], str]:
    lines = swmd_text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, swmd_text
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}, swmd_text
    fm_lines = lines[1:end]
    body = "\n".join(lines[end + 1 :])
    meta: Dict[str, Any] = {}
    for raw in fm_lines:
        m = re.match(r"^([A-Za-z0-9_]+):\s*(.+?)\s*$", raw.strip())
        if m:
            meta[m.group(1)] = m.group(2).strip().strip('"')
    endings: List[Dict[str, Any]] = []
    pending: Dict[str, Any] = {}
    for raw in fm_lines:
        s = raw.rstrip()
        m_id = re.match(r'^\s*-\s+id:\s*"?(.+?)"?\s*$', s)
        if m_id:
            if pending:
                endings.append(pending)
            pending = {"id": m_id.group(1)}
            continue
        m_attr = re.match(r'^\s+([A-Za-z0-9_]+):\s*"?(.+?)"?\s*$', s)
        if m_attr and pending:
            key = m_attr.group(1)
            raw_val = m_attr.group(2).strip()
            if key == "expected_critic_score":
                try:
                    pending[key] = float(raw_val)
                except Exception:
                    pending[key] = raw_val
            else:
                pending[key] = raw_val
    if pending:
        endings.append(pending)
    if endings:
        meta["endings"] = endings
    return meta, body


def _extract_swmd_samples(swmd_text: str, max_encounters: int = 50, max_reactions: int = 200) -> Dict[str, Any]:
    encounters: List[Dict[str, Any]] = []
    reactions: List[Dict[str, Any]] = []
    current_enc = ""
    enc_seen = 0
    rxn_seen = 0

    for raw in swmd_text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("ENC "):
            if enc_seen >= max_encounters:
                continue
            # Example: ENC page_0000 turn=0..0
            parts = line.split()
            enc_id = parts[1] if len(parts) > 1 else f"enc_{enc_seen:04d}"
            current_enc = enc_id
            encounters.append(
                {
                    "id": enc_id,
                    "title": "",
                    "text": line,
                    "connected_spools": [],
                    "spool_context": [],
                    "acceptability_script": True,
                    "desirability_script": 0,
                    "script_refs": {"operators": [], "pointer_types": [], "variables": [], "involved_characters": []},
                    "involved_characters": [],
                }
            )
            enc_seen += 1
            continue

        if line.startswith("ORX "):
            if rxn_seen >= max_reactions:
                continue
            # Example:
            # ORX opt_page_0000_0/opt_page_0000_0_r1 -> page_0001 | O:... | E:... | D:...
            left, *pipes = [p.strip() for p in line.split("|")]
            m = re.match(r"^ORX\s+(.+?)\s*->\s*(\S+)", left)
            combo = m.group(1) if m else f"orx_{rxn_seen:05d}"
            consequence = m.group(2) if m else ""
            if "/" in combo:
                option_id, reaction_id = combo.split("/", 1)
            else:
                option_id, reaction_id = combo, combo

            option_text = ""
            desirability = 0
            effect_count = 0
            script_ops: List[str] = []
            for p in pipes:
                if p.startswith("O:"):
                    option_text = p[2:].strip()
                elif p.startswith("D:"):
                    desirability = p[2:].strip()
                elif p.startswith("E:"):
                    e = p[2:].strip()
                    effect_count = e.count("SET ")
                    script_ops.extend(re.findall(r"\b(NUDGE|ADD|SUB|MUL|ARITHMETIC MEAN|IF THEN|ARITHMETIC COMPARATOR)\b", e))
            if isinstance(desirability, str):
                script_ops.extend(re.findall(r"\b(NUDGE|ADD|SUB|MUL|ARITHMETIC MEAN|IF THEN|ARITHMETIC COMPARATOR)\b", desirability))
            script_ops = list(dict.fromkeys(script_ops))

            enc_id = current_enc or "enc_unknown"
            reactions.append(
                {
                    "id": f"{enc_id}::{option_id}::{reaction_id}",
                    "encounter_id": enc_id,
                    "option_id": option_id,
                    "reaction_id": reaction_id,
                    "option_text": option_text,
                    "text": line,
                    "option_visibility_script": True,
                    "option_performability_script": True,
                    "desirability_script": desirability,
                    "after_effects_count": effect_count,
                    "script_refs": {
                        "operators": script_ops,
                        "pointer_types": [],
                        "variables": [],
                        "involved_characters": [],
                    },
                    "involved_characters": [],
                    "consequence_id": consequence,
                }
            )
            rxn_seen += 1

    return {
        "characters": [],
        "encounters": encounters[:max_encounters],
        "reactions": reactions[:max_reactions],
    }


def _build_holistic_corpus(data: Dict[str, Any], max_chars: int = 30000) -> str:
    parts: List[str] = []
    title = str(data.get("title", "") or "")
    about = _extract_text(data.get("about_text"))
    if title:
        parts.append(f"# Title\n{title}\n")
    if about:
        parts.append(f"# About\n{about}\n")

    for enc in data.get("encounters", []) or []:
        eid = str(enc.get("id", "") or "")
        et = _extract_text(enc.get("text_script"))
        if eid and et:
            parts.append(f"## Encounter {eid}\n{et}\n")
        for opt in enc.get("options", []) or []:
            oid = str(opt.get("id", "") or "")
            ot = _extract_text(opt.get("text_script"))
            if oid and ot:
                parts.append(f"### Option {eid}::{oid}\n{ot}\n")
            for rxn in opt.get("reactions", []) or []:
                rid = str(rxn.get("id", "") or "")
                rt = _extract_text(rxn.get("text_script"))
                if rid and rt:
                    parts.append(f"#### Reaction {eid}::{oid}::{rid}\n{rt}\n")

        joined = "\n".join(parts)
        if len(joined) >= max_chars:
            return _truncate(joined, max_chars)
    return _truncate("\n".join(parts), max_chars)


def extract_samples(data: Dict[str, Any], max_encounters: int = 50, max_reactions: int = 200) -> Dict[str, Any]:
    character_ids = {str(c.get("id", "")) for c in data.get("characters", []) or [] if str(c.get("id", ""))}
    char_name = {str(c.get("id", "")): str(c.get("name", "")) for c in data.get("characters", []) or [] if str(c.get("id", ""))}
    spool_map: Dict[str, Dict[str, Any]] = {
        str(s.get("id", "")): s for s in (data.get("spools", []) or []) if isinstance(s, dict) and str(s.get("id", ""))
    }
    encounters = []
    reactions = []
    for enc in data.get("encounters", []) or []:
        eid = str(enc.get("id", ""))
        etxt = _extract_text(enc.get("text_script"))
        if eid and etxt:
            enc_refs = _collect_script_refs(
                {
                    "acceptability_script": enc.get("acceptability_script", True),
                    "desirability_script": enc.get("desirability_script", 0),
                },
                character_ids=character_ids,
            )
            connected_spools = enc.get("connected_spools") or enc.get("connectedSpools") or enc.get("spools") or []
            if not isinstance(connected_spools, list):
                connected_spools = []
            spool_ctx = []
            for sid in connected_spools:
                s = spool_map.get(str(sid))
                if not s:
                    continue
                spool_ctx.append(
                    {
                        "id": str(s.get("id", "")),
                        "name": str(s.get("spool_name", "")),
                        "starts_active": bool(s.get("starts_active", False)),
                        "encounters_count": len(s.get("encounters", []) or []),
                    }
                )
            involved = enc_refs.get("involved_characters", [])
            encounters.append(
                {
                    "id": eid,
                    "title": str(enc.get("title", "")),
                    "text": etxt,
                    "connected_spools": [str(s) for s in connected_spools if str(s)],
                    "spool_context": spool_ctx,
                    "acceptability_script": enc.get("acceptability_script", True),
                    "desirability_script": enc.get("desirability_script", 0),
                    "script_refs": enc_refs,
                    "involved_characters": [{"id": cid, "name": char_name.get(cid, "")} for cid in involved],
                }
            )
        for opt in enc.get("options", []) or []:
            oid = str(opt.get("id", ""))
            otxt = _extract_text(opt.get("text_script"))
            for rxn in opt.get("reactions", []) or []:
                rid = str(rxn.get("id", ""))
                rtxt = _extract_text(rxn.get("text_script"))
                if eid and oid and rid and rtxt:
                    rxn_blob = {
                        "option_visibility_script": opt.get("visibility_script", True),
                        "option_performability_script": opt.get("performability_script", True),
                        "reaction_desirability_script": rxn.get("desirability_script", 0),
                        "after_effects": rxn.get("after_effects", []) or [],
                    }
                    rxn_refs = _collect_script_refs(rxn_blob, character_ids=character_ids)
                    involved = rxn_refs.get("involved_characters", [])
                    reactions.append(
                        {
                            "id": f"{eid}::{oid}::{rid}",
                            "encounter_id": eid,
                            "option_id": oid,
                            "reaction_id": rid,
                            "option_text": otxt,
                            "text": rtxt,
                            "option_visibility_script": opt.get("visibility_script", True),
                            "option_performability_script": opt.get("performability_script", True),
                            "desirability_script": rxn.get("desirability_script", 0),
                            "after_effects_count": len(rxn.get("after_effects", []) or []),
                            "script_refs": rxn_refs,
                            "involved_characters": [{"id": cid, "name": char_name.get(cid, "")} for cid in involved],
                        }
                    )
    return {
        "characters": [
            {
                "id": str(c.get("id", "")),
                "name": str(c.get("name", "")),
                "pronoun": str(c.get("pronoun", "")),
            }
            for c in data.get("characters", []) or []
        ],
        "encounters": encounters[:max_encounters],
        "reactions": reactions[:max_reactions],
    }


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
    text_richness = (narrative + reaction_voice) / 2.0
    mechanics_relevance = 0.5
    characterization_relevance = 0.5
    holistic_theme = thematic
    overall = (thematic + non_rep + narrative + reaction_voice + mechanics_relevance + characterization_relevance + holistic_theme) / 7.0
    return {
        "overall_score": round(overall, 4),
        "dimension_scores": {
            "text_richness": round(text_richness, 4),
            "thematic_relevance": round(thematic, 4),
            "stylistic_distinctiveness": round(non_rep, 4),
            "encounter_narrative_quality": round(narrative, 4),
            "reaction_voice_quality": round(reaction_voice, 4),
            "specificity_and_imagery": round(narrative, 4),
            "coherence_and_consistency": round(thematic, 4),
            "non_repetition": round(non_rep, 4),
            "choice_consequence_clarity": round(reaction_voice, 4),
            "mechanics_relevance": round(mechanics_relevance, 4),
            "characterization_relevance": round(characterization_relevance, 4),
            "holistic_theme_coherence": round(holistic_theme, 4),
        },
        "summary": "Dry-run heuristic report (no model call).",
        "top_issues": [],
        "revision_instructions": [],
        "failing_examples": [],
    }


def _heuristic_report_from_samples(samples: Dict[str, Any], title: str = "", about: str = "") -> Dict[str, Any]:
    return _heuristic_report({"title": title, "about_text": {"pointer_type": "String Constant", "value": about}}, samples)


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
    source_format: str = "auto",
    swmd_path: str = "",
) -> Dict[str, Any]:
    source = (source_format or "auto").strip().lower()
    if source not in {"auto", "json", "swmd"}:
        raise ValueError(f"Unsupported source format: {source}")

    data: Dict[str, Any] = {}
    title = ""
    about = ""
    holistic_corpus = ""
    resolved_source = "json"
    resolved_swmd = _resolve_swmd_path(storyworld_path, swmd_path)

    if source in {"auto", "swmd"} and resolved_swmd is not None:
        swmd_text = resolved_swmd.read_text(encoding="utf-8", errors="replace")
        swmd_frontmatter, swmd_body = _split_swmd_frontmatter(swmd_text)
        samples = _extract_swmd_samples(swmd_body, max_encounters=max_encounters, max_reactions=max_reactions)
        holistic_corpus = _truncate(swmd_text, 30000)
        # Lightweight title extraction from SWMD header line: title: ...
        tm = re.search(r"(?m)^title:\s*(.+?)\s*$", swmd_text)
        if tm:
            title = tm.group(1).strip()
        if not title and isinstance(swmd_frontmatter.get("title"), str):
            title = str(swmd_frontmatter.get("title", ""))
        resolved_source = "swmd"
    else:
        swmd_frontmatter = {}
        data = json.loads(storyworld_path.read_text(encoding="utf-8"))
        samples = extract_samples(data, max_encounters=max_encounters, max_reactions=max_reactions)
        title = str(data.get("title", "") or "")
        about = _extract_text(data.get("about_text"))
        holistic_corpus = _build_holistic_corpus(data, max_chars=30000)
        resolved_source = "json"

    if dry_run or not api_key:
        if resolved_source == "swmd":
            parsed = _heuristic_report_from_samples(samples, title=title, about=about)
        else:
            parsed = _heuristic_report(data, samples)
        return {
            "mode": "dry-run",
            "model": judge_model,
            "storyworld": str(storyworld_path),
            "source_format": resolved_source,
            "swmd_path": str(resolved_swmd) if resolved_swmd else "",
            "samples": {"encounters": len(samples["encounters"]), "reactions": len(samples["reactions"])},
            "judge": parsed,
            "raw_response_text": "",
        }

    base_dir = Path(__file__).resolve().parent
    system_prompt = (base_dir / "judge_system_prompt.md").read_text(encoding="utf-8")
    system_card = (base_dir / "storyworld_system_card.md").read_text(encoding="utf-8")
    user_payload = {
        "source_format": resolved_source,
        "title": title,
        "about": about,
        "swmd_frontmatter": swmd_frontmatter if resolved_source == "swmd" else {},
        "samples": samples,
        "holistic_corpus": holistic_corpus,
    }
    req_body = {
        "model": judge_model,
        "input": [
            {"role": "system", "content": [{"type": "input_text", "text": system_prompt + "\n\n" + system_card}]},
            {"role": "user", "content": [{"type": "input_text", "text": json.dumps(user_payload, ensure_ascii=True)}]},
        ],
        "max_output_tokens": 1900,
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
        "source_format": resolved_source,
        "swmd_path": str(resolved_swmd) if resolved_swmd else "",
        "samples": {"encounters": len(samples["encounters"]), "reactions": len(samples["reactions"])},
        "usage": resp.get("usage", {}),
        "judge": parsed,
        "raw_response_text": text,
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Storyworld text quality judge")
    p.add_argument("--storyworld", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--judge-model", default="gpt-5-mini")
    p.add_argument("--api-key-file", default="")
    p.add_argument("--source-format", choices=["auto", "json", "swmd"], default="auto")
    p.add_argument("--swmd-path", default="")
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
        source_format=str(args.source_format),
        swmd_path=str(args.swmd_path),
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
