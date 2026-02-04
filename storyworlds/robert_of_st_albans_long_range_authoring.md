# Long-Range Authoring Report: robert_of_st_albans.json

Runs: 5000 | Seed: 42

## Ending Distribution
- page_end_suhrawardi: 75.6%
- page_end_exile: 16.4%
- page_end_betray_salahudin: 6.8%
- page_end_regret: 0.4%
- page_end_templar: 0.2%
- DEAD_END: 0.6%

## Tuning Notes
- page_end_suhrawardi too high: raise acceptability or lower desirability.
- page_end_regret too low: lower acceptability or raise desirability.
- page_end_templar too low: lower acceptability or raise desirability.

## Raw Monte Carlo Output
```
Chain: 0 encounters | 10 endings | 1 secrets
======================================================================
MONTE CARLO RESULTS (5000 runs)
======================================================================

--- Ending Distribution ---
  page_end_suhrawardi                   3781 ( 75.6%) #####################################
  page_end_exile                         818 ( 16.4%) ########
  page_end_betray_salahudin              339 (  6.8%) ###
  DEAD_END                                28 (  0.6%) 
  page_end_regret                         22 (  0.4%) 
  page_end_templar                        12 (  0.2%) 

  Dead-end rate: 28/5000 (0.6%)

--- Late-Game Gate Blocking ---

--- Secret Reachability ---
  page_secret_mureed                          177 (3.5%)

--- Property Distributions ---
  char_player.Faith_Doubt                        mean=+0.2284  std=0.0439
  char_player.Honor_Expediency                   mean=+0.0820  std=0.0563
  char_player.Loyalty_Betrayal                   mean=+0.1685  std=0.0532
  char_player.pFaith_Doubt                       mean=+0.0045  std=0.0081
  char_player.pHonor_Expediency                  mean=+0.0001  std=0.0040
  char_player.pLoyalty_Betrayal                  mean=+0.0019  std=0.0041

--- Unreachable Endings ---
  page_end_convert
  page_end_hattin
  page_end_legend
  page_end_salahudin
  page_end_betray_suhrawardi
```
