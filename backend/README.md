# Selling Tours — Backend

FastAPI + SQLModel + Postgres (SQLite for local dev) backend for the tours platform.

## Quick start (SQLite, no Docker)

```bash
cd tours-app/backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json

The lifespan hook creates tables and seeds tours from `../contracts/tours_seed.json` if the table is empty.

## Quick start (Postgres via Docker)

From `tours-app/`:

```bash
docker compose up --build
```

This starts Postgres on `localhost:5432` and the backend on `localhost:8000`.

## Configuration

Environment variables (see `.env.example`):

| Variable | Default | Notes |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:///./tours.db` | Use `postgresql+psycopg://user:pass@host:5432/db` for Postgres |
| `SEED_PATH` | `../contracts/tours_seed.json` | Absolute path to seed JSON |
| `CORS_ORIGINS` | localhost:3000, 5173, 8001 | JSON list (pydantic-settings parses it) |

## API surface

All under `/api`:

- `GET /api/health` — liveness probe
- `GET /api/tours` — list with `country`, `price_min`, `price_max`, `date_from`, `date_to`, `sort`, `page`, `size`
- `GET /api/tours/{id}` — single tour
- `GET /api/countries` — distinct country list
- `POST /api/bookings` — create a booking (decrements `available_slots`)
- `GET /api/bookings?email=` — list bookings for an email

All 4xx responses follow the envelope:

```json
{ "error": { "code": "string", "message": "string", "details": {} } }
```

## Tests

```bash
make test       # or: python -m pytest -q
```

Tests use an isolated SQLite DB under `/tmp` and seed from `../contracts/tours_seed.json`.

## Project layout

```
backend/
  app/
    main.py          # FastAPI app, CORS, lifespan, error envelope
    core/
      config.py      # pydantic-settings
      db.py          # engine, init_db, get_session
    models/          # SQLModel ORM models
    schemas/         # request/response DTOs
    services/        # seeder, filter query builder
    api/routes/      # health, tours, countries, bookings
  alembic/           # migrations
  tests/
  Dockerfile
  Makefile
  requirements.txt
```

## Contract

Source of truth lives in `../contracts/openapi.yaml`. The FastAPI app must not drift from it.

The generated spec is available at runtime under `/openapi.json` for cross-checking.

## Make targets

| Target | What it does |
| --- | --- |
| `make install` | `pip install -r requirements.txt` |
| `make dev` | `uvicorn` with `--reload` on port 8000 |
| `make test` | run pytest |
| `make seed` | re-seed the configured database |
| `make migrate` | `alembic upgrade head` |
| `make migration name=add_x` | autogenerate a new revision |
