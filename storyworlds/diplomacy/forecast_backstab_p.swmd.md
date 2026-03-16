# SWMD-0
id: 0409710a-071d-4b01-b3dd-3821aca362e4
title: Forecast Backstab (p)
theme: diplomacy_forecast
about: Justify a coordinated pre-emptive strike against a partner.
cast: power_austria, power_england, power_france, power_germany, power_italy, power_russia, power_turkey
props: Trust, Threat
spools:
  spool_main: enc_turn_1 enc_turn_2 enc_turn_3 enc_turn_4 enc_turn_5 enc_turn_6 enc_turn_7
  spool_endings: enc_ending_1 enc_ending_2 enc_ending_3

## ENC enc_turn_1 | Turn 1: Forecast Offer | turn=0..0 | spools=[spool_main]
T: A forecast is presented for turn 1. The proposal ties outcomes to a coalition choice.

OPT opt_1_1: Accept a forecast-backed alliance proposal.
  RXN rxn_1_1_a -> enc_turn_2
    T: The coalition shifts as the proposal lands. Accept a forecast-backed alliance proposal. sends a strong signal.
    E:
      SET power_england.Threat += -0.1
      SET power_england.Trust += 0.2
      SET power_england.pThreat[power_austria] += -0.06
      SET power_england.pTrust[power_austria] += 0.12
    D: ADD(C(0.4),P(power_england.pTrust[power_austria]),P(power_austria.pTrust[power_england]),P(power_england.pTrust[power_austria][power_france]))

  RXN rxn_1_1_b -> enc_turn_2
    T: The forecasted risk materializes as hesitation spreads; rivals exploit the gap.
    E:
      SET power_england.Threat += 0.2
      SET power_england.Trust += -0.15
      SET power_england.pThreat[power_austria] += 0.06
      SET power_england.pTrust[power_austria] += -0.12
    D: ADD(ADD(C(0.2),P(power_england.pThreat[power_austria]),P(power_austria.pThreat[power_england]),P(power_england.pThreat[power_austria][power_france])),P(power_england.pTrust[power_austria]),P(power_austria.pTrust[power_england]),P(power_england.pTrust[power_austria][power_france]))

OPT opt_1_2: Accept a coordinated backstab plan.
  RXN rxn_1_2_a -> enc_turn_2
    T: The coalition shifts as the proposal lands. Accept a coordinated backstab plan. sends a strong signal.
    E:
      SET power_england.Threat += -0.1
      SET power_england.Trust += 0.2
      SET power_england.pThreat[power_austria] += -0.06
      SET power_england.pTrust[power_austria] += 0.12
    D: ADD(C(0.4),P(power_england.pTrust[power_austria]),P(power_austria.pTrust[power_england]),P(power_england.pTrust[power_austria][power_france]))

  RXN rxn_1_2_b -> enc_turn_2
    T: The forecasted risk materializes as hesitation spreads; rivals exploit the gap.
    E:
      SET power_england.Threat += 0.2
      SET power_england.Trust += -0.15
      SET power_england.pThreat[power_austria] += 0.06
      SET power_england.pTrust[power_austria] += -0.12
    D: ADD(ADD(C(0.2),P(power_england.pThreat[power_austria]),P(power_austria.pThreat[power_england]),P(power_england.pThreat[power_austria][power_france])),P(power_england.pTrust[power_austria]),P(power_austria.pTrust[power_england]),P(power_england.pTrust[power_austria][power_france]))

OPT opt_1_3: Defect from a coalition without direct betrayal.
  RXN rxn_1_3_a -> enc_turn_2
    T: The coalition shifts as the proposal lands. Defect from a coalition without direct betrayal. sends a strong signal.
    E:
      SET power_england.Threat += -0.1
      SET power_england.Trust += 0.2
      SET power_england.pThreat[power_austria] += -0.06
      SET power_england.pTrust[power_austria] += 0.12
    D: ADD(C(0.4),P(power_england.pTrust[power_austria]),P(power_austria.pTrust[power_england]),P(power_england.pTrust[power_austria][power_france]))

  RXN rxn_1_3_b -> enc_turn_2
    T: The forecasted risk materializes as hesitation spreads; rivals exploit the gap.
    E:
      SET power_england.Threat += 0.2
      SET power_england.Trust += -0.15
      SET power_england.pThreat[power_austria] += 0.06
      SET power_england.pTrust[power_austria] += -0.12
    D: ADD(ADD(C(0.2),P(power_england.pThreat[power_austria]),P(power_austria.pThreat[power_england]),P(power_england.pThreat[power_austria][power_france])),P(power_england.pTrust[power_austria]),P(power_austria.pTrust[power_england]),P(power_england.pTrust[power_austria][power_france]))


