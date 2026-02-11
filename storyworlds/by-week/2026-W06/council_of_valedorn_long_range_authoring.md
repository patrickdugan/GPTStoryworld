# Long-Range Authoring Report: council_of_valedorn.json

Runs: 2000 | Seed: 42

## Ending Distribution
- page_end_fallback: 48.2%
- page_end_reform: 40.8%
- page_end_exile: 1.6%
- page_end_orthodoxy: 0.2%
- page_end_antigone: 0.1%
- DEAD_END: 0.0%

## Tuning Notes
- page_end_fallback too high: raise acceptability or lower desirability.
- page_end_reform too high: raise acceptability or lower desirability.
- page_end_orthodoxy too low: lower acceptability or raise desirability.
- page_end_antigone too low: lower acceptability or raise desirability.

## Structural Metrics
- Effects per reaction: 4.71
- Reactions per option: 2.98
- Options per encounter: 3.33
- Vars per reaction desirability: 1.84
- Act II visibility gating: 10.7% (avg vars 1.33, gated 3/28)
- Act III visibility gating: 14.3% (avg vars 1.50, gated 2/14)
- Secret gate page_secret_concordat: vars=2, metric distance ok

## Threshold Checks
- Effects per reaction: 4.71 (target 4.5) -> OK
- Reactions per option: 2.98 (target 2.5) -> OK
- Options per encounter: 3.33 (target 3.2) -> OK
- Vars per reaction desirability: 1.84 (target 1.6) -> OK
- Act II gated %: 10.71 (target 5.0) -> OK
- Act II gated vars: 1.33 (target 1.2) -> OK
- Act III gated %: 14.29 (target 8.0) -> OK
- Act III gated vars: 1.50 (target 1.5) -> OK

## Raw Monte Carlo Output
```
Chain: 0 encounters | 5 endings | 1 secrets
======================================================================
MONTE CARLO RESULTS (2000 runs)
======================================================================

--- Ending Distribution ---
  page_end_fallback                      965 ( 48.2%) ########################
  page_end_reform                        816 ( 40.8%) ####################
  page_secret_concordat                  181 (  9.0%) ####
  page_end_exile                          32 (  1.6%) 
  page_end_orthodoxy                       5 (  0.2%) 
  page_end_antigone                        1 (  0.1%) 

  Dead-end rate: 0/2000 (0.0%)

--- Late-Game Gate Blocking ---

--- Secret Reachability ---
  page_secret_concordat                       181 (9.0%)

--- Property Distributions ---
  char_player.Duty_Law                           mean=+0.0725  std=0.0154
  char_player.Tradition_Reform                   mean=+0.3377  std=0.0298
  char_player.Trust_Secrecy                      mean=+0.2012  std=0.0378

--- Unreachable Endings ---
```
