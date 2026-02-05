# Long-Range Authoring Report: elysin_prince.json

Runs: 2000 | Seed: 42

## Ending Distribution
- page_end_fallback: 37.1%
- page_end_usurp: 30.0%
- page_end_exile: 3.2%
- DEAD_END: 0.0%

## Tuning Notes
- page_end_fallback too high: raise acceptability or lower desirability.

## Structural Metrics
- Effects per reaction: 4.66
- Reactions per option: 2.83
- Options per encounter: 3.42
- Vars per reaction desirability: 1.90
- Act II visibility gating: 10.7% (avg vars 1.67, gated 3/28)
- Act III visibility gating: 13.3% (avg vars 2.00, gated 2/15)
- Secret gate page_secret_restore: vars=2, metric distance ok

## Threshold Checks
- Effects per reaction: 4.66 (target 4.5) -> OK
- Reactions per option: 2.83 (target 2.5) -> OK
- Options per encounter: 3.42 (target 3.2) -> OK
- Vars per reaction desirability: 1.90 (target 1.6) -> OK
- Act II gated %: 10.71 (target 5.0) -> OK
- Act II gated vars: 1.67 (target 1.2) -> OK
- Act III gated %: 13.33 (target 8.0) -> OK
- Act III gated vars: 2.00 (target 1.5) -> OK

## Raw Monte Carlo Output
```
Chain: 0 encounters | 5 endings | 1 secrets
======================================================================
MONTE CARLO RESULTS (2000 runs)
======================================================================

--- Ending Distribution ---
  page_end_fallback                      742 ( 37.1%) ##################
  page_end_usurp                         601 ( 30.0%) ###############
  page_secret_restore                    593 ( 29.6%) ##############
  page_end_exile                          64 (  3.2%) #

  Dead-end rate: 0/2000 (0.0%)

--- Late-Game Gate Blocking ---

--- Secret Reachability ---
  page_secret_restore                         593 (29.6%)

--- Property Distributions ---
  char_player.Cunning_Honor                      mean=+0.3437  std=0.0302
  char_player.Grief_Duty                         mean=+0.0846  std=0.0142
  char_player.Trust_Suspicion                    mean=+0.2330  std=0.0180

--- Unreachable Endings ---
  page_end_revenge
  page_end_mercy
```