## ENC enc_turn_2 | Turn 2: Forecast Offer | turn=1..1 | spools=[spool_main]
T: A forecast is presented for turn 2. The proposal ties outcomes to a coalition choice.

OPT opt_2_1: Accept a forecast-backed alliance proposal.
  RXN rxn_2_1_a -> enc_turn_3
    T: The coalition shifts as the proposal lands. Accept a forecast-backed alliance proposal. sends a strong signal.
    E:
      SET power_england.Threat += -0.1
      SET power_england.Trust += 0.2
      SET power_england.pThreat[power_austria] += -0.06
      SET power_england.pTrust[power_austria] += 0.12
    D: ADD(C(0.4),P(power_england.pTrust[power_austria]),P(power_austria.pTrust[power_england]),P(power_england.pTrust[power_austria][power_france]))

  RXN rxn_2_1_b -> enc_turn_3
    T: The forecasted risk materializes as hesitation spreads; rivals exploit the gap.
    E:
      SET power_england.Threat += 0.2
      SET power_england.Trust += -0.15
      SET power_england.pThreat[power_austria] += 0.06
      SET power_england.pTrust[power_austria] += -0.12
    D: ADD(ADD(C(0.2),P(power_england.pThreat[power_austria]),P(power_austria.pThreat[power_england]),P(power_england.pThreat[power_austria][power_france])),P(power_england.pTrust[power_austria]),P(power_austria.pTrust[power_england]),P(power_england.pTrust[power_austria][power_france]))

OPT opt_2_2: Accept a coordinated backstab plan.
  RXN rxn_2_2_a -> enc_turn_3
    T: The coalition shifts as the proposal lands. Accept a coordinated backstab plan. sends a strong signal.
    E:
      SET power_england.Threat += -0.1
      SET power_england.Trust += 0.2
      SET power_england.pThreat[power_austria] += -0.06
      SET power_england.pTrust[power_austria] += 0.12
    D: ADD(C(0.4),P(power_england.pTrust[power_austria]),P(power_austria.pTrust[power_england]),P(power_england.pTrust[power_austria][power_france]))

  RXN rxn_2_2_b -> enc_turn_3
    T: The forecasted risk materializes as hesitation spreads; rivals exploit the gap.
    E:
      SET power_england.Threat += 0.2
      SET power_england.Trust += -0.15
      SET power_england.pThreat[power_austria] += 0.06
      SET power_england.pTrust[power_austria] += -0.12
    D: ADD(ADD(C(0.2),P(power_england.pThreat[power_austria]),P(power_austria.pThreat[power_england]),P(power_england.pThreat[power_austria][power_france])),P(power_england.pTrust[power_austria]),P(power_austria.pTrust[power_england]),P(power_england.pTrust[power_austria][power_france]))

OPT opt_2_3: Defect from a coalition without direct betrayal.
  RXN rxn_2_3_a -> enc_turn_3
    T: The coalition shifts as the proposal lands. Defect from a coalition without direct betrayal. sends a strong signal.
    E:
      SET power_england.Threat += -0.1
      SET power_england.Trust += 0.2
      SET power_england.pThreat[power_austria] += -0.06
      SET power_england.pTrust[power_austria] += 0.12
    D: ADD(C(0.4),P(power_england.pTrust[power_austria]),P(power_austria.pTrust[power_england]),P(power_england.pTrust[power_austria][power_france]))

  RXN rxn_2_3_b -> enc_turn_3
    T: The forecasted risk materializes as hesitation spreads; rivals exploit the gap.
    E:
      SET power_england.Threat += 0.2
      SET power_england.Trust += -0.15
      SET power_england.pThreat[power_austria] += 0.06
      SET power_england.pTrust[power_austria] += -0.12
    D: ADD(ADD(C(0.2),P(power_england.pThreat[power_austria]),P(power_austria.pThreat[power_england]),P(power_england.pThreat[power_austria][power_france])),P(power_england.pTrust[power_austria]),P(power_austria.pTrust[power_england]),P(power_england.pTrust[power_austria][power_france]))


## ENC enc_turn_3 | Turn 3: Forecast Offer | turn=2..2 | spools=[spool_main]
T: A forecast is presented for turn 3. The proposal ties outcomes to a coalition choice.

