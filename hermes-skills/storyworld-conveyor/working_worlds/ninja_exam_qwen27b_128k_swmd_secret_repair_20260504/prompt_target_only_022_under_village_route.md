Return ONLY one SWMD target-only patch block. No prose. No T lines.

Allowed targets: page_022_under_village_route, page_end_village_witness, page_end_shadow_rank, page_end_council_tool, page_end_merciful_failure, page_end_silent_veil.

Objective: structurally narrow the secret path.
Rules:
- Preserve exact ENC, OPT, RXN ids.
- Emit the encounter header and all OPT/RXN lines below with revised targets.
- Exactly ONE reaction targets page_end_silent_veil: the clean vulnerable-witness reaction. Zero self-loops. All other reactions terminate in existing non-secret endings.

Source:
## ENC page_022_under_village_route | The Under-Village Route | turn=19..30
OPT page_022_under_village_route_opt_01: Take the quiet route through the under-village route, preserving evidence before ego.
  RXN page_022_under_village_route_opt_01_r1 -> page_end_village_witness
  RXN page_022_under_village_route_opt_01_r2 -> page_end_village_witness
  RXN page_022_under_village_route_opt_01_r3 -> page_022_under_village_route
OPT page_022_under_village_route_opt_02: Coordinate with the team even if it gives Varek a visible advantage.
  RXN page_022_under_village_route_opt_02_r1 -> page_end_village_witness
  RXN page_022_under_village_route_opt_02_r2 -> page_end_village_witness
  RXN page_022_under_village_route_opt_02_r3 -> page_end_shadow_rank
OPT page_022_under_village_route_opt_03: Force the pace and dare the examiners to score results over restraint.
  RXN page_022_under_village_route_opt_03_r1 -> page_end_village_witness
  RXN page_022_under_village_route_opt_03_r2 -> page_end_village_witness
  RXN page_022_under_village_route_opt_03_r3 -> page_end_council_tool
OPT page_022_under_village_route_opt_04: Protect the vulnerable witness even if the mission clock turns hostile.
  RXN page_022_under_village_route_opt_04_r1 -> page_end_silent_veil
  RXN page_022_under_village_route_opt_04_r2 -> page_end_silent_veil
  RXN page_022_under_village_route_opt_04_r3 -> page_022_under_village_route
