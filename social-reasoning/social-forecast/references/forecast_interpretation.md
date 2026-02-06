# Forecast Interpretation

## Key report fields

- `recommendation.posture`
  - `coalition-first persuasion`: trust conditions are favorable; push alliance framing.
  - `counter-betrayal hardening`: betrayal/defection pressure is elevated; tighten commitments.
  - `high-volatility containment`: death-ground or total-war behavior is active; prioritize damage control.
  - `balanced hedge`: mixed landscape; avoid over-commitment.

- `recommendation.instability_index`
  - `defect_rate + betray_rate` from recursive simulation.

- `recommendation.commit_total_war_rate`
  - proxy for escalation pressure.

- `recursive_summary.metrics.death_ground_entries`
  - number of death-ground mode transitions; higher means survival panic conditions.

## Practical thresholds (default heuristic)

- `instability_index >= 0.12`: high betrayal risk.
- `commit_total_war_rate > 0.35` or `death_ground_entries > 0`: treat as high volatility.
- `propose_coalition_rate > 0.60` with low instability: coalition messaging is likely viable.

## Trace usage

Use `trace_log` JSONL for granular evidence:
- `decision.scan`: weakness, triangle conflict, threat ranking.
- `decision.utility_parts`: decomposed scoring terms.
- `decision.rationale_text`: concise decision explanation emitted by the model.
