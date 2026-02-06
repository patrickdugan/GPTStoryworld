# Game-Theory Pattern Library for Storyworld Negotiation

This list is organized to align with existing `AI_Diplomacy` archetype naming where possible.

## Core decision patterns

1. Coalition compact
- Existing anchor: `coalition_compact_01`.
- Decision: join anti-hegemon bloc now vs stay uncommitted.
- pValue signature: high `p[i,j,reciprocity]` and converging threat beliefs.
- p2 signature: high `p2[i,j,i,promise_keeping]`.

2. Insurance alliance
- Existing anchor: `insurance_alliance_10`.
- Decision: limited pact with explicit escape hatch.
- Signature: medium trust, high uncertainty, two-front risk.
- Outcome: downside reduction without full lock-in.

3. Common enemy alignment
- Existing anchor: `common_enemy_07`.
- Decision: cooperate despite low bilateral trust because third party threat is dominant.
- Signature: low bilateral loyalty but high threat gradient vs third actor.

4. DMZ bargain
- Existing anchor: `dmz_bargain_05`.
- Decision: convert border conflict into temporary peace for tempo gain elsewhere.
- Signature: moderate trust, strong short-horizon opportunity cost.

5. Defection without betrayal
- Existing anchors: `tradeoff_split_06`, partial overlap with `deterrent_signal_09`.
- Decision: reduce support or re-prioritize fronts without explicit lie/backstab.
- Signature: pValue drop in reciprocity, but limited drop in promise_keeping.

6. Betrayal / backstab first
- Existing anchor: `backstab_first_03`.
- Decision: pre-emptively strike partner before they scale.
- Signature: sharp expected gain, high immediate reputation cost.
- p2 role: if `p2[i,j,i,promise_keeping]` collapses, betrayal probability spikes.

7. Grudger memory / retaliatory equilibrium
- Existing anchor: `grudger_memory_02`.
- Decision: punish once-betrayed partner even at short-term cost.
- Signature: low forgiveness parameter and long memory of betrayal events.

8. Tit-for-tat reciprocity loop
- Existing anchor: `tit_for_tat_08`.
- Decision: mirror prior support or prior defection.
- Signature: high responsiveness, moderate noise tolerance.

9. Credible threat signaling
- Existing anchor: `credible_threat_04` and `deterrent_signal_09`.
- Decision: pay small current cost to make punishment promise believable.
- Signature: rise in perceived risk_tolerance and promise_keeping consistency.

10. Isolation / hedged neutrality
- Existing anchor: partial overlap with `insurance_alliance_10`.
- Decision: avoid deep commitments while preserving optionality.
- Signature: medium to low trust everywhere, low coalition stability expectation.

11. Death-ground commitment
- Decision: choose irreversible commitment when retreat set is collapsing.
- Signature: high existential risk + high commitment credibility when no safe fallback remains.
- Use: increases deterrence and can force coordination from allies.

## Transition graph (macro)

- `coalition -> insurance -> isolation` when trust erodes slowly.
- `coalition -> betrayal` when short-term advantage exceeds reputation penalty.
- `betrayal -> grudger` when memory is persistent.
- `isolation -> death_ground` when threat pressure removes safe neutrality.
- `death_ground -> deterrence success` if commitment is believed.

## Minimal storyworld implementation hooks

- Every pattern should define:
  - one forecast question,
  - one explicit ask,
  - one verification event next turn,
  - one pValue update,
  - one p2Value update.

- Strong patterns should also include:
  - one witness-based p2 update (`A` updates belief about `B`'s belief on `C`),
  - one reputational spillover effect to non-target agent.
