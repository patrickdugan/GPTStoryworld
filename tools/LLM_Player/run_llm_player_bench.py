#!/usr/bin/env python3
"""Benchmark LLM player behavior on storyworld encounter prompts."""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class EncounterPrompt:
    encounter_id: str
    turn_span: str
    is_terminal: bool
    prompt_text: str


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _script_text(value: Any) -> str:
    if isinstance(value, dict):
        if value.get("pointer_type") == "String Constant":
            return str(value.get("value", "") or "")
        if isinstance(value.get("value"), str):
            return value["value"]
    if isinstance(value, str):
        return value
    return ""


def _is_terminal(encounter: Dict[str, Any]) -> bool:
    return not bool(encounter.get("options") or [])


def _pick_option_id_from_text(text: str, option_ids: List[str]) -> str:
    s = str(text or "")
    if not s or not option_ids:
        return ""
    ordered = sorted({str(x) for x in option_ids if str(x)}, key=len, reverse=True)
    for oid in ordered:
        pat = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(oid)}(?![A-Za-z0-9_])", flags=re.IGNORECASE)
        if pat.search(s):
            return oid
    m = re.search(r"PICK\s+(\d+)", s, flags=re.IGNORECASE)
    if m:
        ix = int(m.group(1))
        if 1 <= ix <= len(ordered):
            return ordered[ix - 1]
    return ""


def load_storyworld(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_prompts(
    data: Dict[str, Any],
    max_encounters: int = 0,
    include_terminals: bool = True,
) -> List[EncounterPrompt]:
    title = str(data.get("storyworld_title", "") or "")
    about = _script_text(data.get("about_text"))
    encounters = sorted(
        data.get("encounters", []) or [],
        key=lambda e: (int(e.get("creation_index", 10**9) or 10**9), str(e.get("id", ""))),
    )
    out: List[EncounterPrompt] = []
    for enc in encounters:
        is_terminal = _is_terminal(enc)
        if (not include_terminals) and is_terminal:
            continue
        enc_id = str(enc.get("id", ""))
        text = _script_text(enc.get("text_script")).strip()
        earliest = enc.get("earliest_turn", "?")
        latest = enc.get("latest_turn", "?")
        turn_span = f"{earliest}..{latest}"
        prompt_text = (
            f"Storyworld: {title}\n"
            f"About: {about}\n"
            f"Encounter ID: {enc_id}\n"
            f"Turn Span: {turn_span}\n"
            f"Terminal: {str(is_terminal).lower()}\n\n"
            "Encounter Scene:\n"
            f"{text}\n\n"
            "As the player, produce:\n"
            "1) intended action (one concise line)\n"
            "2) in-world dialogue (2-4 lines)\n"
            "3) moral tradeoff rationale (2-4 lines)\n"
            "Keep tone grounded in the scene."
        )
        out.append(
            EncounterPrompt(
                encounter_id=enc_id,
                turn_span=turn_span,
                is_terminal=is_terminal,
                prompt_text=prompt_text,
            )
        )
        if max_encounters > 0 and len(out) >= max_encounters:
            break
    return out


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, obj: Dict[str, Any]) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(obj, ensure_ascii=True, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_jsonl(path: Path, rows: List[Dict[str, Any]]) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=True) + "\n")


