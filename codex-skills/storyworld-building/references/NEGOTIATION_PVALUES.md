# Negotiation PValues and P2Values (4-Turn / 10-Encounter Template)

This guide defines how to express first- and second-order beliefs for short negotiation storyworlds
(4 turns, ~10 encounters, 3 characters) so that multi-agent reasoning is explicit and causal.

## Target Structure
- 3 characters: A, B, C.
- 4 turns with ~10 encounters total (2-3 encounters per turn).
- 2-3 key properties per character (e.g., Trust_Threat, Loyal_Treacherous).
- pValues drive early perception; p2Values drive late-stage betrayal/defection decisions.

## Minimal Belief Set (Per Property)
PValues (first-order): 6 total
- A->B, A->C, B->A, B->C, C->A, C->B

P2Values (second-order): 6 total
- A about B's belief on C, A about C's belief on B
- B about A's belief on C, B about C's belief on A
- C about A's belief on B, C about B's belief on A

## Turn-by-Turn Causality
Turn 1 (setup, 2 encounters)
- Establish initial pValues from direct offers.
- Example effect: A accepts B's offer -> Nudge pValue(A, Trust_Threat[B]) up.

Turn 2 (signals, 2-3 encounters)
- Introduce conflicting signals and third-party gossip.
- Example effect: A sees C contradict B -> Nudge pValue(A, Trust_Threat[B]) down; Nudge pValue(A, Threat_Trust[C]) up.

Turn 3 (second-order inference, 2-3 encounters)
- Introduce p2Values tied to explicit claims about who trusts whom.
- Example effect: B tells A that C expects A to defect -> Nudge p2Value(A, Trust_Threat[C, perceived=B]) upward.

Turn 4 (commitment/betrayal, 2-3 encounters)
- Use p2Values in desirability scripts to trigger betrayal/defection choices.
- Example desirability: if p2Value(A believes B believes C is treacherous) is high, A prefers to defect first.

## Design Rules
- Each encounter should update at least one pValue or p2Value.
- Do not introduce p2Values before turn 3.
- Gate betrayal options on p2Values, not just base properties.
- Include at least one witness-driven update per turn (third-party observation).

## Example Desiderata Patterns
- "Defect now" option is more desirable if p2Value(A about B->C) indicates B expects C to betray.
- "Join coalition" option is more desirable if pValue(A->B) is high AND p2Value(A about C->B) is low.

## Output Naming for Bank Upgrades
- When upgrading storyworlds, append _p to the storyworld id and filename.
- Example: forecast_coalition -> forecast_coalition_p
- Preserve the original; only add new pValue/p2Value effects and desirability scripts.
