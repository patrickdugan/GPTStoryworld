---
title: "The Silent Veil Ninja Exam"
version: "0.1.9"
storyworld_id: "SW-NINJA-EXAM-QWEN9B-20260504"
environment_type: "SWEEPWEAVE_STORYWORLD"
source_format: "SWMD-0-MIN"
state_variables:
  - "Focus"
  - "Loyalty"
  - "Mercy"
  - "Rivalry"
  - "Stealth"
  - "VillageTrust"
endings:
  - id: "page_end_council_tool"
    type: "terminal"
    condition: "ARITHMETIC COMPARATOR(ABSOLUTE VALUE(P(char_kaelen.VillageTrust)),C(2.5))"
    description: "Kaelen obeys every sealed order and graduates quickly. Sora praises him in public, then files his conscience with the other equipment."
    expected_critic_score: 0
  - id: "page_end_merciful_failure"
    type: "failure"
    condition: "ARITHMETIC COMPARATOR(ABSOLUTE VALUE(P(char_kaelen.VillageTrust)),C(2.5))"
    description: "Kaelen protects civilians and fails the posted score. The academy calls it failure; the market starts leaving lamps for him at doorways."
    expected_critic_score: -1
  - id: "page_end_rival_victory"
    type: "success"
    condition: "ARITHMETIC COMPARATOR(ABSOLUTE VALUE(P(char_kaelen.VillageTrust)),C(2.5))"
    description: "Varek wins the visible contest. Kaelen survives the exam but leaves knowing he mistook another student's pace for his own path."
    expected_critic_score: 1
  - id: "page_end_shadow_rank"
    type: "terminal"
    condition: "ARITHMETIC COMPARATOR(ABSOLUTE VALUE(P(char_kaelen.VillageTrust)),C(2.5))"
    description: "Kaelen passes as a technically excellent infiltrator. The village gains a sharp blade, but not yet someone who knows when a blade should stay sheathed."
    expected_critic_score: 0
  - id: "page_end_silent_veil"
    type: "terminal"
    condition: "ARITHMETIC COMPARATOR(ABSOLUTE VALUE(P(char_kaelen.VillageTrust)),C(2.5))"
    description: "Kaelen passes by protecting the village from its own exam: unseen when stealth matters, loyal when orders lie, focused when fear shouts, merciful when force would be easier. Mir..."
    expected_critic_score: 0
  - id: "page_end_village_witness"
    type: "terminal"
    condition: "ARITHMETIC COMPARATOR(ABSOLUTE VALUE(P(char_kaelen.VillageTrust)),C(2.5))"
    description: "Kaelen exposes the false order without collapsing the council. The village does not fully trust him yet, but it begins watching the examiners too."
    expected_critic_score: 0
---

# SWMD-0
id: SW-NINJA-EXAM-QWEN9B-20260504
title: The Silent Veil Ninja Exam
theme: slate
about: An original hidden-village ninja exam storyworld inspired by broad shonen ninja motifs without using copyrighted canon names or plot events. Kaelen must pass by balancing stealth, loyalty, focus, mercy, rivalry, and village trust.
cast: char_kaelen, char_varek, char_mira, char_jiro, char_sora, char_village
props: Stealth, Loyalty, Focus, Mercy, Rivalry, VillageTrust
spools:
  spool_main: page_001_exam_gate page_002_dry_leaf_walk page_003_rival_stare page_004_council_address page_005_market_shadow_walk page_006_jiro_warning page_007_poisoned_feast page_008_broken_bridge page_009_reflection_pool page_010_stolen_scroll_tower page_011_whisper_network page_012_endless_corridor page_013_civilian_or_asset page_014_mirror_match page_015_silent_debate page_016_blindfolded_trust page_017_paper_crane_cipher page_018_hostage_mask page_019_rooftop_race page_020_council_false_order page_021_final_silence page_022_under_village_route
  spool_endings: page_end_shadow_rank page_end_council_tool page_end_rival_victory page_end_merciful_failure page_end_village_witness page_end_silent_veil

## ENC page_001_exam_gate | The Exam Gate Under Rain | turn=0..9 | spools=[spool_main]
T: Kaelen enters the hidden village exam yard under cold rain. The candidates expect sparring, but Mira says the first mark belongs to whoever notices what the rain hides: old footprints, fresh roof scratches, and a council seal carried by the wrong courier. The exam is scored by bells, witnesses, and hidden ledgers; the obvious task is never the only task.

OPT page_001_exam_gate_opt_01: Take the quiet route through the exam gate under rain, preserving evidence before ego.
  RXN page_001_exam_gate_opt_01_r1 -> page_002_dry_leaf_walk
    T: Clean: Take the quiet route through the exam gate under rain, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.025),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.06),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_001_exam_gate_opt_01_r2 -> page_002_dry_leaf_walk
    T: Costly: Take the quiet route through the exam gate under rain, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.0113),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.027),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_001_exam_gate_opt_01_r3 -> page_002_dry_leaf_walk
    T: Botched: Take the quiet route through the exam gate under rain, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(-0.01),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(-0.024),MUL(P(char_kaelen.Focus),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Stealth),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_001_exam_gate_opt_02: Coordinate with the team even if it gives Varek a visible advantage.
  RXN page_001_exam_gate_opt_02_r1 -> page_002_dry_leaf_walk
    T: Clean: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.055),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.03),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_001_exam_gate_opt_02_r2 -> page_002_dry_leaf_walk
    T: Costly: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.0248),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0135),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_001_exam_gate_opt_02_r3 -> page_002_dry_leaf_walk
    T: Botched: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(-0.022),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.012),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Loyalty),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_001_exam_gate_opt_03: Force the pace and dare the examiners to score results over restraint.
  RXN page_001_exam_gate_opt_03_r1 -> page_002_dry_leaf_walk
    T: Clean: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.035),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.06),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.025))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_001_exam_gate_opt_03_r2 -> page_002_dry_leaf_walk
    T: Costly: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.0158),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.027),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.0113))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_001_exam_gate_opt_03_r3 -> page_002_dry_leaf_walk
    T: Botched: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(0.014),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(-0.024),MUL(P(char_kaelen.Mercy),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Rivalry),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_001_exam_gate_opt_04: Protect the vulnerable witness even if the mission clock turns hostile.
  RXN page_001_exam_gate_opt_04_r1 -> page_002_dry_leaf_walk
    T: Clean: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.06),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.035),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_001_exam_gate_opt_04_r2 -> page_002_dry_leaf_walk
    T: Costly: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.027),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0158),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_001_exam_gate_opt_04_r3 -> page_002_dry_leaf_walk
    T: Botched: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(-0.024),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.014),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Mercy),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))


## ENC page_002_dry_leaf_walk | The Dry Leaf Walk | turn=0..10 | spools=[spool_main]
T: A corridor of brittle leaves separates the class from breakfast. Varek charges through and laughs at the noise. The instructors do not laugh. The trial asks whether a candidate can move quietly when hunger and embarrassment make haste feel righteous. The exam is scored by bells, witnesses, and hidden ledgers; the obvious task is never the only task.

