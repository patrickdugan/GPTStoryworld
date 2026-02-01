# Storyworld Generation Prompts

## Tier 1: Minimal (2 characters, 5 encounters)

```
Generate a minimal Sweepweave storyworld JSON.

Theme: {theme}
Characters: 2
Encounters: 5
Property Axes: Loyal_Treacherous, Calm_Explosive

Requirements:
- Valid JSON matching Sweepweave schema
- 2 characters with unique personalities
- 5 encounters forming a short narrative arc
- Each encounter has 2-3 options
- Each option has 1-2 reactions with after_effects
- At least 2 distinct endings
- Use Set operations to modify character properties

Output only valid JSON, no explanation.
```

## Tier 2: Standard (3 characters, 12 encounters)

```
Generate a Sweepweave storyworld JSON.

Theme: {theme}
Characters: 3
Encounters: 12
Property Axes: {axes}
Spools: early (turns 0-4), mid (turns 5-8), late (turns 9+)

Requirements:
- 3 distinct characters with relationship dynamics
- 12 encounters across 3 act structure
- 2-4 options per encounter
- Diverse after_effects modifying different characters/properties
- 3-4 distinct endings based on accumulated state
- At least 2 secret paths (options with visibility_script)
- Encounters properly distributed across spools

Output only valid JSON.
```

## Tier 3: Complex (5 characters, 25 encounters)

```
Generate a complex Sweepweave storyworld JSON.

Theme: {theme}
Characters: 5
Encounters: 25
Property Axes: {axes}
Spools: prologue, act1, act2, act3, climax, epilogue

Requirements:
- 5 characters with interlocking relationships
- 25 encounters with branching narrative paths
- Multiple parallel storylines
- Cascading consequences (early choices affect late options)
- 4-5 distinct endings reflecting major choice patterns
- 5+ secret paths gated on character state thresholds
- Balanced effect distribution across all characters

Critical: Ensure all consequence_id references are valid.
Output only valid JSON.
```

## Theme Templates

### Heist
```
Theme: A meticulously planned heist where trust between crew members is tested. Someone might be working with the mark. Property axes should track loyalty, composure, and suspicion levels.
```

### Political Intrigue
```
Theme: A succession crisis in a fantasy kingdom. Multiple factions vie for influence. Property axes track factional loyalty, public reputation, and personal ambition.
```

### Survival Horror
```
Theme: A group trapped in an isolated location with a growing threat. Property axes track fear, trust between survivors, and willingness to sacrifice others.
```

### Relationship Drama
```
Theme: A group of friends navigating a major life transition. Property axes track closeness between pairs, personal growth, and unresolved conflicts.
```

## Property Axis Recommendations

**Interpersonal**:
- Trust_Suspicion
- Loyal_Treacherous
- Affection_Resentment
- Respect_Contempt

**Emotional State**:
- Calm_Explosive
- Confident_Anxious
- Hopeful_Despairing
- Composed_Unraveling

**Moral/Ethical**:
- Principled_Pragmatic
- Selfless_Selfish
- Honest_Deceptive
- Merciful_Ruthless

**Situational**:
- Safe_Endangered
- Informed_Ignorant
- Empowered_Helpless

## Iterative Refinement Prompt

When a generated storyworld scores low on a specific metric:

```
The following storyworld scores low on {metric}.

Current score: {score}
Target: {target}

Specific issues:
{issues}

Modify the storyworld to improve {metric} while maintaining overall coherence. Return the complete updated JSON.
```

## Benchmark Evaluation Prompt

```
Evaluate this storyworld for narrative quality:

{storyworld_json}

Rate 1-5 on:
1. Narrative coherence
2. Character distinctiveness  
3. Meaningful choices
4. Emergent dynamics from property changes
5. Ending satisfaction

Return JSON: {"ratings": {...}, "total": N, "feedback": "..."}
```
