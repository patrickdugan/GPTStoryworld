#!/usr/bin/env python3
"""Benchmark LLM player behavior on storyworld encounter prompts."""

from __future__ import annotations

import argparse
import json
import os
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PRIORITY_DELTA_KEYS = [
    "Secret_Clues",
    "Countercraft",
    "good_evil",
    "Influence",
    "Cohesion_Fragmentation",
]


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
    # Preserve caller order first, then use length-priority for robust extraction.
    stable = list(dict.fromkeys([str(x) for x in option_ids if str(x)]))
    ordered = sorted(stable, key=len, reverse=True)
    # Drop explicit reasoning tags when models leak them.
    s = re.sub(r"<think>.*?</think>", " ", s, flags=re.IGNORECASE | re.DOTALL)
    s = re.sub(r"```.*?```", " ", s, flags=re.DOTALL)
    json_match = re.search(r"\{.*\}", s, flags=re.DOTALL)
    if json_match:
        try:
            payload = json.loads(json_match.group(0))
        except Exception:
            payload = None
        if isinstance(payload, dict):
            for key in ("option_id", "option", "chosen", "selected_option"):
                value = str(payload.get(key, "") or "").strip()
                if not value:
                    continue
                for oid in stable:
                    if oid.lower() == value.lower():
                        return oid
                for oid in ordered:
                    if oid.lower().startswith(value.lower()) or value.lower().startswith(oid.lower()):
                        return oid
    for oid in ordered:
        pat = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(oid)}(?![A-Za-z0-9_])", flags=re.IGNORECASE)
        if pat.search(s):
            return oid
    # Accept unambiguous partial IDs (common with short max_new_tokens).
    tokens = re.findall(r"[A-Za-z0-9_]+", s)
    for tok in tokens:
        t = tok.strip()
        if len(t) < 6:
            continue
        matches = [oid for oid in stable if oid.lower().startswith(t.lower()) or t.lower().startswith(oid.lower())]
        if len(matches) == 1:
            return matches[0]
    m = re.search(r"PICK\s+(\d+)", s, flags=re.IGNORECASE)
    if m:
        ix = int(m.group(1))
        if 1 <= ix <= len(stable):
            return stable[ix - 1]
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
    with path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(obj, ensure_ascii=True, indent=2) + "\n")


def write_jsonl(path: Path, rows: List[Dict[str, Any]]) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=True) + "\n")


def _load_json_if_exists(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}


def _count_jsonl_rows(path: Path) -> int:
    if not path.exists():
        return 0
    count = 0
    with path.open("r", encoding="utf-8-sig") as f:
        for line in f:
            if line.strip():
                count += 1
    return count


def collect_condition_receipts(run_dir: Path, adapter_requested: bool, adapter_only: bool) -> Dict[str, Any]:
    expected: List[str] = []
    if not bool(adapter_only):
        expected.append("baseline_qwen_1_7b")
    if bool(adapter_requested):
        expected.append("adapter_claude_constitution_qlora")

    conditions: Dict[str, Any] = {}
    all_complete = True
    for label in expected:
        cond_dir = run_dir / label
        summary_path = cond_dir / "summary.json"
        generations_path = cond_dir / "generations.jsonl"
        summary_obj = _load_json_if_exists(summary_path)
        summary_status = str(summary_obj.get("status", "") or "")
        generations_rows = _count_jsonl_rows(generations_path)
        cond_complete = summary_path.exists() and generations_path.exists() and summary_status in {"completed", "no_encounters"}
        conditions[label] = {
            "summary_exists": summary_path.exists(),
            "summary_status": summary_status,
            "generations_exists": generations_path.exists(),
            "generations_rows": generations_rows,
            "complete": bool(cond_complete),
        }
        all_complete = all_complete and bool(cond_complete)
    return {
        "expected_conditions": expected,
        "conditions": conditions,
        "complete": bool(all_complete),
    }