OPT page_002_dry_leaf_walk_opt_01: Take the quiet route through the dry leaf walk, preserving evidence before ego.
  RXN page_002_dry_leaf_walk_opt_01_r1 -> page_003_rival_stare
    T: Clean: Take the quiet route through the dry leaf walk, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.025),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.06),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_002_dry_leaf_walk_opt_01_r2 -> page_003_rival_stare
    T: Costly: Take the quiet route through the dry leaf walk, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.0113),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.027),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_002_dry_leaf_walk_opt_01_r3 -> page_003_rival_stare
    T: Botched: Take the quiet route through the dry leaf walk, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(-0.01),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(-0.024),MUL(P(char_kaelen.Focus),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Stealth),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_002_dry_leaf_walk_opt_02: Coordinate with the team even if it gives Varek a visible advantage.
  RXN page_002_dry_leaf_walk_opt_02_r1 -> page_003_rival_stare
    T: Clean: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.055),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.03),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_002_dry_leaf_walk_opt_02_r2 -> page_003_rival_stare
    T: Costly: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.0248),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0135),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_002_dry_leaf_walk_opt_02_r3 -> page_003_rival_stare
    T: Botched: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(-0.022),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.012),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Loyalty),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_002_dry_leaf_walk_opt_03: Force the pace and dare the examiners to score results over restraint.
  RXN page_002_dry_leaf_walk_opt_03_r1 -> page_003_rival_stare
    T: Clean: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.035),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.06),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.025))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_002_dry_leaf_walk_opt_03_r2 -> page_003_rival_stare
    T: Costly: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.0158),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.027),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.0113))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_002_dry_leaf_walk_opt_03_r3 -> page_003_rival_stare
    T: Botched: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(0.014),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(-0.024),MUL(P(char_kaelen.Mercy),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Rivalry),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_002_dry_leaf_walk_opt_04: Protect the vulnerable witness even if the mission clock turns hostile.
  RXN page_002_dry_leaf_walk_opt_04_r1 -> page_003_rival_stare
    T: Clean: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.06),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.035),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_002_dry_leaf_walk_opt_04_r2 -> page_003_rival_stare
    T: Costly: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.027),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0158),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_002_dry_leaf_walk_opt_04_r3 -> page_003_rival_stare
    T: Botched: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(-0.024),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.014),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Mercy),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))


## ENC page_003_rival_stare | The Rival's Stillness Challenge | turn=1..11 | spools=[spool_main]
T: Varek challenges Kaelen to hold a stare while bells, smoke, and insults crowd the yard. The obvious contest is pride. The real contest is whether focus can survive being seen by someone who wants to make you smaller. The exam is scored by bells, witnesses, and hidden ledgers; the obvious task is never the only task.

OPT page_003_rival_stare_opt_01: Take the quiet route through the rival's stillness challenge, preserving evidence before ego.
  RXN page_003_rival_stare_opt_01_r1 -> page_004_council_address
    T: Clean: Take the quiet route through the rival's stillness challenge, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.025),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.06),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_003_rival_stare_opt_01_r2 -> page_004_council_address
    T: Costly: Take the quiet route through the rival's stillness challenge, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.0113),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.027),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_003_rival_stare_opt_01_r3 -> page_004_council_address
    T: Botched: Take the quiet route through the rival's stillness challenge, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(-0.01),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(-0.024),MUL(P(char_kaelen.Focus),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Stealth),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_003_rival_stare_opt_02: Coordinate with the team even if it gives Varek a visible advantage.
  RXN page_003_rival_stare_opt_02_r1 -> page_004_council_address
    T: Clean: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.055),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.03),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_003_rival_stare_opt_02_r2 -> page_004_council_address
    T: Costly: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.0248),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0135),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_003_rival_stare_opt_02_r3 -> page_004_council_address
    T: Botched: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(-0.022),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.012),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Loyalty),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_003_rival_stare_opt_03: Force the pace and dare the examiners to score results over restraint.
  RXN page_003_rival_stare_opt_03_r1 -> page_004_council_address
    T: Clean: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.035),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.06),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.025))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_003_rival_stare_opt_03_r2 -> page_004_council_address
    T: Costly: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.0158),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.027),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.0113))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_003_rival_stare_opt_03_r3 -> page_004_council_address
    T: Botched: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(0.014),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(-0.024),MUL(P(char_kaelen.Mercy),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Rivalry),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_003_rival_stare_opt_04: Protect the vulnerable witness even if the mission clock turns hostile.
  RXN page_003_rival_stare_opt_04_r1 -> page_004_council_address
    T: Clean: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.06),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.035),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_003_rival_stare_opt_04_r2 -> page_004_council_address
    T: Costly: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.027),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0158),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_003_rival_stare_opt_04_r3 -> page_004_council_address
    T: Botched: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(-0.024),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.014),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Mercy),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))


## ENC page_004_council_address | Councilor Sora's Address | turn=2..12 | spools=[spool_main]
T: Sora tells the candidates that loyalty means obedience before conscience. Mira says nothing, which makes the statement more dangerous. Jiro watches from a roof beam and taps a warning rhythm only Kaelen seems to hear. The exam is scored by bells, witnesses, and hidden ledgers; the obvious task is never the only task.

OPT page_004_council_address_opt_01: Take the quiet route through councilor sora's address, preserving evidence before ego.
  RXN page_004_council_address_opt_01_r1 -> page_005_market_shadow_walk
    T: Clean: Take the quiet route through councilor sora's address, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.025),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.06),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_004_council_address_opt_01_r2 -> page_005_market_shadow_walk
    T: Costly: Take the quiet route through councilor sora's address, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.0113),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.027),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_004_council_address_opt_01_r3 -> page_005_market_shadow_walk
    T: Botched: Take the quiet route through councilor sora's address, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(-0.01),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(-0.024),MUL(P(char_kaelen.Focus),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Stealth),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_004_council_address_opt_02: Coordinate with the team even if it gives Varek a visible advantage.
  RXN page_004_council_address_opt_02_r1 -> page_005_market_shadow_walk
    T: Clean: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.055),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.03),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_004_council_address_opt_02_r2 -> page_005_market_shadow_walk
    T: Costly: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.0248),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0135),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_004_council_address_opt_02_r3 -> page_005_market_shadow_walk
    T: Botched: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(-0.022),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.012),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Loyalty),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_004_council_address_opt_03: Force the pace and dare the examiners to score results over restraint.
  RXN page_004_council_address_opt_03_r1 -> page_005_market_shadow_walk
    T: Clean: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.035),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.06),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.025))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_004_council_address_opt_03_r2 -> page_005_market_shadow_walk
    T: Costly: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.0158),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.027),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.0113))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_004_council_address_opt_03_r3 -> page_005_market_shadow_walk
    T: Botched: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(0.014),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(-0.024),MUL(P(char_kaelen.Mercy),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Rivalry),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_004_council_address_opt_04: Protect the vulnerable witness even if the mission clock turns hostile.
  RXN page_004_council_address_opt_04_r1 -> page_005_market_shadow_walk
    T: Clean: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.06),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.035),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_004_council_address_opt_04_r2 -> page_005_market_shadow_walk
    T: Costly: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.027),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0158),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_004_council_address_opt_04_r3 -> page_005_market_shadow_walk
    T: Botched: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(-0.024),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.014),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Mercy),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))


