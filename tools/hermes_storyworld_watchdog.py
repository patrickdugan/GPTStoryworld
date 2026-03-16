#!/usr/bin/env python3
"""
Recover storyworld JSON blocks from Hermes session files and save versioned outputs.

Typical use:
  python tools/hermes_storyworld_watchdog.py \
    --source-glob ~/.hermes/sessions/session_*.json \
    --out-dir /mnt/c/projects/GPTStoryworld/storyworlds/by-week/2026-W11 \
    --prefix macbeth_storyworld \
    --watch
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import re
import time
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

JSON_FENCE_RE = re.compile(r"```json\s*\n(.*?)\n```", re.DOTALL | re.IGNORECASE)


def load_state(path: Path) -> Dict[str, object]:
    if not path.exists():
        return {"seen_hashes": []}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"seen_hashes": []}


def save_state(path: Path, state: Dict[str, object]) -> None:
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def find_next_version(out_dir: Path, prefix: str) -> int:
    pattern = f"{prefix}_v*.json"
    versions = []
    for p in out_dir.glob(pattern):
        m = re.match(rf"^{re.escape(prefix)}_v(\d+)\.json$", p.name)
        if m:
            versions.append(int(m.group(1)))
    return (max(versions) + 1) if versions else 2


def storyworld_score(obj: Dict[str, object], raw_len: int) -> int:
    keys = set(obj.keys())
    score = raw_len
    if "storyworld_title" in keys:
        score += 10000
    if "encounters" in keys:
        score += 5000
    if "IFID" in keys:
        score += 3000
    if "authored_properties" in keys:
        score += 2000
    return score


def extract_candidates(session_path: Path) -> List[Tuple[int, Dict[str, object], int]]:
    try:
        payload = json.loads(session_path.read_text(encoding="utf-8"))
    except Exception:
        return []
    out = []
    for idx, msg in enumerate(payload.get("messages", [])):
        content = msg.get("content") if isinstance(msg, dict) else None
        if not isinstance(content, str):
            continue
        for block in JSON_FENCE_RE.findall(content):
            block = block.strip()
            try:
                parsed = json.loads(block)
            except Exception:
                continue
            if not isinstance(parsed, dict):
                continue
            if "storyworld_title" not in parsed and "encounters" not in parsed and "IFID" not in parsed:
                continue
            out.append((idx, parsed, len(block)))
    return out


def iter_sessions(source_glob: str) -> Iterable[Path]:
    paths = [Path(p).expanduser() for p in glob.glob(os.path.expanduser(source_glob))]
    return sorted(paths, key=lambda p: p.stat().st_mtime)


def recover_once(
    source_glob: str,
    out_dir: Path,
    prefix: str,
    state_path: Path,
) -> List[Path]:
    state = load_state(state_path)
    seen = set(state.get("seen_hashes", []))
    written: List[Path] = []

    for sess in iter_sessions(source_glob):
        candidates = extract_candidates(sess)
        if not candidates:
            continue
        best = max(candidates, key=lambda row: storyworld_score(row[1], row[2]))
        msg_idx, payload, raw_len = best
        canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
        digest = hashlib.sha256(canonical).hexdigest()
        if digest in seen:
            continue

        version = find_next_version(out_dir, prefix)
        out_json = out_dir / f"{prefix}_v{version}.json"
        out_meta = out_dir / f"{prefix}_v{version}.recovery.txt"
        out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        out_meta.write_text(
            f"source_session={sess}\nmessage_index={msg_idx}\njson_chars={raw_len}\nsha256={digest}\n",
            encoding="utf-8",
        )
        print(f"[recovered] {out_json}")
        written.append(out_json)
        seen.add(digest)

    state["seen_hashes"] = sorted(seen)
    save_state(state_path, state)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description="Recover and version storyworld JSON from Hermes sessions.")
    parser.add_argument("--source-glob", default="~/.hermes/sessions/session_*.json")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--prefix", default="macbeth_storyworld")
    parser.add_argument("--state-file", default=".hermes_storyworld_watchdog_state.json")
    parser.add_argument("--watch", action="store_true")
    parser.add_argument("--poll-seconds", type=float, default=3.0)
    args = parser.parse_args()

    out_dir = Path(args.out_dir).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)
    state_path = out_dir / args.state_file

    if not args.watch:
        recover_once(args.source_glob, out_dir, args.prefix, state_path)
        return 0

    print(f"[watching] {args.source_glob} -> {out_dir}")
    while True:
        recover_once(args.source_glob, out_dir, args.prefix, state_path)
        time.sleep(args.poll_seconds)


if __name__ == "__main__":
    raise SystemExit(main())

