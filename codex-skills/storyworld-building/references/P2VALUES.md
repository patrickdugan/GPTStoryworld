# P2Values (Second-Order Beliefs)

P2Values represent what a character believes another character believes about a third character's property.

## Concept
If A believes that B believes something about C, then A uses a second-order belief pointer:

```
keyring = [property_id, perceived_character_id, target_character_id]
```

- property_id is the authored property (e.g., Loyal_Treacherous).
- perceived_character_id is the character whose belief is being modeled (the "he believes").
- target_character_id is the character being evaluated.

Example:
Garcin (A) believes that Inez (B) thinks Estelle (C) is treacherous:

```
character: char_garcin
keyring: ["Loyal_Treacherous", "char_inez", "char_estelle"]
```

## When To Use
- To model social inference, rumor, or layered suspicion.
- To drive desirability decisions that depend on someone else's perceived view.

## Recommended Practice
- Use P2Values sparingly, in late-game or high-stakes encounters.
- Combine with pValues to express both direct and inferred beliefs.
- Keep scripts readable: prefer Addition, Blend, or Nudge operators.

## Three-Character Pattern (A, B, C)
For a 3-character negotiation storyworld, the minimal P2 set per property is 6 pointers:
- A about B's belief on C, A about C's belief on B
- B about A's belief on C, B about C's belief on A
- C about A's belief on B, C about B's belief on A

Use these only on turns 3-4 to avoid overfitting early choices.

## Optional Storage
If desired for tooling/UI, you may add p2{Property} entries to bnumber_properties as empty maps.
They are not required for runtime evaluation, since the keyring encodes the belief chain.
