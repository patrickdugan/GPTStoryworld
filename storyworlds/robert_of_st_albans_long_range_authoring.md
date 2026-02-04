# Long-Range Authoring Report: robert_of_st_albans.json

Runs: 5000 | Seed: 42

## Ending Distribution
- page_end_legend: 47.0%
- page_end_regret: 31.1%
- page_end_templar: 21.9%
- DEAD_END: 0.0%

## Tuning Notes
- page_end_legend too high: raise acceptability or lower desirability.
- page_end_regret too high: raise acceptability or lower desirability.

## Raw Monte Carlo Output
```
Chain: 0 encounters | 5 endings | 0 secrets
======================================================================
MONTE CARLO RESULTS (5000 runs)
======================================================================

--- Ending Distribution ---
  page_end_legend                       2349 ( 47.0%) #######################
  page_end_regret                       1555 ( 31.1%) ###############
  page_end_templar                      1096 ( 21.9%) ##########

  Dead-end rate: 0/5000 (0.0%)

--- Late-Game Gate Blocking ---

--- Secret Reachability ---
  None reachable

--- Property Distributions ---
  char_player.Faith_Doubt                        mean=+0.1885  std=0.0283
  char_player.Honor_Expediency                   mean=+0.0800  std=0.0319
  char_player.Loyalty_Betrayal                   mean=+0.1585  std=0.0284
  char_player.pFaith_Doubt                       mean=+0.0018  std=0.0047
  char_player.pHonor_Expediency                  mean=-0.0001  std=0.0035
  char_player.pLoyalty_Betrayal                  mean=+0.0020  std=0.0041

--- Unreachable Endings ---
  page_end_convert
  page_end_hattin
```
