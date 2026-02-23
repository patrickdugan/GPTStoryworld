from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List


ORX_LINE_RE = re.compile(r"^ORX\s+[^/]+/[^\s]+\s+->\s+[^|]+\|.+$", re.M)
ENC_RE = re.compile(r"^ENC\s+(\S+)\s+turn=([^\s]+)\s*$", re.M)


def _load_swmd_tools() -> Any:
    module_dir = Path(r"C:\projects\GPTStoryworld\mcp-storyworld-encounter")
    if str(module_dir) not in sys.path:
        sys.path.insert(0, str(module_dir))
    import swmd_store  # type: ignore

    return swmd_store


def _extract_replacement_block(text: str, encounter_id: str) -> str:
    lines = [ln.rstrip() for ln in text.splitlines() if ln.strip()]
    start = -1
    for i, ln in enumerate(lines):
        if ln.startswith(f"ENC {encounter_id} "):
            start = i
            break
    if start < 0:
        return ""
    out = [lines[start]]
    for ln in lines[start + 1 :]:
        if ln.startswith("ENC "):
            break
        if ln.startswith("ORX "):
            out.append(ln)
    if len(out) < 2:
        return ""
    return "\n".join(out)


def _phase_prompt(phase: str, packet: Dict[str, Any], act_label: str) -> str:
    plan = packet["planning_card"]
    poetics = packet.get("mathematical_poetics", {})
    neighbors = packet.get("neighbors", [])
    neighbor_txt = "\n\n".join([f"NEIGHBOR {n['encounter_id']}\n{n['block']}" for n in neighbors])
    target = packet["target_block"]

    if phase == "plan":
        return (
            "You are planning one encounter revision under 8k context constraints.\n"
            "Output JSON only with keys: objective, constraints, risks, checks.\n"
            "No prose wrappers.\n"
            f"ACT={act_label}\nPLAN_CARD\n{json.dumps(plan, ensure_ascii=True)}\n\n"
            f"POETICS\n{json.dumps(poetics, ensure_ascii=True)}\n\n"
            f"TARGET\n{target}\n\n{neighbor_txt}\n"
        )
    if phase in ("characterize", "recharacterize"):
        return (
            "You are producing compact characterization notes for this encounter.\n"
            "Output JSON only with keys: voices, tensions, stance_shift, dialogue_style.\n"
            "No prose wrappers.\n"
            f"ACT={act_label}\nPLAN_CARD\n{json.dumps(plan, ensure_ascii=True)}\n\n"
            f"TARGET\n{target}\n\n{neighbor_txt}\n"
        )
    if phase == "act_complete":
        return (
            "You are auditing act-level coherence for this encounter's act segment.\n"
            "Output JSON only with keys: act_status, continuity_risks, unresolved_threads, next_focus.\n"
            "Include numeric before/after where invariant values are available.\n"
            "No prose wrappers.\n"
            f"ACT={act_label}\nPLAN_CARD\n{json.dumps(plan, ensure_ascii=True)}\n\n"
            f"POETICS\n{json.dumps(poetics, ensure_ascii=True)}\n\n"
            f"TARGET\n{target}\n\n{neighbor_txt}\n"
        )
    if phase in ("encounter_build", "late_stage_holistic"):
        return (
            "You are revising one SWMD-0-MIN encounter block.\n"
            "Output ONLY the revised block.\n"
            "Rules:\n"
            "1) First line must be ENC <same id> turn=<same turn span>\n"
            "2) Keep ORX IDs stable\n"
            "3) Keep consequence semantics consistent\n"
            "4) Include at least one ORX line\n"
            "5) Prefer concise, dialogue-forward lines\n"
            "6) Improve non-repetition and character voice distinctiveness\n\n"
            f"ACT={act_label}\nPLAN_CARD\n{json.dumps(plan, ensure_ascii=True)}\n\n"
            f"POETICS\n{json.dumps(poetics, ensure_ascii=True)}\n\n"
            f"TARGET\n{target}\n\n{neighbor_txt}\n\n"
            "BEGIN_OUTPUT_TEMPLATE\n"
            f"ENC {packet['encounter_id']} turn={packet['turn_span']}\n"
            "ORX "
        )
    raise ValueError(f"unsupported phase: {phase}")


