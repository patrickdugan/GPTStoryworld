from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Dict, List

import requests


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            s = line.strip()
            if s:
                rows.append(json.loads(s))
    return rows


def clamp_text(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit]


def build_prompt(world_card: str, encounter_row: Dict[str, Any], neighbor_rows: List[Dict[str, Any]], max_input_chars: int) -> str:
    neighbor_blocks = "\n\n".join(
        f"NEIGHBOR {row['encounter_id']}\n{row['block']}" for row in neighbor_rows
    )
    instruction = (
        "You are revising exactly one SWMD-0-MIN encounter block.\n"
        "Rules:\n"
        "1) Keep ENC id identical.\n"
        "2) Keep ORX option/reaction IDs stable unless malformed.\n"
        "3) Output ONLY the revised block, starting with ENC ... and ORX lines below.\n"
        "4) Include at least one ORX line.\n"
        "5) Keep style compact and deterministic.\n"
    )
    main_block = f"TARGET {encounter_row['encounter_id']}\n{encounter_row['block']}"
    payload = (
        f"{instruction}\n"
        f"WORLD_CARD\n{world_card}\n\n"
        f"{main_block}\n\n"
        f"{neighbor_blocks}\n"
        f"\nBEGIN_OUTPUT_TEMPLATE\nENC {encounter_row['encounter_id']} turn={encounter_row['turn_span']}\nORX "
    )
    return clamp_text(payload, max_input_chars)


def call_chat(base_url: str, model: str, prompt: str, max_output_tokens: int, temperature: float) -> str:
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Return only SWMD-0-MIN encounter block text."},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_output_tokens,
        "temperature": temperature,
    }
    response = requests.post(base_url, json=body, timeout=180)
    response.raise_for_status()
    data = response.json()
    choices = data.get("choices") or []
    if not choices:
        raise RuntimeError(f"no choices in response: {data}")
    message = choices[0].get("message") or {}
    content = message.get("content")
    if not isinstance(content, str):
        raise RuntimeError(f"unexpected response payload: {data}")
    return content.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run per-encounter MCP-style generation pass using a chat endpoint.")
    parser.add_argument("--swmd", type=str, required=True)
    parser.add_argument("--index", type=str, required=True)
    parser.add_argument("--base-url", type=str, default="http://127.0.0.1:8080/v1/chat/completions")
    parser.add_argument("--model", type=str, default="nanbeige-3b-f16")
    parser.add_argument("--max-input-chars", type=int, default=26000)
    parser.add_argument("--max-output-tokens", type=int, default=1200)
    parser.add_argument("--temperature", type=float, default=0.3)
    parser.add_argument("--encounter-id", type=str, default="")
    parser.add_argument("--max-encounters", type=int, default=0)
    parser.add_argument("--out", type=str, default="")
    args = parser.parse_args()

    swmd_path = Path(args.swmd)
    index_rows = load_jsonl(Path(args.index))
    world_card_path = Path(args.index).with_name("world_card.txt")
    world_card = world_card_path.read_text(encoding="utf-8") if world_card_path.exists() else ""

    if args.encounter_id:
        index_rows = [r for r in index_rows if r.get("encounter_id") == args.encounter_id]

    if args.max_encounters > 0:
        index_rows = index_rows[: args.max_encounters]

    out_path = Path(args.out) if args.out else swmd_path.parent / f"{swmd_path.stem}.encounter_pass.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", encoding="utf-8", newline="\n") as handle:
        for idx, row in enumerate(index_rows):
            neighbors: List[Dict[str, Any]] = []
            if idx > 0:
                neighbors.append(index_rows[idx - 1])
            if idx + 1 < len(index_rows):
                neighbors.append(index_rows[idx + 1])

            prompt = build_prompt(world_card, row, neighbors, args.max_input_chars)
            started = time.time()
            revised = call_chat(args.base_url, args.model, prompt, args.max_output_tokens, args.temperature)
            elapsed_ms = int((time.time() - started) * 1000)
            lines = [ln.strip() for ln in revised.splitlines() if ln.strip()]
            model_parse_ok = bool(lines and lines[0].startswith(f"ENC {row['encounter_id']} ") and any(ln.startswith("ORX ") for ln in lines))
            fallback_used = False
            final_block = revised
            if not model_parse_ok:
                final_block = row["block"]
                fallback_used = True

            log_row = {
                "encounter_id": row["encounter_id"],
                "input_chars": len(prompt),
                "output_chars": len(revised),
                "latency_ms": elapsed_ms,
                "model_parse_ok": model_parse_ok,
                "fallback_used": fallback_used,
                "revised_block": final_block,
            }
            handle.write(json.dumps(log_row, ensure_ascii=True) + "\n")
            print(f"ok: {row['encounter_id']} ({elapsed_ms} ms) model_parse_ok={model_parse_ok} fallback_used={fallback_used}")

    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
