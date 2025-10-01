#!/usr/bin/env python3
"""
storyworld_summarizer.py
Summarize a Sweepweave storyworld .json into a compact .yaml index.

Usage:
    python storyworld_summarizer.py input.json output.yaml
"""

import sys, json, yaml
from collections import defaultdict

def summarize_storyworld(input_path: str, output_path: str):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    summary = {}

    # Characters
    chars = []
    for ch in data.get("characters", []):
        entry = {"id": ch.get("id"), "name": ch.get("name", "")}
        if "bnumber_properties" in ch:
            entry["variables"] = list(ch["bnumber_properties"].keys())
        chars.append(entry)
    summary["characters"] = chars

    # Spools
    spools = []
    for s in data.get("spools", []):
        if isinstance(s, dict):
            spools.append({"id": s.get("id")})
        else:
            spools.append({"id": s})
    summary["spools"] = spools

    # Encounters grouped by spool
    spool_map = defaultdict(list)
    for e in data.get("encounters", []):
        for s in e.get("connected_spools", []):
            spool_map[s].append(e)

    encs = {}
    for spool, ens in spool_map.items():
        encs[spool] = []
        for e in ens:
            e_entry = {"id": e.get("id"), "title": e.get("title", "")}
            opts = []
            for opt in e.get("options", []):
                o_entry = {"id": opt.get("id")}
                reactions = []
                for rx in opt.get("reactions", []):
                    reactions.append({
                        "id": rx.get("id"),
                        "consequence": rx.get("consequence_id"),
                        "effects": [ae.get("effect_type") for ae in rx.get("after_effects", [])]
                    })
                o_entry["reactions"] = reactions
                opts.append(o_entry)
            e_entry["options"] = opts
            encs[spool].append(e_entry)
    summary["encounters"] = encs

    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(summary, f, sort_keys=False, allow_unicode=True)

    print(f"✅ Summary written to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python storyworld_summarizer.py input.json output.yaml")
        sys.exit(1)
    summarize_storyworld(sys.argv[1], sys.argv[2])
