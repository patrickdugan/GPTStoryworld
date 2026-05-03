#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def first_nonempty(packets: list[dict[str, Any]], key: str, fallback: Any) -> Any:
    for packet in packets:
        value = packet.get(key)
        if value:
            return value
    return fallback


def main() -> int:
    parser = argparse.ArgumentParser(description="Combine chunked Hermes storyworld packets into one packet.")
    parser.add_argument("packets", nargs="+", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    packets = [read_json(path) for path in args.packets]
    encounters: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for packet in packets:
        for encounter in packet.get("encounters", []):
            if not isinstance(encounter, dict):
                continue
            encounter_id = str(encounter.get("id") or f"encounter_{len(encounters) + 1}")
            if encounter_id in seen_ids:
                encounter = dict(encounter)
                encounter["id"] = f"{encounter_id}_{len(encounters) + 1}"
            seen_ids.add(str(encounter["id"]))
            encounters.append(encounter)

    combined = {
        "title": first_nonempty(packets, "title", "Hermes Chunked Storyworld"),
        "subtitle": first_nonempty(packets, "subtitle", ""),
        "about": first_nonempty(packets, "about", ""),
        "characters": first_nonempty(packets, "characters", []),
        "variables": first_nonempty(packets, "variables", []),
        "encounters": encounters,
        "final_encounter": first_nonempty(packets, "final_encounter", {}),
        "secret_bridge": first_nonempty(packets, "secret_bridge", {}),
        "endings": first_nonempty(packets, "endings", []),
        "source_chunks": [str(path) for path in args.packets],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(combined, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    print(args.out)
    print(f"encounters={len(encounters)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
