# Storyworld Manifold Geometry

Mathematical foundations for treating storyworlds as navigable manifolds with inner-product dynamics.

## State Space as Vector Bundle

A storyworld with `N` distinct property axes and `C` characters defines a state space:

```
S = R^N  (civilization-level variables)
    × R^(N×C)  (per-character replication)
    × {0,1}^|Spools|  (spool activation flags)
```

The **narrative manifold** M ⊂ S is the subspace reachable via valid action sequences from initial state s₀.

## Inner Product Structure

Each property axis `p_i` defines a dimension. The **narrative distance** between states uses the inner product:

```
⟨s₁, s₂⟩ = Σᵢ wᵢ · s₁[i] · s₂[i]
```

where `wᵢ` are axis-specific weights (e.g., Embodiment_Virtuality may have higher narrative salience than Influence).

### Effect Operators as Linear Maps

After-effects act as operators on the state vector:

```
s' = s + M · a
```

where:
- `s` is current state vector
- `a` is action encoding (one-hot or semantic embedding)
- `M` is the effect matrix mapping actions to state deltas

For Sweepweave's `Set` operation with `Nudge`:
```
M[i,j] = δ_ij · coefficient · delta_value
```

### Inner-Product Effects (Advanced)

For richer dynamics, effects can compute inner products with "virtue/vice" basis vectors:

```json
{
  "effect_type": "InnerProduct",
  "basis_vector": "virtue_compassion",
  "target_property": "Cosmic_Ambition_Humility",
  "coefficient": 0.1
}
```

This enables: `new_value = old_value + 0.1 * ⟨state, compassion_basis⟩`

## Guards as Manifold Constraints

### Boolean Guards (Hard Boundaries)

```
G_bool(s) = (s[Trust] > 0.6) ∧ (s[has_radio] = true)
```

These create **chart boundaries** — regions where certain options vanish entirely.

### Weighted Gates (Soft Access)

```
G_soft(s) = σ(w · s + b) > τ
```

where σ is sigmoid. This creates **probability gradients** rather than hard cutoffs.

### Visibility Scripts (Sweepweave Implementation)

```json
{
  "visibility_script": {
    "operator_type": "Arithmetic Comparator",
    "operator_subtype": "GTE",
    "operands": [
      {"pointer_type": "Bounded Number Pointer", "character": "char_civ", "keyring": ["Embodiment_Virtuality"]},
      {"pointer_type": "Bounded Number Constant", "value": 0.7}
    ]
  }
}
```

## Manifold Topology

### Local Dimension

At state `s`, the **local dimension** equals the number of variables that can change via available actions:

```
dim_local(s) = |{i : ∃ action a where effect(a)[i] ≠ 0 and guard(a, s) = true}|
```

### Curvature

**Narrative curvature** measures how fast guards prune paths:

```
κ(s) = -d/dt [log |A_valid(s_t)|]
```

High curvature = rapid option collapse (crisis points).
Low curvature = open exploration (stable plateaus).

### Recovery Radius

For a state `s` off the main path, the **recovery radius** `r(s)` is the minimum actions needed to reach any ending:

```
r(s) = min_{e ∈ Endings} d(s, e)
```

Storyworlds should maintain bounded recovery radius to avoid dead ends.

## Counter-Archivist Dynamics

The Counter-Archivist operates as an **adversarial agent** in the state space:

### Countercraft Accumulation

```
Countercraft_{t+1} = Countercraft_t + η · f(civ_transgression, civ_ambition)
```

When `Countercraft > threshold`, the Counter-Archivist can:
- Inject competing options
- Modify guard thresholds
- Reveal/hide information

### Grudge Mechanics

```json
{
  "character": "char_counter_archivist",
  "properties": {
    "Influence": 0,      // Narrative weight
    "Grudge": 0,         // Accumulated grievance
    "Countercraft": 0    // Strategic resources
  }
}
```

Grudge increases when civilization ignores Counter-Archivist challenges; high Grudge unlocks hostile options.

## Path-Dependent Gating (Priming)

Options in late-game can require **accumulated path history**, not just current state:

### Integral Guards

```
visible_if: ∫₀ᵗ Transgression(τ) dτ > threshold
```

Approximated via running sum property (prefix `p` properties in Sweepweave):

```json
{
  "id": "pTransgression_Order",
  "property_name": "pTransgression_Order", 
  "property_type": "bounded number",
  "depth": 1
}
```

### Implementation Pattern

1. Define both instantaneous (`Transgression_Order`) and cumulative (`pTransgression_Order`) properties
2. Effects update both: instant for current state, cumulative adds to history
3. Late-game guards check cumulative values

```json
{
  "visibility_script": {
    "operator_type": "Logical And",
    "operands": [
      {"operator_type": "GTE", "operands": [
        {"character": "char_civ", "keyring": ["pTransgression_Order"]},
        {"value": 0.5}
      ]},
      {"operator_type": "GTE", "operands": [
        {"character": "char_civ", "keyring": ["Cosmic_Ambition_Humility"]},  
        {"value": 0.3}
      ]}
    ]
  }
}
```

## Secret Endings as Attractors

Secret endings are **local minima** in the narrative potential landscape, reachable only via specific trajectories.

### Attractor Basin

For ending `e`, its basin `B(e)` is the set of states from which `e` is reachable:

```
B(e) = {s : ∃ action sequence π where π(s) → e}
```

### Secrecy Gradient

An ending is "more secret" when:
1. `|B(e)|` is small (narrow basin)
2. `|Guards(e)|` is high (many conditions)
3. `d(s₀, e)` is large (far from start)
4. Path requires non-obvious actions

### Implementation

```json
{
  "id": "page_end_boundary_hacking",
  "title": "Ending: Beyond the Laws",
  "acceptability_script": {
    "operator_type": "Logical And",
    "operands": [
      {"operator_type": "GTE", "operands": [
        {"keyring": ["pTransgression_Order"]}, {"value": 0.6}
      ]},
      {"operator_type": "GTE", "operands": [
        {"keyring": ["Risk_Stasis"]}, {"value": 0.4}
      ]},
      {"operator_type": "LTE", "operands": [
        {"character": "char_counter_archivist", "keyring": ["Countercraft"]},
        {"value": 0.3}
      ]}
    ]
  }
}
```

This ending requires: high cumulative transgression, risk-taking civilization, AND having kept the Counter-Archivist's resources low.

## Spectral Analysis (QFT Pipeline)

For long trajectories, compress via spectral decomposition:

1. Embed turns → matrix `E ∈ R^(T×N)`
2. Apply DFT per dimension → `Ê(ω)`
3. Extract salient frequency bands (recurring patterns)
4. PCA → compact "spectral motif card"

Cards enable cross-run similarity and retrieval for N-tries learning.

## Affordance Cardinality

At state `s`, the **affordance cardinality** is:

```
C(s) = |{a ∈ Actions : Guard(a, s) = true}|
```

Track `C(s)` along trajectories:
- High C = exploration phase
- Low C = commitment/crisis
- C → 1 = approaching ending

## Multi-Agent Roles

### Scout
- Maximizes state coverage
- Logs anomalies and guard boundaries
- Objective: `max Σ_t |visited_states_t|`

### Solver  
- Focuses on decoding requirements for secret endings
- Proposes action scripts
- Objective: `max P(secret_ending | actions)`

### Archivist
- Compresses trajectories into spectral cards
- Maintains cross-episode memory
- Objective: `min bits/symbol, max retrieval_hit@k`
