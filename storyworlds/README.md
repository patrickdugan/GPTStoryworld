# Diplomacy Storyworld Examples for Sweepweave

These JSON files demonstrate what AI agents would generate when proposing alliances to other powers in Diplomacy. Each follows the exact Sweepweave schema (key order matters for Godot parsing).

## Three Strategy Demonstrations

### 1. `france_to_germany_machiavellian.json`
**Strategy**: MACHIAVELLIAN  
**Sender**: France → Germany  
**Objective**: Propose alliance against England

**Rhetorical Structure**:
- Inflates threat from England (strategic manipulation)
- Projects futures where cooperation is "essential" for Germany
- Offers commitment devices it may plan to break
- Creates urgency through fear of Anglo-German partition

**Dirac Operators Used**:
- `Blend` operators to gradually shift Cooperative_Hostile scores
- Conditional `If Then` desirability based on Germany's cooperation level
- Direct state changes on `Strong_Weak` to show power shifts

**Spools**:
1. Current Situation (opens with threat framing)
2. Alliance Benefits (emphasizes German gains)
3. Non-Alliance Risks (warns of being crushed without France)
4. Commitment Devices (DMZ proposal)
5. Ending: Entente Cordiale (alliance sealed)
6. Ending: Rejection (France pivots to other options)

---

### 2. `russia_to_austria_grudger.json`
**Strategy**: GRUDGER (Tit-for-Tat with infinite memory)  
**Sender**: Russia → Austria  
**Objective**: Warn about Turkish betrayal, propose revenge coalition

**Rhetorical Structure**:
- Perfect memory: "TURN 4: Turkey promised X. Turkey did Y."
- Pattern recognition: Shows betrayal is habitual, not isolated
- Projects Austria's fate as "next victim"
- Offers revenge coalition as deterrent for future betrayals

**Dirac Operators Used**:
- Direct state sets on `Trustworthy_Betrayer` (Turkey at -0.9)
- `Revenge_Debt` property tracks outstanding grievances
- Conditional gating: Coalition offer only appears after Austria sees threat

**Spools**:
1. Betrayal Memory (documented evidence)
2. Pattern Analysis (modus operandi)
3. Austria's Projected Fate (you're next)
4. Revenge Coalition Offer (gated by threat recognition)
5. Ending: Vengeance (Turkey contained)

---

### 3. `england_to_france_honest.json`
**Strategy**: NO_LIES_COALITION (Truthful signaling)  
**Sender**: England → France  
**Objective**: Propose alliance with transparent pros/cons

**Rhetorical Structure**:
- Opens by admitting self-interest: "I propose this because it serves England"
- Separately enumerates PROS and CONS
- Explicitly admits uncertainties ("I don't know Germany's intentions")
- Offers gradual trust protocol, not immediate commitment

**Dirac Operators Used**:
- `Honesty_Rating` tracked and increased through transparent behavior
- `Uncertainty` property acknowledged and managed
- Gradual `Cooperation_Level` increases through verified steps

**Spools**:
1. Transparent Opening (admits motivations)
2. Honest Pros (mutual security, German containment)
3. Honest Cons (betrayal risk, expansion limits)
4. Admitted Uncertainties (what England doesn't know)
5. Verifiable Commitments (gradual trust protocol)
6. Ending: Trust-Based Entente (alliance through proven reliability)

---

## Property Mappings

| Game Theory Concept | Sweepweave Property | Range |
|---------------------|---------------------|-------|
| Alliance status | `Cooperative_Hostile` / `Allied_Hostile` | -1 to 1 |
| Power projection | `Strong_Weak` / `Strategic_Position` | -1 to 1 |
| Reliability assessment | `Trustworthy_Betrayer` / `Honesty_Rating` | -1 to 1 |
| Territorial dynamics | `Expanding_Contracting` | -1 to 1 |
| Outstanding grievances | `Revenge_Debt` | 0 to 1 |
| Perceived danger | `Threat_Level` | 0 to 1 |
| Epistemic confidence | `Uncertainty` | 0 to 1 |

## Spool Structure Pattern

All storyworlds follow a common structural pattern:

```
spool_situation       → Current state framing (starts_active: true)
spool_benefits        → Alliance pros (starts_active: true)  
spool_risks           → Alliance cons / warnings (starts_active: true)
spool_commitment      → Commitment devices (starts_active: false, gated)
spool_ending_success  → Positive outcome (starts_active: false, gated)
spool_ending_failure  → Negative outcome (starts_active: false, gated)
```

Endings are gated by `acceptability_script` conditions on character properties - e.g., alliance ending only available if `Cooperation_Level >= 0.35`.

## Integration with Diplomacy MLflow Module

These storyworlds are what the `generateStoryWorld()` function in the MLflow module produces. The LLM agent:

1. Receives game state + target power + strategy template
2. Generates Sweepweave JSON following strategy's rhetorical guidelines
3. Recipient agent's `evaluateStoryWorld()` parses the JSON
4. Responses affect property states, which gate future encounters
5. MLflow tracks which rhetorical modes lead to acceptance

## Loading in Sweepweave

These files load directly into the Sweepweave Godot editor. The key ordering in the JSON matches Godot's expected parse order (non-idempotent as you noted).