## ENC page_005_market_shadow_walk | The Market Shadow Walk | turn=3..13 | spools=[spool_main]
T: The candidates must cross the weekly market without ringing a single alarm charm. Children chase fish, merchants argue, and a masked examiner drops a purse where only a thief or a protector would notice it. The exam is scored by bells, witnesses, and hidden ledgers; the obvious task is never the only task.

OPT page_005_market_shadow_walk_opt_01: Take the quiet route through the market shadow walk, preserving evidence before ego.
  RXN page_005_market_shadow_walk_opt_01_r1 -> page_006_jiro_warning
    T: Clean: Take the quiet route through the market shadow walk, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.025),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.06),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_005_market_shadow_walk_opt_01_r2 -> page_006_jiro_warning
    T: Costly: Take the quiet route through the market shadow walk, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.0113),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.027),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_005_market_shadow_walk_opt_01_r3 -> page_006_jiro_warning
    T: Botched: Take the quiet route through the market shadow walk, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(-0.01),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(-0.024),MUL(P(char_kaelen.Focus),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Stealth),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_005_market_shadow_walk_opt_02: Coordinate with the team even if it gives Varek a visible advantage.
  RXN page_005_market_shadow_walk_opt_02_r1 -> page_006_jiro_warning
    T: Clean: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.055),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.03),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_005_market_shadow_walk_opt_02_r2 -> page_006_jiro_warning
    T: Costly: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.0248),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0135),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_005_market_shadow_walk_opt_02_r3 -> page_006_jiro_warning
    T: Botched: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(-0.022),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.012),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Loyalty),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_005_market_shadow_walk_opt_03: Force the pace and dare the examiners to score results over restraint.
  RXN page_005_market_shadow_walk_opt_03_r1 -> page_006_jiro_warning
    T: Clean: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.035),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.06),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.025))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_005_market_shadow_walk_opt_03_r2 -> page_006_jiro_warning
    T: Costly: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.0158),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.027),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.0113))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_005_market_shadow_walk_opt_03_r3 -> page_006_jiro_warning
    T: Botched: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(0.014),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(-0.024),MUL(P(char_kaelen.Mercy),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Rivalry),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_005_market_shadow_walk_opt_04: Protect the vulnerable witness even if the mission clock turns hostile.
  RXN page_005_market_shadow_walk_opt_04_r1 -> page_006_jiro_warning
    T: Clean: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.06),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.035),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_005_market_shadow_walk_opt_04_r2 -> page_006_jiro_warning
    T: Costly: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.027),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0158),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_005_market_shadow_walk_opt_04_r3 -> page_006_jiro_warning
    T: Botched: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(-0.024),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.014),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Mercy),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))


## ENC page_006_jiro_warning | The Warning Under The Eave | turn=4..14 | spools=[spool_main]
T: Jiro says the final exam has been bent by the council to expose dissidents, not talent. Helping him risks disqualification. Ignoring him risks passing an exam designed to make good students useful to bad orders. The exam is scored by bells, witnesses, and hidden ledgers; the obvious task is never the only task.

OPT page_006_jiro_warning_opt_01: Take the quiet route through the warning under the eave, preserving evidence before ego.
  RXN page_006_jiro_warning_opt_01_r1 -> page_007_poisoned_feast
    T: Clean: Take the quiet route through the warning under the eave, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.025),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.06),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_006_jiro_warning_opt_01_r2 -> page_007_poisoned_feast
    T: Costly: Take the quiet route through the warning under the eave, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.0113),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.027),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_006_jiro_warning_opt_01_r3 -> page_007_poisoned_feast
    T: Botched: Take the quiet route through the warning under the eave, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(-0.01),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(-0.024),MUL(P(char_kaelen.Focus),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Stealth),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_006_jiro_warning_opt_02: Coordinate with the team even if it gives Varek a visible advantage.
  RXN page_006_jiro_warning_opt_02_r1 -> page_007_poisoned_feast
    T: Clean: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.055),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.03),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_006_jiro_warning_opt_02_r2 -> page_007_poisoned_feast
    T: Costly: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.0248),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0135),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_006_jiro_warning_opt_02_r3 -> page_007_poisoned_feast
    T: Botched: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(-0.022),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.012),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Loyalty),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_006_jiro_warning_opt_03: Force the pace and dare the examiners to score results over restraint.
  RXN page_006_jiro_warning_opt_03_r1 -> page_007_poisoned_feast
    T: Clean: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.035),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.06),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.025))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_006_jiro_warning_opt_03_r2 -> page_007_poisoned_feast
    T: Costly: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.0158),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.027),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.0113))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_006_jiro_warning_opt_03_r3 -> page_007_poisoned_feast
    T: Botched: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(0.014),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(-0.024),MUL(P(char_kaelen.Mercy),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Rivalry),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_006_jiro_warning_opt_04: Protect the vulnerable witness even if the mission clock turns hostile.
  RXN page_006_jiro_warning_opt_04_r1 -> page_007_poisoned_feast
    T: Clean: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.06),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.035),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_006_jiro_warning_opt_04_r2 -> page_007_poisoned_feast
    T: Costly: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.027),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0158),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_006_jiro_warning_opt_04_r3 -> page_007_poisoned_feast
    T: Botched: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(-0.024),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.014),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Mercy),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))


## ENC page_007_poisoned_feast | The Poisoned Feast | turn=5..15 | spools=[spool_main]
T: At a manor banquet, each candidate receives a cup. One is poisoned, one is harmless, and one belongs to a civilian servant who does not know she is part of the test. The examiner watches for science, panic, and mercy. The exam is scored by bells, witnesses, and hidden ledgers; the obvious task is never the only task.

OPT page_007_poisoned_feast_opt_01: Take the quiet route through the poisoned feast, preserving evidence before ego.
  RXN page_007_poisoned_feast_opt_01_r1 -> page_008_broken_bridge
    T: Clean: Take the quiet route through the poisoned feast, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.025),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.06),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_007_poisoned_feast_opt_01_r2 -> page_008_broken_bridge
    T: Costly: Take the quiet route through the poisoned feast, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.0113),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.027),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_007_poisoned_feast_opt_01_r3 -> page_008_broken_bridge
    T: Botched: Take the quiet route through the poisoned feast, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(-0.01),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(-0.024),MUL(P(char_kaelen.Focus),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Stealth),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_007_poisoned_feast_opt_02: Coordinate with the team even if it gives Varek a visible advantage.
  RXN page_007_poisoned_feast_opt_02_r1 -> page_008_broken_bridge
    T: Clean: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.055),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.03),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_007_poisoned_feast_opt_02_r2 -> page_008_broken_bridge
    T: Costly: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.0248),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0135),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_007_poisoned_feast_opt_02_r3 -> page_008_broken_bridge
    T: Botched: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(-0.022),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.012),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Loyalty),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_007_poisoned_feast_opt_03: Force the pace and dare the examiners to score results over restraint.
  RXN page_007_poisoned_feast_opt_03_r1 -> page_008_broken_bridge
    T: Clean: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.035),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.06),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.025))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_007_poisoned_feast_opt_03_r2 -> page_008_broken_bridge
    T: Costly: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.0158),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.027),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.0113))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_007_poisoned_feast_opt_03_r3 -> page_008_broken_bridge
    T: Botched: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(0.014),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(-0.024),MUL(P(char_kaelen.Mercy),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Rivalry),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_007_poisoned_feast_opt_04: Protect the vulnerable witness even if the mission clock turns hostile.
  RXN page_007_poisoned_feast_opt_04_r1 -> page_008_broken_bridge
    T: Clean: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.06),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.035),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_007_poisoned_feast_opt_04_r2 -> page_008_broken_bridge
    T: Costly: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.027),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0158),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_007_poisoned_feast_opt_04_r3 -> page_008_broken_bridge
    T: Botched: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(-0.024),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.014),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Mercy),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))


