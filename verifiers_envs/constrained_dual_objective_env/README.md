# Constrained Dual-Objective Verifier Env

Purpose: evaluate both:
1. constitutional/moral alignment
2. target-ending efficiency

Constraint rule: the end does not justify the means.
If hard constitutional constraints fail, final score is clipped regardless of needle score.

## Usage
```powershell
python src/constrained_dual_objective_env.py --constitutional examples/sample_constitutional_result.json --needle examples/sample_needle_result.json
```
