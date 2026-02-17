from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List


ENC_LINE_RE = re.compile(r"^ENC\s+(\S+)\s+turn=([^\s]+)\s*$", re.M)
ORX_LINE_RE = re.compile(r"^ORX\s+[^/]+/[^\s]+\s+->\s+[^|]+\|.+$", re.M)


def _load_swmd_tools() -> Any:
    module_dir = Path(r"C:\projects\GPTStoryworld\mcp-storyworld-encounter")
    if str(module_dir) not in sys.path:
        sys.path.insert(0, str(module_dir))
    import swmd_store  # type: ignore

    return swmd_store


def _extract_replacement_block(text: str, encounter_id: str) -> str:
    lines = [ln.rstrip() for ln in text.splitlines() if ln.strip()]
    start_idx = -1
    for i, ln in enumerate(lines):
        if ln.startswith(f"ENC {encounter_id} "):
            start_idx = i
            break
    if start_idx < 0:
        return ""
    out = [lines[start_idx]]
    for ln in lines[start_idx + 1 :]:
        if ln.startswith("ENC "):
            break
        if ln.startswith("ORX "):
            out.append(ln)
    if len(out) < 2:
        return ""
    return "\n".join(out)


def _build_prompt(packet: Dict[str, Any]) -> str:
    plan = packet["planning_card"]
    poetics = packet.get("mathematical_poetics", {})
    neighbors = packet.get("neighbors", [])
    neighbor_txt = "\n\n".join([f"NEIGHBOR {n['encounter_id']}\n{n['block']}" for n in neighbors])
    return (
        "You are revising one SWMD-0-MIN encounter block under tight context budget.\n"
        "Output ONLY the revised block.\n"
        "Rules:\n"
        "1) First line must be ENC <same id> turn=<same turn span>\n"
        "2) Keep existing ORX ids stable\n"
        "3) Keep consequence links valid\n"
        "4) Include at least one ORX line\n"
        "5) Prefer concise dialogue-forward phrasing\n\n"
        f"PLAN_CARD\n{json.dumps(plan, ensure_ascii=True)}\n\n"
        f"POETICS\n{json.dumps(poetics, ensure_ascii=True)}\n\n"
        f"TARGET\n{packet['target_block']}\n\n"
        f"{neighbor_txt}\n\n"
        "BEGIN_OUTPUT_TEMPLATE\n"
        f"ENC {packet['encounter_id']} turn={packet['turn_span']}\n"
        "ORX "
    )


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


def main() -> int:
    p = argparse.ArgumentParser(description="Budgeted 8k MCP iteration loop for SWMD encounters.")
    p.add_argument("--swmd", type=str, required=True)
    p.add_argument("--model-path", type=str, required=True)
    p.add_argument("--adapter-path", type=str, default="")
    p.add_argument("--max-encounters", type=int, default=8)
    p.add_argument("--start-index", type=int, default=0)
    p.add_argument("--neighbor-hops", type=int, default=1)
    p.add_argument("--context-budget-tokens", type=int, default=8192)
    p.add_argument("--reserve-output-tokens", type=int, default=1024)
    p.add_argument("--planning-card-tokens", type=int, default=900)
    p.add_argument("--max-new-tokens", type=int, default=220)
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--out-jsonl", type=str, required=True)
    p.add_argument("--apply", action="store_true")
    args = p.parse_args()

    swmd_tools = _load_swmd_tools()
    swmd_path = Path(args.swmd)
    doc = swmd_tools.parse_swmd_min(swmd_path)
    all_ids = doc.encounter_order
    selected = all_ids[args.start_index : args.start_index + args.max_encounters]

    tok, model = _load_model(Path(args.model_path), Path(args.adapter_path) if args.adapter_path else None)
    out_path = Path(args.out_jsonl)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", encoding="utf-8", newline="\n") as handle:
        for encounter_id in selected:
            packet = swmd_tools.iteration_packet(
                path=swmd_path,
                encounter_id=encounter_id,
                neighbor_hops=args.neighbor_hops,
                context_budget_tokens=args.context_budget_tokens,
                reserve_output_tokens=args.reserve_output_tokens,
                planning_card_tokens=args.planning_card_tokens,
                include_poetics=True,
            )
            prompt = _build_prompt(packet)
            t0 = time.time()
            output = _generate(tok, model, prompt, args.max_new_tokens, args.temperature)
            ms = int((time.time() - t0) * 1000)
            replacement = _extract_replacement_block(output, encounter_id)
            model_parse_ok = bool(replacement and ORX_LINE_RE.search(replacement))
            parse_ok = model_parse_ok
            fallback_used = False
            if not parse_ok:
                replacement = packet["target_block"]
                parse_ok = bool(ENC_LINE_RE.search(replacement) and ORX_LINE_RE.search(replacement))
                fallback_used = True
            if args.apply and parse_ok:
                swmd_tools.apply_encounter_block(swmd_path, encounter_id, replacement)
            row = {
                "encounter_id": encounter_id,
                "latency_ms": ms,
                "budget": packet["budget"],
                "prompt_estimated_tokens": packet["budget"]["estimated_tokens_used"],
                "parse_ok": parse_ok,
                "model_parse_ok": model_parse_ok,
                "fallback_used": fallback_used,
                "applied": bool(args.apply and parse_ok),
                "replacement_preview": replacement[:400],
            }
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")
            print(f"ok={parse_ok} id={encounter_id} latency_ms={ms}")

    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