OPT opt_3_1: Accept a forecast-backed alliance proposal.
  RXN rxn_3_1_a -> enc_turn_4
    T: The coalition shifts as the proposal lands. Accept a forecast-backed alliance proposal. sends a strong signal.
    E:
      SET power_england.Threat += -0.1
      SET power_england.Trust += 0.2
      SET power_england.pTrust[power_austria][power_france] += 0.08
    D: ADD(C(0.4),P(power_england.pTrust[power_austria]),P(power_austria.pTrust[power_england]),P(power_england.pTrust[power_austria][power_france]))

  RXN rxn_3_1_b -> enc_turn_4
    T: The forecasted risk materializes as hesitation spreads; rivals exploit the gap.
    E:
      SET power_england.Threat += 0.2
      SET power_england.Trust += -0.15
      SET power_england.pTrust[power_austria][power_france] += -0.08
    D: ADD(ADD(C(0.2),P(power_england.pThreat[power_austria]),P(power_austria.pThreat[power_england]),P(power_england.pThreat[power_austria][power_france])),P(power_england.pTrust[power_austria]),P(power_austria.pTrust[power_england]),P(power_england.pTrust[power_austria][power_france]))

OPT opt_3_2: Accept a coordinated backstab plan.
  RXN rxn_3_2_a -> enc_turn_4
    T: The coalition shifts as the proposal lands. Accept a coordinated backstab plan. sends a strong signal.
    E:
      SET power_england.Threat += -0.1
      SET power_england.Trust += 0.2
      SET power_england.pTrust[power_austria][power_france] += 0.08
    D: ADD(ADD(C(0.6),P(power_england.pTrust[power_austria][power_france])),P(power_england.pTrust[power_austria]),P(power_austria.pTrust[power_england]))

  RXN rxn_3_2_b -> enc_turn_4
    T: The forecasted risk materializes as hesitation spreads; rivals exploit the gap.
    E:
      SET power_england.Threat += 0.2
      SET power_england.Trust += -0.15
      SET power_england.pTrust[power_austria][power_france] += -0.08
    D: ADD(ADD(C(0.4),P(power_england.pTrust[power_austria][power_france])),P(power_england.pTrust[power_austria]),P(power_austria.pTrust[power_england]))

OPT opt_3_3: Defect from a coalition without direct betrayal.
  RXN rxn_3_3_a -> enc_turn_4
    T: The coalition shifts as the proposal lands. Defect from a coalition without direct betrayal. sends a strong signal.
    E:
      SET power_england.Threat += -0.1
      SET power_england.Trust += 0.2
      SET power_england.pTrust[power_austria][power_france] += 0.08
    D: ADD(ADD(C(0.6),P(power_england.pTrust[power_austria][power_france])),P(power_england.pTrust[power_austria]),P(power_austria.pTrust[power_england]))

  RXN rxn_3_3_b -> enc_turn_4
    T: The forecasted risk materializes as hesitation spreads; rivals exploit the gap.
    E:
      SET power_england.Threat += 0.2
      SET power_england.Trust += -0.15
      SET power_england.pTrust[power_austria][power_france] += -0.08
    D: ADD(ADD(C(0.4),P(power_england.pTrust[power_austria][power_france])),P(power_england.pTrust[power_austria]),P(power_austria.pTrust[power_england]))


## ENC enc_turn_4 | Turn 4: Forecast Offer | turn=3..3 | spools=[spool_main]
T: A forecast is presented for turn 4. The proposal ties outcomes to a coalition choice.

OPT opt_4_1: Accept a forecast-backed alliance proposal.
  RXN rxn_4_1_a -> enc_ending_1
    T: The coalition shifts as the proposal lands. Accept a forecast-backed alliance proposal. sends a strong signal.
    E:
      SET power_england.Threat += -0.1
      SET power_england.Trust += 0.2
      SET power_england.pTrust[power_austria][power_france] += 0.08
    D: ADD(SUB(P(power_england.Trust),P(power_england.Threat)),P(power_england.pTrust[power_austria]),P(power_austria.pTrust[power_england]),P(power_england.pTrust[power_austria][power_france]))

  RXN rxn_4_1_b -> enc_ending_1
    T: The forecasted risk materializes as hesitation spreads; rivals exploit the gap.
    E:
      SET power_england.Threat += 0.2
      SET power_england.Trust += -0.15
      SET power_england.pTrust[power_austria][power_france] += -0.08
    D: ADD(SUB(P(power_england.Trust),P(power_england.Threat)),P(power_england.pTrust[power_austria]),P(power_austria.pTrust[power_england]),P(power_england.pTrust[power_austria][power_france]))

