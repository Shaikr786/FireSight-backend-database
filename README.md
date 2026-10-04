# FireSight Sports — Backend + Database

This package is ready to drop into the existing repo structure:

```
FireSight-Sports/
├── backend/api/          ← copy contents of app/ here (or replace)
├── database/             ← copy schema.sql + seed.sql
├── docker-compose.yml    ← use the one from this package
└── ...
```

## What you get

- Complete PostgreSQL schema (`database/schema.sql`)
- Realistic seed data for one 12-minute football match (`database/seed.sql`)
- FastAPI app with:
  - Context service (the most important endpoint)
  - Events, highlights, players, stats
  - AI ask / recap placeholders (AI teammate can enhance)
  - Highlight search
  - Next big moment

## Quick start (local)

```bash
# 1. Start Postgres + load schema & seed
docker compose up -d db

# 2. Create a virtualenv and install deps
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Run the API
export DATABASE_URL=postgresql+psycopg2://firesight:firesight@localhost:5432/firesight
uvicorn app.main:app --reload --port 8080
```

Or run everything with Docker:

```bash
docker compose up --build
```

API docs: http://localhost:8080/docs  
Health:   http://localhost:8080/health

## Key endpoints for the team

| Method | Path | Used by |
|--------|------|---------|
| GET | `/api/v1/matches/{id}/context?timestamp_seconds=412` | Frontend + AI |
| GET | `/api/v1/matches/{id}/events` | Frontend |
| GET | `/api/v1/matches/{id}/highlights` | Frontend |
| GET | `/api/v1/matches/{id}/players` | Frontend |
| GET | `/api/v1/matches/{id}/next-big-moment` | Frontend |
| POST | `/api/v1/matches/{id}/ai/ask` | AI teammate |
| POST | `/api/v1/matches/{id}/ai/recap` | AI teammate |
| POST | `/api/v1/matches/{id}/highlights/search` | Frontend / AI |

## How the frontend seeks to a goal

1. User asks “Show me the last goal”
2. Frontend or AI calls `/context` or `/ai/ask` or `/events?event_type=goal`
3. Backend returns `timestamp_seconds` (e.g. 455)
4. Frontend does `video.seek(455)`

No computer vision required.

## Ownership

You (Backend + Database) own this package.  
Frontend and AI teammates only call the HTTP endpoints.
