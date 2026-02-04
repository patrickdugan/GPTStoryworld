# Long-Range Authoring Report: robert_of_st_albans.json

Runs: 5000 | Seed: 42

## Ending Distribution
- page_end_suhrawardi: 70.7%
- page_end_convert: 6.6%
- page_end_regret: 4.7%
- page_end_exile: 0.9%
- page_end_betray_salahudin: 0.1%
- DEAD_END: 17.0%

## Tuning Notes
- Dead-end rate high: widen fallback ending gate.
- page_end_suhrawardi too high: raise acceptability or lower desirability.
- page_end_exile too low: lower acceptability or raise desirability.
- page_end_betray_salahudin too low: lower acceptability or raise desirability.

## Raw Monte Carlo Output
```
Chain: 0 encounters | 11 endings | 1 secrets
======================================================================
MONTE CARLO RESULTS (5000 runs)
======================================================================

--- Ending Distribution ---
  page_end_suhrawardi                   3534 ( 70.7%) ###################################
  DEAD_END                               851 ( 17.0%) ########
  page_end_convert                       329 (  6.6%) ###
  page_end_regret                        236 (  4.7%) ##
  page_end_exile                          47 (  0.9%) 
  page_end_betray_salahudin                3 (  0.1%) 

  Dead-end rate: 851/5000 (17.0%)

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
