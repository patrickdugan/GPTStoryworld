#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def iter_messages(export_path: Path) -> list[dict[str, Any]]:
    messages: list[dict[str, Any]] = []
    with export_path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            raw_messages = row.get("messages")
            if isinstance(raw_messages, list):
                messages.extend(msg for msg in raw_messages if isinstance(msg, dict))
            elif isinstance(row, dict) and row.get("role"):
                messages.append(row)
    return messages


def message_text(message: dict[str, Any]) -> str:
    content = message.get("content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
            elif isinstance(item, str):
                parts.append(item)
        return "\n".join(parts)
    return ""


def marked_payload(text: str) -> str | None:
    start = "BEGIN_STORYWORLD_PACKET"
    end = "END_STORYWORLD_PACKET"
    if start not in text or end not in text:
        return None
    return text.split(start, 1)[1].split(end, 1)[0].strip()


def first_balanced_json(text: str) -> str:
    start = text.find("{")
    if start < 0:
        raise ValueError("no JSON object start found")
    depth = 0
    in_string = False
    escaped = False
    for index, char in enumerate(text[start:], start=start):
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    raise ValueError("no balanced JSON object found")


def extract_packet(export_path: Path) -> tuple[dict[str, Any], str]:
    assistant_texts = [
        message_text(message)
        for message in iter_messages(export_path)
        if message.get("role") == "assistant"
    ]
    for text in reversed(assistant_texts):
        if not text.strip() or text.strip() == "(empty)":
            continue
        payload = marked_payload(text) or first_balanced_json(text)
        data = json.loads(payload)
        if isinstance(data, dict) and isinstance(data.get("encounters"), list):
            return data, text
    raise ValueError(f"no storyworld packet found in {export_path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract a marked storyworld packet from a Hermes session export.")
    parser.add_argument("session_export", type=Path)
    parser.add_argument("--packet-out", type=Path, required=True)
    parser.add_argument("--assistant-out", type=Path, required=True)
    args = parser.parse_args()

    packet, assistant_text = extract_packet(args.session_export)
    args.packet_out.parent.mkdir(parents=True, exist_ok=True)
    args.assistant_out.parent.mkdir(parents=True, exist_ok=True)
    args.packet_out.write_text(json.dumps(packet, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    args.assistant_out.write_text(assistant_text.strip() + "\n", encoding="utf-8", newline="\n")
    print(args.packet_out)
    print(args.assistant_out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
