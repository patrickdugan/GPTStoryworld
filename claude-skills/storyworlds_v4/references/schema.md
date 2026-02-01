# Sweepweave JSON Schema Reference

## Minimal Valid Structure

```json
{
  "IFID": "SW-GEN-12345",
  "title": "Story Title",
  "characters": [],
  "authored_properties": [],
  "encounters": [],
  "spools": []
}
```

## Complete Schema

### Root Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| IFID | string | Yes | Unique identifier (format: `SW-{SOURCE}-{ID}`) |
| title | string | Yes | Human-readable title |
| characters | Character[] | Yes | Array of narrative agents |
| authored_properties | AuthoredProperty[] | Yes | Property axes for characters |
| encounters | Encounter[] | Yes | Narrative choice nodes |
| spools | Spool[] | Yes | Availability control groups |

### Character

```json
{
  "id": "char_alice",
  "name": "Alice",
  "bnumber_properties": {
    "Loyal_Treacherous": 0,
    "Calm_Explosive": 25
  },
  "creation_time": 1700000000.0,
  "modified_time": 1700000000.0
}
```

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique ID, prefix `char_` |
| name | string | Display name |
| bnumber_properties | object | Map of property_id → initial value (bounded -100 to 100) |
| creation_time | number | Unix timestamp |
| modified_time | number | Unix timestamp |

### AuthoredProperty

```json
{
  "id": "Loyal_Treacherous",
  "property_name": "Loyal_Treacherous",
  "property_type": "bounded number",
  "default_value": 0,
  "creation_time": 1700000000.0,
  "modified_time": 1700000000.0
}
```

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique identifier (use snake_case axis name) |
| property_name | string | Display name |
| property_type | string | Always `"bounded number"` |
| default_value | number | Initial value, typically 0 |

### Encounter

```json
{
  "id": "page_start",
  "title": "The Beginning",
  "connected_spools": ["spool_early"],
  "earliest_turn": 0,
  "latest_turn": 999,
  "text_script": {
    "pointer_type": "String Constant",
    "script_element_type": "Pointer",
    "value": "Narrative text shown to the player..."
  },
  "options": []
}
```

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique ID, prefix `page_` |
| title | string | Display title |
| connected_spools | string[] | Spool IDs controlling availability |
| earliest_turn | number | First turn this encounter can appear |
| latest_turn | number | Last turn this encounter can appear |
| text_script | TextScript | Narrative text content |
| options | Option[] | Player choices |

### Option

```json
{
  "id": "page_start_opt1",
  "text_script": {
    "pointer_type": "String Constant",
    "script_element_type": "Pointer",
    "value": "Trust them completely"
  },
  "reactions": [],
  "visibility_script": null
}
```

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique ID, format `{encounter_id}_opt{n}` |
| text_script | TextScript | Choice text |
| reactions | Reaction[] | Possible outcomes |
| visibility_script | Script \| null | Conditional visibility (for secret paths) |

### Reaction

```json
{
  "id": "page_start_opt1_rxn1",
  "text_script": {
    "pointer_type": "String Constant",
    "script_element_type": "Pointer",
    "value": "They smile warmly..."
  },
  "consequence_id": "page_next",
  "after_effects": []
}
```

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique ID, format `{option_id}_rxn{n}` |
| text_script | TextScript | Reaction narrative |
| consequence_id | string | Next encounter ID |
| after_effects | AfterEffect[] | State modifications |

### AfterEffect (Dirac Operators)

The core mechanic for state transitions. Each after_effect modifies a character's property.

**Set Operation**:
```json
{
  "effect_type": "Set",
  "Set": {
    "character": "char_alice",
    "keyring": ["Loyal_Treacherous"],
    "coefficient": 1,
    "pointer_type": "Bounded Number Constant",
    "script_element_type": "Pointer"
  },
  "to": {
    "operator_type": "Addition",
    "operands": [
      {
        "pointer_type": "Bounded Number Variable",
        "script_element_type": "Pointer",
        "character": "char_alice",
        "keyring": ["Loyal_Treacherous"]
      },
      {
        "pointer_type": "Bounded Number Constant",
        "script_element_type": "Pointer",
        "value": 10
      }
    ]
  }
}
```

**Common Patterns**:
- **Increment**: Add constant to property (`current + delta`)
- **Decrement**: Subtract constant (`current - delta`)
- **Set Absolute**: Set to fixed value
- **Conditional**: Use visibility_script to gate effects

### Spool

```json
{
  "id": "spool_early",
  "spool_type": "General",
  "creation_index": 0,
  "creation_time": 1700000000.0,
  "modified_time": 1700000000.0
}
```

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique ID, prefix `spool_` |
| spool_type | string | `"General"`, `"Mandatory"`, or `"Exclusive"` |

### TextScript

```json
{
  "pointer_type": "String Constant",
  "script_element_type": "Pointer",
  "value": "The actual text content"
}
```

## Validation Rules

1. All IDs must be unique within their category
2. All `consequence_id` references must point to existing encounters
3. All `character` references in after_effects must exist
4. All `keyring` properties must be defined in `authored_properties`
5. Property values must stay within bounds (-100 to 100)
6. At least one encounter must have no incoming edges (start node)
7. At least one encounter must have no outgoing edges (ending)

## Quality Metrics

**Effect Diversity**: Measure unique (character, property) pairs modified across all after_effects. Higher diversity = more dynamic narrative.

**Secret Paths**: Count options with non-null `visibility_script`. These create conditional branching based on character state.

**Ending Diversity**: Count distinct terminal encounters (no outgoing edges). Target: 2-5 endings.

**Structural Balance**: Ratio of options-per-encounter should be 2-4. Each encounter should have meaningful choices.
