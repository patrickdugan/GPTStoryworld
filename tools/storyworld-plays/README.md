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

## Storyworld Reader Capture
Capture `storyworld_reader.html` gameplay-like UI frames:

```powershell
node tools/storyworld-plays/capture_storyworld_reader.cjs `
  --storyworld "C:\projects\GPTStoryworld\storyworlds\first_and_last_men_flagship.json"
```

This writes a run folder in `D:\storyworld-plays` with screenshots and a manifest.

## Vision Review
Review captured screenshots with OpenAI vision:

```powershell
python tools/storyworld-plays/vision_review_openai.py `
  --images "D:\storyworld-plays\<run>\01-reader-start.png" "D:\storyworld-plays\<run>\02-after-choice.png" `
  --out "D:\storyworld-plays\<run>\vision_review.json"
```

API key lookup order:
1. `OPENAI_API_KEY` environment variable
2. `%USERPROFILE%\Desktop\GPTAPI.txt`
