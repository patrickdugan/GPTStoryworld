# Ending Reachability Discipline

Use this checklist when Monte Carlo reports unreachable endings.

Checklist
1) Verify the ending is in the Endings spool.
2) Ensure at least one encounter option can route to the ending.
3) Set a non-zero desirability script for the ending.
4) Loosen acceptability gates if the ending remains unreachable.
5) Re-run Monte Carlo to confirm reachability.

Common causes of unreachable endings
- Ending is never routed to by any option.
- Acceptability_script too strict relative to achievable properties.
- Desirability_script is always lower than other endings (never chosen).

Recommended tuning steps
- Add a small desirability bias (0.003–0.02) to the ending.
- Prefer property-based desirability to avoid pure randomness.
- If necessary, add a low-threshold acceptability gate or remove it.

Automation
- Use scripts/ending_reachability_balance.py to set a desirability floor and
  print unreachable endings for a quick fix loop.
