# Long-Range Authoring Report: robert_of_st_albans.json

Runs: 5000 | Seed: 42

## Ending Distribution
- page_end_legend: 76.6%
- page_end_exile: 16.1%
- page_end_betray_salahudin: 6.4%
- page_end_regret: 0.6%
- page_end_salahudin: 0.1%
- DEAD_END: 0.1%

## Tuning Notes
- page_end_legend too high: raise acceptability or lower desirability.
- page_end_regret too low: lower acceptability or raise desirability.
- page_end_salahudin too low: lower acceptability or raise desirability.

## Raw Monte Carlo Output
```
Chain: 0 encounters | 10 endings | 1 secrets
======================================================================
MONTE CARLO RESULTS (5000 runs)
======================================================================

--- Ending Distribution ---
  page_end_legend                       3832 ( 76.6%) ######################################
  page_end_exile                         806 ( 16.1%) ########
  page_end_betray_salahudin              322 (  6.4%) ###
  page_end_regret                         31 (  0.6%) 
  DEAD_END                                 6 (  0.1%) 
  page_end_salahudin                       3 (  0.1%) 

  Dead-end rate: 6/5000 (0.1%)

--- Late-Game Gate Blocking ---

--- Secret Reachability ---
  page_secret_mureed                          150 (3.0%)

--- Property Distributions ---
  char_player.Faith_Doubt                        mean=+0.1910  std=0.0303
  char_player.Honor_Expediency                   mean=+0.0665  std=0.0390
  char_player.Loyalty_Betrayal                   mean=+0.1458  std=0.0349
  char_player.pFaith_Doubt                       mean=+0.0033  std=0.0059
  char_player.pHonor_Expediency                  mean=+0.0000  std=0.0035
  char_player.pLoyalty_Betrayal                  mean=+0.0019  std=0.0041

--- Unreachable Endings ---
  page_end_templar
  page_end_convert
  page_end_hattin
  page_end_suhrawardi
  page_end_betray_suhrawardi
```
