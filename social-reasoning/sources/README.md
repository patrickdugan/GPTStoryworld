# Sources Mirror

This folder mirrors all cited references used in the social-reasoning draft.

## Layout

- `web/`: HTML snapshots of cited web pages.
- `pdf/`: ArXiv PDFs copied from `papers/arxiv/`.
- `local/`: Local repo files copied for continuity.
- `source_manifest.csv`: Inventory with status, source URL/path, and local file path.

## Refresh

```powershell
powershell -ExecutionPolicy Bypass -File C:\projects\GPTStoryworld\social-reasoning\scripts\fetch_sources.ps1
```

The refresh script is cache-safe and rewrites `source_manifest.csv`.
