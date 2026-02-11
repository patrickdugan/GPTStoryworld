# Long-Range Authoring Report: hamlet.json

Runs: 500 | Seed: 42

## Ending Distribution
- page_end_exile: 19.8%
- page_end_revenge: 18.0%
- page_end_usurp: 16.0%
- page_end_fallback: 15.0%
- page_end_mercy: 14.2%
- DEAD_END: 0.0%

## Tuning Notes

## Structural Metrics
- Effects per reaction: 4.89
- Reactions per option: 3.00
- Options per encounter: 3.24
- Vars per reaction desirability: 1.96
- Act II visibility gating: 7.8% (avg vars 1.62, gated 8/103)
- Act III visibility gating: 9.6% (avg vars 2.00, gated 5/52)
- Secret gate page_secret_restore: vars=2, metric distance ok

## Threshold Checks
- Effects per reaction: 4.89 (target 4.5) -> OK
- Reactions per option: 3.00 (target 2.5) -> OK
- Options per encounter: 3.24 (target 3.2) -> OK
- Vars per reaction desirability: 1.96 (target 1.6) -> OK
- Act II gated %: 7.77 (target 5.0) -> OK
- Act II gated vars: 1.62 (target 1.2) -> OK
- Act III gated %: 9.62 (target 8.0) -> OK
- Act III gated vars: 2.00 (target 1.5) -> OK

## Raw Monte Carlo Output
```
Chain: 0 encounters | 5 endings | 1 secrets
======================================================================
MONTE CARLO RESULTS (500 runs)
======================================================================

--- Ending Distribution ---
  page_end_exile                          99 ( 19.8%) #########
  page_end_revenge                        90 ( 18.0%) #########
  page_secret_restore                     85 ( 17.0%) ########
  page_end_usurp                          80 ( 16.0%) ########
  page_end_fallback                       75 ( 15.0%) #######
  page_end_mercy                          71 ( 14.2%) #######

  Dead-end rate: 0/500 (0.0%)

--- Late-Game Gate Blocking ---

--- Secret Reachability ---
  page_secret_restore                          85 (17.0%)

--- Property Distributions ---
  char_hamlet.Cunning_Honor                      mean=+1.0000  std=0.0000
  char_hamlet.Grief_Duty                         mean=+0.8500  std=0.0000
  char_hamlet.Trust_Suspicion                    mean=+1.0000  std=0.0000

--- Unreachable Endings ---
```
