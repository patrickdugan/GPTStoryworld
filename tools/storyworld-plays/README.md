# Storyworld Plays Capture

This folder standardizes UI spot-check captures for storyworld quality review.

## Purpose
- Launch local SweepWeave UI (`npm run dev`) in `sweepweave-ts`.
- Load one or more storyworld JSON files.
- Capture screenshots across key tabs.
- Store artifacts in `D:\storyworld-plays\...` for taste/reference corpora.

## Usage
```powershell
powershell -ExecutionPolicy Bypass -File tools/storyworld-plays/run_spotcheck.ps1 `
  -Files "C:\projects\GPTStoryworld\storyworlds\diplomacy\forecast_backstab_p.json","C:\projects\GPTStoryworld\storyworlds\robert_of_st_albans.json"
```

Default output root: `D:\storyworld-plays`

## Output
Each run creates:
- `manifest.json`
- One folder per storyworld with:
  - `01-overview.png`
  - `02-encounters.png`
  - `03-rehearsal.png`
  - `04-notable-outcomes.png`