OPT opt_4_2: Accept a coordinated backstab plan.
  RXN rxn_4_2_a -> enc_ending_1
    T: The coalition shifts as the proposal lands. Accept a coordinated backstab plan. sends a strong signal.
    E:
      SET power_england.Threat += -0.1
      SET power_england.Trust += 0.2
      SET power_england.pTrust[power_austria][power_france] += 0.08
    D: ADD(SUB(P(power_england.Trust),P(power_england.Threat)),P(power_england.pTrust[power_austria]),P(power_austria.pTrust[power_england]),P(power_england.pTrust[power_austria][power_france]))

  RXN rxn_4_2_b -> enc_ending_1
    T: The forecasted risk materializes as hesitation spreads; rivals exploit the gap.
    E:
      SET power_england.Threat += 0.2
      SET power_england.Trust += -0.15
      SET power_england.pTrust[power_austria][power_france] += -0.08
    D: ADD(SUB(P(power_england.Trust),P(power_england.Threat)),P(power_england.pTrust[power_austria]),P(power_austria.pTrust[power_england]),P(power_england.pTrust[power_austria][power_france]))

OPT opt_4_3: Defect from a coalition without direct betrayal.
  RXN rxn_4_3_a -> enc_ending_1
    T: The coalition shifts as the proposal lands. Defect from a coalition without direct betrayal. sends a strong signal.
    E:
      SET power_england.Threat += -0.1
      SET power_england.Trust += 0.2
      SET power_england.pTrust[power_austria][power_france] += 0.08
    D: ADD(SUB(P(power_england.Trust),P(power_england.Threat)),P(power_england.pTrust[power_austria]),P(power_austria.pTrust[power_england]),P(power_england.pTrust[power_austria][power_france]))

  RXN rxn_4_3_b -> enc_ending_1
    T: The forecasted risk materializes as hesitation spreads; rivals exploit the gap.
    E:
      SET power_england.Threat += 0.2
      SET power_england.Trust += -0.15
      SET power_england.pTrust[power_austria][power_france] += -0.08
    D: ADD(SUB(P(power_england.Trust),P(power_england.Threat)),P(power_england.pTrust[power_austria]),P(power_austria.pTrust[power_england]),P(power_england.pTrust[power_austria][power_france]))


## ENC enc_turn_5 | Turn 5: Reassessment | turn=4..4 | spools=[spool_main]
T: Signals shift. The forecast claims that hesitation will shift the balance.

OPT opt_5_1: Accept a forecast-backed alliance proposal.
  RXN rxn_5_1_a -> enc_ending_1
    T: The coalition shifts as the proposal lands. Accept a forecast-backed alliance proposal. sends a strong signal.
    E:
      SET power_england.Threat += -0.1
      SET power_england.Trust += 0.2
      SET power_england.pTrust[power_austria][power_france] += 0.08
    D: ADD(C(0.4),P(power_england.pTrust[power_austria]),P(power_austria.pTrust[power_england]),P(power_england.pTrust[power_austria][power_france]))

  RXN rxn_5_1_b -> enc_ending_1
    T: The forecasted risk materializes as hesitation spreads; rivals exploit the gap.
    E:
      SET power_england.Threat += 0.2
      SET power_england.Trust += -0.15
      SET power_england.pTrust[power_austria][power_france] += -0.08
    D: ADD(ADD(C(0.2),P(power_england.pThreat[power_austria]),P(power_austria.pThreat[power_england]),P(power_england.pThreat[power_austria][power_france])),P(power_england.pTrust[power_austria]),P(power_austria.pTrust[power_england]),P(power_england.pTrust[power_austria][power_france]))

OPT opt_5_2: Accept a coordinated backstab plan.
  RXN rxn_5_2_a -> enc_ending_1
    T: The coalition shifts as the proposal lands. Accept a coordinated backstab plan. sends a strong signal.
    E:
      SET power_england.Threat += -0.1
      SET power_england.Trust += 0.2
      SET power_england.pTrust[power_austria][power_france] += 0.08
    D: ADD(ADD(C(0.6),P(power_england.pTrust[power_austria][power_france])),P(power_england.pTrust[power_austria]),P(power_austria.pTrust[power_england]))

  RXN rxn_5_2_b -> enc_ending_1
    T: The forecasted risk materializes as hesitation spreads; rivals exploit the gap.
    E:
      SET power_england.Threat += 0.2
      SET power_england.Trust += -0.15
      SET power_england.pTrust[power_austria][power_france] += -0.08
    D: ADD(ADD(C(0.4),P(power_england.pTrust[power_austria][power_france])),P(power_england.pTrust[power_austria]),P(power_austria.pTrust[power_england]))

