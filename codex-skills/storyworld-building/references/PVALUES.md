# PValues (First-Order Perceptions)

PValues represent what a character directly believes about another character's property.

## Concept
If A forms a belief about B's property, A uses a first-order belief pointer:

```
keyring = [property_id, perceived_character_id]
```

- property_id is the authored property (e.g., Trust_Threat, Loyal_Treacherous).
- perceived_character_id is the character being evaluated.
- The pointer lives on the perceiver (the character whose beliefs you are modeling).

Example:
Garcin (A) believes Estelle (B) is untrustworthy:

```
character: char_garcin
keyring: ["Trust_Threat", "char_estelle"]
```

## When To Use
- For direct impressions: promises kept/broken, threats, generosity, competence.
- For descriptive belief updates after each negotiation exchange.

## Recommended Practice
- For 3 characters (A, B, C), the minimal pValue set per property is 6 pointers:
  - A about B, A about C
  - B about A, B about C
  - C about A, C about B
- Update pValues in early turns (turns 1-2) to establish perception drift.
- Use pValues in desirability scripts so choices reflect what the actor thinks, not just objective facts.

## Example Use In Causality
- Turn 1: A hears B's offer -> increase A's pValue Trust about B.
- Turn 2: A sees C undermine B -> decrease A's pValue Trust about B; increase A's pValue Threat about C.
- Turn 3-4: p2Values build on the stabilized pValues.
