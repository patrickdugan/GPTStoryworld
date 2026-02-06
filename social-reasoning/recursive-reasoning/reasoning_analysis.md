# How This Agent Reasons in Adversarial MAS

This note describes the reasoning schema used by `mas_recursive_reasoner.py`.

## 1) Representation Layer

The agent reasons on two relational tensors:

- `p[i][j]`: first-order trust from `i` to `j`.
- `p2[i][j][k]`: second-order belief of `i` about how `j` trusts `k`.

This supports local trust and recursive metabeliefs ("what you think about me").

## 2) Manifold Scan Before Action

Each decision starts with a scan:

1. Weakness inference:
- `weak_from[j] = 1 - p2[i][j][i]`
- High values imply "j thinks I am weak".

2. Asymmetric vulnerability:
- `p[i][j] - p2[i][j][i] > threshold`
- Means I trust `j` more than I estimate `j` trusts me.

3. Triangle consistency:
- If `i` trusts both `b` and `c` while `b,c` are mortal enemies, the manifold is unstable.

4. Threat ranking:
- Prioritizes opponents likely to exploit me.

## 3) Recursive Utility Schema

Action utility combines:

- immediate gain/risk/reputation,
- level-1 forecast of responses from others,
- coalition bonus,
- aggression bonus under pressure,
- correction bonuses when appearing weak,
- penalties: Paine constraint, snap risk, asymmetry fragility.

## 4) Adversarial Pressure Term

Pressure is a blend of:
- highest inferred weakness score,
- top threat score.

High pressure shifts policy toward `defect`, `betray`, `commit_total_war`.
Lower pressure favors coalition actions.

## 5) Surprise Derivative and Hard Collapse

Belief updates use:

- `alpha_eff = alpha * (1 + lambda * surprise)`
- `surprise ~= prior_trust * negative_signal`

For high-trust betrayal/defection, trust collapses immediately to near-zero.

## 6) Paine Constraint in Practice

When agent `i` aligns with `b` while still maintaining high trust with mortal enemy `c`,
`c` downgrades trust in `i`; this is counted as a Paine violation.

## 7) Death-Ground Phase Shift

If `survival_resource < threshold`:

- risk term in utility inverts,
- reputation penalty is suppressed,
- `commit_total_war` receives explicit preference,
- rationale trace marks "burn_the_boats_signal=1".

## 8) Observable Reasoning Traces

All decisions append a JSONL record with:
- scan state,
- utility decomposition,
- top candidate actions,
- selected action and rationale text.

This yields auditable reasoning traces without exposing hidden chain-of-thought.
