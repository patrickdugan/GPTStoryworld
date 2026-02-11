# Long-Range Authoring Report: no_exit_p2.json

Runs: 500 | Seed: 42

## Ending Distribution
- page_end_two_leave: 27.6%
- page_end_stay: 27.4%
- page_end_fallback: 24.6%
- page_end_three_leave: 20.4%
- DEAD_END: 0.0%

## Tuning Notes

## Structural Metrics
- Effects per reaction: 6.83
- Reactions per option: 2.82
- Options per encounter: 3.21
- Vars per reaction desirability: 1.95
- Act II visibility gating: 7.9% (avg vars 2.00, gated 3/38)
- Act III visibility gating: 10.5% (avg vars 2.00, gated 2/19)
- Secret gate check: no secret encounters found

## Threshold Checks
- Effects per reaction: 6.83 (target 4.5) -> OK
- Reactions per option: 2.82 (target 2.5) -> OK
- Options per encounter: 3.21 (target 3.2) -> OK
- Vars per reaction desirability: 1.95 (target 1.6) -> OK
- Act II gated %: 7.89 (target 5.0) -> OK
- Act II gated vars: 2.00 (target 1.2) -> OK
- Act III gated %: 10.53 (target 8.0) -> OK
- Act III gated vars: 2.00 (target 1.5) -> OK

## Raw Monte Carlo Output
```
Chain: 0 encounters | 4 endings | 0 secrets
======================================================================
MONTE CARLO RESULTS (500 runs)
======================================================================

--- Ending Distribution ---
  page_end_two_leave                     138 ( 27.6%) #############
  page_end_stay                          137 ( 27.4%) #############
  page_end_fallback                      123 ( 24.6%) ############
  page_end_three_leave                   102 ( 20.4%) ##########

  Dead-end rate: 0/500 (0.0%)

--- Late-Game Gate Blocking ---

--- Secret Reachability ---
  None reachable

--- Property Distributions ---
  char_estelle.Compassion_Cruelty                mean=-0.0872  std=0.1503
  char_estelle.Escape_Resign                     mean=+0.3469  std=0.3647
  char_garcin.Escape_Resign                      mean=-0.0413  std=0.1473
  char_garcin.Pride_Shame                        mean=+0.6374  std=0.3760
  char_inez.Compassion_Cruelty                   mean=+0.3712  std=0.3683
  char_inez.Pride_Shame                          mean=-0.1732  std=0.1688

--- Unreachable Endings ---
```