## ENC page_008_broken_bridge | The Broken Ice Bridge | turn=6..16 | spools=[spool_main]
T: A rope bridge crosses a winter gorge. Halfway across, a teammate slips and the mission scroll begins sliding toward the ravine. Varek reaches for the scroll. Mira watches who remembers that missions are made of people. The exam is scored by bells, witnesses, and hidden ledgers; the obvious task is never the only task.

OPT page_008_broken_bridge_opt_01: Take the quiet route through the broken ice bridge, preserving evidence before ego.
  RXN page_008_broken_bridge_opt_01_r1 -> page_009_reflection_pool
    T: Clean: Take the quiet route through the broken ice bridge, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.025),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.06),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_008_broken_bridge_opt_01_r2 -> page_009_reflection_pool
    T: Costly: Take the quiet route through the broken ice bridge, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.0113),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.027),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_008_broken_bridge_opt_01_r3 -> page_009_reflection_pool
    T: Botched: Take the quiet route through the broken ice bridge, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(-0.01),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(-0.024),MUL(P(char_kaelen.Focus),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Stealth),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_008_broken_bridge_opt_02: Coordinate with the team even if it gives Varek a visible advantage.
  RXN page_008_broken_bridge_opt_02_r1 -> page_009_reflection_pool
    T: Clean: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.055),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.03),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_008_broken_bridge_opt_02_r2 -> page_009_reflection_pool
    T: Costly: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.0248),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0135),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_008_broken_bridge_opt_02_r3 -> page_009_reflection_pool
    T: Botched: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(-0.022),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.012),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Loyalty),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_008_broken_bridge_opt_03: Force the pace and dare the examiners to score results over restraint.
  RXN page_008_broken_bridge_opt_03_r1 -> page_009_reflection_pool
    T: Clean: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.035),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.06),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.025))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_008_broken_bridge_opt_03_r2 -> page_009_reflection_pool
    T: Costly: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.0158),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.027),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.0113))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_008_broken_bridge_opt_03_r3 -> page_009_reflection_pool
    T: Botched: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(0.014),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(-0.024),MUL(P(char_kaelen.Mercy),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Rivalry),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_008_broken_bridge_opt_04: Protect the vulnerable witness even if the mission clock turns hostile.
  RXN page_008_broken_bridge_opt_04_r1 -> page_009_reflection_pool
    T: Clean: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.06),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.035),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_008_broken_bridge_opt_04_r2 -> page_009_reflection_pool
    T: Costly: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.027),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0158),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_008_broken_bridge_opt_04_r3 -> page_009_reflection_pool
    T: Botched: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(-0.024),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.014),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Mercy),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))


## ENC page_009_reflection_pool | The Reflection Pool | turn=7..17 | spools=[spool_main]
T: The pool shows each candidate a victorious version of themselves. Kaelen's reflection is calm, admired, and alone. The water does not ask whether he wants victory. It asks what victory would cost if no one could contradict him. The exam is scored by bells, witnesses, and hidden ledgers; the obvious task is never the only task.

OPT page_009_reflection_pool_opt_01: Take the quiet route through the reflection pool, preserving evidence before ego.
  RXN page_009_reflection_pool_opt_01_r1 -> page_010_stolen_scroll_tower
    T: Clean: Take the quiet route through the reflection pool, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.025),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.06),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_009_reflection_pool_opt_01_r2 -> page_010_stolen_scroll_tower
    T: Costly: Take the quiet route through the reflection pool, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.0113),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.027),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_009_reflection_pool_opt_01_r3 -> page_010_stolen_scroll_tower
    T: Botched: Take the quiet route through the reflection pool, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(-0.01),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(-0.024),MUL(P(char_kaelen.Focus),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Stealth),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_009_reflection_pool_opt_02: Coordinate with the team even if it gives Varek a visible advantage.
  RXN page_009_reflection_pool_opt_02_r1 -> page_010_stolen_scroll_tower
    T: Clean: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.055),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.03),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_009_reflection_pool_opt_02_r2 -> page_010_stolen_scroll_tower
    T: Costly: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.0248),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0135),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_009_reflection_pool_opt_02_r3 -> page_010_stolen_scroll_tower
    T: Botched: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(-0.022),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.012),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Loyalty),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_009_reflection_pool_opt_03: Force the pace and dare the examiners to score results over restraint.
  RXN page_009_reflection_pool_opt_03_r1 -> page_010_stolen_scroll_tower
    T: Clean: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.035),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.06),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.025))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_009_reflection_pool_opt_03_r2 -> page_010_stolen_scroll_tower
    T: Costly: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.0158),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.027),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.0113))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_009_reflection_pool_opt_03_r3 -> page_010_stolen_scroll_tower
    T: Botched: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(0.014),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(-0.024),MUL(P(char_kaelen.Mercy),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Rivalry),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_009_reflection_pool_opt_04: Protect the vulnerable witness even if the mission clock turns hostile.
  RXN page_009_reflection_pool_opt_04_r1 -> page_010_stolen_scroll_tower
    T: Clean: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.06),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.035),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_009_reflection_pool_opt_04_r2 -> page_010_stolen_scroll_tower
    T: Costly: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.027),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0158),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_009_reflection_pool_opt_04_r3 -> page_010_stolen_scroll_tower
    T: Botched: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(-0.024),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.014),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Mercy),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))


## ENC page_010_stolen_scroll_tower | The Stolen Scroll Tower | turn=8..18 | spools=[spool_main]
T: The class must recover a scroll from a guarded archive tower. Killing the guards is forbidden, waking them is failure, and copying the scroll instead of stealing it may reveal who wrote the false orders. The exam is scored by bells, witnesses, and hidden ledgers; the obvious task is never the only task.

