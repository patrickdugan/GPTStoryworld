# Integration Guide: Frontend + Original CLI

This document explains how the **GPT Storyworld Frontend** integrates with the original [CLI-based GPT Storyworld system](https://github.com/patrickdugan/GPTStoryworld).

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│         GPT Storyworld Frontend                 │
│  (This React App - Web-based Generation)        │
│                                                  │
│  • Visual parameter configuration                │
│  • Direct GPT-4 API calls                       │
│  • JSON export of encounters                    │
└─────────────────┬───────────────────────────────┘
                  │
                  │ Downloads: encounter_*.json
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│      Original CLI System (Node.js)              │
│                                                  │
│  • Iterative metadata tracking (meta.json)      │
│  • Encounter expansion from raw_storyworld.json │
│  • Balance analysis & guided generation         │
└─────────────────────────────────────────────────┘
```

## Workflow Options

### Option 1: Frontend-First Workflow

**Use Case**: Quick prototyping, visual configuration preference

1. **Configure in Frontend**: Use sliders to set parameters
2. **Generate Initial Encounter**: Download `encounter_1.json`
3. **Import to CLI**: 
   ```bash
   # Copy generated JSON to CLI project
   cp encounter_1.json ~/GPTStoryworld/encounters/
   
   # Run CLI for iterative expansion
   cd ~/GPTStoryworld
   npm start
   ```
4. **Iterate**: CLI handles metadata tracking and balance

### Option 2: CLI-First Workflow

**Use Case**: Batch processing, existing storyworld expansion

1. **Start with CLI**: Use `raw_storyworld.json` as normal
2. **Generate Multiple Encounters**: Let CLI build your world
3. **Fine-tune in Frontend**: When you need custom branches:
   - Load CLI's `meta.json` into memory
   - Use Frontend to generate specific encounters
   - Manually integrate back into CLI system

### Option 3: Hybrid Workflow

**Use Case**: Maximum flexibility, production storyworlds

```
Frontend (Initial Design) 
    ↓
CLI (Expansion + Balance)
    ↓
Frontend (Custom Branches)
    ↓
CLI (Metadata Integration)
```

## Data Format Compatibility

Both systems use the same JSON structure:

```json
{
  "encounter": "string",
  "choices": ["string", "string", "string"],
  "variables_affected": {
    "var_name": "delta_value"
  },
  "metadata": {
    "characters_present": ["string"],
    "themes_emphasized": ["string"],
    "narrative_weight": 0
  }
}
```

### Frontend Output

```json
// encounter_1732485920345.json
{
  "encounter": "You stand at the crossroads...",
  "choices": [
    "Take the forest path",
    "Follow the river",
    "Return to town"
  ],
  "variables_affected": {
    "suspicion": 5,
    "courage": -2
  },
  "metadata": {
    "characters_present": ["Player", "Mysterious Stranger"],
    "themes_emphasized": ["isolation", "choice"],
    "narrative_weight": 7
  }
}
```

### CLI's `raw_storyworld.json` Format

```json
{
  "title": "The Crossroads",
  "characters": [
    {"name": "Player", "traits": ["brave", "curious"]},
    {"name": "Mysterious Stranger", "traits": ["enigmatic"]}
  ],
  "themes": ["isolation", "choice", "destiny"],
  "variables": {
    "suspicion": 0,
    "courage": 10,
    "gold": 50
  },
  "encounters": []
}
```

## Migration Script

To migrate Frontend output → CLI format:

```javascript
// migrate.js
const fs = require('fs');

// Read Frontend output
const frontendEncounter = JSON.parse(
  fs.readFileSync('./encounter_1732485920345.json', 'utf8')
);

// Read CLI storyworld
const storyworld = JSON.parse(
  fs.readFileSync('./raw_storyworld.json', 'utf8')
);

// Merge encounter into CLI format
storyworld.encounters.push({
  id: `enc_${Date.now()}`,
  text: frontendEncounter.encounter,
  choices: frontendEncounter.choices.map((choice, idx) => ({
    text: choice,
    next: null, // You'll need to wire this up
    effects: frontendEncounter.variables_affected
  })),
  metadata: frontendEncounter.metadata
});

// Write back
fs.writeFileSync(
  './raw_storyworld.json',
  JSON.stringify(storyworld, null, 2)
);

console.log('✅ Encounter imported successfully');
```

## API Key Management

**Frontend**: Stores in `localStorage` (browser-based)
**CLI**: Uses `.env` file (Node.js)

### Sharing Keys Between Systems

```bash
# Export from Frontend localStorage
localStorage.getItem('openai_api_key')

# Add to CLI .env
echo "OPENAI_API_KEY=sk-..." > .env
```

## Best Practices

### 1. Use Frontend For

- Initial world design & prototyping
- Custom encounter generation
- Parameter experimentation
- Quick iterations without CLI setup

### 2. Use CLI For

- Batch generation of 10+ encounters
- Metadata balance tracking over time
- Automated expansion workflows
- Production storyworld builds

### 3. Integration Points

| Task | Best Tool | Why |
|------|-----------|-----|
| World concept | Frontend | Visual, intuitive |
| First 3-5 encounters | Frontend | Fast iteration |
| Expansion (5-50 enc) | CLI | Automation, tracking |
| Custom branches | Frontend | Precision control |
| Final balance pass | CLI | Meta.json analysis |

## Environment Variables

### Frontend (Optional)

Create `.env` in frontend root:

```bash
VITE_DEFAULT_MODEL=gpt-4
VITE_DEFAULT_TEMP=0.8
VITE_MAX_TOKENS=2000
```

Access via `import.meta.env.VITE_*`

### CLI (Required)

```bash
# .env
OPENAI_API_KEY=sk-...
GPT_MODEL=gpt-4
TEMPERATURE=0.7
```

## Troubleshooting

### "API Key Invalid" in Frontend

- Check key format: `sk-...`
- Verify at https://platform.openai.com/api-keys
- Try pasting directly (no spaces)

### JSON Format Mismatch

```bash
# Validate Frontend output
node -e "JSON.parse(require('fs').readFileSync('./encounter_*.json'))"
```

### CLI Not Finding Encounters

Ensure encounters are in `encounters/` directory:

```bash
mkdir -p encounters
cp ~/Downloads/encounter_*.json encounters/
```

## Future Enhancements

Potential integration features:

- [ ] Frontend imports CLI's `meta.json` for balance display
- [ ] CLI generates static site from Frontend UI
- [ ] Shared database (SQLite) for real-time sync
- [ ] CLI command: `gpt-sw import --frontend encounter_*.json`
- [ ] Frontend visualizes encounter graph from CLI data

## Support

Questions about integration? Open an issue:

- [Frontend Issues](https://github.com/patrickdugan/GPTStoryworld/issues)
- [CLI Issues](https://github.com/patrickdugan/GPTStoryworld/issues)

---

**TL;DR**: Frontend = visual design tool. CLI = production system. Use both!