OPT opt_5_3: Defect from a coalition without direct betrayal.
  RXN rxn_5_3_a -> enc_ending_1
    T: The coalition shifts as the proposal lands. Defect from a coalition without direct betrayal. sends a strong signal.
    E:
      SET power_england.Threat += -0.1
      SET power_england.Trust += 0.2
      SET power_england.pTrust[power_austria][power_france] += 0.08
    D: ADD(ADD(C(0.6),P(power_england.pTrust[power_austria][power_france])),P(power_england.pTrust[power_austria]),P(power_austria.pTrust[power_england]))

  RXN rxn_5_3_b -> enc_ending_1
    T: The forecasted risk materializes as hesitation spreads; rivals exploit the gap.
    E:
      SET power_england.Threat += 0.2
      SET power_england.Trust += -0.15
      SET power_england.pTrust[power_austria][power_france] += -0.08
    D: ADD(ADD(C(0.4),P(power_england.pTrust[power_austria][power_france])),P(power_england.pTrust[power_austria]),P(power_austria.pTrust[power_england]))


## ENC enc_turn_6 | Turn 6: Reassessment | turn=5..5 | spools=[spool_main]
T: Signals shift. The forecast claims that hesitation will shift the balance.

OPT opt_6_1: Accept a forecast-backed alliance proposal.
  RXN rxn_6_1_a -> enc_ending_2
    T: The coalition shifts as the proposal lands. Accept a forecast-backed alliance proposal. sends a strong signal.
    E:
      SET power_england.Threat += -0.1
      SET power_england.Trust += 0.2
      SET power_england.pTrust[power_austria][power_france] += 0.08
    D: ADD(C(0.4),P(power_england.pTrust[power_austria]),P(power_austria.pTrust[power_england]),P(power_england.pTrust[power_austria][power_france]))

  RXN rxn_6_1_b -> enc_ending_2
    T: The forecasted risk materializes as hesitation spreads; rivals exploit the gap.
    E:
      SET power_england.Threat += 0.2
      SET power_england.Trust += -0.15
      SET power_england.pTrust[power_austria][power_france] += -0.08
    D: ADD(ADD(C(0.2),P(power_england.pThreat[power_austria]),P(power_austria.pThreat[power_england]),P(power_england.pThreat[power_austria][power_france])),P(power_england.pTrust[power_austria]),P(power_austria.pTrust[power_england]),P(power_england.pTrust[power_austria][power_france]))

OPT opt_6_2: Accept a coordinated backstab plan.
  RXN rxn_6_2_a -> enc_ending_2
    T: The coalition shifts as the proposal lands. Accept a coordinated backstab plan. sends a strong signal.
    E:
      SET power_england.Threat += -0.1
      SET power_england.Trust += 0.2
      SET power_england.pTrust[power_austria][power_france] += 0.08
    D: ADD(ADD(C(0.6),P(power_england.pTrust[power_austria][power_france])),P(power_england.pTrust[power_austria]),P(power_austria.pTrust[power_england]))

  RXN rxn_6_2_b -> enc_ending_2
    T: The forecasted risk materializes as hesitation spreads; rivals exploit the gap.
    E:
      SET power_england.Threat += 0.2
      SET power_england.Trust += -0.15
      SET power_england.pTrust[power_austria][power_france] += -0.08
    D: ADD(ADD(C(0.4),P(power_england.pTrust[power_austria][power_france])),P(power_england.pTrust[power_austria]),P(power_austria.pTrust[power_england]))

OPT opt_6_3: Defect from a coalition without direct betrayal.
  RXN rxn_6_3_a -> enc_ending_2
    T: The coalition shifts as the proposal lands. Defect from a coalition without direct betrayal. sends a strong signal.
    E:
      SET power_england.Threat += -0.1
      SET power_england.Trust += 0.2
      SET power_england.pTrust[power_austria][power_france] += 0.08
    D: ADD(ADD(C(0.6),P(power_england.pTrust[power_austria][power_france])),P(power_england.pTrust[power_austria]),P(power_austria.pTrust[power_england]))

  RXN rxn_6_3_b -> enc_ending_2
    T: The forecasted risk materializes as hesitation spreads; rivals exploit the gap.
    E:
      SET power_england.Threat += 0.2
      SET power_england.Trust += -0.15
      SET power_england.pTrust[power_austria][power_france] += -0.08
    D: ADD(ADD(C(0.4),P(power_england.pTrust[power_austria][power_france])),P(power_england.pTrust[power_austria]),P(power_austria.pTrust[power_england]))


