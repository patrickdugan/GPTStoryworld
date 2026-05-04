You are editing a SweepWeave storyworld using SWMD sparse patch blocks.

Task: narrow an overexposed secret ending route in a ninja exam storyworld while preserving validity.

Important token rule: do NOT rewrite the whole storyworld. Produce only sparse SWMD patch blocks for the encounters you change. The patcher accepts partial blocks with encounter ids, title/text, option ids, reaction ids, reaction text, and consequence targets. Omit E: and D: formula lines unless you need to explain a design intent in prose. Preserve all ids exactly.

Current issue from Hilbert pathing:
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
- `page_002_dry_leaf_walk` depth=1 nearest_secret=page_end_silent_veil dist=20: relax_early_gate_density
- `page_001_exam_gate` depth=0 nearest_secret=page_end_silent_veil dist=21: relax_early_gate_density
- `page_end_silent_veil` depth=21 nearest_secret=page_end_silent_veil dist=0: add_pvalue_gate_support, add_p2value_late_turn_support


Design goal:
- The secret ending page_end_silent_veil should be reachable, foreshadowed, and rewarding.
- It should NOT be available from too many ordinary paths.
- Make it require a legible convergent route through silence/mercy/refusal-to-perform, especially around page_021_final_silence and page_022_under_village_route.
- Ordinary action/compliance/spectacle choices should route to non-secret outcomes already present in the source blocks.
- Keep all existing encounter ids, option ids, reaction ids.
- Prefer changing only T: prose and selected RXN -> target consequence ids.
- Do not invent new ids.
- Return ONLY SWMD blocks. No markdown fence. No analysis.

Sparse output example shape:
## ENC page_021_final_silence | Final Silence
T: revised encounter text
OPT opt_01 | revised option text
RXN rxn_01 -> existing_consequence_id
T: revised reaction text

Source blocks:

## ENC page_020_council_false_order | The False Order | turn=18..28 | spools=[spool_main]
T: Sora gives Kaelen a sealed order to arrest Jiro before the final trial. The seal is real, the order is false, and obeying it would prove loyalty to office rather than village. The exam is scored by bells, witnesses, and hidden ledgers; the obvious task is never the only task.

OPT page_020_council_false_order_opt_01: Take the quiet route through the false order, preserving evidence before ego.
  RXN page_020_council_false_order_opt_01_r1 -> page_021_final_silence
    T: Clean: Take the quiet route through the false order, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.025),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.06),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_020_council_false_order_opt_01_r2 -> page_021_final_silence
    T: Costly: Take the quiet route through the false order, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.0113),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.027),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_020_council_false_order_opt_01_r3 -> page_021_final_silence
    T: Botched: Take the quiet route through the false order, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(-0.01),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(-0.024),MUL(P(char_kaelen.Focus),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Stealth),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_020_council_false_order_opt_02: Coordinate with the team even if it gives Varek a visible advantage.
  RXN page_020_council_false_order_opt_02_r1 -> page_end_merciful_failure
    T: Clean: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.055),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.03),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_020_council_false_order_opt_02_r2 -> page_end_merciful_failure
    T: Costly: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.0248),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0135),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_020_council_false_order_opt_02_r3 -> page_end_merciful_failure
    T: Botched: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(-0.022),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.012),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Loyalty),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_020_council_false_order_opt_03: Force the pace and dare the examiners to score results over restraint.
  RXN page_020_council_false_order_opt_03_r1 -> page_end_village_witness
    T: Clean: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.035),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.06),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.025))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_020_council_false_order_opt_03_r2 -> page_end_village_witness
    T: Costly: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.0158),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.027),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.0113))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_020_council_false_order_opt_03_r3 -> page_end_village_witness
    T: Botched: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(0.014),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(-0.024),MUL(P(char_kaelen.Mercy),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Rivalry),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_020_council_false_order_opt_04: Protect the vulnerable witness even if the mission clock turns hostile.
  RXN page_020_council_false_order_opt_04_r1 -> page_end_shadow_rank
    T: Clean: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.06),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.035),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_020_council_false_order_opt_04_r2 -> page_end_shadow_rank
    T: Costly: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.027),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0158),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_020_council_false_order_opt_04_r3 -> page_end_shadow_rank
    T: Botched: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(-0.024),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.014),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Mercy),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))
## ENC page_021_final_silence | The Final Silence | turn=19..29 | spools=[spool_main]
T: The last public trial requires an hour of perfect stillness while bells, memories, hunger, and accusation circle the candidates. The examiners expect endurance. Mira expects someone to hear the one child crying outside the wall. The exam is scored by bells, witnesses, and hidden ledgers; the obvious task is never the only task.

