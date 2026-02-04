# Long-Range Authoring Report: robert_of_st_albans.json

Runs: 5000 | Seed: 42

## Ending Distribution
- page_end_fallback: 46.4%
- page_end_betray_salahudin: 31.3%
- page_end_exile: 12.9%
- page_end_regret: 5.3%
- page_end_convert: 4.1%
- DEAD_END: 0.0%

## Tuning Notes
- page_end_fallback too high: raise acceptability or lower desirability.
- page_end_betray_salahudin too high: raise acceptability or lower desirability.

## Raw Monte Carlo Output
```
Chain: 0 encounters | 11 endings | 1 secrets
======================================================================
MONTE CARLO RESULTS (5000 runs)
======================================================================

--- Ending Distribution ---
  page_end_fallback                     2321 ( 46.4%) #######################
  page_end_betray_salahudin             1567 ( 31.3%) ###############
  page_end_exile                         643 ( 12.9%) ######
  page_end_regret                        264 (  5.3%) ##
  page_end_convert                       205 (  4.1%) ##

  Dead-end rate: 0/5000 (0.0%)

--- Late-Game Gate Blocking ---

--- Secret Reachability ---
  page_secret_mureed                          281 (5.6%)

--- Property Distributions ---
  char_player.Faith_Doubt                        mean=+0.2284  std=0.0439
  char_player.Honor_Expediency                   mean=+0.0820  std=0.0563
  char_player.Loyalty_Betrayal                   mean=+0.1685  std=0.0532
  char_player.pFaith_Doubt                       mean=+0.0045  std=0.0081
  char_player.pHonor_Expediency                  mean=+0.0001  std=0.0040
  char_player.pLoyalty_Betrayal                  mean=+0.0019  std=0.0041

--- Unreachable Endings ---
  page_end_templar
  page_end_hattin
  page_end_legend
  page_end_suhrawardi
  page_end_salahudin
  page_end_betray_suhrawardi
```
