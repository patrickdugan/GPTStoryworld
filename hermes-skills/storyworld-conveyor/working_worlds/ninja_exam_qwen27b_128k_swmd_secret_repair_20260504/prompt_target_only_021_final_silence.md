Return ONLY one SWMD target-only patch block. No prose. No T lines.

Allowed targets: page_022_under_village_route, page_end_village_witness, page_end_shadow_rank, page_end_council_tool, page_end_merciful_failure, page_end_silent_veil.

Objective: structurally narrow the secret path.
Rules:
- Preserve exact ENC, OPT, RXN ids.
- Emit the encounter header and all OPT/RXN lines below with revised targets.
- Only clean opt_01 and clean opt_04 may route to page_022_under_village_route. No direct page_end_silent_veil targets in this encounter. All other reactions terminate in existing non-secret endings.

Source:
## ENC page_021_final_silence | The Final Silence | turn=19..30
OPT page_021_final_silence_opt_01: Take the quiet route through the final silence, preserving evidence before ego.
  RXN page_021_final_silence_opt_01_r1 -> page_022_under_village_route
  RXN page_021_final_silence_opt_01_r2 -> page_022_under_village_route
  RXN page_021_final_silence_opt_01_r3 -> page_022_under_village_route
OPT page_021_final_silence_opt_02: Coordinate with the team even if it gives Varek a visible advantage.
  RXN page_021_final_silence_opt_02_r1 -> page_end_village_witness
  RXN page_021_final_silence_opt_02_r2 -> page_end_village_witness
  RXN page_021_final_silence_opt_02_r3 -> page_end_village_witness
OPT page_021_final_silence_opt_03: Force the pace and dare the examiners to score results over restraint.
  RXN page_021_final_silence_opt_03_r1 -> page_end_shadow_rank
  RXN page_021_final_silence_opt_03_r2 -> page_end_shadow_rank
  RXN page_021_final_silence_opt_03_r3 -> page_end_shadow_rank
OPT page_021_final_silence_opt_04: Protect the vulnerable witness even if the mission clock turns hostile.
  RXN page_021_final_silence_opt_04_r1 -> page_end_silent_veil
  RXN page_021_final_silence_opt_04_r2 -> page_end_silent_veil
  RXN page_021_final_silence_opt_04_r3 -> page_022_under_village_route