OPT page_021_final_silence_opt_01: Take the quiet route through the final silence, preserving evidence before ego.
  RXN page_021_final_silence_opt_01_r1 -> page_022_under_village_route
    T: Clean: Take the quiet route through the final silence, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.025),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.06),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_021_final_silence_opt_01_r2 -> page_022_under_village_route
    T: Costly: Take the quiet route through the final silence, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.0113),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.027),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_021_final_silence_opt_01_r3 -> page_022_under_village_route
    T: Botched: Take the quiet route through the final silence, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(-0.01),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(-0.024),MUL(P(char_kaelen.Focus),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Stealth),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_021_final_silence_opt_02: Coordinate with the team even if it gives Varek a visible advantage.
  RXN page_021_final_silence_opt_02_r1 -> page_end_village_witness
    T: Clean: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.055),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.03),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_021_final_silence_opt_02_r2 -> page_end_village_witness
    T: Costly: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.0248),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0135),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_021_final_silence_opt_02_r3 -> page_end_village_witness
    T: Botched: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(-0.022),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.012),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Loyalty),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_021_final_silence_opt_03: Force the pace and dare the examiners to score results over restraint.
  RXN page_021_final_silence_opt_03_r1 -> page_end_shadow_rank
    T: Clean: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.035),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.06),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.025))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_021_final_silence_opt_03_r2 -> page_end_shadow_rank
    T: Costly: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.0158),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.027),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.0113))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_021_final_silence_opt_03_r3 -> page_end_shadow_rank
    T: Botched: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(0.014),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(-0.024),MUL(P(char_kaelen.Mercy),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Rivalry),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_021_final_silence_opt_04: Protect the vulnerable witness even if the mission clock turns hostile.
  RXN page_021_final_silence_opt_04_r1 -> page_end_silent_veil
    T: Clean: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.06),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.035),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_021_final_silence_opt_04_r2 -> page_end_silent_veil
    T: Costly: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.027),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0158),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_021_final_silence_opt_04_r3 -> page_022_under_village_route
    T: Botched: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(-0.024),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.014),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Mercy),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))
## ENC page_022_under_village_route | The Under-Village Route | turn=20..30 | spools=[spool_main]
T: A crawlspace beneath the exam yard leads to the council archive, the children's shelter, and the bell tower. The secret route is not hidden by difficulty. It is hidden by the assumption that passing means staying inside the marked course. The exam is scored by bells, witnesses, and hidden ledgers; the obvious task is never the only task.

OPT page_022_under_village_route_opt_01: Take the quiet route through the under-village route, preserving evidence before ego.
  RXN page_022_under_village_route_opt_01_r1 -> page_end_village_witness
    T: Clean: Take the quiet route through the under-village route, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.025),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.06),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_022_under_village_route_opt_01_r2 -> page_end_village_witness
    T: Costly: Take the quiet route through the under-village route, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.0113),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.027),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_022_under_village_route_opt_01_r3 -> page_022_under_village_route
    T: Botched: Take the quiet route through the under-village route, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(-0.01),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(-0.024),MUL(P(char_kaelen.Focus),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Stealth),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_022_under_village_route_opt_02: Coordinate with the team even if it gives Varek a visible advantage.
  RXN page_022_under_village_route_opt_02_r1 -> page_end_village_witness
    T: Clean: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.055),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.03),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_022_under_village_route_opt_02_r2 -> page_end_village_witness
    T: Costly: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.0248),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0135),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_022_under_village_route_opt_02_r3 -> page_end_shadow_rank
    T: Botched: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(-0.022),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.012),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Loyalty),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_022_under_village_route_opt_03: Force the pace and dare the examiners to score results over restraint.
  RXN page_022_under_village_route_opt_03_r1 -> page_end_village_witness
    T: Clean: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.035),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.06),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.025))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_022_under_village_route_opt_03_r2 -> page_end_village_witness
    T: Costly: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.0158),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.027),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.0113))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_022_under_village_route_opt_03_r3 -> page_end_council_tool
    T: Botched: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(0.014),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(-0.024),MUL(P(char_kaelen.Mercy),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Rivalry),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_022_under_village_route_opt_04: Protect the vulnerable witness even if the mission clock turns hostile.
  RXN page_022_under_village_route_opt_04_r1 -> page_end_silent_veil
    T: Clean: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.06),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.035),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_022_under_village_route_opt_04_r2 -> page_end_silent_veil
    T: Costly: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.027),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0158),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_022_under_village_route_opt_04_r3 -> page_022_under_village_route
    T: Botched: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(-0.024),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.014),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Mercy),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))
## ENC page_end_silent_veil | Secret Ending: The Silent Veil | turn=12..120 | spools=[spool_endings]
T: Kaelen passes by protecting the village from its own exam: unseen when stealth matters, loyal when orders lie, focused when fear shouts, merciful when force would be easier. Mira awards no headband in public. At dawn, every bell in the village is tied silent.
