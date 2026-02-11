#!/usr/bin/env python3
"""Review storyworld screenshots with OpenAI vision models."""

from __future__ import annotations

import argparse
import base64
import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List


def _read_key(explicit: str | None) -> str:
    if explicit:
        return Path(explicit).read_text(encoding="utf-8").strip()
    env_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if env_key:
        return env_key
    desktop = Path.home() / "Desktop" / "GPTAPI.txt"
    if desktop.exists():
        return desktop.read_text(encoding="utf-8").strip()
    raise FileNotFoundError("No API key found. Set OPENAI_API_KEY or provide --api-key-file.")


def _img_to_data_url(path: Path) -> str:
    suffix = path.suffix.lower()
    mime = "image/png" if suffix == ".png" else "image/jpeg"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def _extract_text(resp: Dict[str, Any]) -> str:
    if "output_text" in resp and resp["output_text"]:
        return str(resp["output_text"])
    out = []
    for item in resp.get("output", []):
        for c in item.get("content", []):
            if c.get("type") == "output_text":
                out.append(c.get("text", ""))
    return "\n".join(out).strip()


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="OpenAI vision review for storyworld screenshots.")
    p.add_argument("--images", nargs="+", required=True, help="PNG/JPG screenshot paths")
    p.add_argument("--out", required=True, help="Output JSON report")
    p.add_argument("--api-key-file", default="", help="Optional API key file path")
    p.add_argument("--model", default="gpt-4.1-mini", help="Vision-capable model")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    key = _read_key(args.api_key_file if args.api_key_file else None)
    image_paths = [Path(p).resolve() for p in args.images]

    prompt = (
        "You are auditing storyworld UI quality and narrative craftsmanship.\n"
        "Score 1-10 for: visual clarity, narrative atmosphere, choice legibility, stats readability, and perceived narrative depth.\n"
        "Then provide:\n"
        "1) Top 5 concrete improvements\n"
        "2) Any UI defects seen\n"
        "3) Whether this feels publish-ready for a premium storyworld demo\n"
    )

    content: List[Dict[str, Any]] = [{"type": "input_text", "text": prompt}]
    for p in image_paths:
        content.append({"type": "input_image", "image_url": _img_to_data_url(p)})

    payload = {
        "model": args.model,
        "input": [{"role": "user", "content": content}],
        "max_output_tokens": 900,
    }
    body = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"OpenAI API error: HTTP {exc.code} {detail}") from exc

    parsed = json.loads(raw)
    report = {
        "model": args.model,
        "images": [str(p) for p in image_paths],
        "review_text": _extract_text(parsed),
        "raw_response": parsed,
    }

    out_path = Path(args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
