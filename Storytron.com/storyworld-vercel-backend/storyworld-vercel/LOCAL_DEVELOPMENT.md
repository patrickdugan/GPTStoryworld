# Local Backend Quickstart

This backend can run locally on SQLite while preserving the same API contract used by the frontend:

- `GET /api/storyworlds`
- `POST /api/storyworlds`
- `GET/PATCH/DELETE /api/storyworlds/:id`
- `POST /api/storyworlds/:id/like?action=like|unlike`
- `GET /api/stats`

## Commands

```bash
npm install
npm run db:migrate
npm run db:seed
npm run dev
```

The API will be available at `http://127.0.0.1:3000/api`.

SQLite database file:

- `data/storyworld.local.db`

## Frontend Env

Set in `storyworld-frontend/storyworld-frontend/.env.local`:

```bash
VITE_API_BASE_URL=http://127.0.0.1:3000/api
```
