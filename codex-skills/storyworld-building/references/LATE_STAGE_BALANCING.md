# Late-Stage Balancing (Tail Endings)

This note captures a practical Monte Carlo tuning loop for late-stage storyworlds
where special endings (rare or "tail" endings) are too rare or too dominant.

Goals
- Keep special endings reachable but not dominant.
- Avoid dead-ends.
- Preserve narrative coherence (no hidden impossible gates).

Workflow
1) Validate
   - python scripts/sweepweave_validator.py validate storyworld.json

2) Baseline Monte Carlo
   - python scripts/monte_carlo_rehearsal.py storyworld.json --runs 5000 --seed 42
   - Record ending distribution and property means.

3) Tune Gates and Weights
   - For special endings: loosen acceptability thresholds slightly, or
     increase desirability weights tied to intended properties.
   - If special endings dominate, tighten acceptability thresholds or
     reduce desirability bias.
   - If an ending is unreachable, verify there is a visible option path
     that can set the required properties.

4) Re-run Monte Carlo and Iterate
   - Aim for special ending share in a target tail band (e.g., 5-15%).

5) Final Validation
   - Re-run validator.
   - Optionally run a higher-run Monte Carlo (10k+) to smooth variance.

Tips
- Prefer small nudges in desirability or thresholds (0.005-0.02) and re-run.
- Keep at least one always-visible option per encounter to avoid blocking.
- When chain length is 0 in Monte Carlo, the simulator is sampling spools;
  focus on ending distribution and property means.

Automation
- Use scripts/late_stage_balance.py to apply ending gates/weights and
  run Monte Carlo to check tail distribution.
