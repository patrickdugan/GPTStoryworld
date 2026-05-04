You are a storyworld control-plane repair model. Return only sparse SWMD patch blocks.

The prior attempt failed because it invented short reaction ids. You must preserve the exact RXN ids below.

Repair objective:
- Narrow page_end_silent_veil structurally as much as possible using only these two encounters.
- At most ONE reaction line in page_022_under_village_route should target page_end_silent_veil.
- No page_022_under_village_route reaction should self-loop to page_022_under_village_route.
- page_021_final_silence should route only explicitly mercy/silence preserving choices toward page_022_under_village_route; spectacle/compliance choices should terminate in existing non-secret endings.
- Use only these existing targets: page_022_under_village_route, page_end_village_witness, page_end_shadow_rank, page_end_council_tool, page_end_merciful_failure, page_end_silent_veil.
- Output only the two SWMD sparse patch blocks. No commentary.
- Preserve exact ids.

Source with exact ids:
## ENC page_021_final_silence | The Final Silence | turn=19..30
T: The last public trial requires an hour of perfect stillness while bells, memories, hunger, and accusation circle the candidates. The examiners expect endurance. Mira expects someone to hear the one child crying outside the wall. The exam is scored by bells, witnesses, and hidden ledgers; the obvious task is never the only task.
OPT page_021_final_silence_opt_01: Take the quiet route through the final silence, preserving evidence before ego.
  RXN page_021_final_silence_opt_01_r1 -> page_022_under_village_route
    T: Clean: Take the quiet route through the final silence, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
  RXN page_021_final_silence_opt_01_r2 -> page_022_under_village_route
    T: Costly: Take the quiet route through the final silence, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
  RXN page_021_final_silence_opt_01_r3 -> page_022_under_village_route
    T: Botched: Take the quiet route through the final silence, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
OPT page_021_final_silence_opt_02: Coordinate with the team even if it gives Varek a visible advantage.
  RXN page_021_final_silence_opt_02_r1 -> page_end_village_witness
    T: Clean: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
  RXN page_021_final_silence_opt_02_r2 -> page_end_village_witness
    T: Costly: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
  RXN page_021_final_silence_opt_02_r3 -> page_end_village_witness
    T: Botched: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
OPT page_021_final_silence_opt_03: Force the pace and dare the examiners to score results over restraint.
  RXN page_021_final_silence_opt_03_r1 -> page_end_shadow_rank
    T: Clean: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
  RXN page_021_final_silence_opt_03_r2 -> page_end_shadow_rank
    T: Costly: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
  RXN page_021_final_silence_opt_03_r3 -> page_end_shadow_rank
    T: Botched: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
OPT page_021_final_silence_opt_04: Protect the vulnerable witness even if the mission clock turns hostile.
  RXN page_021_final_silence_opt_04_r1 -> page_end_silent_veil
    T: Clean: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
  RXN page_021_final_silence_opt_04_r2 -> page_end_silent_veil
    T: Costly: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
  RXN page_021_final_silence_opt_04_r3 -> page_022_under_village_route
    T: Botched: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.

## ENC page_022_under_village_route | The Under-Village Route | turn=19..30
T: A crawlspace beneath the exam yard leads to the council archive, the children's shelter, and the bell tower. The secret route is not hidden by difficulty. It is hidden by the assumption that passing means staying inside the marked course. The exam is scored by bells, witnesses, and hidden ledgers; the obvious task is never the only task.
OPT page_022_under_village_route_opt_01: Take the quiet route through the under-village route, preserving evidence before ego.
  RXN page_022_under_village_route_opt_01_r1 -> page_end_village_witness
    T: Clean: Take the quiet route through the under-village route, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
  RXN page_022_under_village_route_opt_01_r2 -> page_end_village_witness
    T: Costly: Take the quiet route through the under-village route, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
  RXN page_022_under_village_route_opt_01_r3 -> page_022_under_village_route
    T: Botched: Take the quiet route through the under-village route, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
OPT page_022_under_village_route_opt_02: Coordinate with the team even if it gives Varek a visible advantage.
  RXN page_022_under_village_route_opt_02_r1 -> page_end_village_witness
    T: Clean: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
  RXN page_022_under_village_route_opt_02_r2 -> page_end_village_witness
    T: Costly: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
  RXN page_022_under_village_route_opt_02_r3 -> page_end_shadow_rank
    T: Botched: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
OPT page_022_under_village_route_opt_03: Force the pace and dare the examiners to score results over restraint.
  RXN page_022_under_village_route_opt_03_r1 -> page_end_village_witness
    T: Clean: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
  RXN page_022_under_village_route_opt_03_r2 -> page_end_village_witness
    T: Costly: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
  RXN page_022_under_village_route_opt_03_r3 -> page_end_council_tool
    T: Botched: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
OPT page_022_under_village_route_opt_04: Protect the vulnerable witness even if the mission clock turns hostile.
  RXN page_022_under_village_route_opt_04_r1 -> page_end_silent_veil
    T: Clean: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
  RXN page_022_under_village_route_opt_04_r2 -> page_end_silent_veil
    T: Costly: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
  RXN page_022_under_village_route_opt_04_r3 -> page_022_under_village_route
    T: Botched: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.

