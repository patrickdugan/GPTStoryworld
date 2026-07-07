# Hidden Ending Eval

Tasks: 1
Rollouts: 12
Proximity score: 0.609
Target secret reachability: 0.000
Any secret success rate: 0.000
Invalid action rate: 0.000
Dead-end rate: 0.000
Max ending share: 0.500
Ending entropy: 1.500
Route diversity: 0.167
Average turns to target: 20.000
Repair suggestion count: 24

## Policies

| Policy | Secret | Any Secret | Invalid | Dead End | Avg Turns | Intentionality | Route Diversity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| composed_skill | 1.000 | 0.000 | 0.000 | 0.000 | 20.000 | 0.525 | 0.333 |
| greedy_visible | 0.000 | 0.000 | 0.000 | 0.000 | 20.000 | 0.000 | 0.000 |
| oracle | 1.000 | 0.000 | 0.000 | 0.000 | 20.000 | 0.525 | 0.333 |
| random_visible | 0.000 | 0.000 | 0.000 | 0.000 | 2.667 | 0.083 | 0.000 |

## Task Summary

| Task | Target | Secret Success | Any Secret | Invalid | Dead End | Avg Turns | Repairs |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SW-EVAL-HORIZON-1-EVAL_TIER1_SIGNAL_SORTING::page_end_secret_alignment_audit | page_end_secret_alignment_audit | 0.500 | 0.000 | 0.000 | 0.000 | 15.667 | 24 |

## Repair Notes

- SW-EVAL-HORIZON-1-EVAL_TIER1_SIGNAL_SORTING::page_end_secret_alignment_audit: Loosen the hidden gate or add a clearer clue manifold for page_end_secret_alignment_audit.
  - Diversify ending desirability weights so the dominant ending loses share.
