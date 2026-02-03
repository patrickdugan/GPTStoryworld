# Late-Stage Tail Tuning (Ending Dominance Control)

Use this when Monte Carlo shows a single ending >30% or a tail ending too rare.

Checklist
1) Identify the dominant ending(s) and the tail endings.
2) Reduce dominant ending desirability weight or bias.
3) Increase tail ending desirability bias slightly (0.005–0.03).
4) Avoid tightening acceptability too far; prefer desirability tweaks first.
5) Re-run Monte Carlo (5k–10k runs) until max ending <30%.

Rules of Thumb
- Reduce dominant desirability multiplier by ~0.2–0.4 per iteration.
- Add a small constant bias (0.005–0.02) to tail endings.
- Keep at least one always-acceptable ending as fallback.

Automation
- Use scripts/late_stage_tail_tuning.py to apply a multiplier to one ending
  and a small bias to a list of tail endings, then run Monte Carlo.
