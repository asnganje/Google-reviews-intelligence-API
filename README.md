# Google Reviews Intelligence API

A SerpApi-style platform that returns structured, real-time data from Google Maps: businesses, place details, and reviews. See [project_plan.md](project_plan.md) for the full design.

## Quick start with Docker

```bash
cp .env.example .env
docker compose up --build
```

This starts the API (http://localhost:8000), a worker, PostgreSQL, and Redis.

- Swagger UI: http://localhost:8000/docs
- Health check: http://localhost:8000/api/v1/health

## Running locally without Docker

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # adjust DATABASE_URL / REDIS_URL if needed

uvicorn app.main:app --reload          # API
arq app.workers.main.WorkerSettings    # worker, in a second terminal
```

## Tests

```bash
pytest
```

## Project layout

```
app/
  api/        HTTP routes (versioned under api/v1)
  core/       configuration and logging
  database/   SQLAlchemy engine and session
  engines/    data-source engines (google_maps, ...)
  models/     SQLAlchemy models
  schemas/    Pydantic request/response schemas
  scraping/   HTTP client, browser pool, proxies, anti-bot handling
  services/   application logic used by the API and workers
  workers/    arq worker and background jobs
alembic/      database migrations
tests/
```
