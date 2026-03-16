#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import urllib.request
from pathlib import Path
from typing import Dict, List, Tuple

WORKS: Dict[str, Dict[str, str]] = {
    "house_of_mirth": {"gutenberg_id": "284", "title": "The House of Mirth", "author": "Edith Wharton"},
    "age_of_innocence": {"gutenberg_id": "541", "title": "The Age of Innocence", "author": "Edith Wharton"},
    "ethan_frome": {"gutenberg_id": "4517", "title": "Ethan Frome", "author": "Edith Wharton"},
    "turn_of_screw": {"gutenberg_id": "209", "title": "The Turn of the Screw", "author": "Henry James"},
    "jekyll_hyde": {"gutenberg_id": "43", "title": "Strange Case of Dr Jekyll and Mr Hyde", "author": "Robert Louis Stevenson"},
    "dorian_gray": {"gutenberg_id": "174", "title": "The Picture of Dorian Gray", "author": "Oscar Wilde"},
    "yellow_wallpaper": {"gutenberg_id": "1952", "title": "The Yellow Wallpaper", "author": "Charlotte Perkins Gilman"},
    "bleak_house": {"gutenberg_id": "1023", "title": "Bleak House", "author": "Charles Dickens"},
    "bartleby": {"gutenberg_id": "11231", "title": "Bartleby, the Scrivener", "author": "Herman Melville"},
    "jude_obscure": {"gutenberg_id": "153", "title": "Jude the Obscure", "author": "Thomas Hardy"},
    "robinson_crusoe": {"gutenberg_id": "521", "title": "Robinson Crusoe", "author": "Daniel Defoe"},
    "treasure_island": {"gutenberg_id": "120", "title": "Treasure Island", "author": "Robert Louis Stevenson"},
    "call_of_wild": {"gutenberg_id": "215", "title": "The Call of the Wild", "author": "Jack London"},
    "mysterious_island": {"gutenberg_id": "1268", "title": "The Mysterious Island", "author": "Jules Verne"},
    "jane_eyre": {"gutenberg_id": "1260", "title": "Jane Eyre", "author": "Charlotte Bronte"},
    "wuthering_heights": {"gutenberg_id": "768", "title": "Wuthering Heights", "author": "Emily Bronte"},
    "anna_karenina": {"gutenberg_id": "1399", "title": "Anna Karenina", "author": "Leo Tolstoy"},
    "madame_bovary": {"gutenberg_id": "2413", "title": "Madame Bovary", "author": "Gustave Flaubert"},
    "dracula": {"gutenberg_id": "345", "title": "Dracula", "author": "Bram Stoker"},
    "great_expectations": {"gutenberg_id": "1400", "title": "Great Expectations", "author": "Charles Dickens"},
}


