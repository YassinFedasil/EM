# EURO-STAT

Full-stack EuroMillions statistics app.

- **`euro-stat-BE`** — FastAPI + MongoDB + Google Drive (Python 3.12)
- **`euro-stat-FE`** — React 19 + TypeScript + Vite + Tailwind + ApexCharts

The backend extracts draw data from Google Drive, stores it in MongoDB and
exposes aggregated statistics/charts. The frontend renders those statistics
in dashboards and per-chart pages.

## Project layout

```
euro-stat-BE/
  app/
    core/         # configuration
    db/           # Mongo client + collection helpers
    models/       # Pydantic schemas
    repositories/ # data access
    services/     # business logic (aggregation, parsing, Drive, charts, ...)
    api/          # FastAPI router (all /api endpoints)
    main.py       # app factory (app.main:app)
  scripts/        # one-off maintenance scripts
  tests/          # pytest suite
euro-stat-FE/
  src/
    components/charts/  # generic BarChart + ChartPage + chart configs
    services/           # API layer (src/services/api.ts, src/services/*)
    config.ts           # API base URL
```

## Prerequisites

- Python 3.12+
- Node.js 20+
- MongoDB (local or via Docker)

## Backend (local)

```bash
cd euro-stat-BE
python -m venv .venv
.venv\Scripts\activate            # Windows
# source .venv/bin/activate       # Linux/macOS
pip install -r requirements.txt
py -m uvicorn app.main:app --reload
```

The API is served at http://localhost:8000 (interactive docs at `/docs`).
Importing the app does **not** connect to MongoDB or Google Drive; those
connections are lazy.

### Tests

```bash
pip install -r requirements-dev.txt
py -m pytest
```

### Google Drive

Drop a Google service-account file at `euro-stat-BE/credentials.json`
(override the path with `GOOGLE_CREDENTIALS_FILE`). The file is git-ignored.

## Frontend (local)

```bash
cd euro-stat-FE
npm install
npm run dev
```

The dev server runs at http://localhost:5173 and talks to the backend using
`VITE_API_URL` (defaults to `http://localhost:8000`). Copy `.env.example` to
`.env` to override it.

```bash
npm run build     # type-check + production build
npm run lint      # eslint
```

## Environment variables

See the root `.env.example` and `euro-stat-FE/.env.example`.

| Variable | Default | Used by |
| --- | --- | --- |
| `MONGO_URL` | `mongodb://localhost:27017` | backend |
| `MONGO_DB` | `euro_stat_db` | backend |
| `MONGO_COLLECTION_NUMBERS` | `numbers_full` | backend |
| `MONGO_COLLECTION_STARS` | `stars_full` | backend |
| `MONGO_COLLECTION_DRAW_DATA` | `draw_data` | backend |
| `DRIVE_DATA_FOLDER_ID` | *(built-in folder id)* | backend |
| `GOOGLE_CREDENTIALS_FILE` | `credentials.json` | backend |
| `CORS_ORIGINS` | localhost dev origins | backend |
| `VITE_API_URL` | `http://localhost:8000` | frontend |

> The `MONGO_URL` default has no credentials (local dev). Docker Compose
> provides a credentialed URL via `MONGO_URL`.

## Docker

```bash
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- MongoDB: localhost:27018 (root credentials default to `admin` / `admin123`)

Override defaults by creating a `.env` at the repository root (see
`.env.example`).

## Maintenance scripts

```bash
cd euro-stat-BE
py -m scripts.migrate_legacy_ids   # migrate legacy draw ids
```

## API overview

All routes are prefixed with `/api`:

- `GET /api/draw-data`, `DELETE /api/draw-data/{id}`, `POST /api/extract-drive`
- `GET /api/numbers/{date}`, `GET /api/numbers/{date}/filter-options`
- `GET /api/stars/{date}`
- `GET /api/charts/top`, `GET /api/charts/top-stars`
- `GET /api/chart-*` — chart aggregates (out, report, delay, ecarts,
  frequency, progression, recent-frequency, frequency-previous-period, ...)