class HFRunner:
    def __init__(
        self,
        model_path: str,
        adapter_path: str = "",
        device_map: str = "auto",
        dtype: str = "auto",
    ) -> None:
        self.model_path = model_path
        self.adapter_path = adapter_path
        self.device_map = device_map
        self.dtype = dtype
        self.model = None
        self.tokenizer = None
        self._load()

    def _resolve_dtype(self, torch_mod: Any) -> Any:
        if self.dtype == "float16":
            return torch_mod.float16
        if self.dtype == "bfloat16":
            return torch_mod.bfloat16
        if self.dtype == "float32":
            return torch_mod.float32
        return "auto"

    def _load(self) -> None:
        import torch  # type: ignore
        from transformers import AutoModelForCausalLM, AutoTokenizer  # type: ignore

        tokenizer = AutoTokenizer.from_pretrained(self.model_path, use_fast=True)
        dtype = self._resolve_dtype(torch)
        model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            torch_dtype=dtype,
            device_map=self.device_map,
        )
        if self.adapter_path:
            from peft import PeftModel  # type: ignore

            model = PeftModel.from_pretrained(model, self.adapter_path)
        model.eval()
        self.model = model
        self.tokenizer = tokenizer

    def generate(
        self,
        prompt: str,
        max_new_tokens: int,
        temperature: float,
        top_p: float,
        do_sample: bool,
    ) -> Dict[str, Any]:
        assert self.model is not None
        assert self.tokenizer is not None
        import torch  # type: ignore

        tok = self.tokenizer
        model = self.model
        messages = [
            {"role": "system", "content": "You are an in-world player making coherent, morally aware decisions."},
            {"role": "user", "content": prompt},
        ]
        if hasattr(tok, "apply_chat_template"):
            rendered = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        else:
            rendered = f"System: {messages[0]['content']}\nUser: {messages[1]['content']}\nAssistant:"

        encoded = tok(rendered, return_tensors="pt")
        device = next(model.parameters()).device
        encoded = {k: v.to(device) for k, v in encoded.items()}

        t0 = time.time()
        with torch.no_grad():
            out_ids = model.generate(
                **encoded,
                max_new_tokens=max_new_tokens,
                do_sample=do_sample,
                temperature=temperature if do_sample else None,
                top_p=top_p if do_sample else None,
                pad_token_id=tok.eos_token_id,
            )
        latency = time.time() - t0
        new_ids = out_ids[0][encoded["input_ids"].shape[1] :]
        text = tok.decode(new_ids, skip_special_tokens=True).strip()
        return {
            "text": text,
            "prompt_tokens": int(encoded["input_ids"].shape[1]),
            "completion_tokens": int(new_ids.shape[0]),
            "latency_sec": round(latency, 4),
        }

    def score_option(self, prompt: str, option_text: str) -> Dict[str, Any]:
        assert self.model is not None
        assert self.tokenizer is not None
        import torch  # type: ignore

        tok = self.tokenizer
        model = self.model
        completion = f"\nChosen option: {option_text}"
        full = prompt + completion

        p_ids = tok(prompt, return_tensors="pt")["input_ids"]
        f = tok(full, return_tensors="pt")
        input_ids = f["input_ids"]
        attn = f["attention_mask"]
        prompt_len = int(p_ids.shape[1])
        if int(input_ids.shape[1]) <= prompt_len:
            return {"score": -1e9, "prompt_tokens": prompt_len, "completion_tokens": 0, "latency_sec": 0.0}

        device = next(model.parameters()).device
        input_ids = input_ids.to(device)
        attn = attn.to(device)
        t0 = time.time()
        with torch.no_grad():
            logits = model(input_ids=input_ids, attention_mask=attn).logits
            logprobs = torch.log_softmax(logits[:, :-1, :], dim=-1)
            target = input_ids[:, 1:]
            start = max(0, prompt_len - 1)
            comp_lp = logprobs[:, start:, :]
            comp_t = target[:, start:]
            gathered = comp_lp.gather(-1, comp_t.unsqueeze(-1)).squeeze(-1)
            score = float(gathered.mean().item())
        latency = time.time() - t0
        completion_tokens = max(0, int(input_ids.shape[1]) - int(prompt_len))
        return {
            "score": score,
            "prompt_tokens": prompt_len,
            "completion_tokens": completion_tokens,
            "latency_sec": round(latency, 4),
        }

    def pick_option(self, prompt: str, option_ids: List[str], max_new_tokens: int = 24) -> Dict[str, Any]:
        assert self.model is not None
        assert self.tokenizer is not None
        import torch  # type: ignore

        tok = self.tokenizer
        model = self.model
        valid_ids = [str(x) for x in option_ids if str(x)]
        sys_msg = (
            "Choose exactly one option id from the allowed list. "
            "Return only the id token and nothing else."
        )
        user_msg = (
            f"{prompt}\n\n"
            f"Allowed option ids: {', '.join(valid_ids)}\n"
            "Output format: <option_id>"
        )
        messages = [
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": user_msg},
        ]
        if hasattr(tok, "apply_chat_template"):
            rendered = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        else:
            rendered = f"System: {sys_msg}\nUser: {user_msg}\nAssistant:"

        encoded = tok(rendered, return_tensors="pt")
        device = next(model.parameters()).device
        encoded = {k: v.to(device) for k, v in encoded.items()}

        t0 = time.time()
        with torch.no_grad():
            out_ids = model.generate(
                **encoded,
                max_new_tokens=max(8, int(max_new_tokens)),
                do_sample=False,
                pad_token_id=tok.eos_token_id,
            )
        latency = time.time() - t0
        new_ids = out_ids[0][encoded["input_ids"].shape[1] :]
        raw_text = tok.decode(new_ids, skip_special_tokens=True).strip()
        chosen = _pick_option_id_from_text(raw_text, valid_ids)
        fallback = False
        if not chosen and valid_ids:
            chosen = valid_ids[0]
            fallback = True
        return {
            "option_id": chosen,
            "raw_text": raw_text,
            "fallback": bool(fallback),
            "prompt_tokens": int(encoded["input_ids"].shape[1]),
            "completion_tokens": int(new_ids.shape[0]),
            "latency_sec": round(latency, 4),
        }