def normalize_space(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def fetch_gutenberg_text(gid: str) -> str:
    candidates = [
        f"https://www.gutenberg.org/files/{gid}/{gid}-0.txt",
        f"https://www.gutenberg.org/files/{gid}/{gid}.txt",
        f"https://www.gutenberg.org/cache/epub/{gid}/pg{gid}.txt",
    ]
    last_err = None
    for url in candidates:
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                data = resp.read().decode("utf-8", errors="replace")
                if data and len(data) > 1000:
                    return data
        except Exception as exc:  # noqa: BLE001
            last_err = exc
    raise RuntimeError(f"Failed to fetch Gutenberg id {gid}: {last_err}")


def strip_boilerplate(text: str) -> str:
    start_match = re.search(r"\*\*\*\s*START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK[^\n]*\*\*\*", text, flags=re.IGNORECASE)
    end_match = re.search(r"\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK[^\n]*\*\*\*", text, flags=re.IGNORECASE)
    start = start_match.end() if start_match else 0
    end = end_match.start() if end_match else len(text)
    return text[start:end]


def paragraph_pool(text: str) -> List[str]:
    clean = strip_boilerplate(text)
    paras_raw = re.split(r"\n\s*\n+", clean)
    out: List[str] = []
    for p in paras_raw:
        p2 = normalize_space(p)
        if len(p2) < 120:
            continue
        low = p2.lower()
        if "project gutenberg" in low or "ebook" in low:
            continue
        if re.fullmatch(r"[ivxlcdm\-\s\.]+", low):
            continue
        out.append(p2)
    if not out:
        raise RuntimeError("No usable paragraphs extracted")
    return out


def shorten_excerpt(text: str, limit: int = 220) -> str:
    t = normalize_space(text).strip('"')
    if len(t) <= limit:
        return t
    cut = t[:limit]
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    return cut + "..."


def pick_excerpt(paras: List[str], seed: str) -> Tuple[str, int]:
    h = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    idx = int(h[:12], 16) % len(paras)
    return paras[idx], idx


def detect_slug(filename: str) -> str:
    m = re.match(r"^pd_(.+?)_multiending_v\d+\.json$", filename)
    if not m:
        raise ValueError(f"Cannot detect slug from {filename}")
    return m.group(1)


def inject_world(path: Path, paras: List[str], meta: Dict[str, str]) -> Dict[str, object]:
    doc = json.loads(path.read_text(encoding="utf-8"))
    encounters = doc.get("encounters", [])
    manifest_entries = []
    gid = meta["gutenberg_id"]
    source_url = f"https://www.gutenberg.org/ebooks/{gid}"

    for enc in encounters:
        enc_id = enc.get("id", "unknown")
        seed = f"{path.stem}:{enc_id}:{gid}"
        raw_ex, idx = pick_excerpt(paras, seed)
        ex = shorten_excerpt(raw_ex, limit=220)

        prompt = enc.get("prompt_script")
        if isinstance(prompt, dict) and isinstance(prompt.get("value"), str):
            base = prompt["value"]
            base = re.sub(r"\n\n\[Public-domain excerpt \| .*?\]\n\".*?\"$", "", base, flags=re.DOTALL)
            prompt["value"] = (
                f"{base}\n\n"
                f"[Public-domain excerpt | {meta['author']}, {meta['title']} (Project Gutenberg #{gid})]\n"
                f"\"{ex}\""
            )

        manifest_entries.append(
            {
                "encounter_id": enc_id,
                "excerpt": ex,
                "paragraph_index": idx,
                "source": {
                    "title": meta["title"],
                    "author": meta["author"],
                    "project_gutenberg_id": gid,
                    "url": source_url,
                },
            }
        )

    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return {
        "storyworld": path.name,
        "source": {
            "title": meta["title"],
            "author": meta["author"],
            "project_gutenberg_id": gid,
            "url": source_url,
        },
        "encounter_count": len(encounters),
        "citations": manifest_entries,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True, help="Directory containing pd_*_multiending_v*.json files")
    ap.add_argument("--report-dir", default="_reports", help="Report subfolder name")
    args = ap.parse_args()

    root = Path(args.dir)
    report_dir = root / args.report_dir
    report_dir.mkdir(parents=True, exist_ok=True)

    cache: Dict[str, List[str]] = {}
    summary = {"updated_worlds": [], "errors": []}

    for path in sorted(root.glob("pd_*_multiending_v*.json")):
        try:
            slug = detect_slug(path.name)
            if slug not in WORKS:
                raise KeyError(f"No source mapping for slug '{slug}'")
            meta = WORKS[slug]
            gid = meta["gutenberg_id"]

            if gid not in cache:
                txt = fetch_gutenberg_text(gid)
                cache[gid] = paragraph_pool(txt)

            world_manifest = inject_world(path, cache[gid], meta)
            man_name = f"{path.stem}.citations.json"
            (report_dir / man_name).write_text(json.dumps(world_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            summary["updated_worlds"].append({"file": path.name, "manifest": man_name, "encounter_count": world_manifest["encounter_count"]})
        except Exception as exc:  # noqa: BLE001
            summary["errors"].append({"file": path.name, "error": str(exc)})

    (report_dir / "public_domain_excerpt_injection_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    if summary["errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
