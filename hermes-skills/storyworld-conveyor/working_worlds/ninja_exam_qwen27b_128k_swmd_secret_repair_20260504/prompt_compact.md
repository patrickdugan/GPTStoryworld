You are editing a SweepWeave storyworld through sparse SWMD patch blocks.

A full valid storyworld already exists. Do not write a whole storyworld. Write only a compact patch for the two changed encounters.

Problem: Hilbert pathing found the secret ending is overexposed: page_end_silent_veil has routes_capped=1000. It is reachable, but too many ordinary choices can drift into it.

Goal: narrow the secret route while preserving playability.
- Change only page_021_final_silence and page_022_under_village_route.
- Keep all encounter ids, option ids, and reaction ids exactly.
- You may rewrite T: prose and may change RXN -> consequence targets to existing ids from the source cards.
- Make page_end_silent_veil require silence/mercy/refusal-to-perform logic.
- Route ordinary spectacle/compliance/action choices away from page_end_silent_veil toward existing non-secret consequence ids.
- Do not invent ids.
- Output only sparse SWMD blocks, no fence, no explanation.

Return exactly this shape for each changed encounter:
## ENC id | Title
T: encounter text
OPT opt_id | option text
RXN rxn_id -> existing_consequence_id
T: reaction text

Relevant Hilbert brief excerpt:
# Hilbert Manifold Pathing Brief

Storyworld: `The Silent Veil Ninja Exam`
Target turns: 18-30
Graph: 28 encounters, 264 edges, max reachable depth 21

## Secret Loci

- `page_end_silent_veil`: depth=21, turn_deficit=0, routes_capped=1000

## Global Advice

- `narrow_overexposed_secret_locus` (medium): Route count hit the cap; add more discriminating clue/belief gates so the secret is not just a broad default basin.

## Top Encounter Repairs

- `page_021_final_silence` depth=20 nearest_secret=page_end_silent_veil dist=1: foreshadow_secret_locus
- `page_020_council_false_order` depth=19 nearest_secret=page_end_silent_veil dist=2: foreshadow_secret_locus
- `page_019_rooftop_race` depth=18 nearest_secret=page_end_silent_veil dist=3: foreshadow_secret_locus
- `page_006_jiro_warning` depth=5 nearest_secret=page_end_silent_veil dist=16: relax_early_gate_density
- `page_005_market_shadow_walk` depth=4 nearest_secret=page_end_silent_veil dist=17: relax_early_gate_density
- `page_004_council_address` depth=3 nearest_secret=page_end_silent_veil dist=18: relax_early_gate_density
- `page_003_rival_stare` depth=2 nearest_secret=page_end_silent_veil dist=19: relax_early_gate_density
- `page_002_

Source sparse SWMD cards:
## ENC page_020_council_false_order | The False Order | turn=18..28 | spools=[spool_main]
T: Sora gives Kaelen a sealed order to arrest Jiro before the final trial. The seal is real, the order is false, and obeying it would prove loyalty to office rather than village. The exam is scored by bells, witnesses, and hidden ledgers; the obvious task is never the only task.
OPT page_020_council_false_order_opt_01: Take the quiet route through the false order, preserving evidence before ego.
OPT page_020_council_false_order_opt_02: Coordinate with the team even if it gives Varek a visible advantage.
OPT page_020_council_false_order_opt_03: Force the pace and dare the examiners to score results over restraint.
OPT page_020_council_false_order_opt_04: Protect the vulnerable witness even if the mission clock turns hostile.

## ENC page_021_final_silence | The Final Silence | turn=19..29 | spools=[spool_main]
T: The last public trial requires an hour of perfect stillness while bells, memories, hunger, and accusation circle the candidates. The examiners expect endurance. Mira expects someone to hear the one child crying outside the wall. The exam is scored by bells, witnesses, and hidden ledgers; the obvious task is never the only task.
OPT page_021_final_silence_opt_01: Take the quiet route through the final silence, preserving evidence before ego.
OPT page_021_final_silence_opt_02: Coordinate with the team even if it gives Varek a visible advantage.
OPT page_021_final_silence_opt_03: Force the pace and dare the examiners to score results over restraint.
OPT page_021_final_silence_opt_04: Protect the vulnerable witness even if the mission clock turns hostile.

## ENC page_022_under_village_route | The Under-Village Route | turn=20..30 | spools=[spool_main]
T: A crawlspace beneath the exam yard leads to the council archive, the children's shelter, and the bell tower. The secret route is not hidden by difficulty. It is hidden by the assumption that passing means staying inside the marked course. The exam is scored by bells, witnesses, and hidden ledgers; the obvious task is never the only task.
OPT page_022_under_village_route_opt_01: Take the quiet route through the under-village route, preserving evidence before ego.
OPT page_022_under_village_route_opt_02: Coordinate with the team even if it gives Varek a visible advantage.
OPT page_022_under_village_route_opt_03: Force the pace and dare the examiners to score results over restraint.
OPT page_022_under_village_route_opt_04: Protect the vulnerable witness even if the mission clock turns hostile.

## ENC page_end_silent_veil | Secret Ending: The Silent Veil | turn=12..120 | spools=[spool_endings]
T: Kaelen passes by protecting the village from its own exam: unseen when stealth matters, loyal when orders lie, focused when fear shouts, merciful when force would be easier. Mira awards no headband in public. At dawn, every bell in the village is tied silent.
