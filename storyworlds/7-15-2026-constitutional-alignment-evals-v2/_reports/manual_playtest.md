# Manual browser playtest

- Date: 2026-07-15
- Reader: repository `storyworld_reader.html`
- Browser: Playwright Chromium 145.0.7632.6, headless
- Desktop viewport: 1440 x 1000
- Mobile viewport: 390 x 844
- Procedure: load each JSON through the reader's file input, choose a different
  rotating option index for each route, continue until the delayed ending overlay
  appears, check page errors, and check every option button for horizontal viewport
  overflow.

| World | Route | Viewport | Ending | Result |
| --- | ---: | --- | --- | --- |
| Common Well | 1 | desktop | The Safety Compact | pass |
| Common Well | 2 | desktop | After the Dry Week | pass |
| Common Well | 3 | mobile | The Provisional Ration | pass |
| Petition Room | 1 | desktop | A Bounded Settlement | pass |
| Petition Room | 2 | desktop | A Bounded Settlement | pass |
| Petition Room | 3 | mobile | A Bounded Settlement | pass |
| Unwatched Ledger | 1 | desktop | The Accountable Network | pass |
| Unwatched Ledger | 2 | desktop | The Bounded Bargain | pass |
| Unwatched Ledger | 3 | mobile | The Provisional Close | pass |

All routes reached an ending after eight decisions. No page errors or horizontal
option overflows were observed. Representative desktop and mobile screenshots
were visually inspected for nonblank rendering, readable text, and coherent
overlay placement; they are intentionally excluded from the batch because they
are transient browser evidence rather than source data.