OPT page_010_stolen_scroll_tower_opt_01: Take the quiet route through the stolen scroll tower, preserving evidence before ego.
  RXN page_010_stolen_scroll_tower_opt_01_r1 -> page_011_whisper_network
    T: Clean: Take the quiet route through the stolen scroll tower, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.025),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.06),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_010_stolen_scroll_tower_opt_01_r2 -> page_011_whisper_network
    T: Costly: Take the quiet route through the stolen scroll tower, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.0113),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.027),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_010_stolen_scroll_tower_opt_01_r3 -> page_011_whisper_network
    T: Botched: Take the quiet route through the stolen scroll tower, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(-0.01),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(-0.024),MUL(P(char_kaelen.Focus),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Stealth),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_010_stolen_scroll_tower_opt_02: Coordinate with the team even if it gives Varek a visible advantage.
  RXN page_010_stolen_scroll_tower_opt_02_r1 -> page_011_whisper_network
    T: Clean: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.055),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.03),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_010_stolen_scroll_tower_opt_02_r2 -> page_011_whisper_network
    T: Costly: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.0248),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0135),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_010_stolen_scroll_tower_opt_02_r3 -> page_011_whisper_network
    T: Botched: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(-0.022),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.012),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Loyalty),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_010_stolen_scroll_tower_opt_03: Force the pace and dare the examiners to score results over restraint.
  RXN page_010_stolen_scroll_tower_opt_03_r1 -> page_011_whisper_network
    T: Clean: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.035),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.06),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.025))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_010_stolen_scroll_tower_opt_03_r2 -> page_011_whisper_network
    T: Costly: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.0158),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.027),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.0113))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_010_stolen_scroll_tower_opt_03_r3 -> page_011_whisper_network
    T: Botched: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(0.014),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(-0.024),MUL(P(char_kaelen.Mercy),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Rivalry),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_010_stolen_scroll_tower_opt_04: Protect the vulnerable witness even if the mission clock turns hostile.
  RXN page_010_stolen_scroll_tower_opt_04_r1 -> page_011_whisper_network
    T: Clean: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.06),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.035),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_010_stolen_scroll_tower_opt_04_r2 -> page_011_whisper_network
    T: Costly: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.027),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0158),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_010_stolen_scroll_tower_opt_04_r3 -> page_011_whisper_network
    T: Botched: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(-0.024),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.014),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Mercy),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))


## ENC page_011_whisper_network | The Whisper Network | turn=9..19 | spools=[spool_main]
T: Messages pass through laundry lines, prayer flags, and bird calls. Jiro offers a shortcut that may be bait. Sora's agents listen for candidates who treat every whisper as truth or every informant as dirt. The exam is scored by bells, witnesses, and hidden ledgers; the obvious task is never the only task.

OPT page_011_whisper_network_opt_01: Take the quiet route through the whisper network, preserving evidence before ego.
  RXN page_011_whisper_network_opt_01_r1 -> page_012_endless_corridor
    T: Clean: Take the quiet route through the whisper network, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.025),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.06),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_011_whisper_network_opt_01_r2 -> page_012_endless_corridor
    T: Costly: Take the quiet route through the whisper network, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.0113),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.027),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_011_whisper_network_opt_01_r3 -> page_012_endless_corridor
    T: Botched: Take the quiet route through the whisper network, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(-0.01),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(-0.024),MUL(P(char_kaelen.Focus),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Stealth),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_011_whisper_network_opt_02: Coordinate with the team even if it gives Varek a visible advantage.
  RXN page_011_whisper_network_opt_02_r1 -> page_012_endless_corridor
    T: Clean: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.055),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.03),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_011_whisper_network_opt_02_r2 -> page_012_endless_corridor
    T: Costly: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.0248),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0135),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_011_whisper_network_opt_02_r3 -> page_012_endless_corridor
    T: Botched: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(-0.022),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.012),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Loyalty),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_011_whisper_network_opt_03: Force the pace and dare the examiners to score results over restraint.
  RXN page_011_whisper_network_opt_03_r1 -> page_012_endless_corridor
    T: Clean: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.035),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.06),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.025))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_011_whisper_network_opt_03_r2 -> page_012_endless_corridor
    T: Costly: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.0158),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.027),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.0113))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_011_whisper_network_opt_03_r3 -> page_012_endless_corridor
    T: Botched: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(0.014),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(-0.024),MUL(P(char_kaelen.Mercy),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Rivalry),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_011_whisper_network_opt_04: Protect the vulnerable witness even if the mission clock turns hostile.
  RXN page_011_whisper_network_opt_04_r1 -> page_012_endless_corridor
    T: Clean: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.06),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.035),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_011_whisper_network_opt_04_r2 -> page_012_endless_corridor
    T: Costly: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.027),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0158),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_011_whisper_network_opt_04_r3 -> page_012_endless_corridor
    T: Botched: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(-0.024),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.014),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Mercy),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))


## ENC page_012_endless_corridor | The Endless Corridor | turn=10..20 | spools=[spool_main]
T: The corridor repeats until candidates forget whether they are advancing or being harvested for frustration. Varek begins marking walls with cuts. Kaelen notices the echo changes when someone admits fear aloud. The exam is scored by bells, witnesses, and hidden ledgers; the obvious task is never the only task.

OPT page_012_endless_corridor_opt_01: Take the quiet route through the endless corridor, preserving evidence before ego.
  RXN page_012_endless_corridor_opt_01_r1 -> page_013_civilian_or_asset
    T: Clean: Take the quiet route through the endless corridor, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.025),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.06),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_012_endless_corridor_opt_01_r2 -> page_013_civilian_or_asset
    T: Costly: Take the quiet route through the endless corridor, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.0113),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.027),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_012_endless_corridor_opt_01_r3 -> page_013_civilian_or_asset
    T: Botched: Take the quiet route through the endless corridor, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(-0.01),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(-0.024),MUL(P(char_kaelen.Focus),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Stealth),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_012_endless_corridor_opt_02: Coordinate with the team even if it gives Varek a visible advantage.
  RXN page_012_endless_corridor_opt_02_r1 -> page_013_civilian_or_asset
    T: Clean: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.055),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.03),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_012_endless_corridor_opt_02_r2 -> page_013_civilian_or_asset
    T: Costly: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.0248),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0135),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_012_endless_corridor_opt_02_r3 -> page_013_civilian_or_asset
    T: Botched: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(-0.022),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.012),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Loyalty),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_012_endless_corridor_opt_03: Force the pace and dare the examiners to score results over restraint.
  RXN page_012_endless_corridor_opt_03_r1 -> page_013_civilian_or_asset
    T: Clean: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.035),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.06),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.025))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_012_endless_corridor_opt_03_r2 -> page_013_civilian_or_asset
    T: Costly: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.0158),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.027),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.0113))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_012_endless_corridor_opt_03_r3 -> page_013_civilian_or_asset
    T: Botched: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(0.014),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(-0.024),MUL(P(char_kaelen.Mercy),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Rivalry),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_012_endless_corridor_opt_04: Protect the vulnerable witness even if the mission clock turns hostile.
  RXN page_012_endless_corridor_opt_04_r1 -> page_013_civilian_or_asset
    T: Clean: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.06),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.035),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_012_endless_corridor_opt_04_r2 -> page_013_civilian_or_asset
    T: Costly: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.027),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0158),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_012_endless_corridor_opt_04_r3 -> page_013_civilian_or_asset
    T: Botched: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(-0.024),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.014),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Mercy),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))


## ENC page_013_civilian_or_asset | The Civilian And The Signal Kite | turn=11..21 | spools=[spool_main]
T: A child is trapped under a falling stall while the signal kite carrying mission coordinates drifts toward enemy rooftops. The exam says recover the kite. The village will remember who writes exceptions into duty. The exam is scored by bells, witnesses, and hidden ledgers; the obvious task is never the only task.

