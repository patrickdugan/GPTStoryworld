# Long-Range Authoring Report: robert_of_st_albans.json

Runs: 5000 | Seed: 42

## Ending Distribution
- page_end_exile: 99.8%
- page_end_regret: 0.2%
- DEAD_END: 0.0%

## Tuning Notes
- page_end_exile too high: raise acceptability or lower desirability.
- page_end_regret too low: lower acceptability or raise desirability.

## Raw Monte Carlo Output
```
Chain: 0 encounters | 6 endings | 0 secrets
======================================================================
MONTE CARLO RESULTS (5000 runs)
======================================================================

--- Ending Distribution ---
  page_end_exile                        4991 ( 99.8%) #################################################
  page_end_regret                          9 (  0.2%) 

  Dead-end rate: 0/5000 (0.0%)

--- Late-Game Gate Blocking ---

--- Secret Reachability ---
  None reachable

--- Property Distributions ---
  char_player.Faith_Doubt                        mean=+0.1894  std=0.0288
  char_player.Honor_Expediency                   mean=+0.0638  std=0.0369
  char_player.Loyalty_Betrayal                   mean=+0.1617  std=0.0296
  char_player.pFaith_Doubt                       mean=+0.0019  std=0.0048
  char_player.pHonor_Expediency                  mean=-0.0001  std=0.0033
  char_player.pLoyalty_Betrayal                  mean=+0.0020  std=0.0041

--- Unreachable Endings ---
  page_end_templar
  page_end_convert
  page_end_hattin
  page_end_legend
```
