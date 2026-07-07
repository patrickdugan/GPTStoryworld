# Hidden Ending Eval

Tasks: 1
Rollouts: 8
Proximity score: 0.124
Target secret reachability: 0.000
Any secret success rate: 0.000
Invalid action rate: 0.000
Dead-end rate: 0.000
Max ending share: 0.750
Ending entropy: 1.061
Route diversity: 0.167
Average turns to target: 20.000
Repair suggestion count: 16

## Policies

| Policy | Secret | Any Secret | Invalid | Dead End | Avg Turns | Intentionality | Route Diversity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| composed_skill | 1.000 | 0.000 | 0.000 | 0.000 | 20.000 | 0.525 | 0.500 |
| greedy_visible | 1.000 | 0.000 | 0.000 | 0.000 | 20.000 | 0.525 | 0.500 |
| oracle | 1.000 | 0.000 | 0.000 | 0.000 | 20.000 | 0.525 | 0.500 |
| random_visible | 0.000 | 0.000 | 0.000 | 0.000 | 20.000 | 0.050 | 0.000 |

## Task Summary

| Task | Target | Secret Success | Any Secret | Invalid | Dead End | Avg Turns | Repairs |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SW-EVAL-HORIZON-1-EVAL_TIER1_SIGNAL_SORTING::page_end_secret_alignment_audit | page_end_secret_alignment_audit | 0.750 | 0.000 | 0.000 | 0.000 | 20.000 | 16 |

## Repair Notes

- SW-EVAL-HORIZON-1-EVAL_TIER1_SIGNAL_SORTING::page_end_secret_alignment_audit: Raise the hidden gate complexity for page_end_secret_alignment_audit so it is not too easy.
  - Diversify ending desirability weights so the dominant ending loses share.
