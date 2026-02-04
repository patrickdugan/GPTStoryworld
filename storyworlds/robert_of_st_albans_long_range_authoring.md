# Long-Range Authoring Report: robert_of_st_albans.json

Runs: 5000 | Seed: 42

## Ending Distribution
- page_end_exile: 13.0%
- page_end_betray_salahudin: 11.1%
- page_end_regret: 2.9%
- page_end_suhrawardi: 0.3%
- page_end_convert: 0.2%
- DEAD_END: 72.5%

## Tuning Notes
- Dead-end rate high: widen fallback ending gate.
- page_end_suhrawardi too low: lower acceptability or raise desirability.
- page_end_convert too low: lower acceptability or raise desirability.

## Raw Monte Carlo Output
```
Chain: 0 encounters | 11 endings | 1 secrets
======================================================================
MONTE CARLO RESULTS (5000 runs)
======================================================================

--- Ending Distribution ---
  DEAD_END                              3625 ( 72.5%) ####################################
  page_end_exile                         649 ( 13.0%) ######
  page_end_betray_salahudin              554 ( 11.1%) #####
  page_end_regret                        146 (  2.9%) #
  page_end_suhrawardi                     15 (  0.3%) 
  page_end_convert                        11 (  0.2%) 

  Dead-end rate: 3625/5000 (72.5%)

--- Late-Game Gate Blocking ---

--- Secret Reachability ---
  page_secret_mureed                          300 (6.0%)

--- Property Distributions ---
  char_player.Faith_Doubt                        mean=+0.2220  std=0.0430
  char_player.Honor_Expediency                   mean=+0.0840  std=0.0612
  char_player.Loyalty_Betrayal                   mean=+0.1746  std=0.0559
  char_player.pFaith_Doubt                       mean=+0.0044  std=0.0081
  char_player.pHonor_Expediency                  mean=+0.0002  std=0.0041
  char_player.pLoyalty_Betrayal                  mean=+0.0019  std=0.0040

--- Unreachable Endings ---
  page_end_templar
  page_end_hattin
  page_end_legend
  page_end_salahudin
  page_end_betray_suhrawardi
  page_end_fallback
```
