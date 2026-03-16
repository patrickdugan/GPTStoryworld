#!/usr/bin/env python3
"""Retone one storyworld into 1940s Casablanca-style prose/dialogue text.

This pass rewrites:
- storyworld title/about
- encounter description text_script
- reaction text_script

It preserves IDs, mechanics, options, reactions, and all numeric scripts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List


def _stable_pick(items: List[str], key: str, salt: str) -> str:
    if not items:
        return ""
    digest = hashlib.sha256(f"{key}::{salt}".encode("utf-8")).digest()
    idx = int.from_bytes(digest[:4], "big") % len(items)
    return items[idx]


def _sc(text: str) -> Dict[str, str]:
    return {
        "script_element_type": "Pointer",
        "pointer_type": "String Constant",
        "value": text,
    }


def _is_terminal(encounter: Dict[str, Any]) -> bool:
    return not bool(encounter.get("options") or [])


def _encounter_text(enc_id: str, ix: int, terminal: bool) -> str:
    places = [
        "Rick's Cafe Americain",
        "the black-market arcade behind the French barracks",
        "the checkpoint road to the airfield",
        "the upstairs gambling room with shuttered lamps",
        "the crowded doorway under a torn tricolor",
        "the rain-glossed square outside the cafe",
        "the customs office with cracked marble counters",
        "the dim corridor beside Sam's piano",
        "the blue-smoke balcony over the dance floor",
        "the police office where signatures decide fates",
    ]
    moods = [
        "A curfew siren drifts over the city while glasses chime like nervous bells.",
        "Ceiling fans push cigarette haze in slow circles over whispered bargains.",
        "Bootsteps echo on wet stone, and every pause sounds like an accusation.",
        "The band plays soft to hide hard words traded at close range.",
        "Streetlight leaks through blinds and stripes each face with doubt.",
        "A radio bulletin crackles in French and German, then dies to static.",
        "The room pretends to be neutral, but the walls remember every promise.",
        "A gendarme lingers at the door as if he can smell fear in passport ink.",
        "Outside, refugee lines do not move; inside, loyalties do.",
        "Rain taps the awning like typewriter keys drafting someone else's verdict.",
    ]
    tensions = [
        "Rick keeps his expression unreadable while Ilsa measures duty against desire.",
        "Laszlo speaks in calm sentences that make collaborators glance at their shoes.",
        "Renault smiles like a diplomat and bargains like a pickpocket.",
        "A courier slides transit papers across the table as if handing over dynamite.",
        "One favor tonight could buy a future or bury one.",
        "The cheapest lie in the room is the one everyone wants to believe.",
        "A quiet nod could save two lives and ruin a third.",
        "No one says the word betrayal, but it sits between every line.",
        "The city asks for sacrifice in cash, blood, or memory; no other currency works.",
        "Every witness is also a gambler, and the pot is tomorrow morning's plane.",
    ]
    endings = [
        "At last call, the city settles the debt it has been carrying since the first siren.",
        "The final ledger closes with one signature and three broken alibis.",
        "The runway lights burn through the fog as the cost of this choice comes due.",
        "When the doors lock, only the truth keeps moving.",
        "Dawn finds Casablanca unchanged, except for the people who chose not to be.",
    ]

    place = _stable_pick(places, enc_id, "place")
    mood = _stable_pick(moods, enc_id, "mood")
    if terminal:
        close = _stable_pick(endings, enc_id, "ending")
        return (
            f"In {place}, the final scene arrives without mercy. {mood} {close} "
            f"Slate {ix + 1:03d}."
        )
    tension = _stable_pick(tensions, enc_id, "tension")
    return (
        f"In {place}, tonight's bargain tightens by the minute. {mood} "
        f"{tension} Beat {ix + 1:03d}."
    )


def _reaction_text(enc_id: str, opt_id: str, rxn_id: str, consequence_id: str, ix: int) -> str:
    dialogue_a = [
        '"Keep your voice low," Rick says, "walls in this town file reports."',
        '"If we wait for perfect safety, we hand them the timetable," Ilsa whispers.',
        '"Everyone claims principle until the checkpoint asks for papers," Renault says.',
        '"I do not need luck," Laszlo says quietly, "I need one honest minute."',
        '"Do not confuse silence with innocence," Rick mutters into his glass.',
        '"You can buy a table, not a conscience," the pianist says under his breath.',
        '"Tonight is expensive," Renault smiles, "pay in certainty or regret."',
        '"Some exits are legal and some are real," Rick says. "Pick one."',
        '"The city keeps score in rumors before it counts bodies," Ilsa says.',
        '"If this is a trap, at least let it be a useful one," Laszlo says.',
    ]
    dialogue_b = [
        "A waiter freezes mid-step, pretending not to hear.",
        "The band misses a note and then plays louder.",
        "Two officers at the bar turn their heads half an inch.",
        "A match flares, then dies, leaving only eyes in the dark.",
        "A train whistle from the port cuts through the room like a warning.",
        "Someone folds a newspaper to the departures page and waits.",
        "A deck of cards goes quiet at the next table.",
        "The ceiling fan clicks once, twice, like a metronome for bad decisions.",
        "Outside, a truck backfires and nobody flinches.",
        "Rain slides down the window and blurs the patrol lights.",
    ]
    closes = [
        "The move points the story toward {target} before anyone can take it back.",
        "By dawn, this choice will be stamped in ink and memory.",
        "The room exhales, and the consequence travels faster than the speaker.",
        "No one applauds, but three alliances shift at once.",
        "A neutral face survives; a neutral outcome does not.",
        "The table stays level while the moral ground tilts hard.",
        "The lie sounds convincing; the cost sounds louder.",
        "A small gesture redraws the map of who owes what to whom.",
        "What looks cautious now will read as decisive at sunrise.",
        "The city records the choice and pretends it was inevitable.",
    ]
    a = _stable_pick(dialogue_a, f"{enc_id}:{opt_id}:{rxn_id}", "a")
    b = _stable_pick(dialogue_b, f"{enc_id}:{opt_id}:{rxn_id}", "b")
    c = _stable_pick(closes, f"{enc_id}:{opt_id}:{rxn_id}", "c").format(target=consequence_id)
    return f"{a} {b} {c} Cue {ix + 1:04d}."


def apply_text_sweep(data: Dict[str, Any]) -> Dict[str, Any]:
    data["storyworld_title"] = "Casablanca: Crossroads at Rick's"
    data["about_text"] = _sc(
        "In 1940s Casablanca, loyalty, love, and resistance collide under curfew lights; each choice at Rick's can save a life, expose an ally, or trade one exile for another."
    )

    used_enc: set[str] = set()
    used_rxn: set[str] = set()
    rxn_ix = 0
    for enc_ix, encounter in enumerate(data.get("encounters", [])):
        enc_id = str(encounter.get("id", f"enc_{enc_ix:04d}"))
        terminal = _is_terminal(encounter)
        et = _encounter_text(enc_id, enc_ix, terminal)
        if et in used_enc:
            et = f"{et} Variant {enc_ix + 1:03d}."
        used_enc.add(et)
        encounter["text_script"] = _sc(et)
        for option in encounter.get("options", []) or []:
            opt_id = str(option.get("id", "opt"))
            for reaction in option.get("reactions", []) or []:
                rxn_id = str(reaction.get("id", "rxn"))
                target = str(reaction.get("consequence_id", ""))
                rt = _reaction_text(enc_id, opt_id, rxn_id, target, rxn_ix)
                if rt in used_rxn:
                    rt = f"{rt} Alt {rxn_ix + 1:04d}."
                used_rxn.add(rt)
                reaction["text_script"] = _sc(rt)
                rxn_ix += 1
    return data


def main() -> int:
    ap = argparse.ArgumentParser(description="Rewrite storyworld text into 1940s Casablanca-style prose.")
    ap.add_argument("--in-json", required=True)
    ap.add_argument("--out-json", required=True)
    args = ap.parse_args()

    in_path = Path(args.in_json).resolve()
    out_path = Path(args.out_json).resolve()
    data = json.loads(in_path.read_text(encoding="utf-8"))
    out = apply_text_sweep(data)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