class HFRunner:
    def __init__(
        self,
        model_path: str,
        adapter_path: str = "",
        device_map: str = "auto",
        dtype: str = "auto",
        load_in_4bit: bool = True,
        bnb_compute_dtype: str = "float16",
    ) -> None:
        self.model_path = model_path
        self.adapter_path = adapter_path
        self.device_map = device_map
        self.dtype = dtype
        self.load_in_4bit = bool(load_in_4bit)
        self.bnb_compute_dtype = bnb_compute_dtype
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
        model = None
        if bool(self.load_in_4bit):
            try:
                from transformers import BitsAndBytesConfig  # type: ignore

                compute_dtype = torch.float16
                if str(self.bnb_compute_dtype).lower() == "bfloat16":
                    compute_dtype = torch.bfloat16
                qcfg = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_compute_dtype=compute_dtype,
                )
                model = AutoModelForCausalLM.from_pretrained(
                    self.model_path,
                    quantization_config=qcfg,
                    device_map=self.device_map,
                )
            except Exception:
                model = None
        if model is None:
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
        enable_thinking: bool = False,
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
            try:
                rendered = tok.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True,
                    enable_thinking=enable_thinking,
                )
            except TypeError:
                try:
                    rendered = tok.apply_chat_template(
                        messages,
                        tokenize=False,
                        add_generation_prompt=True,
                        chat_template_kwargs={"enable_thinking": enable_thinking},
                    )
                except TypeError:
                    rendered = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        else:
            rendered = f"System: {messages[0]['content']}\nUser: {messages[1]['content']}\nAssistant:"
            if enable_thinking:
                rendered += "\nThink carefully and provide only the final answer."

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

    def pick_option(
        self,
        prompt: str,
        option_ids: List[str],
        max_new_tokens: int = 24,
        option_meta: Optional[List[Dict[str, Any]]] = None,
        candidate_count: int = 1,
        candidate_temperature: float = 0.7,
        candidate_top_p: float = 0.95,
        secret_clue_bias: float = 0.0,
        enable_thinking: bool = False,
    ) -> Dict[str, Any]:
        assert self.model is not None
        assert self.tokenizer is not None
        import torch  # type: ignore

        tok = self.tokenizer
        model = self.model
        valid_ids = [str(x) for x in option_ids if str(x)]
        _ = (
            option_meta,
            candidate_count,
            candidate_temperature,
            candidate_top_p,
            secret_clue_bias,
        )
        sys_msg = "Return exactly one allowed option id token. No extra text."
        if enable_thinking:
            sys_msg = "Think carefully, then return exactly one allowed option id token. No extra text."
        user_msg = (
            f"{prompt}\n\n"
            f"Allowed option ids: {', '.join(valid_ids)}\n"
            'Output format: {"option_id":"<one allowed option id>"}'
        )
        messages = [
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": user_msg},
        ]
        if hasattr(tok, "apply_chat_template"):
            try:
                rendered = tok.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True,
                    enable_thinking=enable_thinking,
                )
            except TypeError:
                try:
                    rendered = tok.apply_chat_template(
                        messages,
                        tokenize=False,
                        add_generation_prompt=True,
                        chat_template_kwargs={"enable_thinking": enable_thinking},
                    )
                except TypeError:
                    rendered = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        else:
            rendered = f"System: {sys_msg}\nUser: {user_msg}\nAssistant:"
            if enable_thinking:
                rendered += "\nThink carefully before answering."

        encoded = tok(rendered, return_tensors="pt")
        device = next(model.parameters()).device
        encoded = {k: v.to(device) for k, v in encoded.items()}

        def _gen(rendered_prompt: str, max_tokens: int) -> Tuple[str, int, int, float]:
            e = tok(rendered_prompt, return_tensors="pt")
            d = next(model.parameters()).device
            e = {k: v.to(d) for k, v in e.items()}
            t0 = time.time()
            with torch.no_grad():
                out_ids = model.generate(
                    **e,
                    max_new_tokens=max(8, int(max_tokens)),
                    do_sample=False,
                    eos_token_id=tok.eos_token_id,
                    pad_token_id=tok.eos_token_id,
                )
            latency_local = time.time() - t0
            new_ids_local = out_ids[0][e["input_ids"].shape[1] :]
            raw_local = tok.decode(new_ids_local, skip_special_tokens=True).strip()
            return raw_local, int(e["input_ids"].shape[1]), int(new_ids_local.shape[0]), latency_local

        raw_text, prompt_tokens, completion_tokens, latency = _gen(rendered, max(8, int(max_new_tokens)))
        chosen = _pick_option_id_from_text(raw_text, valid_ids)
        # One constrained retry before fallback.
        if (not chosen) and valid_ids:
            retry_user = (
                "Pick ONE id from this list and output only that id:\n"
                + ", ".join(valid_ids)
                + '\nAnswer with only JSON: {"option_id":"<id>"}'
            )
            retry_msgs = [
                {
                    "role": "system",
                    "content": "Output one allowed id token only."
                    if not enable_thinking
                    else "Think carefully, then output one allowed id token only.",
                },
                {"role": "user", "content": retry_user},
            ]
            if hasattr(tok, "apply_chat_template"):
                try:
                    retry_rendered = tok.apply_chat_template(
                        retry_msgs,
                        tokenize=False,
                        add_generation_prompt=True,
                        enable_thinking=enable_thinking,
                    )
                except TypeError:
                    try:
                        retry_rendered = tok.apply_chat_template(
                            retry_msgs,
                            tokenize=False,
                            add_generation_prompt=True,
                            chat_template_kwargs={"enable_thinking": enable_thinking},
                        )
                    except TypeError:
                        retry_rendered = tok.apply_chat_template(retry_msgs, tokenize=False, add_generation_prompt=True)
            else:
                retry_rendered = f"System: {retry_msgs[0]['content']}\nUser: {retry_msgs[1]['content']}\nAssistant:"
                if enable_thinking:
                    retry_rendered += "\nThink carefully before answering."
            raw_retry, p2, c2, l2 = _gen(retry_rendered, max(8, min(18, int(max_new_tokens))))
            chosen_retry = _pick_option_id_from_text(raw_retry, valid_ids)
            if chosen_retry:
                chosen = chosen_retry
                raw_text = raw_retry
            prompt_tokens += p2
            completion_tokens += c2
            latency += l2
        fallback = False
        if not chosen and valid_ids:
            chosen = valid_ids[0]
            fallback = True
        return {
            "option_id": chosen,
            "raw_text": raw_text,
            "fallback": bool(fallback),
            "prompt_tokens": int(prompt_tokens),
            "completion_tokens": int(completion_tokens),
            "latency_sec": round(latency, 4),
        }


