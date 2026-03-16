#!/usr/bin/env python3
"""TRM-style storyworld player benchmark: score options and pick top choices."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
import warnings
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def configure_runtime_warnings() -> None:
    # Keep heavy-run logs readable: these are informative but non-fatal in this harness.
    warnings.filterwarnings(
        "ignore",
        message=r".*Torch was not compiled with flash attention.*",
        category=UserWarning,
    )
    warnings.filterwarnings(
        "ignore",
        message=r".*requires 256 bytes of buffer for offloaded layers.*",
        category=UserWarning,
    )
    warnings.filterwarnings(
        "ignore",
        message=r".*copying from a non-meta parameter in the checkpoint to a meta parameter.*",
        category=UserWarning,
    )


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


def _state_snapshot(data: Dict[str, Any]) -> Dict[str, float]:
    props = [
        str(p.get("id", ""))
        for p in data.get("authored_properties", [])
        if str(p.get("id", "")) and int(p.get("depth", 0) or 0) == 0
    ]
    chars = data.get("characters", []) or []
    out: Dict[str, float] = {}
    for pid in props:
        vals: List[float] = []
        for c in chars:
            b = c.get("bnumber_properties", {})
            v = b.get(pid)
            if isinstance(v, (int, float)):
                vals.append(float(v))
        if vals:
            out[pid] = round(sum(vals) / len(vals), 6)
        else:
            out[pid] = 0.0
    return out


@dataclass
class EncounterCard:
    encounter_id: str
    turn_span: str
    encounter_text: str
    context_text: str
    state_snapshot: Dict[str, float]
    options: List[Tuple[str, str]]


def load_storyworld(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_cards(data: Dict[str, Any], max_encounters: int, context_window: int) -> List[EncounterCard]:
    title = str(data.get("storyworld_title", "") or "")
    about = _script_text(data.get("about_text"))
    state = _state_snapshot(data)
    encounters = sorted(
        data.get("encounters", []) or [],
        key=lambda e: (int(e.get("creation_index", 10**9) or 10**9), str(e.get("id", ""))),
    )
    prior: List[str] = []
    cards: List[EncounterCard] = []
    for enc in encounters:
        enc_text = _script_text(enc.get("text_script")).strip()
        enc_id = str(enc.get("id", ""))
        turn_span = f"{enc.get('earliest_turn', '?')}..{enc.get('latest_turn', '?')}"
        opts: List[Tuple[str, str]] = []
        if not _is_terminal(enc):
            for opt in sorted(enc.get("options", []) or [], key=lambda o: str(o.get("id", ""))):
                opt_id = str(opt.get("id", ""))
                opt_text = _script_text(opt.get("text_script")).strip()
                if opt_id and opt_text:
                    opts.append((opt_id, opt_text))
        if opts:
            local = prior[-max(0, context_window) :]
            context_text = (
                f"Storyworld: {title}\n"
                f"About: {about}\n"
                "Prior Story Context:\n"
                + ("\n".join(local) if local else "(none)")
            )
            cards.append(
                EncounterCard(
                    encounter_id=enc_id,
                    turn_span=turn_span,
                    encounter_text=enc_text,
                    context_text=context_text,
                    state_snapshot=state,
                    options=opts,
                )
            )
            if max_encounters > 0 and len(cards) >= max_encounters:
                break
        if enc_text:
            prior.append(f"[{enc_id}] {enc_text}")
    return cards


class OptionScorer:
    def __init__(self, model_path: str, adapter_path: str, device_map: str, dtype: str) -> None:
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

        tok = AutoTokenizer.from_pretrained(self.model_path, use_fast=True)
        model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            dtype=self._resolve_dtype(torch),
            device_map=self.device_map,
            low_cpu_mem_usage=True,
            offload_buffers=True,
        )
        if self.adapter_path:
            from peft import PeftModel  # type: ignore

            offload_dir = Path(__file__).resolve().parent / "out" / "offload"
            offload_dir.mkdir(parents=True, exist_ok=True)
            # Some PEFT/transformers combinations fail resolving offload module keys.
            # Retry a clean reload without offload metadata when that happens.
            try:
                model = PeftModel.from_pretrained(
                    model,
                    self.adapter_path,
                    offload_folder=str(offload_dir),
                    offload_buffers=True,
                )
            except KeyError:
                try:
                    model = AutoModelForCausalLM.from_pretrained(
                        self.model_path,
                        dtype=self._resolve_dtype(torch),
                        device_map=self.device_map,
                        low_cpu_mem_usage=True,
                        offload_buffers=True,
                    )
                    model = PeftModel.from_pretrained(model, self.adapter_path, offload_buffers=True)
                except KeyError:
                    # Final fallback: avoid auto offload/meta init entirely, then attach adapter.
                    model = AutoModelForCausalLM.from_pretrained(
                        self.model_path,
                        dtype=self._resolve_dtype(torch),
                        device_map=None,
                        low_cpu_mem_usage=False,
                    )
                    model = PeftModel.from_pretrained(model, self.adapter_path, offload_buffers=True)
                    if str(self.device_map).lower() != "cpu" and torch.cuda.is_available():
                        model = model.to("cuda")
        model.eval()
        self.model = model
        self.tokenizer = tok

    def score_option(self, prompt: str, option_text: str) -> float:
        """Average log-prob of completion 'Chosen option: <text>' conditioned on prompt."""
        import torch  # type: ignore

        assert self.model is not None and self.tokenizer is not None
        tok = self.tokenizer
        model = self.model
        completion = f"\nChosen option: {option_text}"
        full = prompt + completion

        p_ids = tok(prompt, return_tensors="pt")["input_ids"]
        f = tok(full, return_tensors="pt")
        input_ids = f["input_ids"]
        attn = f["attention_mask"]
        prompt_len = int(p_ids.shape[1])
        total_len = int(input_ids.shape[1])
        if total_len <= prompt_len:
            return -1e9

        device = next(model.parameters()).device
        input_ids = input_ids.to(device)
        attn = attn.to(device)
        with torch.no_grad():
            logits = model(input_ids=input_ids, attention_mask=attn).logits
            logprobs = torch.log_softmax(logits[:, :-1, :], dim=-1)
            target = input_ids[:, 1:]

            start = max(0, prompt_len - 1)
            comp_lp = logprobs[:, start:, :]
            comp_t = target[:, start:]
            gathered = comp_lp.gather(-1, comp_t.unsqueeze(-1)).squeeze(-1)
            mean_lp = float(gathered.mean().item())
        return mean_lp


def _fake_score(enc_id: str, opt_id: str, label: str) -> float:
    h = hashlib.sha256(f"{label}:{enc_id}:{opt_id}".encode("utf-8")).digest()
    v = int.from_bytes(h[:4], "big") / 2**32
    return -2.5 + (v * 1.5)


def _build_prompt(card: EncounterCard) -> str:
    opts = "\n".join([f"- {oid}: {otxt}" for oid, otxt in card.options])
    return (
        f"{card.context_text}\n\n"
        f"Encounter ID: {card.encounter_id}\n"
        f"Turn Span: {card.turn_span}\n"
        "State Snapshot:\n"
        f"{json.dumps(card.state_snapshot, ensure_ascii=True)}\n\n"
        "Encounter Text:\n"
        f"{card.encounter_text}\n\n"
        "Available Options:\n"
        f"{opts}\n"
    )


def run_condition(
    label: str,
    cards: List[EncounterCard],
    out_dir: Path,
    scorer: Optional[OptionScorer],
    top_k: int,
    dry_run: bool,
) -> Dict[str, Any]:
    ensure_dir(out_dir)
    rows: List[Dict[str, Any]] = []
    t0 = time.time()
    for card in cards:
        prompt = _build_prompt(card)
        st = time.time()
        scored: List[Dict[str, Any]] = []
        for opt_id, opt_text in card.options:
            if dry_run:
                score = _fake_score(card.encounter_id, opt_id, label)
            else:
                assert scorer is not None
                score = scorer.score_option(prompt, opt_text)
            scored.append({"option_id": opt_id, "option_text": opt_text, "score": float(score)})
        ranked = sorted(scored, key=lambda x: x["score"], reverse=True)
        chosen = ranked[0] if ranked else {"option_id": "", "option_text": "", "score": -1e9}
        rows.append(
            {
                "model_label": label,
                "encounter_id": card.encounter_id,
                "turn_span": card.turn_span,
                "prompt_text": prompt,
                "chosen_option_id": chosen["option_id"],
                "chosen_option_text": chosen["option_text"],
                "chosen_score": chosen["score"],
                "top_k": ranked[: max(1, top_k)],
                "num_options": len(card.options),
                "latency_sec": round(time.time() - st, 4),
                "timestamp_utc": utc_now(),
            }
        )

    choice_diversity = len({r["chosen_option_id"] for r in rows}) if rows else 0
    summary = {
        "model_label": label,
        "num_encounters": len(rows),
        "avg_options_per_encounter": (sum(int(r["num_options"]) for r in rows) / len(rows)) if rows else 0.0,
        "avg_latency_sec": (sum(float(r["latency_sec"]) for r in rows) / len(rows)) if rows else 0.0,
        "choice_diversity_count": choice_diversity,
        "wall_time_sec": round(time.time() - t0, 3),
    }
    write_jsonl(out_dir / "decisions.jsonl", rows)
    write_json(out_dir / "summary.json", summary)
    return summary


def compare_conditions(run_dir: Path, baseline_dir: Path, adapter_dir: Path) -> Dict[str, Any]:
    b_path = baseline_dir / "decisions.jsonl"
    a_path = adapter_dir / "decisions.jsonl"
    if (not b_path.exists()) or (not a_path.exists()):
        return {"status": "missing_condition_outputs"}
    b_rows = [json.loads(x) for x in b_path.read_text(encoding="utf-8").splitlines() if x.strip()]
    a_rows = [json.loads(x) for x in a_path.read_text(encoding="utf-8").splitlines() if x.strip()]
    b_by = {r["encounter_id"]: r for r in b_rows}
    a_by = {r["encounter_id"]: r for r in a_rows}
    shared = sorted(set(b_by.keys()) & set(a_by.keys()))
    agree = 0
    score_delta: List[float] = []
    for eid in shared:
        br = b_by[eid]
        ar = a_by[eid]
        if br.get("chosen_option_id") == ar.get("chosen_option_id"):
            agree += 1
        score_delta.append(float(ar.get("chosen_score", 0.0)) - float(br.get("chosen_score", 0.0)))
    out = {
        "shared_encounters": len(shared),
        "top1_agreement_count": agree,
        "top1_agreement_rate": (agree / len(shared)) if shared else 0.0,
        "avg_chosen_score_delta_adapter_minus_baseline": (sum(score_delta) / len(score_delta)) if score_delta else 0.0,
        "timestamp_utc": utc_now(),
    }
    write_json(run_dir / "comparisons" / "comparison_summary.json", out)
    return out


def export_bench_rows(run_dir: Path, baseline_dir: Path, adapter_dir: Path) -> Dict[str, Any]:
    b_path = baseline_dir / "decisions.jsonl"
    a_path = adapter_dir / "decisions.jsonl"
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
                "prompt_text": br.get("prompt_text", ""),
                "baseline": {
                    "model_label": br.get("model_label", "baseline_qwen_1_7b_trm"),
                    "chosen_option_id": br.get("chosen_option_id", ""),
                    "chosen_option_text": br.get("chosen_option_text", ""),
                    "chosen_score": float(br.get("chosen_score", 0.0)),
                    "top_k": br.get("top_k", []),
                },
                "adapter": {
                    "model_label": ar.get("model_label", "adapter_claude_constitution_qlora_trm"),
                    "chosen_option_id": ar.get("chosen_option_id", ""),
                    "chosen_option_text": ar.get("chosen_option_text", ""),
                    "chosen_score": float(ar.get("chosen_score", 0.0)),
                    "top_k": ar.get("top_k", []),
                },
                "top1_same": br.get("chosen_option_id") == ar.get("chosen_option_id"),
                "chosen_score_delta_adapter_minus_baseline": float(ar.get("chosen_score", 0.0))
                - float(br.get("chosen_score", 0.0)),
                "timestamp_utc": utc_now(),
            }
        )
    out_path = run_dir / "comparisons" / "bench_rows.jsonl"
    write_jsonl(out_path, out_rows)
    return {"status": "ok", "rows": len(out_rows), "path": str(out_path)}


def main() -> int:
    configure_runtime_warnings()
    ap = argparse.ArgumentParser(description="TRM-style option ranking benchmark over storyworld encounters.")
    ap.add_argument("--storyworld", required=True)
    ap.add_argument("--base-model-path", required=True)
    ap.add_argument("--adapter-path", default="")
    ap.add_argument("--output-root", default=r"D:\Research_Engine\Storyworld_LLM_Plays")
    ap.add_argument("--run-id", default="")
    ap.add_argument("--max-encounters", type=int, default=0)
    ap.add_argument("--context-window", type=int, default=4)
    ap.add_argument("--top-k", type=int, default=3)
    ap.add_argument("--device-map", default="auto")
    ap.add_argument("--dtype", choices=["auto", "float16", "bfloat16", "float32"], default="auto")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    story_path = Path(args.storyworld).resolve()
    data = load_storyworld(story_path)
    cards = build_cards(data, max_encounters=int(args.max_encounters), context_window=int(args.context_window))
    if not cards:
        raise SystemExit("No encounter cards found with options.")

    run_id = args.run_id.strip() or f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{story_path.stem}_trm_player"
    run_dir = Path(args.output_root).resolve() / run_id
    ensure_dir(run_dir / "meta")
    ensure_dir(run_dir / "prompts")
    write_json(
        run_dir / "meta" / "run_config.json",
        {
            "started_at_utc": utc_now(),
            "storyworld": str(story_path),
            "base_model_path": args.base_model_path,
            "adapter_path": args.adapter_path,
            "max_encounters": int(args.max_encounters),
            "context_window": int(args.context_window),
            "top_k": int(args.top_k),
            "device_map": str(args.device_map),
            "dtype": str(args.dtype),
            "dry_run": bool(args.dry_run),
            "hostname": os.environ.get("COMPUTERNAME", ""),
        },
    )
    write_jsonl(
        run_dir / "prompts" / "encounter_cards.jsonl",
        [
            {
                "encounter_id": c.encounter_id,
                "turn_span": c.turn_span,
                "encounter_text": c.encounter_text,
                "context_text": c.context_text,
                "state_snapshot": c.state_snapshot,
                "options": [{"option_id": oid, "option_text": otxt} for oid, otxt in c.options],
            }
            for c in cards
        ],
    )

    baseline_scorer = None if args.dry_run else OptionScorer(
        model_path=str(args.base_model_path),
        adapter_path="",
        device_map=str(args.device_map),
        dtype=str(args.dtype),
    )
    baseline_summary = run_condition(
        label="baseline_qwen_1_7b_trm",
        cards=cards,
        out_dir=run_dir / "baseline_qwen_1_7b_trm",
        scorer=baseline_scorer,
        top_k=int(args.top_k),
        dry_run=bool(args.dry_run),
    )

    adapter_summary: Dict[str, Any] = {"status": "skipped_no_adapter"}
    if args.adapter_path:
        adapter_scorer = None if args.dry_run else OptionScorer(
            model_path=str(args.base_model_path),
            adapter_path=str(args.adapter_path),
            device_map=str(args.device_map),
            dtype=str(args.dtype),
        )
        adapter_summary = run_condition(
            label="adapter_claude_constitution_qlora_trm",
            cards=cards,
            out_dir=run_dir / "adapter_claude_constitution_qlora_trm",
            scorer=adapter_scorer,
            top_k=int(args.top_k),
            dry_run=bool(args.dry_run),
        )

    comparison = compare_conditions(
        run_dir=run_dir,
        baseline_dir=run_dir / "baseline_qwen_1_7b_trm",
        adapter_dir=run_dir / "adapter_claude_constitution_qlora_trm",
    )
    bench_rows_export = export_bench_rows(
        run_dir=run_dir,
        baseline_dir=run_dir / "baseline_qwen_1_7b_trm",
        adapter_dir=run_dir / "adapter_claude_constitution_qlora_trm",
    )
    manifest = {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "storyworld": str(story_path),
        "encounter_count": len(cards),
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