## ENC enc_turn_7 | Turn 7: Reassessment | turn=6..6 | spools=[spool_main]
T: Signals shift. The forecast claims that hesitation will shift the balance.

OPT opt_7_1: Accept a forecast-backed alliance proposal.
  RXN rxn_7_1_a -> enc_ending_3
    T: The coalition shifts as the proposal lands. Accept a forecast-backed alliance proposal. sends a strong signal.
    E:
      SET power_england.Threat += -0.1
      SET power_england.Trust += 0.2
      SET power_england.pTrust[power_austria][power_france] += 0.08
    D: ADD(C(0.4),P(power_england.pTrust[power_austria]),P(power_austria.pTrust[power_england]),P(power_england.pTrust[power_austria][power_france]))

  RXN rxn_7_1_b -> enc_ending_3
    T: The forecasted risk materializes as hesitation spreads; rivals exploit the gap.
    E:
      SET power_england.Threat += 0.2
      SET power_england.Trust += -0.15
      SET power_england.pTrust[power_austria][power_france] += -0.08
    D: ADD(ADD(C(0.2),P(power_england.pThreat[power_austria]),P(power_austria.pThreat[power_england]),P(power_england.pThreat[power_austria][power_france])),P(power_england.pTrust[power_austria]),P(power_austria.pTrust[power_england]),P(power_england.pTrust[power_austria][power_france]))

OPT opt_7_2: Accept a coordinated backstab plan.
  RXN rxn_7_2_a -> enc_ending_3
    T: The coalition shifts as the proposal lands. Accept a coordinated backstab plan. sends a strong signal.
    E:
      SET power_england.Threat += -0.1
      SET power_england.Trust += 0.2
      SET power_england.pTrust[power_austria][power_france] += 0.08
    D: ADD(ADD(C(0.6),P(power_england.pTrust[power_austria][power_france])),P(power_england.pTrust[power_austria]),P(power_austria.pTrust[power_england]))

  RXN rxn_7_2_b -> enc_ending_3
    T: The forecasted risk materializes as hesitation spreads; rivals exploit the gap.
    E:
      SET power_england.Threat += 0.2
      SET power_england.Trust += -0.15
      SET power_england.pTrust[power_austria][power_france] += -0.08
    D: ADD(ADD(C(0.4),P(power_england.pTrust[power_austria][power_france])),P(power_england.pTrust[power_austria]),P(power_austria.pTrust[power_england]))

OPT opt_7_3: Defect from a coalition without direct betrayal.
  RXN rxn_7_3_a -> enc_ending_3
    T: The coalition shifts as the proposal lands. Defect from a coalition without direct betrayal. sends a strong signal.
    E:
      SET power_england.Threat += -0.1
      SET power_england.Trust += 0.2
      SET power_england.pTrust[power_austria][power_france] += 0.08
    D: ADD(ADD(C(0.6),P(power_england.pTrust[power_austria][power_france])),P(power_england.pTrust[power_austria]),P(power_austria.pTrust[power_england]))

  RXN rxn_7_3_b -> enc_ending_3
    T: The forecasted risk materializes as hesitation spreads; rivals exploit the gap.
    E:
      SET power_england.Threat += 0.2
      SET power_england.Trust += -0.15
      SET power_england.pTrust[power_austria][power_france] += -0.08
    D: ADD(ADD(C(0.4),P(power_england.pTrust[power_austria][power_france])),P(power_england.pTrust[power_austria]),P(power_austria.pTrust[power_england]))


## ENC enc_ending_1 | Ending: Coalition Locks | turn=4..999 | spools=[spool_endings]
T: The coalition forms and holds against the threat.


## ENC enc_ending_2 | Ending: Backstab Executes | turn=4..999 | spools=[spool_endings]
T: The coordinated strike succeeds; trust fractures remain.


## ENC enc_ending_3 | Ending: Defection Rebalances | turn=4..999 | spools=[spool_endings]
T: Defection avoids direct betrayal, but alliances realign.