def fake_generate(prompt: str, ix: int) -> Dict[str, Any]:
    text = (
        "Intended action: broker a risky passage with minimum collateral.\n"
        "Dialogue: \"Keep it quiet and keep it moving. Dawn is not on our side.\"\n"
        "Rationale: prioritize survival while accepting personal cost to preserve allied trust.\n"
        f"Dry-run sample index: {ix + 1}."
    )
    return {
        "text": text,
        "prompt_tokens": max(1, len(prompt) // 4),
        "completion_tokens": max(1, len(text) // 4),
        "latency_sec": 0.0,
    }


def _encounters_sorted(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    return sorted(
        data.get("encounters", []) or [],
        key=lambda e: (int(e.get("creation_index", 10**9) or 10**9), str(e.get("id", ""))),
    )


def _option_consequences(opt: Dict[str, Any]) -> List[str]:
    out: List[str] = []
    for r in opt.get("reactions", []) or []:
        cid = str(r.get("consequence_id", "") or "").strip()
        if cid and cid.lower() != "wild":
            out.append(cid)
    return sorted(set(out))


def _reaction_for_consequence(opt: Dict[str, Any], consequence_id: str) -> Optional[Dict[str, Any]]:
    for r in opt.get("reactions", []) or []:
        if str(r.get("consequence_id", "") or "").strip() == consequence_id:
            return r
    rs = opt.get("reactions", []) or []
    return rs[0] if rs else None


def _effect_items(reaction: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not reaction:
        return []
    if isinstance(reaction.get("after_effects"), list):
        return list(reaction.get("after_effects") or [])
    if isinstance(reaction.get("effects"), list):
        return list(reaction.get("effects") or [])
    return []


def _effect_delta_tokens(effects: List[Dict[str, Any]], max_items: int) -> List[str]:
    out: List[str] = []
    for ef in effects:
        set_ptr = ef.get("Set", {}) if isinstance(ef, dict) else {}
        keyring = set_ptr.get("keyring", []) if isinstance(set_ptr, dict) else []
        if not keyring:
            continue
        key = str(keyring[0])
        delta = None
        to = ef.get("to", {}) if isinstance(ef, dict) else {}
        if isinstance(to, dict):
            ops = to.get("operands", []) or []
            if len(ops) >= 2 and isinstance(ops[1], dict):
                val = ops[1].get("value")
                if isinstance(val, (int, float)):
                    delta = float(val)
        if delta is None:
            out.append(f"{key}:set")
        else:
            sign = "+" if delta >= 0 else ""
            out.append(f"{key}:{sign}{delta:.3g}")
        if len(out) >= max(1, int(max_items)):
            break
    return out


def _compact_text(text: str, max_len: int) -> str:
    s = " ".join(str(text or "").split())
    if len(s) <= max(1, int(max_len)):
        return s
    return s[: max(1, int(max_len))].rstrip() + "..."


def _build_turn_response(
    encounter_id: str,
    chosen_id: str,
    chosen_text: str,
    reaction_text: str,
    next_id: str,
    deltas: List[str],
) -> str:
    parts = [
        f"encounter={encounter_id}",
        f"pick={chosen_id}",
        f"option={_compact_text(chosen_text, 96)}",
    ]
    if reaction_text:
        parts.append(f"reaction={_compact_text(reaction_text, 96)}")
    if next_id:
        parts.append(f"next={next_id}")
    if deltas:
        parts.append("deltas=" + ",".join(deltas))
    return " | ".join(parts)


def _build_turn_prompt(
    title: str,
    about: str,
    enc_id: str,
    enc_text: str,
    options: List[Tuple[str, str]],
    diary: List[str],
    context_window: int,
    context_char_cap: int,
) -> str:
    diary_ctx = "\n".join(diary[-max(0, int(context_window)) :]) if diary else "(none)"
    if int(context_char_cap) > 0 and len(diary_ctx) > int(context_char_cap):
        diary_ctx = "... " + diary_ctx[-int(context_char_cap) :]
    options_txt = "\n".join([f"- {oid}: {otxt}" for oid, otxt in options])
    return (
        f"Storyworld: {title}\n"
        f"About: {about}\n"
        "Compact Prior Diary (diffs):\n"
        f"{diary_ctx}\n\n"
        f"Encounter: {enc_id}\n"
        f"Scene:\n{enc_text}\n\n"
        "Choose one option from this fixed list:\n"
        f"{options_txt}\n"
    )


def run_playthrough_condition(
    label: str,
    data: Dict[str, Any],
    out_dir: Path,
    runner: Optional[HFRunner],
    playthroughs: int,
    max_steps: int,
    context_window: int,
    context_char_cap: int,
    max_diary_effects: int,
    include_option_text_in_diary: bool,
    include_scene_text_in_diary: bool,
    selection_mode: str,
    pick_max_new_tokens: int,
    dry_run: bool,
) -> Dict[str, Any]:
    ensure_dir(out_dir)
    encs = _encounters_sorted(data)
    enc_by = {str(e.get("id", "")): e for e in encs}
    if not encs:
        write_jsonl(out_dir / "generations.jsonl", [])
        write_json(out_dir / "summary.json", {"model_label": label, "num_prompts": 0, "status": "no_encounters"})
        return {"model_label": label, "num_prompts": 0, "status": "no_encounters"}

    title = str(data.get("storyworld_title", "") or "")
    about = _script_text(data.get("about_text"))
    start_id = str(encs[0].get("id", "") or "")
    rows: List[Dict[str, Any]] = []
    start = time.time()
    global_diary: List[str] = []
    completed = 0

    for play_ix in range(1, max(1, int(playthroughs)) + 1):
        cur = start_id
        local_diary: List[str] = []
        reached_terminal = False
        for step_ix in range(1, max(1, int(max_steps)) + 1):
            enc = enc_by.get(cur)
            if not enc:
                break
            if _is_terminal(enc):
                reached_terminal = True
                break
            raw_opts = sorted(enc.get("options", []) or [], key=lambda o: str(o.get("id", "")))
            options: List[Tuple[str, str, Dict[str, Any]]] = []
            for o in raw_opts:
                oid = str(o.get("id", "") or "").strip()
                otext = _script_text(o.get("text_script")).strip()
                if oid and otext:
                    options.append((oid, otext, o))
            if not options:
                break

            diary = global_diary + local_diary
            prompt = _build_turn_prompt(
                title=title,
                about=about,
                enc_id=cur,
                enc_text=_script_text(enc.get("text_script")).strip(),
                options=[(oid, otext) for oid, otext, _ in options],
                diary=diary,
                context_window=context_window,
                context_char_cap=context_char_cap,
            )

            pick_raw = ""
            pick_fallback = False
            if dry_run:
                chosen_idx = 0
                chosen = options[chosen_idx]
                score_pack = {
                    "score": 0.0,
                    "prompt_tokens": max(1, len(prompt) // 4),
                    "completion_tokens": max(1, len(chosen[1]) // 4),
                    "latency_sec": 0.0,
                }
            else:
                assert runner is not None
                if str(selection_mode) == "score_all":
                    ranked: List[Tuple[float, Dict[str, Any], Tuple[str, str, Dict[str, Any]]]] = []
                    for opt in options:
                        sp = runner.score_option(prompt, opt[1])
                        ranked.append((float(sp["score"]), sp, opt))
                    ranked.sort(key=lambda x: x[0], reverse=True)
                    _, score_pack, chosen = ranked[0]
                else:
                    pick = runner.pick_option(
                        prompt=prompt,
                        option_ids=[oid for oid, _, _ in options],
                        max_new_tokens=max(8, int(pick_max_new_tokens)),
                    )
                    pick_raw = str(pick.get("raw_text", "") or "")
                    pick_fallback = bool(pick.get("fallback", False))
                    chosen_id = str(pick.get("option_id", "") or "")
                    by_id = {oid: (oid, otext, oobj) for oid, otext, oobj in options}
                    chosen = by_id.get(chosen_id, options[0])
                    score_pack = {
                        "score": 0.0,
                        "prompt_tokens": int(pick.get("prompt_tokens", 0) or 0),
                        "completion_tokens": int(pick.get("completion_tokens", 0) or 0),
                        "latency_sec": float(pick.get("latency_sec", 0.0) or 0.0),
                    }

            chosen_id, chosen_text, chosen_opt = chosen
            cons = _option_consequences(chosen_opt)
            next_id = cons[0] if cons else ""
            reaction = _reaction_for_consequence(chosen_opt, next_id if next_id else "")
            reaction_id = str((reaction or {}).get("id", "") or "")
            reaction_text = _script_text((reaction or {}).get("text_script"))
            deltas = _effect_delta_tokens(_effect_items(reaction), max_diary_effects)
            diary_token = f"p{play_ix:02d}t{step_ix:02d} e={cur} o={chosen_id}"
            if reaction_id:
                diary_token += f" r={reaction_id}"
            if next_id:
                diary_token += f" -> {next_id}"
            if deltas:
                diary_token += " d[" + ",".join(deltas) + "]"
            if include_option_text_in_diary:
                diary_token += f" ot={_compact_text(chosen_text, 80)}"
            if include_scene_text_in_diary:
                diary_token += f" sc={_compact_text(_script_text(enc.get('text_script')), 64)}"
            if reaction_text:
                diary_token += f" rx={_compact_text(reaction_text, 64)}"
            local_diary.append(diary_token)

            response_text = _build_turn_response(
                encounter_id=cur,
                chosen_id=chosen_id,
                chosen_text=chosen_text,
                reaction_text=reaction_text,
                next_id=next_id,
                deltas=deltas,
            )

            rows.append(
                {
                    "model_label": label,
                    "playthrough_index": play_ix,
                    "step_index": step_ix,
                    "encounter_id": cur,
                    "is_terminal": False,
                    "prompt_text": prompt,
                    "response_text": response_text,
                    "chosen_option_id": chosen_id,
                    "chosen_option_text": chosen_text,
                    "chosen_reaction_id": reaction_id,
                    "chosen_reaction_text": reaction_text,
                    "next_encounter_id": next_id,
                    "diary_diff": diary_token,
                    "effect_deltas": deltas,
                    "selection_mode": str(selection_mode),
                    "pick_raw_text": pick_raw,
                    "pick_fallback": bool(pick_fallback),
                    "prompt_tokens": int(score_pack["prompt_tokens"]),
                    "completion_tokens": int(score_pack["completion_tokens"]),
                    "latency_sec": float(score_pack["latency_sec"]),
                    "timestamp_utc": utc_now(),
                }
            )

            if not next_id:
                break
            cur = next_id

        global_diary.extend(local_diary)
        if reached_terminal or _is_terminal(enc_by.get(cur, {})):
            completed += 1

    total_prompt = sum(int(r["prompt_tokens"]) for r in rows)
    total_completion = sum(int(r["completion_tokens"]) for r in rows)
    elapsed = max(0.0001, time.time() - start)
    summary = {
        "model_label": label,
        "run_mode": "playthrough",
        "selection_mode": str(selection_mode),
        "playthroughs_requested": int(playthroughs),
        "playthroughs_completed": int(completed),
        "num_prompts": len(rows),
        "total_prompt_tokens": total_prompt,
        "total_completion_tokens": total_completion,
        "total_tokens": total_prompt + total_completion,
        "avg_completion_tokens": (total_completion / len(rows)) if rows else 0.0,
        "avg_latency_sec": (sum(float(r["latency_sec"]) for r in rows) / len(rows)) if rows else 0.0,
        "wall_time_sec": round(elapsed, 3),
        "tokens_per_sec": round((total_prompt + total_completion) / elapsed, 3),
    }
    write_jsonl(out_dir / "generations.jsonl", rows)
    write_json(out_dir / "summary.json", summary)
    return summary


def run_condition(
    label: str,
    prompts: List[EncounterPrompt],
    out_dir: Path,
    runner: Optional[HFRunner],
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    do_sample: bool,
    dry_run: bool,
) -> Dict[str, Any]:
    ensure_dir(out_dir)
    rows: List[Dict[str, Any]] = []
    start = time.time()
    for i, p in enumerate(prompts):
        if dry_run:
            gen = fake_generate(p.prompt_text, i)
        else:
            assert runner is not None
            gen = runner.generate(
                prompt=p.prompt_text,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=do_sample,
            )
        rows.append(
            {
                "model_label": label,
                "encounter_id": p.encounter_id,
                "turn_span": p.turn_span,
                "is_terminal": p.is_terminal,
                "prompt_text": p.prompt_text,
                "response_text": gen["text"],
                "prompt_tokens": gen["prompt_tokens"],
                "completion_tokens": gen["completion_tokens"],
                "latency_sec": gen["latency_sec"],
                "timestamp_utc": utc_now(),
            }
        )

    total_prompt = sum(int(r["prompt_tokens"]) for r in rows)
    total_completion = sum(int(r["completion_tokens"]) for r in rows)
    elapsed = max(0.0001, time.time() - start)
    summary = {
        "model_label": label,
        "num_prompts": len(rows),
        "total_prompt_tokens": total_prompt,
        "total_completion_tokens": total_completion,
        "total_tokens": total_prompt + total_completion,
        "avg_completion_tokens": (total_completion / len(rows)) if rows else 0.0,
        "avg_latency_sec": (sum(float(r["latency_sec"]) for r in rows) / len(rows)) if rows else 0.0,
        "wall_time_sec": round(elapsed, 3),
        "tokens_per_sec": round((total_prompt + total_completion) / elapsed, 3),
    }
    write_jsonl(out_dir / "generations.jsonl", rows)
    write_json(out_dir / "summary.json", summary)
    return summary


def compare_conditions(run_dir: Path, baseline_dir: Path, adapter_dir: Path) -> Dict[str, Any]:
    b_path = baseline_dir / "generations.jsonl"
    a_path = adapter_dir / "generations.jsonl"
    if (not b_path.exists()) or (not a_path.exists()):
        return {"status": "missing_condition_outputs"}

    b_rows = [json.loads(x) for x in b_path.read_text(encoding="utf-8").splitlines() if x.strip()]
    a_rows = [json.loads(x) for x in a_path.read_text(encoding="utf-8").splitlines() if x.strip()]
    b_by = {r["encounter_id"]: r for r in b_rows}
    a_by = {r["encounter_id"]: r for r in a_rows}
    shared = sorted(set(b_by.keys()) & set(a_by.keys()))
    changed = 0
    token_deltas: List[int] = []
    for eid in shared:
        br = b_by[eid]
        ar = a_by[eid]
        if str(br.get("response_text", "")).strip() != str(ar.get("response_text", "")).strip():
            changed += 1
        token_deltas.append(int(ar.get("completion_tokens", 0)) - int(br.get("completion_tokens", 0)))

    out = {
        "shared_encounters": len(shared),
        "response_changed_count": changed,
        "response_changed_rate": (changed / len(shared)) if shared else 0.0,
        "avg_completion_token_delta_adapter_minus_baseline": (sum(token_deltas) / len(token_deltas)) if token_deltas else 0.0,
        "timestamp_utc": utc_now(),
    }
    write_json(run_dir / "comparisons" / "comparison_summary.json", out)
    return out


def export_bench_rows(run_dir: Path, baseline_dir: Path, adapter_dir: Path) -> Dict[str, Any]:
    b_path = baseline_dir / "generations.jsonl"
    a_path = adapter_dir / "generations.jsonl"
    if (not b_path.exists()) or (not a_path.exists()):
        return {"status": "missing_condition_outputs"}

    b_rows = [json.loads(x) for x in b_path.read_text(encoding="utf-8").splitlines() if x.strip()]
    a_rows = [json.loads(x) for x in a_path.read_text(encoding="utf-8").splitlines() if x.strip()]
    b_by = {r["encounter_id"]: r for r in b_rows}
    a_by = {r["encounter_id"]: r for r in a_rows}
    shared = sorted(set(b_by.keys()) & set(a_by.keys()))

    out_rows: List[Dict[str, Any]] = []
    for eid in shared:
        br = b_by[eid]
        ar = a_by[eid]
        out_rows.append(
            {
                "encounter_id": eid,
                "turn_span": br.get("turn_span", ""),
                "is_terminal": bool(br.get("is_terminal", False)),
                "prompt_text": br.get("prompt_text", ""),
                "baseline": {
                    "model_label": br.get("model_label", "baseline_qwen_1_7b"),
                    "response_text": br.get("response_text", ""),
                    "prompt_tokens": int(br.get("prompt_tokens", 0)),
                    "completion_tokens": int(br.get("completion_tokens", 0)),
                    "latency_sec": float(br.get("latency_sec", 0.0)),
                },
                "adapter": {
                    "model_label": ar.get("model_label", "adapter_claude_constitution_qlora"),
                    "response_text": ar.get("response_text", ""),
                    "prompt_tokens": int(ar.get("prompt_tokens", 0)),
                    "completion_tokens": int(ar.get("completion_tokens", 0)),
                    "latency_sec": float(ar.get("latency_sec", 0.0)),
                },
                "response_changed": str(br.get("response_text", "")).strip() != str(ar.get("response_text", "")).strip(),
                "completion_token_delta_adapter_minus_baseline": int(ar.get("completion_tokens", 0))
                - int(br.get("completion_tokens", 0)),
                "timestamp_utc": utc_now(),
            }
        )
    out_path = run_dir / "comparisons" / "bench_rows.jsonl"
    write_jsonl(out_path, out_rows)
    return {"status": "ok", "rows": len(out_rows), "path": str(out_path)}


def main() -> int:
    ap = argparse.ArgumentParser(description="LLM Player benchmark harness for storyworld encounter prompts.")
    ap.add_argument("--run-mode", choices=["playthrough", "encounter_bench"], default="playthrough")
    ap.add_argument("--selection-mode", choices=["generate_pick", "score_all"], default="generate_pick")
    ap.add_argument("--storyworld", required=True, help="Path to storyworld JSON.")
    ap.add_argument("--base-model-path", required=True, help="HF base model path (Qwen baseline).")
    ap.add_argument("--adapter-path", default="", help="Optional PEFT adapter path for constitution-tuned condition.")
    ap.add_argument("--adapter-only", action=argparse.BooleanOptionalAction, default=False)
    ap.add_argument("--output-root", default=r"D:\Research_Engine\Storyworld_LLM_Plays")
    ap.add_argument("--run-id", default="")
    ap.add_argument("--max-encounters", type=int, default=0, help="Legacy encounter_bench cap.")
    ap.add_argument("--include-terminals", action="store_true")
    ap.add_argument("--playthroughs", type=int, default=2)
    ap.add_argument("--max-steps", type=int, default=128)
    ap.add_argument("--context-window", type=int, default=48)
    ap.add_argument("--context-char-cap", type=int, default=6000)
    ap.add_argument("--max-diary-effects", type=int, default=4)
    ap.add_argument("--include-option-text-in-diary", action=argparse.BooleanOptionalAction, default=True)
    ap.add_argument("--include-scene-text-in-diary", action=argparse.BooleanOptionalAction, default=True)
    ap.add_argument("--pick-max-new-tokens", type=int, default=24)
    ap.add_argument("--max-new-tokens", type=int, default=180)
    ap.add_argument("--temperature", type=float, default=0.2)
    ap.add_argument("--top-p", type=float, default=0.9)
    ap.add_argument("--do-sample", action="store_true")
    ap.add_argument("--device-map", default="auto")
    ap.add_argument("--dtype", choices=["auto", "float16", "bfloat16", "float32"], default="auto")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if bool(args.adapter_only) and (not str(args.adapter_path).strip()):
        raise SystemExit("--adapter-only requires --adapter-path.")

    story_path = Path(args.storyworld).resolve()
    data = load_storyworld(story_path)
    prompts: List[EncounterPrompt] = []
    if str(args.run_mode) == "encounter_bench":
        prompts = build_prompts(
            data,
            max_encounters=int(args.max_encounters),
            include_terminals=bool(args.include_terminals),
        )
        if not prompts:
            raise SystemExit("No prompts generated; check storyworld content and flags.")

    run_id = args.run_id.strip() or f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{story_path.stem}_llm_player"
    run_dir = Path(args.output_root).resolve() / run_id
    ensure_dir(run_dir)
    ensure_dir(run_dir / "meta")
    ensure_dir(run_dir / "prompts")

    write_json(
        run_dir / "meta" / "run_config.json",
        {
            "started_at_utc": utc_now(),
            "storyworld": str(story_path),
            "base_model_path": args.base_model_path,
            "adapter_path": args.adapter_path,
            "adapter_only": bool(args.adapter_only),
            "run_mode": str(args.run_mode),
            "selection_mode": str(args.selection_mode),
            "max_encounters": int(args.max_encounters),
            "include_terminals": bool(args.include_terminals),
            "playthroughs": int(args.playthroughs),
            "max_steps": int(args.max_steps),
            "context_window": int(args.context_window),
            "context_char_cap": int(args.context_char_cap),
            "pick_max_new_tokens": int(args.pick_max_new_tokens),
            "include_option_text_in_diary": bool(args.include_option_text_in_diary),
            "include_scene_text_in_diary": bool(args.include_scene_text_in_diary),
            "max_new_tokens": int(args.max_new_tokens),
            "temperature": float(args.temperature),
            "top_p": float(args.top_p),
            "do_sample": bool(args.do_sample),
            "device_map": str(args.device_map),
            "dtype": str(args.dtype),
            "dry_run": bool(args.dry_run),
            "hostname": os.environ.get("COMPUTERNAME", ""),
        },
    )
    write_jsonl(
        run_dir / "prompts" / "encounter_prompts.jsonl",
        [
            {
                "encounter_id": p.encounter_id,
                "turn_span": p.turn_span,
                "is_terminal": p.is_terminal,
                "prompt_text": p.prompt_text,
            }
            for p in prompts
        ],
    )

    baseline_summary: Dict[str, Any] = {"status": "skipped_adapter_only"}
    if not bool(args.adapter_only):
        baseline_runner = None if args.dry_run else HFRunner(
            model_path=str(args.base_model_path),
            adapter_path="",
            device_map=str(args.device_map),
            dtype=str(args.dtype),
        )
        if str(args.run_mode) == "playthrough":
            baseline_summary = run_playthrough_condition(
                label="baseline_qwen_1_7b",
                data=data,
                out_dir=run_dir / "baseline_qwen_1_7b",
                runner=baseline_runner,
                playthroughs=int(args.playthroughs),
                max_steps=int(args.max_steps),
                context_window=int(args.context_window),
                context_char_cap=int(args.context_char_cap),
                max_diary_effects=int(args.max_diary_effects),
                include_option_text_in_diary=bool(args.include_option_text_in_diary),
                include_scene_text_in_diary=bool(args.include_scene_text_in_diary),
                selection_mode=str(args.selection_mode),
                pick_max_new_tokens=int(args.pick_max_new_tokens),
                dry_run=bool(args.dry_run),
            )
        else:
            baseline_summary = run_condition(
                label="baseline_qwen_1_7b",
                prompts=prompts,
                out_dir=run_dir / "baseline_qwen_1_7b",
                runner=baseline_runner,
                max_new_tokens=int(args.max_new_tokens),
                temperature=float(args.temperature),
                top_p=float(args.top_p),
                do_sample=bool(args.do_sample),
                dry_run=bool(args.dry_run),
            )

    adapter_summary = {"status": "skipped_no_adapter"}
    if args.adapter_path:
        adapter_runner = None if args.dry_run else HFRunner(
            model_path=str(args.base_model_path),
            adapter_path=str(args.adapter_path),
            device_map=str(args.device_map),
            dtype=str(args.dtype),
        )
        if str(args.run_mode) == "playthrough":
            adapter_summary = run_playthrough_condition(
                label="adapter_claude_constitution_qlora",
                data=data,
                out_dir=run_dir / "adapter_claude_constitution_qlora",
                runner=adapter_runner,
                playthroughs=int(args.playthroughs),
                max_steps=int(args.max_steps),
                context_window=int(args.context_window),
                context_char_cap=int(args.context_char_cap),
                max_diary_effects=int(args.max_diary_effects),
                include_option_text_in_diary=bool(args.include_option_text_in_diary),
                include_scene_text_in_diary=bool(args.include_scene_text_in_diary),
                selection_mode=str(args.selection_mode),
                pick_max_new_tokens=int(args.pick_max_new_tokens),
                dry_run=bool(args.dry_run),
            )
        else:
            adapter_summary = run_condition(
                label="adapter_claude_constitution_qlora",
                prompts=prompts,
                out_dir=run_dir / "adapter_claude_constitution_qlora",
                runner=adapter_runner,
                max_new_tokens=int(args.max_new_tokens),
                temperature=float(args.temperature),
                top_p=float(args.top_p),
                do_sample=bool(args.do_sample),
                dry_run=bool(args.dry_run),
            )

    if bool(args.adapter_only):
        comparison = {"status": "skipped_adapter_only"}
        bench_rows_export = {"status": "skipped_adapter_only"}
    else:
        comparison = compare_conditions(
            run_dir=run_dir,
            baseline_dir=run_dir / "baseline_qwen_1_7b",
            adapter_dir=run_dir / "adapter_claude_constitution_qlora",
        )
        bench_rows_export = export_bench_rows(
            run_dir=run_dir,
            baseline_dir=run_dir / "baseline_qwen_1_7b",
            adapter_dir=run_dir / "adapter_claude_constitution_qlora",
        )
    manifest = {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "storyworld": str(story_path),
        "prompt_count": len(prompts),
        "run_mode": str(args.run_mode),
        "selection_mode": str(args.selection_mode),
        "adapter_only": bool(args.adapter_only),
        "baseline_summary": baseline_summary,
        "adapter_summary": adapter_summary,
        "comparison": comparison,
        "bench_rows_export": bench_rows_export,
        "finished_at_utc": utc_now(),
    }
    write_json(run_dir / "manifest.json", manifest)
    print(str(run_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
