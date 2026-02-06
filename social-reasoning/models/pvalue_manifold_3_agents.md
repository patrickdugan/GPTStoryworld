# 3-Agent pValue/p2Value Manifold Model

## 1) Entities and latent personality space

Let agents be `A`, `B`, `C`.

Each agent `i` has a latent personality vector:

`theta_i in R^d`

Example trait axes in `d`:
- loyalty
- risk_tolerance
- reciprocity
- aggressiveness
- promise_keeping

These are the "base" personality coordinates.

## 2) Tiny relational dimensions (pValues)

For each ordered pair `(observer=i, target=j)` and trait `k`, define:

`p[i,j,k]`

Interpretation:
- `p[A,B,loyalty]` = A's estimate of B's loyalty.

These are small relational dimensions "attached" to the base manifold.
Think of them as local fibers over each agent's latent state:

`M = (Product_i theta_i) x (Product_{i!=j} p[i,j,:]) x (Product_{i!=j!=m} p2[i,j,m,:])`

So base personality is global; p-values are local directional beliefs.

## 3) Second-order dimensions (p2Values)

For ordered triple `(observer=i, mediator=j, target=m)` and trait `k`:

`p2[i,j,m,k]`

Interpretation examples:
- `p2[A,B,A,loyalty]`: A's belief about B's pValue of A's loyalty.
- `p2[A,B,C,loyalty]`: A's belief about B's pValue of C's loyalty.

This is "I believe what you believe about X" structure.

## 4) Dynamics from events

At turn `t`, observe event `e_t` with actor `u`, target `v`, action `a`.

### 4.1 Direct pValue update

`p_t+1[i,u,k] = clip((1-alpha_k)*p_t[i,u,k] + alpha_k * signal_k(e_t, i), 0, 1)`

Where:
- `signal_k` maps observed behavior to trait evidence.
- `alpha_k` can be trait-specific learning rate.

Typical signal sketches:
- support action -> positive loyalty/reciprocity signal
- unilateral defection -> negative reciprocity signal
- betrayal after pledge -> sharp negative promise_keeping signal
- isolation/non-commitment -> mild negative coalition_compatibility signal

### 4.2 p2Value update (meta-belief assimilation)

`p2_t+1[i,j,m,k] = clip((1-beta_k)*p2_t[i,j,m,k] + beta_k * inferred_p_of_j_about_m, 0, 1)`

Where `inferred_p_of_j_about_m` is inferred from j's messages/orders/actions.

### 4.3 Surprise-weighted update

To make sudden betrayals matter more:

`alpha_eff = alpha_k * (1 + lambda * surprise)`

`surprise = abs(observed_outcome - expected_outcome)`

## 5) Action utility over this state

For agent `i`, target `j`, action `a`:

`U_i(a,j) = w_gain * Gain(a,j)
          + w_rel  * p[i,j,reciprocity]
          + w_meta * p2[i,j,i,promise_keeping]
          - w_risk * Risk(a,j)
          - w_rep  * ReputationCost(a)`

Use softmax over action utilities for stochastic policy.

## 6) Canonical action set (3-agent start)

- join_coalition(i, j, against=m)
- defect_from_coalition(i, j)
- betray_partner(i, j, with=m)
- isolate_or_hedge(i)
- commit_death_ground(i, against=j)

`commit_death_ground` raises immediate risk but can improve deterrence and resolve signaling.

## 7) Storyworld keyring mapping (skill-compatible)

Direct pValue keyring (length 2):
- `[property_id, perceived_character_id]`
- Example: `["loyalty", "B"]` in A's state context.

Second-order p2 keyring (length 3):
- `[property_id, perceived_character_id, target_character_id]`
- Example: `["loyalty", "B", "C"]` in A's state context.

Desirability scripts should read these keys; after-effects should nudge these keys.

## 8) Minimal calibration plan

1. Start with 3 agents and 2 to 4 traits.
2. Initialize p and p2 near neutral (`0.5`) with small personality-informed offsets.
3. Run scripted episodes for archetypes (coalition, betrayal, isolation, death-ground).
4. Fit `alpha`, `beta`, and utility weights to maximize forecast calibration and narrative coherence.
5. Expand to 7 agents only after 3-agent stability is reliable.
