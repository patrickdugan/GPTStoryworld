from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Tuple

ENC_RE = re.compile(r"^ENC\s+(\S+)\s+turn=([^\s]+)\s*$")
ORX_RE = re.compile(r"^ORX\s+([^/]+)/([^\s]+)\s+->\s+([^|]+)\|(.+)$")


@dataclass
class Reaction:
    rxn_id: str
    consequence: str
    option_text: str
    effects: str
    desirability: str


@dataclass
class EncounterCard:
    encounter_id: str
    turn_span: str
    block_lines: List[str] = field(default_factory=list)
    reactions: List[Reaction] = field(default_factory=list)


@dataclass
class WorldDoc:
    world_id: str
    title: str
    encounters: Dict[str, EncounterCard]
    frontmatter: Dict[str, Any] = field(default_factory=dict)


def _split_frontmatter(text: str) -> Tuple[Dict[str, Any], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}, text
    fm_lines = lines[1:end]
    body = "\n".join(lines[end + 1 :])
    meta: Dict[str, Any] = {}
    current_key = ""
    for raw in fm_lines:
        s = raw.rstrip()
        if not s.strip():
            continue
        m_top = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", s.strip())
        if m_top and not s.startswith(" "):
            key = m_top.group(1)
            val = m_top.group(2).strip()
            current_key = key
            if val:
                meta[key] = val.strip('"')
            else:
                meta[key] = []
            continue
        if current_key and s.strip().startswith("- "):
            arr = meta.get(current_key)
            if isinstance(arr, list):
                arr.append(s.strip()[2:].strip().strip('"'))
    endings: List[Dict[str, str]] = []
    pending: Dict[str, str] = {}
    for raw in fm_lines:
        s = raw.rstrip()
        m_id = re.match(r'^\s*-\s+id:\s*"?(.+?)"?\s*$', s)
        if m_id:
            if pending:
                endings.append(pending)
            pending = {"id": m_id.group(1)}
            continue
        m_attr = re.match(r'^\s+([A-Za-z0-9_]+):\s*"?(.+?)"?\s*$', s)
        if m_attr and pending:
            pending[m_attr.group(1)] = m_attr.group(2)
    if pending:
        endings.append(pending)
    if endings:
        meta["endings"] = endings
    return meta, body


def parse_swmd_min(path: Path) -> WorldDoc:
    world_id = "unknown"
    title = "SWMD"
    encounters: Dict[str, EncounterCard] = {}
    current: EncounterCard | None = None

    frontmatter, body = _split_frontmatter(path.read_text(encoding="utf-8"))
    if isinstance(frontmatter.get("storyworld_id"), str):
        world_id = str(frontmatter["storyworld_id"])
    if isinstance(frontmatter.get("title"), str):
        title = str(frontmatter["title"])

    for raw in body.splitlines():
        row = raw.rstrip("\n")
        s = row.strip()
        if not s:
            continue
        if s.startswith("id:"):
            world_id = s.split(":", 1)[1].strip()
            continue
        if s.startswith("title:"):
            title = s.split(":", 1)[1].strip()
            continue
        m_enc = ENC_RE.match(s)
        if m_enc:
            current = EncounterCard(encounter_id=m_enc.group(1), turn_span=m_enc.group(2), block_lines=[s])
            encounters[current.encounter_id] = current
            continue
        if current is None:
            continue
        m_orx = ORX_RE.match(s)
        if m_orx:
            option_text = ""
            effects = ""
            desirability = "C(0)"
            payload = m_orx.group(4)
            for token in payload.split("|"):
                part = token.strip()
                if ":" not in part:
                    continue
                k, v = part.split(":", 1)
                key = k.strip()
                value = v.strip()
                if key == "O":
                    option_text = value
                elif key == "E":
                    effects = value
                elif key == "D":
                    desirability = value
            current.reactions.append(
                Reaction(
                    rxn_id=m_orx.group(2).strip(),
                    consequence=m_orx.group(3).strip(),
                    option_text=option_text,
                    effects=effects,
                    desirability=desirability,
                )
            )
            current.block_lines.append(s)

    return WorldDoc(world_id=world_id, title=title, encounters=encounters, frontmatter=frontmatter)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build encounter index for SWMD-0-MIN files.")
    parser.add_argument("--swmd", type=str, required=True)
    parser.add_argument("--out-dir", type=str, required=True)
    args = parser.parse_args()

    swmd = Path(args.swmd)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    world = parse_swmd_min(swmd)

    world_card = out_dir / "world_card.txt"
    world_card.write_text(
        f"world_id: {world.world_id}\n"
        f"title: {world.title}\n"
        f"encounter_count: {len(world.encounters)}\n"
        f"terminal_endings_count: {len(world.frontmatter.get('endings', []))}\n"
        f"terminal_endings: {','.join(str(e.get('id', '')) for e in world.frontmatter.get('endings', []))}\n"
        "contract: revise one encounter at a time; keep IDs stable; keep syntax SWMD-0-MIN compatible.\n",
        encoding="utf-8",
    )

    rows_path = out_dir / "encounters.jsonl"
    with rows_path.open("w", encoding="utf-8", newline="\n") as handle:
        for encounter_id in sorted(world.encounters.keys()):
            card = world.encounters[encounter_id]
            reaction_count = len(card.reactions)
            unique_targets = sorted({r.consequence for r in card.reactions})
            option_labels = sorted({r.option_text for r in card.reactions if r.option_text})
            row = {
                "encounter_id": encounter_id,
                "turn_span": card.turn_span,
                "reaction_count": reaction_count,
                "option_labels": option_labels,
                "consequences": unique_targets,
                "block": "\n".join(card.block_lines),
            }
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")

    print(f"ok: wrote {rows_path}")
    print(f"ok: wrote {world_card}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