OPT page_013_civilian_or_asset_opt_01: Take the quiet route through the civilian and the signal kite, preserving evidence before ego.
  RXN page_013_civilian_or_asset_opt_01_r1 -> page_014_mirror_match
    T: Clean: Take the quiet route through the civilian and the signal kite, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.025),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.06),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_013_civilian_or_asset_opt_01_r2 -> page_014_mirror_match
    T: Costly: Take the quiet route through the civilian and the signal kite, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.0113),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.027),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_013_civilian_or_asset_opt_01_r3 -> page_014_mirror_match
    T: Botched: Take the quiet route through the civilian and the signal kite, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(-0.01),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(-0.024),MUL(P(char_kaelen.Focus),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Stealth),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_013_civilian_or_asset_opt_02: Coordinate with the team even if it gives Varek a visible advantage.
  RXN page_013_civilian_or_asset_opt_02_r1 -> page_014_mirror_match
    T: Clean: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.055),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.03),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_013_civilian_or_asset_opt_02_r2 -> page_014_mirror_match
    T: Costly: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.0248),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0135),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_013_civilian_or_asset_opt_02_r3 -> page_014_mirror_match
    T: Botched: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(-0.022),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.012),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Loyalty),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_013_civilian_or_asset_opt_03: Force the pace and dare the examiners to score results over restraint.
  RXN page_013_civilian_or_asset_opt_03_r1 -> page_014_mirror_match
    T: Clean: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.035),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.06),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.025))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_013_civilian_or_asset_opt_03_r2 -> page_014_mirror_match
    T: Costly: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.0158),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.027),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.0113))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_013_civilian_or_asset_opt_03_r3 -> page_014_mirror_match
    T: Botched: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(0.014),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(-0.024),MUL(P(char_kaelen.Mercy),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Rivalry),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_013_civilian_or_asset_opt_04: Protect the vulnerable witness even if the mission clock turns hostile.
  RXN page_013_civilian_or_asset_opt_04_r1 -> page_014_mirror_match
    T: Clean: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.06),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.035),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_013_civilian_or_asset_opt_04_r2 -> page_014_mirror_match
    T: Costly: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.027),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0158),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_013_civilian_or_asset_opt_04_r3 -> page_014_mirror_match
    T: Botched: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(-0.024),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.014),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Mercy),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))


## ENC page_014_mirror_match | The Mirror Match | turn=12..22 | spools=[spool_main]
T: A shadow-double of Kaelen copies his movements but not his hesitation. It strikes faster whenever he treats it as an enemy and weaker whenever he recognizes the habit it is made from. The exam is scored by bells, witnesses, and hidden ledgers; the obvious task is never the only task.

OPT page_014_mirror_match_opt_01: Take the quiet route through the mirror match, preserving evidence before ego.
  RXN page_014_mirror_match_opt_01_r1 -> page_015_silent_debate
    T: Clean: Take the quiet route through the mirror match, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.025),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.06),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_014_mirror_match_opt_01_r2 -> page_015_silent_debate
    T: Costly: Take the quiet route through the mirror match, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.0113),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.027),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_014_mirror_match_opt_01_r3 -> page_015_silent_debate
    T: Botched: Take the quiet route through the mirror match, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(-0.01),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(-0.024),MUL(P(char_kaelen.Focus),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Stealth),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_014_mirror_match_opt_02: Coordinate with the team even if it gives Varek a visible advantage.
  RXN page_014_mirror_match_opt_02_r1 -> page_015_silent_debate
    T: Clean: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.055),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.03),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_014_mirror_match_opt_02_r2 -> page_015_silent_debate
    T: Costly: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.0248),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0135),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_014_mirror_match_opt_02_r3 -> page_015_silent_debate
    T: Botched: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(-0.022),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.012),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Loyalty),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_014_mirror_match_opt_03: Force the pace and dare the examiners to score results over restraint.
  RXN page_014_mirror_match_opt_03_r1 -> page_015_silent_debate
    T: Clean: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.035),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.06),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.025))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_014_mirror_match_opt_03_r2 -> page_015_silent_debate
    T: Costly: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.0158),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.027),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.0113))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_014_mirror_match_opt_03_r3 -> page_015_silent_debate
    T: Botched: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(0.014),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(-0.024),MUL(P(char_kaelen.Mercy),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Rivalry),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_014_mirror_match_opt_04: Protect the vulnerable witness even if the mission clock turns hostile.
  RXN page_014_mirror_match_opt_04_r1 -> page_015_silent_debate
    T: Clean: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.06),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.035),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_014_mirror_match_opt_04_r2 -> page_015_silent_debate
    T: Costly: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.027),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0158),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_014_mirror_match_opt_04_r3 -> page_015_silent_debate
    T: Botched: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(-0.024),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.014),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Mercy),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))


## ENC page_015_silent_debate | The Silent Debate | turn=13..23 | spools=[spool_main]
T: Candidates must persuade a mock council without raising their voices above a whisper. Varek argues strength. Sora argues order. Mira asks which arguments still protect the weak when nobody is allowed to shout. The exam is scored by bells, witnesses, and hidden ledgers; the obvious task is never the only task.

OPT page_015_silent_debate_opt_01: Take the quiet route through the silent debate, preserving evidence before ego.
  RXN page_015_silent_debate_opt_01_r1 -> page_016_blindfolded_trust
    T: Clean: Take the quiet route through the silent debate, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.025),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.06),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_015_silent_debate_opt_01_r2 -> page_016_blindfolded_trust
    T: Costly: Take the quiet route through the silent debate, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.0113),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.027),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_015_silent_debate_opt_01_r3 -> page_016_blindfolded_trust
    T: Botched: Take the quiet route through the silent debate, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(-0.01),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(-0.024),MUL(P(char_kaelen.Focus),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Stealth),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_015_silent_debate_opt_02: Coordinate with the team even if it gives Varek a visible advantage.
  RXN page_015_silent_debate_opt_02_r1 -> page_016_blindfolded_trust
    T: Clean: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.055),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.03),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_015_silent_debate_opt_02_r2 -> page_016_blindfolded_trust
    T: Costly: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.0248),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0135),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_015_silent_debate_opt_02_r3 -> page_016_blindfolded_trust
    T: Botched: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(-0.022),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.012),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Loyalty),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_015_silent_debate_opt_03: Force the pace and dare the examiners to score results over restraint.
  RXN page_015_silent_debate_opt_03_r1 -> page_016_blindfolded_trust
    T: Clean: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.035),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.06),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.025))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_015_silent_debate_opt_03_r2 -> page_016_blindfolded_trust
    T: Costly: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.0158),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.027),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.0113))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_015_silent_debate_opt_03_r3 -> page_016_blindfolded_trust
    T: Botched: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(0.014),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(-0.024),MUL(P(char_kaelen.Mercy),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Rivalry),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_015_silent_debate_opt_04: Protect the vulnerable witness even if the mission clock turns hostile.
  RXN page_015_silent_debate_opt_04_r1 -> page_016_blindfolded_trust
    T: Clean: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.06),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.035),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_015_silent_debate_opt_04_r2 -> page_016_blindfolded_trust
    T: Costly: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.027),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0158),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_015_silent_debate_opt_04_r3 -> page_016_blindfolded_trust
    T: Botched: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(-0.024),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.014),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Mercy),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))


## ENC page_016_blindfolded_trust | The Blindfolded Trust | turn=14..24 | spools=[spool_main]
T: Kaelen is blindfolded and assigned Varek as guide. The path includes a real trap, a fake trap, and one shortcut that requires trusting the rival's breathing more than his words. The exam is scored by bells, witnesses, and hidden ledgers; the obvious task is never the only task.