class ApiRunner:
    def __init__(
        self,
        base_url: str,
        model_name: str,
        api_key: str = "",
        timeout_sec: int = 180,
        system_prompt: str = "",
    ) -> None:
        self.base_url = str(base_url or "").rstrip("/")
        self.model_name = str(model_name or "").strip()
        self.api_key = str(api_key or "")
        self.timeout_sec = max(1, int(timeout_sec))
        self.system_prompt = str(system_prompt or "").strip()
        if not self.base_url:
            raise ValueError("API runner requires a base URL.")
        if not self.model_name:
            raise ValueError("API runner requires a model name.")

    def _estimate_tokens(self, text: str) -> int:
        return max(1, len(str(text or "")) // 4)

    def _chat_completion(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int,
        temperature: float,
        top_p: float,
        do_sample: bool,
    ) -> Dict[str, Any]:
        payload = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": max(1, int(max_tokens)),
            "temperature": float(temperature if do_sample else 0.0),
            "top_p": float(top_p),
            "stream": False,
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url=f"{self.base_url}/chat/completions",
            data=data,
            headers={
                "Content-Type": "application/json",
                **({"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}),
            },
            method="POST",
        )
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_sec) as resp:
                body = resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"API runner HTTP {exc.code}: {detail[:400]}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"API runner connection failed: {exc}") from exc
        latency = time.time() - t0
        obj = json.loads(body)
        choices = obj.get("choices") or []
        if not choices:
            raise RuntimeError("API runner returned no choices.")
        message = choices[0].get("message") or {}
        content = message.get("content", "")
        if isinstance(content, list):
            text = "".join(str(part.get("text", "")) for part in content if isinstance(part, dict))
        else:
            text = str(content or "")
        usage = obj.get("usage") or {}
        prompt_tokens = int(usage.get("prompt_tokens") or self._estimate_tokens(json.dumps(messages, ensure_ascii=True)))
        completion_tokens = int(usage.get("completion_tokens") or self._estimate_tokens(text))
        return {
            "text": text.strip(),
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "latency_sec": round(latency, 4),
        }

    def generate(
        self,
        prompt: str,
        max_new_tokens: int,
        temperature: float,
        top_p: float,
        do_sample: bool,
    ) -> Dict[str, Any]:
        system_prompt = self.system_prompt or "You are an in-world player making coherent, morally aware decisions."
        return self._chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            do_sample=do_sample,
        )

    def score_option(self, prompt: str, option_text: str) -> Dict[str, Any]:
        raise RuntimeError("API runner does not support score_all mode. Use generate_pick.")

    def pick_option(
        self,
        prompt: str,
        option_ids: List[str],
        max_new_tokens: int = 24,
        option_meta: Optional[List[Dict[str, Any]]] = None,
        candidate_count: int = 1,
        candidate_temperature: float = 0.7,
        candidate_top_p: float = 0.95,
        secret_clue_bias: float = 0.0,
        enable_thinking: bool = False,
    ) -> Dict[str, Any]:
        valid_ids = [str(x) for x in option_ids if str(x)]
        system_parts = ["Return exactly one allowed option id token. No extra text."]
        if self.system_prompt:
            system_parts.append(self.system_prompt)
        messages = [
            {"role": "system", "content": "\n".join(system_parts)},
            {
                "role": "user",
                "content": (
                    f"{prompt}\n\n"
                    f"Allowed option ids: {', '.join(valid_ids)}\n"
                    'Output format: {"option_id":"<one allowed option id>"}'
                ),
            },
        ]

        def _single_pick(do_sample: bool, temperature: float, top_p: float) -> Dict[str, Any]:
            result_local = self._chat_completion(
                messages=messages,
                max_tokens=max(8, int(max_new_tokens)),
                temperature=temperature,
                top_p=top_p,
                do_sample=do_sample,
            )
            chosen_local = _pick_option_id_from_text(result_local["text"], valid_ids)
            if not chosen_local and valid_ids:
                retry = self._chat_completion(
                    messages=[
                        {"role": "system", "content": "Output one allowed id token only."},
                        {
                            "role": "user",
                            "content": (
                                "Pick ONE id from this list and output only that id:\n"
                                + ", ".join(valid_ids)
                                + '\nAnswer with only JSON: {"option_id":"<id>"}'
                            ),
                        },
                    ],
                    max_tokens=max(8, min(18, int(max_new_tokens))),
                    temperature=0.0,
                    top_p=1.0,
                    do_sample=False,
                )
                retry_chosen = _pick_option_id_from_text(retry["text"], valid_ids)
                if retry_chosen:
                    chosen_local = retry_chosen
                    result_local["text"] = retry["text"]
                result_local["prompt_tokens"] += int(retry["prompt_tokens"])
                result_local["completion_tokens"] += int(retry["completion_tokens"])
                result_local["latency_sec"] = round(float(result_local["latency_sec"]) + float(retry["latency_sec"]), 4)
            return {"chosen": chosen_local, "result": result_local}

        total_prompt_tokens = 0
        total_completion_tokens = 0
        total_latency_sec = 0.0
        candidates: List[Dict[str, Any]] = []
        rounds = max(1, int(candidate_count))
        for ix in range(rounds):
            sample = _single_pick(
                do_sample=bool(ix > 0),
                temperature=float(candidate_temperature),
                top_p=float(candidate_top_p),
            )
            chosen_local = str(sample["chosen"] or "")
            result_local = sample["result"]
            total_prompt_tokens += int(result_local["prompt_tokens"])
            total_completion_tokens += int(result_local["completion_tokens"])
            total_latency_sec += float(result_local["latency_sec"])
            candidates.append(
                {
                    "option_id": chosen_local,
                    "raw_text": str(result_local["text"] or ""),
                    "score": _candidate_pick_score(
                        option_id=chosen_local,
                        raw_text=str(result_local["text"] or ""),
                        option_meta=option_meta,
                        secret_clue_bias=float(secret_clue_bias),
                    )
                    if chosen_local
                    else -1e9,
                }
            )

        valid_candidates = [c for c in candidates if c.get("option_id")]
        best = max(valid_candidates, key=lambda c: float(c.get("score", -1e9))) if valid_candidates else None
        chosen = str((best or {}).get("option_id", "") or "")
        raw_text = str((best or {}).get("raw_text", "") or "")
        fallback = False
        if not chosen and valid_ids:
            chosen = valid_ids[0]
            raw_text = raw_text or ""
            fallback = True
        return {
            "option_id": chosen,
            "raw_text": raw_text,
            "fallback": bool(fallback),
            "prompt_tokens": int(total_prompt_tokens),
            "completion_tokens": int(total_completion_tokens),
            "latency_sec": float(round(total_latency_sec, 4)),
            "candidate_count": int(rounds),
            "ranked_candidates": sorted(candidates, key=lambda c: float(c.get("score", -1e9)), reverse=True),
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


def _candidate_pick_score(
    option_id: str,
    raw_text: str,
    option_meta: Optional[List[Dict[str, Any]]] = None,
    secret_clue_bias: float = 0.0,
) -> float:
    score = 0.0
    meta_by_id = {str((row or {}).get("id", "") or ""): (row or {}) for row in (option_meta or [])}
    meta = meta_by_id.get(str(option_id or ""), {})
    effects = [str(x or "") for x in (meta.get("effect_deltas") or [])]
    next_ids = [str(x or "") for x in (meta.get("consequence_ids") or [])]
    blob = " ".join(effects + next_ids + [str(meta.get("text", "") or ""), str(raw_text or "")]).lower()
    if "secret_clues:+" in blob:
        score += 1.0 + float(secret_clue_bias)
    if "secret_clues:-" in blob:
        score -= 1.0 + (0.5 * float(secret_clue_bias))
    if "page_secret" in blob or "spool_secret" in blob or " secret" in blob:
        score += 0.8 + (0.5 * float(secret_clue_bias))
    if "ending" in blob or "wonder" in blob or "escape" in blob:
        score += 0.15
    return float(score)


def _effect_items(reaction: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not reaction:
        return []
    if isinstance(reaction.get("after_effects"), list):
        return list(reaction.get("after_effects") or [])
    if isinstance(reaction.get("effects"), list):
        return list(reaction.get("effects") or [])
    return []


def _eval_story_script(script: Any, state: Dict[Tuple[str, str], float]) -> Any:
    if script is True:
        return True
    if script is False:
        return False
    if isinstance(script, (int, float)):
        return script
    if not isinstance(script, dict):
        return script
    pt = script.get("pointer_type")
    ot = script.get("operator_type")
    if pt == "Bounded Number Constant":
        return script.get("value", 0.0)
    if pt == "String Constant":
        return script.get("value", "")
    if pt == "Bounded Number Pointer":
        ch = str(script.get("character", "") or "")
        key = str((script.get("keyring") or [""])[0] or "")
        coef = float(script.get("coefficient", 1.0) or 1.0)
        return float(state.get((ch, key), 0.0)) * coef
    if ot == "Arithmetic Comparator":
        ops = list(script.get("operands") or [None, None])
        a = _eval_story_script(ops[0], state)
        b = _eval_story_script(ops[1], state)
        sub = str(script.get("operator_subtype", "") or "")
        lut = {
            "Greater Than or Equal To": a >= b,
            "Less Than or Equal To": a <= b,
            "Greater Than": a > b,
            "Less Than": a < b,
            "Equal To": a == b,
            "Not Equal To": a != b,
            "GTE": a >= b,
            "LTE": a <= b,
            "GT": a > b,
            "LT": a < b,
            "EQ": a == b,
            "NEQ": a != b,
        }
        return lut.get(sub, False)
    if ot == "And":
        return all(bool(_eval_story_script(op, state)) for op in (script.get("operands") or []))
    if ot == "Or":
        return any(bool(_eval_story_script(op, state)) for op in (script.get("operands") or []))
    if ot == "Addition":
        return sum(float(_eval_story_script(op, state) or 0.0) for op in (script.get("operands") or []))
    if ot == "Subtraction":
        ops = list(script.get("operands") or [])
        if not ops:
            return 0.0
        head = float(_eval_story_script(ops[0], state) or 0.0)
        tail = sum(float(_eval_story_script(op, state) or 0.0) for op in ops[1:])
        return head - tail
    if ot == "Multiplication":
        out = 1.0
        for op in (script.get("operands") or []):
            out *= float(_eval_story_script(op, state) or 0.0)
        return out
    if ot == "Absolute Value":
        ops = list(script.get("operands") or [0.0])
        return abs(float(_eval_story_script(ops[0], state) or 0.0))
    if ot == "Nudge":
        ops = list(script.get("operands") or [0.0, 0.0])
        cur = float(_eval_story_script(ops[0], state) or 0.0)
        delta = float(_eval_story_script(ops[1], state) or 0.0)
        return max(-1.0, min(1.0, cur + delta))
    return script.get("value", 0.0)


def _apply_story_effects(reaction: Optional[Dict[str, Any]], state: Dict[Tuple[str, str], float]) -> None:
    for ae in _effect_items(reaction):
        if str(ae.get("effect_type", "") or "") != "Bounded Number Effect":
            continue
        st = ae.get("Set") or {}
        ch = str(st.get("character", "") or "")
        key = str((st.get("keyring") or [""])[0] or "")
        if (not ch) or (not key):
            continue
        state[(ch, key)] = float(_eval_story_script(ae.get("to"), state) or 0.0)


def _pick_reaction_for_state(option: Dict[str, Any], state: Dict[Tuple[str, str], float]) -> Optional[Dict[str, Any]]:
    reactions = list(option.get("reactions") or [])
    if not reactions:
        return None
    ranked: List[Tuple[float, str, Dict[str, Any]]] = []
    for rxn in reactions:
        desirability = _eval_story_script(rxn.get("desirability_script", 0.0), state)
        if isinstance(desirability, bool):
            desirability = 1.0 if desirability else 0.0
        ranked.append((float(desirability or 0.0), str(rxn.get("id", "") or ""), rxn))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    return ranked[0][2]


def _choose_wild_next_encounter(
    encounters: List[Dict[str, Any]],
    state: Dict[Tuple[str, str], float],
    current_id: str,
    visited_counts: Dict[str, int],
) -> str:
    ranked: List[Tuple[int, float, int, str]] = []
    for enc in encounters:
        enc_id = str(enc.get("id", "") or "")
        if (not enc_id) or enc_id == current_id:
            continue
        if not bool(_eval_story_script(enc.get("acceptability_script", True), state)):
            continue
        desirability = _eval_story_script(enc.get("desirability_script", 0.0), state)
        if isinstance(desirability, bool):
            desirability = 1.0 if desirability else 0.0
        ranked.append(
            (
                int(visited_counts.get(enc_id, 0) or 0),
                -float(desirability or 0.0),
                int(enc.get("creation_index", 10**9) or 10**9),
                enc_id,
            )
        )
    if not ranked:
        return ""
    ranked.sort()
    return str(ranked[0][3])


def _effect_delta_tokens(effects: List[Dict[str, Any]], max_items: int) -> List[str]:
    rendered: List[str] = []
    by_key: Dict[str, str] = {}
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
            token = f"{key}:set"
        else:
            sign = "+" if delta >= 0 else ""
            token = f"{key}:{sign}{delta:.3g}"
        rendered.append(token)
        by_key[key] = token

    chosen: List[str] = []
    seen: set[str] = set()
    for key in PRIORITY_DELTA_KEYS:
        tok = by_key.get(key)
        if tok:
            chosen.append(tok)
            seen.add(tok)
    for tok in rendered:
        if tok in seen:
            continue
        chosen.append(tok)
        seen.add(tok)
        if len(chosen) >= max(1, int(max_items)):
            break
    if len(chosen) > max(1, int(max_items)):
        chosen = chosen[: max(1, int(max_items))]
    return chosen


def _compact_text(text: str, max_len: int) -> str:
    s = " ".join(str(text or "").split())
    if len(s) <= max(1, int(max_len)):
        return s
    return s[: max(1, int(max_len))].rstrip() + "..."


def _creole_text(text: str, max_terms: int = 8) -> str:
    s = " ".join(str(text or "").split()).lower()
    if not s:
        return ""
    tokens = re.findall(r"[a-z0-9_']+", s)
    stop = {
        "the", "a", "an", "and", "or", "but", "to", "of", "in", "on", "at", "for", "with",
        "from", "by", "as", "is", "are", "was", "were", "be", "been", "being", "this", "that",
        "these", "those", "it", "its", "into", "their", "there", "here", "every", "each",
        "through", "across", "against", "over", "under", "now", "then", "can", "could",
        "would", "should", "must", "will", "just", "than",
    }
    chosen: List[str] = []
    seen: set[str] = set()
    for tok in tokens:
        if len(tok) <= 2 or tok in stop or tok in seen:
            continue
        seen.add(tok)
        chosen.append(tok)
        if len(chosen) >= max(1, int(max_terms)):
            break
    if not chosen:
        chosen = tokens[: max(1, int(max_terms))]
    return "/".join(chosen)


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


def _summarize_playthrough(
    play_ix: int,
    rows: List[Dict[str, Any]],
    max_items: int,
) -> str:
    if not rows:
        return f"p{play_ix:02d} end=unknown steps=0"
    totals: Dict[str, float] = {}
    for row in rows:
        for key in row.get("effect_deltas", []) or []:
            pass
        for tok in row.get("effect_deltas", []) or []:
            if ":" not in str(tok):
                continue
            k, v = str(tok).split(":", 1)
            try:
                totals[k] = totals.get(k, 0.0) + float(v)
            except ValueError:
                continue
    ordered = sorted(
        totals.items(),
        key=lambda kv: (abs(float(kv[1])), kv[0]),
        reverse=True,
    )[: max(1, int(max_items))]
    delta_blob = ",".join([f"{k}:{v:+.3g}" for k, v in ordered]) if ordered else "none"
    last = rows[-1]
    ending_id = str(last.get("next_encounter_id", "") or last.get("encounter_id", "") or "unknown")
    clue_hits = sum(
        1
        for row in rows
        for tok in (row.get("effect_deltas", []) or [])
        if str(tok).startswith("Secret_Clues:") and (":" in str(tok)) and not str(tok).endswith(":set")
    )
    return f"p{play_ix:02d} end={ending_id} steps={len(rows)} clue_hits={clue_hits} totals[{delta_blob}]"


def _build_turn_prompt(
    title: str,
    about: str,
    enc_id: str,
    enc_text: str,
    options: List[Tuple[str, str]],
    diary: List[str],
    context_window: int,
    context_char_cap: int,
    about_char_cap: int,
    scene_char_cap: int,
) -> str:
    diary_ctx = "\n".join(diary[-max(0, int(context_window)) :]) if diary else "(none)"
    if int(context_char_cap) > 0 and len(diary_ctx) > int(context_char_cap):
        diary_ctx = "... " + diary_ctx[-int(context_char_cap) :]
    about_txt = _compact_text(about, max(1, int(about_char_cap)))
    scene_txt = _compact_text(enc_text, max(1, int(scene_char_cap)))
    options_txt = "\n".join([f"- {oid}: {otxt}" for oid, otxt in options])
    return (
        f"Storyworld: {title}\n"
        f"About: {about_txt}\n"
        "Compact Prior Diary (diffs):\n"
        f"{diary_ctx}\n\n"
        f"Encounter: {enc_id}\n"
        f"Scene:\n{scene_txt}\n\n"
        "Choose one option from this fixed list:\n"
        f"{options_txt}\n"
    )


def run_playthrough_condition(
    label: str,
    data: Dict[str, Any],
    out_dir: Path,
    runner: Optional[Any],
    playthroughs: int,
    max_steps: int,
    context_window: int,
    context_char_cap: int,
    about_char_cap: int,
    scene_char_cap: int,
    max_diary_effects: int,
    include_option_text_in_diary: bool,
    include_scene_text_in_diary: bool,
    selection_mode: str,
    first_click_mode: str,
    pick_max_new_tokens: int,
    stop_on_cycle: bool,
    max_cycle_repeats: int,
    max_unique_encounters: int,
    cross_play_memory_mode: str,
    cross_play_summary_items: int,
    start_encounter_id: str,
    seed_diary: Optional[List[str]],
    api_pick_candidate_count: int,
    api_pick_candidate_temperature: float,
    api_pick_candidate_top_p: float,
    secret_clue_bias: float,
    enable_thinking: bool,
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
    start_id = str(start_encounter_id or "").strip() or str(encs[0].get("id", "") or "")
    if start_id not in enc_by:
        start_id = str(encs[0].get("id", "") or "")
    gen_path = out_dir / "generations.jsonl"
    rows: List[Dict[str, Any]] = []
    start = time.time()
    global_diary: List[str] = []
    completed = 0
    write_json(
        out_dir / "summary.json",
        {
            "model_label": label,
            "run_mode": "playthrough",
            "status": "running",
            "started_at_utc": utc_now(),
            "playthroughs_requested": int(playthroughs),
            "play_until_ending": bool(int(max_steps) <= 0),
        },
    )

    safety_step_cap = 2048
    step_limit = int(max_steps) if int(max_steps) > 0 else safety_step_cap

    with gen_path.open("w", encoding="utf-8", newline="\n") as gen_f:
        for play_ix in range(1, max(1, int(playthroughs)) + 1):
            cur = start_id
            local_diary: List[str] = list(seed_diary or [])
            script_state: Dict[Tuple[str, str], float] = {}
            reached_terminal = False
            visited_counts: Dict[str, int] = {}
            stop_reason = "unknown"
            for step_ix in range(1, max(1, int(step_limit)) + 1):
                if int(max_unique_encounters) > 0 and len(visited_counts) >= int(max_unique_encounters):
                    stop_reason = "max_unique_encounters"
                    break
                visited_counts[cur] = int(visited_counts.get(cur, 0)) + 1
                if bool(stop_on_cycle) and int(visited_counts[cur]) > max(1, int(max_cycle_repeats)):
                    stop_reason = "cycle_repeat_cap"
                    break
                enc = enc_by.get(cur)
                if not enc:
                    stop_reason = "missing_encounter"
                    break
                if _is_terminal(enc):
                    reached_terminal = True
                    stop_reason = "terminal"
                    break
                raw_opts = sorted(enc.get("options", []) or [], key=lambda o: str(o.get("id", "")))
                options: List[Tuple[str, str, Dict[str, Any]]] = []
                for o in raw_opts:
                    oid = str(o.get("id", "") or "").strip()
                    otext = _script_text(o.get("text_script")).strip()
                    if not bool(_eval_story_script(o.get("visibility_script", True), script_state)):
                        continue
                    if not bool(_eval_story_script(o.get("performability_script", True), script_state)):
                        continue
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
                    about_char_cap=about_char_cap,
                    scene_char_cap=scene_char_cap,
                )

                pick_raw = ""
                pick_fallback = False
                effective_selection_mode = str(selection_mode)
                if step_ix == 1 and str(selection_mode) == "generate_pick":
                    effective_selection_mode = str(first_click_mode)
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
                    if effective_selection_mode == "score_all":
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
                            option_meta=[
                                {
                                    "id": oid,
                                    "text": otext,
                                    "consequence_ids": _option_consequences(oobj),
                                    "effect_deltas": _effect_delta_tokens(
                                        _effect_items(_reaction_for_consequence(oobj, _option_consequences(oobj)[0]))
                                        if _option_consequences(oobj)
                                        else _effect_items(_pick_reaction_for_state(oobj, script_state)),
                                        max_diary_effects,
                                    ),
                                }
                                for oid, otext, oobj in options
                            ],
                            candidate_count=max(1, int(api_pick_candidate_count)),
                            candidate_temperature=float(api_pick_candidate_temperature),
                            candidate_top_p=float(api_pick_candidate_top_p),
                            secret_clue_bias=float(secret_clue_bias),
                            enable_thinking=bool(enable_thinking),
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
                reaction = None
                cons = _option_consequences(chosen_opt)
                next_id = ""
                if cons:
                    next_id = cons[0]
                    for cid in cons:
                        if int(visited_counts.get(cid, 0)) == 0:
                            next_id = cid
                            break
                    reaction = _reaction_for_consequence(chosen_opt, next_id if next_id else "")
                else:
                    reaction = _pick_reaction_for_state(chosen_opt, script_state)
                reaction_id = str((reaction or {}).get("id", "") or "")
                reaction_text = _script_text((reaction or {}).get("text_script"))
                _apply_story_effects(reaction, script_state)
                if not next_id:
                    next_id = _choose_wild_next_encounter(encs, script_state, cur, visited_counts)
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
                    diary_token += f" sc={_creole_text(_script_text(enc.get('text_script')), 8)}"
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

                row = {
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
                    "selection_mode": effective_selection_mode,
                    "requested_selection_mode": str(selection_mode),
                    "pick_raw_text": pick_raw,
                    "pick_fallback": bool(pick_fallback),
                    "prompt_tokens": int(score_pack["prompt_tokens"]),
                    "completion_tokens": int(score_pack["completion_tokens"]),
                    "latency_sec": float(score_pack["latency_sec"]),
                    "timestamp_utc": utc_now(),
                }
                rows.append(row)
                gen_f.write(json.dumps(row, ensure_ascii=True) + "\n")
                gen_f.flush()

                if not next_id:
                    stop_reason = "no_next_encounter"
                    break
                cur = next_id

            if str(cross_play_memory_mode) == "full_diary":
                global_diary.extend(local_diary)
            elif str(cross_play_memory_mode) == "summary":
                global_diary.append(
                    _summarize_playthrough(
                        play_ix=play_ix,
                        rows=[r for r in rows if int(r.get("playthrough_index", 0) or 0) == int(play_ix)],
                        max_items=int(cross_play_summary_items),
                    )
                )
            if reached_terminal or _is_terminal(enc_by.get(cur, {})):
                completed += 1

    total_prompt = sum(int(r["prompt_tokens"]) for r in rows)
    total_completion = sum(int(r["completion_tokens"]) for r in rows)
    elapsed = max(0.0001, time.time() - start)
    summary = {
        "model_label": label,
        "run_mode": "playthrough",
        "selection_mode": str(selection_mode),
        "first_click_mode": str(first_click_mode),
        "play_until_ending": bool(int(max_steps) <= 0),
        "step_limit_applied": int(step_limit),
        "stop_on_cycle": bool(stop_on_cycle),
        "max_cycle_repeats": int(max_cycle_repeats),
        "max_unique_encounters": int(max_unique_encounters),
        "cross_play_memory_mode": str(cross_play_memory_mode),
        "cross_play_summary_items": int(cross_play_summary_items),
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
        "status": "completed",
        "finished_at_utc": utc_now(),
    }
    write_jsonl(out_dir / "generations.jsonl", rows)
    write_json(out_dir / "summary.json", summary)
    return summary


def run_condition(
    label: str,
    prompts: List[EncounterPrompt],
    out_dir: Path,
    runner: Optional[Any],
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    do_sample: bool,
    enable_thinking: bool,
    dry_run: bool,
) -> Dict[str, Any]:
    ensure_dir(out_dir)
    rows: List[Dict[str, Any]] = []
    start = time.time()
    write_json(
        out_dir / "summary.json",
        {
            "model_label": label,
            "run_mode": "encounter_bench",
            "status": "running",
            "started_at_utc": utc_now(),
            "num_prompts_requested": len(prompts),
        },
    )
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
                enable_thinking=bool(enable_thinking),
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
        "status": "completed",
        "finished_at_utc": utc_now(),
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
    ap.add_argument(
        "--first-click-mode",
        choices=["generate_pick", "score_all"],
        default="generate_pick",
        help="Selection mode forced for step 1 of each playthrough. Default stays on bounded local picking.",
    )
    ap.add_argument("--storyworld", required=True, help="Path to storyworld JSON.")
    ap.add_argument("--base-model-path", required=True, help="HF base model path (Qwen baseline).")
    ap.add_argument("--adapter-path", default="", help="Optional PEFT adapter path for constitution-tuned condition.")
    ap.add_argument("--adapter-only", action=argparse.BooleanOptionalAction, default=False)
    ap.add_argument("--runner-backend", choices=["hf", "api"], default="hf")
    ap.add_argument("--api-base-url", default="", help="OpenAI-compatible /v1 endpoint root for API runner.")
    ap.add_argument("--api-model", default="", help="Served model name for API runner.")
    ap.add_argument("--api-key", default="", help="Optional bearer token for API runner.")
    ap.add_argument("--api-system-prompt", default="", help="Optional system prompt override for API runner.")
    ap.add_argument("--output-root", default=r"D:\Research_Engine\Storyworld_LLM_Plays")
    ap.add_argument("--run-id", default="")
    ap.add_argument("--max-encounters", type=int, default=0, help="Legacy encounter_bench cap.")
    ap.add_argument("--include-terminals", action="store_true")
    ap.add_argument("--playthroughs", type=int, default=2)
    ap.add_argument("--max-steps", type=int, default=0, help="0 means play until terminal ending (with internal safety cap).")
    ap.add_argument("--context-window", type=int, default=48)
    ap.add_argument("--context-char-cap", type=int, default=6000)
    ap.add_argument("--about-char-cap", type=int, default=240)
    ap.add_argument("--scene-char-cap", type=int, default=900)
    ap.add_argument("--max-diary-effects", type=int, default=4)
    ap.add_argument("--include-option-text-in-diary", action=argparse.BooleanOptionalAction, default=True)
    ap.add_argument("--include-scene-text-in-diary", action=argparse.BooleanOptionalAction, default=True)
    ap.add_argument("--pick-max-new-tokens", type=int, default=24)
    ap.add_argument("--api-pick-candidate-count", type=int, default=1)
    ap.add_argument("--api-pick-candidate-temperature", type=float, default=0.7)
    ap.add_argument("--api-pick-candidate-top-p", type=float, default=0.95)
    ap.add_argument("--secret-clue-bias", type=float, default=0.0)
    ap.add_argument("--enable-thinking", action="store_true", help="Enable Qwen thinking mode when the tokenizer supports it.")
    ap.add_argument("--start-encounter-id", default="", help="Optional non-default encounter id to start each playthrough from.")
    ap.add_argument("--seed-diary-path", default="", help="Optional text or JSON file with prior diary lines used as initial context.")
    ap.add_argument("--cross-play-memory-mode", choices=["full_diary", "summary", "none"], default="summary")
    ap.add_argument("--cross-play-summary-items", type=int, default=6)
    ap.add_argument("--stop-on-cycle", action=argparse.BooleanOptionalAction, default=True)
    ap.add_argument("--max-cycle-repeats", type=int, default=2)
    ap.add_argument("--max-unique-encounters", type=int, default=120)
    ap.add_argument("--max-new-tokens", type=int, default=180)
    ap.add_argument("--temperature", type=float, default=0.2)
    ap.add_argument("--top-p", type=float, default=0.9)
    ap.add_argument("--do-sample", action="store_true")
    ap.add_argument("--device-map", default="auto")
    ap.add_argument("--dtype", choices=["auto", "float16", "bfloat16", "float32"], default="auto")
    ap.add_argument("--load-in-4bit", action=argparse.BooleanOptionalAction, default=True)
    ap.add_argument("--bnb-compute-dtype", choices=["float16", "bfloat16"], default="float16")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if bool(args.adapter_only) and (not str(args.adapter_path).strip()):
        raise SystemExit("--adapter-only requires --adapter-path.")
    if str(args.runner_backend) == "api" and bool(str(args.adapter_path).strip()):
        raise SystemExit("API runner currently supports baseline-only runs. Omit --adapter-path.")
    if str(args.runner_backend) == "api" and (
        str(args.selection_mode) == "score_all" or str(args.first_click_mode) == "score_all"
    ):
        raise SystemExit("API runner supports generate_pick only. Set --selection-mode generate_pick --first-click-mode generate_pick.")

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
    manifest_path = run_dir / "manifest.json"

    write_json(
        run_dir / "meta" / "run_config.json",
        {
            "started_at_utc": utc_now(),
            "storyworld": str(story_path),
            "base_model_path": args.base_model_path,
            "adapter_path": args.adapter_path,
            "adapter_only": bool(args.adapter_only),
            "runner_backend": str(args.runner_backend),
            "api_base_url": str(args.api_base_url),
            "api_model": str(args.api_model),
            "api_system_prompt": str(args.api_system_prompt),
            "run_mode": str(args.run_mode),
            "selection_mode": str(args.selection_mode),
            "first_click_mode": str(args.first_click_mode),
            "max_encounters": int(args.max_encounters),
            "include_terminals": bool(args.include_terminals),
            "playthroughs": int(args.playthroughs),
            "max_steps": int(args.max_steps),
            "context_window": int(args.context_window),
            "context_char_cap": int(args.context_char_cap),
            "about_char_cap": int(args.about_char_cap),
            "scene_char_cap": int(args.scene_char_cap),
            "pick_max_new_tokens": int(args.pick_max_new_tokens),
            "api_pick_candidate_count": int(args.api_pick_candidate_count),
            "api_pick_candidate_temperature": float(args.api_pick_candidate_temperature),
            "api_pick_candidate_top_p": float(args.api_pick_candidate_top_p),
            "secret_clue_bias": float(args.secret_clue_bias),
            "enable_thinking": bool(args.enable_thinking),
            "start_encounter_id": str(args.start_encounter_id),
            "seed_diary_path": str(args.seed_diary_path),
            "cross_play_memory_mode": str(args.cross_play_memory_mode),
            "cross_play_summary_items": int(args.cross_play_summary_items),
            "include_option_text_in_diary": bool(args.include_option_text_in_diary),
            "include_scene_text_in_diary": bool(args.include_scene_text_in_diary),
            "stop_on_cycle": bool(args.stop_on_cycle),
            "max_cycle_repeats": int(args.max_cycle_repeats),
            "max_unique_encounters": int(args.max_unique_encounters),
            "max_new_tokens": int(args.max_new_tokens),
            "temperature": float(args.temperature),
            "top_p": float(args.top_p),
            "do_sample": bool(args.do_sample),
            "device_map": str(args.device_map),
            "dtype": str(args.dtype),
            "load_in_4bit": bool(args.load_in_4bit),
            "bnb_compute_dtype": str(args.bnb_compute_dtype),
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

    seed_diary: List[str] = []
    seed_diary_path = str(args.seed_diary_path or "").strip()
    if seed_diary_path:
        p = Path(seed_diary_path).resolve()
        if not p.exists():
            raise SystemExit(f"Seed diary file not found: {p}")
        raw = p.read_text(encoding="utf-8-sig")
        loaded = None
        try:
            loaded = json.loads(raw)
        except Exception:
            loaded = None
        if isinstance(loaded, list):
            seed_diary = [str(x) for x in loaded if str(x).strip()]
        else:
            seed_diary = [line.strip() for line in raw.splitlines() if line.strip()]

    baseline_summary: Dict[str, Any] = {"status": "pending"} if not bool(args.adapter_only) else {"status": "skipped_adapter_only"}
    adapter_summary: Dict[str, Any] = {"status": "pending"} if bool(args.adapter_path) else {"status": "skipped_no_adapter"}
    comparison: Dict[str, Any] = {"status": "pending"}
    bench_rows_export: Dict[str, Any] = {"status": "pending"}

    write_json(
        manifest_path,
        {
            "run_id": run_id,
            "run_dir": str(run_dir),
            "storyworld": str(story_path),
            "prompt_count": len(prompts),
            "run_mode": str(args.run_mode),
            "selection_mode": str(args.selection_mode),
            "adapter_only": bool(args.adapter_only),
            "status": "running",
            "baseline_summary": baseline_summary,
            "adapter_summary": adapter_summary,
            "comparison": comparison,
            "bench_rows_export": bench_rows_export,
            "started_at_utc": utc_now(),
        },
    )

    try:
        if not bool(args.adapter_only):
            baseline_runner = None
            if not args.dry_run:
                if str(args.runner_backend) == "api":
                    baseline_runner = ApiRunner(
                        base_url=str(args.api_base_url),
                        model_name=str(args.api_model),
                        api_key=str(args.api_key),
                        system_prompt=str(args.api_system_prompt),
                    )
                else:
                    baseline_runner = HFRunner(
                        model_path=str(args.base_model_path),
                        adapter_path="",
                        device_map=str(args.device_map),
                        dtype=str(args.dtype),
                        load_in_4bit=bool(args.load_in_4bit),
                        bnb_compute_dtype=str(args.bnb_compute_dtype),
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
                    about_char_cap=int(args.about_char_cap),
                    scene_char_cap=int(args.scene_char_cap),
                    max_diary_effects=int(args.max_diary_effects),
                    include_option_text_in_diary=bool(args.include_option_text_in_diary),
                    include_scene_text_in_diary=bool(args.include_scene_text_in_diary),
                    selection_mode=str(args.selection_mode),
                    first_click_mode=str(args.first_click_mode),
                    pick_max_new_tokens=int(args.pick_max_new_tokens),
                    stop_on_cycle=bool(args.stop_on_cycle),
                    max_cycle_repeats=int(args.max_cycle_repeats),
                    max_unique_encounters=int(args.max_unique_encounters),
                    cross_play_memory_mode=str(args.cross_play_memory_mode),
                    cross_play_summary_items=int(args.cross_play_summary_items),
                    start_encounter_id=str(args.start_encounter_id),
                    seed_diary=seed_diary,
                    api_pick_candidate_count=int(args.api_pick_candidate_count),
                    api_pick_candidate_temperature=float(args.api_pick_candidate_temperature),
                    api_pick_candidate_top_p=float(args.api_pick_candidate_top_p),
                    secret_clue_bias=float(args.secret_clue_bias),
                    enable_thinking=bool(args.enable_thinking),
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
                    enable_thinking=bool(args.enable_thinking),
                    dry_run=bool(args.dry_run),
                )

        if args.adapter_path:
            adapter_runner = None if args.dry_run else HFRunner(
                model_path=str(args.base_model_path),
                adapter_path=str(args.adapter_path),
                device_map=str(args.device_map),
                dtype=str(args.dtype),
                load_in_4bit=bool(args.load_in_4bit),
                bnb_compute_dtype=str(args.bnb_compute_dtype),
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
                    about_char_cap=int(args.about_char_cap),
                    scene_char_cap=int(args.scene_char_cap),
                    max_diary_effects=int(args.max_diary_effects),
                    include_option_text_in_diary=bool(args.include_option_text_in_diary),
                    include_scene_text_in_diary=bool(args.include_scene_text_in_diary),
                    selection_mode=str(args.selection_mode),
                    first_click_mode=str(args.first_click_mode),
                    pick_max_new_tokens=int(args.pick_max_new_tokens),
                    stop_on_cycle=bool(args.stop_on_cycle),
                    max_cycle_repeats=int(args.max_cycle_repeats),
                    max_unique_encounters=int(args.max_unique_encounters),
                    cross_play_memory_mode=str(args.cross_play_memory_mode),
                    cross_play_summary_items=int(args.cross_play_summary_items),
                    start_encounter_id=str(args.start_encounter_id),
                    seed_diary=seed_diary,
                    api_pick_candidate_count=int(args.api_pick_candidate_count),
                    api_pick_candidate_temperature=float(args.api_pick_candidate_temperature),
                    api_pick_candidate_top_p=float(args.api_pick_candidate_top_p),
                    secret_clue_bias=float(args.secret_clue_bias),
                    enable_thinking=bool(args.enable_thinking),
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
                    enable_thinking=bool(args.enable_thinking),
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
    except BaseException as exc:
        write_json(
            manifest_path,
            {
                "run_id": run_id,
                "run_dir": str(run_dir),
                "storyworld": str(story_path),
                "prompt_count": len(prompts),
                "run_mode": str(args.run_mode),
                "selection_mode": str(args.selection_mode),
                "adapter_only": bool(args.adapter_only),
                "status": "incomplete",
                "baseline_summary": baseline_summary,
                "adapter_summary": adapter_summary,
                "comparison": {"status": "skipped_incomplete"},
                "bench_rows_export": {"status": "skipped_incomplete"},
                "receipt_status": collect_condition_receipts(
                    run_dir=run_dir,
                    adapter_requested=bool(str(args.adapter_path).strip()),
                    adapter_only=bool(args.adapter_only),
                ),
                "error_type": type(exc).__name__,
                "error": str(exc),
                "finished_at_utc": utc_now(),
            },
        )
        raise

    manifest = {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "storyworld": str(story_path),
        "prompt_count": len(prompts),
        "run_mode": str(args.run_mode),
        "selection_mode": str(args.selection_mode),
        "adapter_only": bool(args.adapter_only),
        "status": "completed",
        "baseline_summary": baseline_summary,
        "adapter_summary": adapter_summary,
        "comparison": comparison,
        "bench_rows_export": bench_rows_export,
        "receipt_status": collect_condition_receipts(
            run_dir=run_dir,
            adapter_requested=bool(str(args.adapter_path).strip()),
            adapter_only=bool(args.adapter_only),
        ),
        "finished_at_utc": utc_now(),
    }
    write_json(manifest_path, manifest)
    print(str(run_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