def _load_qlora_examples(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if not path.exists():
        return rows
    for raw in path.read_text(encoding="utf-8").splitlines():
        s = raw.strip()
        if not s:
            continue
        try:
            row = json.loads(s)
        except Exception:
            continue
        if isinstance(row, dict) and "instruction" in row and "output" in row:
            rows.append(row)
    return rows


def _fewshot_snippet(
    examples: List[Dict[str, Any]],
    phase: str,
    encounter_id: str,
    count: int,
    max_chars_each: int = 340,
) -> str:
    if not examples or count <= 0:
        return ""
    # Use compile/compression/repair/edit examples for build-like phases only.
    if phase not in ("encounter_build", "late_stage_holistic"):
        return ""
    salt = sum(ord(ch) for ch in encounter_id) + len(phase) * 17
    start = salt % len(examples)
    picked = [examples[(start + i) % len(examples)] for i in range(min(count, len(examples)))]
    lines = ["FEWSHOT_TRANSFORMS"]
    for i, ex in enumerate(picked, start=1):
        ins = str(ex.get("instruction", ""))[:max_chars_each]
        out = str(ex.get("output", ""))[:max_chars_each]
        lines.append(f"[{i}] INSTRUCTION: {ins}")
        lines.append(f"[{i}] OUTPUT_STYLE: {out}")
    return "\n".join(lines) + "\n"


def _load_model(model_path: Path, adapter_path: Path | None):
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    bnb = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )
    base = AutoModelForCausalLM.from_pretrained(
        str(model_path),
        quantization_config=bnb,
        device_map="auto",
        low_cpu_mem_usage=True,
        torch_dtype=torch.float16,
        local_files_only=True,
        trust_remote_code=True,
    )
    model = PeftModel.from_pretrained(base, str(adapter_path), is_trainable=False) if adapter_path else base
    model.eval()
    tok = AutoTokenizer.from_pretrained(str(model_path), local_files_only=True, trust_remote_code=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    return tok, model


def _generate(tok, model, prompt: str, max_new_tokens: int, temperature: float) -> str:
    import torch

    if hasattr(tok, "apply_chat_template"):
        try:
            rendered = tok.apply_chat_template(
                [{"role": "user", "content": prompt}],
                tokenize=False,
                add_generation_prompt=True,
            )
        except Exception:
            rendered = prompt
    else:
        rendered = prompt
    inputs = tok(rendered, return_tensors="pt", truncation=True, max_length=4096)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=temperature > 0.0,
            temperature=max(0.01, temperature),
            top_p=0.9,
            eos_token_id=tok.eos_token_id,
            pad_token_id=tok.pad_token_id,
        )
    new_tokens = out[0][inputs["input_ids"].shape[1] :]
    return tok.decode(new_tokens, skip_special_tokens=True).strip()