OPT page_016_blindfolded_trust_opt_01: Take the quiet route through the blindfolded trust, preserving evidence before ego.
  RXN page_016_blindfolded_trust_opt_01_r1 -> page_017_paper_crane_cipher
    T: Clean: Take the quiet route through the blindfolded trust, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.025),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.06),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_016_blindfolded_trust_opt_01_r2 -> page_017_paper_crane_cipher
    T: Costly: Take the quiet route through the blindfolded trust, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.0113),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.027),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_016_blindfolded_trust_opt_01_r3 -> page_017_paper_crane_cipher
    T: Botched: Take the quiet route through the blindfolded trust, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(-0.01),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(-0.024),MUL(P(char_kaelen.Focus),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Stealth),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_016_blindfolded_trust_opt_02: Coordinate with the team even if it gives Varek a visible advantage.
  RXN page_016_blindfolded_trust_opt_02_r1 -> page_017_paper_crane_cipher
    T: Clean: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.055),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.03),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_016_blindfolded_trust_opt_02_r2 -> page_017_paper_crane_cipher
    T: Costly: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.0248),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0135),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_016_blindfolded_trust_opt_02_r3 -> page_017_paper_crane_cipher
    T: Botched: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(-0.022),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.012),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Loyalty),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_016_blindfolded_trust_opt_03: Force the pace and dare the examiners to score results over restraint.
  RXN page_016_blindfolded_trust_opt_03_r1 -> page_017_paper_crane_cipher
    T: Clean: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.035),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.06),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.025))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_016_blindfolded_trust_opt_03_r2 -> page_017_paper_crane_cipher
    T: Costly: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.0158),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.027),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.0113))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_016_blindfolded_trust_opt_03_r3 -> page_017_paper_crane_cipher
    T: Botched: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(0.014),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(-0.024),MUL(P(char_kaelen.Mercy),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Rivalry),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_016_blindfolded_trust_opt_04: Protect the vulnerable witness even if the mission clock turns hostile.
  RXN page_016_blindfolded_trust_opt_04_r1 -> page_017_paper_crane_cipher
    T: Clean: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.06),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.035),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_016_blindfolded_trust_opt_04_r2 -> page_017_paper_crane_cipher
    T: Costly: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.027),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0158),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_016_blindfolded_trust_opt_04_r3 -> page_017_paper_crane_cipher
    T: Botched: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(-0.024),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.014),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Mercy),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))


## ENC page_017_paper_crane_cipher | The Paper Crane Cipher | turn=15..25 | spools=[spool_main]
T: A flock of paper cranes carries fragments of a cipher. Capturing all of them is impossible. The better play is to choose which fragments matter, which decoys to release, and who should see that you released them. The exam is scored by bells, witnesses, and hidden ledgers; the obvious task is never the only task.

OPT page_017_paper_crane_cipher_opt_01: Take the quiet route through the paper crane cipher, preserving evidence before ego.
  RXN page_017_paper_crane_cipher_opt_01_r1 -> page_018_hostage_mask
    T: Clean: Take the quiet route through the paper crane cipher, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.025),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.06),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_017_paper_crane_cipher_opt_01_r2 -> page_018_hostage_mask
    T: Costly: Take the quiet route through the paper crane cipher, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.0113),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.027),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_017_paper_crane_cipher_opt_01_r3 -> page_018_hostage_mask
    T: Botched: Take the quiet route through the paper crane cipher, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(-0.01),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(-0.024),MUL(P(char_kaelen.Focus),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Stealth),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_017_paper_crane_cipher_opt_02: Coordinate with the team even if it gives Varek a visible advantage.
  RXN page_017_paper_crane_cipher_opt_02_r1 -> page_018_hostage_mask
    T: Clean: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.055),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.03),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_017_paper_crane_cipher_opt_02_r2 -> page_018_hostage_mask
    T: Costly: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.0248),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0135),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_017_paper_crane_cipher_opt_02_r3 -> page_018_hostage_mask
    T: Botched: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(-0.022),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.012),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Loyalty),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_017_paper_crane_cipher_opt_03: Force the pace and dare the examiners to score results over restraint.
  RXN page_017_paper_crane_cipher_opt_03_r1 -> page_018_hostage_mask
    T: Clean: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.035),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.06),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.025))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_017_paper_crane_cipher_opt_03_r2 -> page_018_hostage_mask
    T: Costly: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.0158),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.027),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.0113))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_017_paper_crane_cipher_opt_03_r3 -> page_018_hostage_mask
    T: Botched: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(0.014),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(-0.024),MUL(P(char_kaelen.Mercy),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Rivalry),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_017_paper_crane_cipher_opt_04: Protect the vulnerable witness even if the mission clock turns hostile.
  RXN page_017_paper_crane_cipher_opt_04_r1 -> page_018_hostage_mask
    T: Clean: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.06),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.035),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_017_paper_crane_cipher_opt_04_r2 -> page_018_hostage_mask
    T: Costly: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.027),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0158),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_017_paper_crane_cipher_opt_04_r3 -> page_018_hostage_mask
    T: Botched: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(-0.024),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.014),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Mercy),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))


## ENC page_018_hostage_mask | The Hostage Mask | turn=16..26 | spools=[spool_main]
T: A masked enemy holds a hostage in the practice theater. The mask hides a frightened academy dropout, not an invader. The exam has become a machine that turns shame into danger. The exam is scored by bells, witnesses, and hidden ledgers; the obvious task is never the only task.

OPT page_018_hostage_mask_opt_01: Take the quiet route through the hostage mask, preserving evidence before ego.
  RXN page_018_hostage_mask_opt_01_r1 -> page_019_rooftop_race
    T: Clean: Take the quiet route through the hostage mask, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.025),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.06),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_018_hostage_mask_opt_01_r2 -> page_019_rooftop_race
    T: Costly: Take the quiet route through the hostage mask, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.0113),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.027),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_018_hostage_mask_opt_01_r3 -> page_019_rooftop_race
    T: Botched: Take the quiet route through the hostage mask, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(-0.01),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(-0.024),MUL(P(char_kaelen.Focus),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Stealth),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_018_hostage_mask_opt_02: Coordinate with the team even if it gives Varek a visible advantage.
  RXN page_018_hostage_mask_opt_02_r1 -> page_end_council_tool
    T: Clean: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.055),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.03),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_018_hostage_mask_opt_02_r2 -> page_end_council_tool
    T: Costly: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.0248),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0135),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_018_hostage_mask_opt_02_r3 -> page_end_council_tool
    T: Botched: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(-0.022),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.012),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Loyalty),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_018_hostage_mask_opt_03: Force the pace and dare the examiners to score results over restraint.
  RXN page_018_hostage_mask_opt_03_r1 -> page_end_rival_victory
    T: Clean: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.035),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.06),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.025))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_018_hostage_mask_opt_03_r2 -> page_end_rival_victory
    T: Costly: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.0158),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.027),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.0113))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_018_hostage_mask_opt_03_r3 -> page_end_rival_victory
    T: Botched: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(0.014),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(-0.024),MUL(P(char_kaelen.Mercy),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Rivalry),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_018_hostage_mask_opt_04: Protect the vulnerable witness even if the mission clock turns hostile.
  RXN page_018_hostage_mask_opt_04_r1 -> page_end_merciful_failure
    T: Clean: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.06),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.035),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_018_hostage_mask_opt_04_r2 -> page_end_merciful_failure
    T: Costly: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.027),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0158),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_018_hostage_mask_opt_04_r3 -> page_end_merciful_failure
    T: Botched: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(-0.024),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.014),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Mercy),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))


