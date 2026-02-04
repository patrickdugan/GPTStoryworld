# Long-Range Authoring Report: robert_of_st_albans.json

Runs: 5000 | Seed: 42

## Ending Distribution
- page_end_suhrawardi: 19.7%
- page_end_salahudin: 18.6%
- page_end_regret: 17.9%
- page_end_legend: 13.4%
- page_end_betray_suhrawardi: 6.3%
- page_end_convert: 4.7%
- page_end_fallback: 4.6%
- page_end_exile: 4.2%
- page_end_hattin: 3.0%
- page_end_templar: 2.4%
- page_end_betray_salahudin: 1.0%
- DEAD_END: 0.0%

## Tuning Notes

## Raw Monte Carlo Output
```
Chain: 0 encounters | 11 endings | 1 secrets
======================================================================
MONTE CARLO RESULTS (5000 runs)
======================================================================

--- Ending Distribution ---
  page_end_suhrawardi                    984 ( 19.7%) #########
  page_end_salahudin                     931 ( 18.6%) #########
  page_end_regret                        894 ( 17.9%) ########
  page_end_legend                        671 ( 13.4%) ######
  page_end_betray_suhrawardi             315 (  6.3%) ###
  page_end_convert                       236 (  4.7%) ##
  page_end_fallback                      231 (  4.6%) ##
  page_end_exile                         208 (  4.2%) ##
  page_secret_mureed                     204 (  4.1%) ##
  page_end_hattin                        152 (  3.0%) #
  page_end_templar                       122 (  2.4%) #
  page_end_betray_salahudin               52 (  1.0%) 

  Dead-end rate: 0/5000 (0.0%)

--- Late-Game Gate Blocking ---

--- Secret Reachability ---
  page_secret_mureed                          204 (4.1%)

--- Property Distributions ---
  char_player.Faith_Doubt                        mean=+0.7145  std=0.0595
  char_player.Honor_Expediency                   mean=+0.2817  std=0.0853
  char_player.Loyalty_Betrayal                   mean=+0.6588  std=0.0540
  char_player.pFaith_Doubt                       mean=+0.0051  std=0.0073
  char_player.pHonor_Expediency                  mean=-0.0008  std=0.0046
  char_player.pLoyalty_Betrayal                  mean=+0.0100  std=0.0070

--- Unreachable Endings ---
```