def _act_label(idx: int, total: int) -> str:
    if total <= 0:
        return "act2"
    cut1 = max(1, total // 3)
    cut2 = max(cut1 + 1, (2 * total) // 3)
    if idx < cut1:
        return "act1"
    if idx < cut2:
        return "act2"
    return "act3"


def main() -> int:
    p = argparse.ArgumentParser(description="Phased MCP pipeline for small-model storyworld iteration.")
    p.add_argument("--swmd", type=str, required=True)
    p.add_argument(
        "--model-path",
        type=str,
        default=r"D:\Research_Engine\Qwen_Storyworld\cache\models--Qwen--Qwen2.5-3B-Instruct\snapshots\aa8e72537993ba99e69dfaafa59ed015b17504d1",
    )
    p.add_argument(
        "--adapter-path",
        type=str,
        default=r"D:\Research_Engine\Qwen_Storyworld\adapters\qwen3b-overnight-20260213-071746\checkpoint-79",
    )
    p.add_argument(
        "--phases",
        type=str,
        default="plan,characterize,encounter_build,act_complete,recharacterize,late_stage_holistic",
    )
    p.add_argument("--max-encounters", type=int, default=20)
    p.add_argument("--start-index", type=int, default=0)
    p.add_argument("--neighbor-hops", type=int, default=1)
    p.add_argument("--context-budget-tokens", type=int, default=8192)
    p.add_argument("--reserve-output-tokens", type=int, default=1024)
    p.add_argument("--planning-card-tokens", type=int, default=900)
    p.add_argument("--max-new-tokens", type=int, default=220)
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--out-jsonl", type=str, required=True)
    p.add_argument("--state-json", type=str, required=True)
    p.add_argument("--qlora-examples-jsonl", type=str, default="")
    p.add_argument("--fewshot-count", type=int, default=0)
    p.add_argument("--apply", action="store_true")
    args = p.parse_args()

    phases = [s.strip() for s in args.phases.split(",") if s.strip()]
    swmd_tools = _load_swmd_tools()
    swmd_path = Path(args.swmd)
    doc = swmd_tools.parse_swmd_min(swmd_path)
    ids = doc.encounter_order[args.start_index : args.start_index + args.max_encounters]
    qlora_examples = _load_qlora_examples(Path(args.qlora_examples_jsonl)) if args.qlora_examples_jsonl else []

    tok, model = _load_model(Path(args.model_path), Path(args.adapter_path) if args.adapter_path else None)
    out_path = Path(args.out_jsonl)
    state_path = Path(args.state_json)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.parent.mkdir(parents=True, exist_ok=True)

    state: Dict[str, Dict[str, Any]] = {}
    with out_path.open("w", encoding="utf-8", newline="\n") as handle:
        for phase in phases:
            for i, encounter_id in enumerate(ids):
                packet = swmd_tools.iteration_packet(
                    path=swmd_path,
                    encounter_id=encounter_id,
                    neighbor_hops=args.neighbor_hops if phase != "late_stage_holistic" else max(2, args.neighbor_hops),
                    context_budget_tokens=args.context_budget_tokens,
                    reserve_output_tokens=args.reserve_output_tokens,
                    planning_card_tokens=args.planning_card_tokens,
                    include_poetics=True,
                )
                act = _act_label(i, len(ids))
                prompt = _phase_prompt(phase, packet, act)
                fewshot = _fewshot_snippet(qlora_examples, phase, encounter_id, args.fewshot_count)
                if fewshot:
                    prompt = f"{prompt}\n\n{fewshot}"
                t0 = time.time()
                output = _generate(tok, model, prompt, args.max_new_tokens, args.temperature)
                latency_ms = int((time.time() - t0) * 1000)

                applied = False
                parse_ok = None
                model_parse_ok = None
                fallback_used = False
                replacement = ""
                if phase in ("encounter_build", "late_stage_holistic"):
                    replacement = _extract_replacement_block(output, encounter_id)
                    model_parse_ok = bool(replacement and ORX_LINE_RE.search(replacement))
                    parse_ok = model_parse_ok
                    if not parse_ok:
                        # Keep pipeline stable: fallback to the current target block when raw model output is malformed.
                        replacement = packet["target_block"]
                        parse_ok = bool(ENC_RE.search(replacement) and ORX_LINE_RE.search(replacement))
                        fallback_used = True
                    if args.apply and parse_ok:
                        swmd_tools.apply_encounter_block(swmd_path, encounter_id, replacement)
                        applied = True
                else:
                    state.setdefault(encounter_id, {})[phase] = output[:1800]

                row = {
                    "phase": phase,
                    "encounter_id": encounter_id,
                    "act": act,
                    "latency_ms": latency_ms,
                    "budget": packet["budget"],
                    "prompt_estimated_tokens": packet["budget"]["estimated_tokens_used"],
                    "parse_ok": parse_ok,
                    "model_parse_ok": model_parse_ok,
                    "fallback_used": fallback_used,
                    "applied": applied,
                    "output_preview": (replacement if replacement else output)[:500],
                }
                handle.write(json.dumps(row, ensure_ascii=True) + "\n")
                print(f"phase={phase} id={encounter_id} parse_ok={parse_ok} latency_ms={latency_ms}")

    state_path.write_text(json.dumps(state, ensure_ascii=True, indent=2), encoding="utf-8")
    print(str(out_path))
    print(str(state_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