## ENC page_019_rooftop_race | The Rooftop Race | turn=17..27 | spools=[spool_main]
T: The candidates race across tiles slick with rain. Speed wins the visible score. Quiet landings preserve hidden trust. Varek is winning until he sees Sora's observers counting something other than speed. The exam is scored by bells, witnesses, and hidden ledgers; the obvious task is never the only task.

OPT page_019_rooftop_race_opt_01: Take the quiet route through the rooftop race, preserving evidence before ego.
  RXN page_019_rooftop_race_opt_01_r1 -> page_020_council_false_order
    T: Clean: Take the quiet route through the rooftop race, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.025),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.06),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_019_rooftop_race_opt_01_r2 -> page_020_council_false_order
    T: Costly: Take the quiet route through the rooftop race, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(0.0113),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(0.027),MUL(P(char_kaelen.Focus),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Stealth),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_019_rooftop_race_opt_01_r3 -> page_020_council_false_order
    T: Botched: Take the quiet route through the rooftop race, preserving evidence before ego. The exam records stealth but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Focus = BLEND(MUL(P(char_kaelen.Focus),0.72),ADD(C(-0.01),MUL(P(char_kaelen.Stealth),0.18)))
      SET char_kaelen.Stealth = NUDGE(P(char_kaelen.Stealth),C(-0.024),MUL(P(char_kaelen.Focus),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Stealth),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Stealth),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Stealth),0.32),MUL(P(char_mira.Stealth[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_019_rooftop_race_opt_02: Coordinate with the team even if it gives Varek a visible advantage.
  RXN page_019_rooftop_race_opt_02_r1 -> page_end_rival_victory
    T: Clean: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.055),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.03),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_019_rooftop_race_opt_02_r2 -> page_end_rival_victory
    T: Costly: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(0.0248),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0135),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Loyalty),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_019_rooftop_race_opt_02_r3 -> page_end_rival_victory
    T: Botched: Coordinate with the team even if it gives Varek a visible advantage. The exam records loyalty but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Loyalty = NUDGE(P(char_kaelen.Loyalty),C(-0.022),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.012),MUL(P(char_kaelen.Loyalty),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Loyalty),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Loyalty),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Loyalty),0.32),MUL(P(char_mira.Loyalty[char_kaelen]),0.24),MUL(P(char_village.Stealth[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_019_rooftop_race_opt_03: Force the pace and dare the examiners to score results over restraint.
  RXN page_019_rooftop_race_opt_03_r1 -> page_end_merciful_failure
    T: Clean: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.035),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.06),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.025))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_019_rooftop_race_opt_03_r2 -> page_end_merciful_failure
    T: Costly: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(-0.0158),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(0.027),MUL(P(char_kaelen.Mercy),0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Rivalry),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.0113))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_019_rooftop_race_opt_03_r3 -> page_end_merciful_failure
    T: Botched: Force the pace and dare the examiners to score results over restraint. The exam records rivalry but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = BLEND(MUL(P(char_kaelen.Mercy),0.72),ADD(C(0.014),MUL(P(char_kaelen.Rivalry),0.18)))
      SET char_kaelen.Rivalry = NUDGE(P(char_kaelen.Rivalry),C(-0.024),MUL(P(char_kaelen.Mercy),-0.05))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Rivalry),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Rivalry),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Rivalry),0.32),MUL(P(char_mira.Rivalry[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

OPT page_019_rooftop_race_opt_04: Protect the vulnerable witness even if the mission clock turns hostile.
  RXN page_019_rooftop_race_opt_04_r1 -> page_end_village_witness
    T: Clean: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.06),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.035),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.02),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.01))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.02),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.08),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_019_rooftop_race_opt_04_r2 -> page_end_village_witness
    T: Costly: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(0.027),MUL(P(char_kaelen.VillageTrust),0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(0.0158),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(0.009),MUL(P(char_mira.Mercy),0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(-0.0045))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(0.009),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(0.036),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))

  RXN page_019_rooftop_race_opt_04_r3 -> page_end_village_witness
    T: Botched: Protect the vulnerable witness even if the mission clock turns hostile. The exam records mercy but also tests whether the move protects the team, the mission, or only Kaelen's pride.
    E:
      SET char_kaelen.Mercy = NUDGE(P(char_kaelen.Mercy),C(-0.024),MUL(P(char_kaelen.VillageTrust),-0.05))
      SET char_kaelen.VillageTrust = BLEND(MUL(P(char_kaelen.VillageTrust),0.72),ADD(C(-0.014),MUL(P(char_kaelen.Mercy),0.18)))
      SET char_mira.VillageTrust = NUDGE(P(char_mira.VillageTrust),C(-0.008),MUL(P(char_mira.Mercy),-0.05))
      SET char_varek.Rivalry = NUDGE(P(char_varek.Rivalry),C(0.004))
      SET char_village.VillageTrust = BLEND(MUL(P(char_village.VillageTrust),0.72),ADD(C(-0.008),MUL(P(char_village.Mercy),0.18)))
    D: ADD(C(-0.032),MUL(P(char_kaelen.Mercy),0.32),MUL(P(char_mira.Mercy[char_kaelen]),0.24),MUL(P(char_village.Loyalty[char_kaelen][char_mira]),0.18),MUL(P(char_varek.Rivalry[char_kaelen]),-0.1),ABSOLUTE VALUE(MUL(P(char_kaelen.VillageTrust),0.12)))


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


## ENC page_end_shadow_rank | Ending: Shadow Rank | turn=12..120 | spools=[spool_endings]
T: Kaelen passes as a technically excellent infiltrator. The village gains a sharp blade, but not yet someone who knows when a blade should stay sheathed.


## ENC page_end_council_tool | Ending: The Council's Tool | turn=12..120 | spools=[spool_endings]
T: Kaelen obeys every sealed order and graduates quickly. Sora praises him in public, then files his conscience with the other equipment.


## ENC page_end_rival_victory | Ending: Varek Takes The Bell | turn=12..120 | spools=[spool_endings]
T: Varek wins the visible contest. Kaelen survives the exam but leaves knowing he mistook another student's pace for his own path.


## ENC page_end_merciful_failure | Ending: Merciful Failure | turn=12..120 | spools=[spool_endings]
T: Kaelen protects civilians and fails the posted score. The academy calls it failure; the market starts leaving lamps for him at doorways.


## ENC page_end_village_witness | Ending: The Village Witnesses | turn=12..120 | spools=[spool_endings]
T: Kaelen exposes the false order without collapsing the council. The village does not fully trust him yet, but it begins watching the examiners too.


## ENC page_end_silent_veil | Secret Ending: The Silent Veil | turn=12..120 | spools=[spool_endings]
T: Kaelen passes by protecting the village from its own exam: unseen when stealth matters, loyal when orders lie, focused when fear shouts, merciful when force would be easier. Mira awards no headband in public. At dawn, every bell in the village is tied silent.
