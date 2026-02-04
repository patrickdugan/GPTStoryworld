# Long-Range Authoring Report: robert_of_st_albans.json

Runs: 5000 | Seed: 42

## Ending Distribution
- page_end_regret: 57.6%
- page_end_legend: 22.3%
- page_end_betray_salahudin: 12.9%
- page_end_templar: 7.2%
- DEAD_END: 0.0%

## Tuning Notes
- page_end_regret too high: raise acceptability or lower desirability.

## Raw Monte Carlo Output
```
Chain: 0 encounters | 10 endings | 1 secrets
======================================================================
MONTE CARLO RESULTS (5000 runs)
======================================================================

--- Ending Distribution ---
  page_end_regret                       2882 ( 57.6%) ############################
  page_end_legend                       1113 ( 22.3%) ###########
  page_end_betray_salahudin              643 ( 12.9%) ######
  page_end_templar                       362 (  7.2%) ###

  Dead-end rate: 0/5000 (0.0%)

--- Late-Game Gate Blocking ---

--- Secret Reachability ---
  page_secret_mureed                         3081 (61.6%)

--- Property Distributions ---
  char_player.Faith_Doubt                        mean=+0.1910  std=0.0303
  char_player.Honor_Expediency                   mean=+0.0665  std=0.0390
  char_player.Loyalty_Betrayal                   mean=+0.1458  std=0.0349
  char_player.pFaith_Doubt                       mean=+0.0033  std=0.0059
  char_player.pHonor_Expediency                  mean=+0.0000  std=0.0035
  char_player.pLoyalty_Betrayal                  mean=+0.0019  std=0.0041

--- Unreachable Endings ---
  page_end_convert
  page_end_hattin
  page_end_exile
  page_end_suhrawardi
  page_end_salahudin
  page_end_betray_suhrawardi
```
