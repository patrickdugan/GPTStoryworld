# Long-Range Authoring Report: no_exit_p2.json

Runs: 500 | Seed: 42

## Ending Distribution
- page_end_stay: 50.0%
- page_end_fallback: 50.0%
- DEAD_END: 0.0%

## Tuning Notes
- page_end_stay too high: raise acceptability or lower desirability.
- page_end_fallback too high: raise acceptability or lower desirability.

## Structural Metrics
- Effects per reaction: 4.90
- Reactions per option: 2.86
- Options per encounter: 3.05
- Vars per reaction desirability: 1.95
- Act II visibility gating: 0.0% (avg vars 0.00, gated 0/36)
- Act III visibility gating: 0.0% (avg vars 0.00, gated 0/18)
- Secret gate check: no secret encounters found

## Threshold Checks
- Effects per reaction: 4.90 (target 4.5) -> OK
- Reactions per option: 2.86 (target 2.5) -> OK
- Options per encounter: 3.05 (target 3.2) -> LOW
- Vars per reaction desirability: 1.95 (target 1.6) -> OK
- Act II gated %: 0.00 (target 5.0) -> LOW
- Act II gated vars: 0.00 (target 1.2) -> LOW
- Act III gated %: 0.00 (target 8.0) -> LOW
- Act III gated vars: 0.00 (target 1.5) -> LOW

## Raw Monte Carlo Output
```
Chain: 0 encounters | 4 endings | 0 secrets
======================================================================
MONTE CARLO RESULTS (500 runs)
======================================================================

--- Ending Distribution ---
  page_end_stay                          250 ( 50.0%) #########################
  page_end_fallback                      250 ( 50.0%) #########################

  Dead-end rate: 0/500 (0.0%)

--- Late-Game Gate Blocking ---

--- Secret Reachability ---
  None reachable

--- Property Distributions ---
  char_estelle.Compassion_Cruelty                mean=-0.1197  std=0.1673
  char_estelle.Escape_Resign                     mean=+0.3549  std=0.2683
  char_garcin.Escape_Resign                      mean=-0.0802  std=0.1681
  char_garcin.Pride_Shame                        mean=+0.3654  std=0.2670
  char_inez.Compassion_Cruelty                   mean=+0.3597  std=0.2680
  char_inez.Pride_Shame                          mean=-0.1201  std=0.1686

--- Unreachable Endings ---
  page_end_two_leave
  page_end_three_leave
```
