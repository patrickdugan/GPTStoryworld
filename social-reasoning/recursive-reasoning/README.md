# Recursive Reasoning (MAS)

This subfolder models recursive social reasoning in adversarial multi-agent settings with coalition dynamics.

## What is implemented

- First-order trust manifold (`p`) and second-order beliefs (`p2`).
- Manifold scan before each action:
  - who thinks I am weak,
  - asymmetry vulnerabilities,
  - triangle conflicts,
  - top threats.
- Adversarial and coalition action set:
  - `propose_coalition`, `defect`, `betray`, `isolate`, `commit_total_war`.
- Surprise-amplified trust updates with hard collapse on trusted betrayal.
- Paine-like alliance constraint penalties.
- Death-ground phase shift (`Survival_Resource < threshold`) with risk inversion and burn-the-boats signaling.

## Files

- `mas_recursive_reasoner.py`: core engine + trace logger.
- `run_recursive_series.py`: runs 4-7 agent series and writes outputs.
- `schemas.md`: explicit schema breakdown.
- `reasoning_analysis.md`: detailed MAS reasoning breakdown and design rationale.
- `logs/decision_trace_stream.jsonl`: appended per-decision trace stream.
- `logs/build_process.log`: build-time work log.
- `outputs/recursive_series_*`: summary and per-episode metrics.

## Important note on reasoning logs

This project logs explicit decision traces and rationale text that are safe to externalize.
It does not log hidden private chain-of-thought.

## Run

```powershell
python C:\projects\GPTStoryworld\social-reasoning\recursive-reasoning\run_recursive_series.py --min-agents 4 --max-agents 7 --episodes 16 --turns 10
```

Outputs:
- `outputs/recursive_series_4_7_summary.json`
- `outputs/recursive_series_4_7_episodes.csv`
- `logs/decision_trace_stream.jsonl`
