# BudgetBuddy

A small FastAPI + SQLAlchemy app for budgeting, with a clean layered architecture (routers → services → repository →
schema) and a pragmatic testing setup.

## Project structure

```
src/
  budgetbuddy/
    api/           # FastAPI app, routers, request/response schemas
    services/      # Business logic
    db/            # Engine/session, models, repository
    banking/       # External integrations
  common/          # Shared utilities (clients, logging, etc.)

tests/
  budgetbuddy/
    api/           # API (integration) tests using TestClient
    services/      # Service-level tests
    db/            # DB helpers (documented) and fixtures live in conftest.py
```

## Requirements

- Python 3.12+
- PostgreSQL (local or Docker)
- Optional: uv package manager (otherwise use pip)

## Installation

Using uv (recommended):

```bash
uv sync
```

Using pip:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
# dev tools
pip install ruff pytest mypy alembic testcontainers
```

## Configuration (Pydantic BaseSettings)

Configuration comes from environment variables with prefix `BB_`, or a `.env` file. See `src/budgetbuddy/db/config.py`
for available settings.

Key variables:

- `BB_DATABASE_USER` (default: postgres)
- `BB_DATABASE_PASSWORD` (default: postgres)
- `BB_DATABASE_HOST` (default: localhost)
- `BB_DATABASE_PORT` (default: 5432)
- `BB_DATABASE_NAME` (default: budgetbuddy)
- `BB_SQLALCHEMY_ECHO` (default: false)

Example `.env`:

```
BB_DATABASE_USER=postgres
BB_DATABASE_PASSWORD=postgres
BB_DATABASE_HOST=localhost
BB_DATABASE_PORT=5432
BB_DATABASE_NAME=budgetbuddy
BB_SQLALCHEMY_ECHO=false
```

The runtime SQLAlchemy URL is computed as `settings.database_url`.

## Running the API

```bash
uvicorn src.budgetbuddy.api.app:app --reload
```

Visit http://127.0.0.1:8000/ and http://127.0.0.1:8000/docs

## Database & migrations (Alembic)

Initialize and run migrations:

```bash
# Autogenerate a migration from model changes
alembic revision --autogenerate -m "init"
# Apply latest migrations
alembic upgrade head
```

Alembic uses your configured DB URL from `BB_…` environment variables. The default schema (`budgetbuddy`) is ensured
before migrations run.

## Testing

We use pytest with three markers:

- `unit`: fast tests without external services
- `integration`: tests that require a real DB (Postgres) or external services
- `smoke`: quick shallow checks that verify startup and core endpoints

Run tests:

```bash
# All tests
pytest

# Only smoke tests
pytest -m smoke

# Only unit tests
pytest -m unit

# Only integration tests
pytest -m integration
```

### Database for tests

By default, integration tests use `TEST_DATABASE_URL` or fallback to
`postgresql+psycopg2://postgres:password@localhost:5432/budgetbuddy_test`.

- Create a separate Postgres database for tests (recommended): `budgetbuddy_test`.
- Tests create the schema and tables automatically and wrap each test in a transaction that rolls back.

You can also run tests against an ephemeral PostgreSQL container:

```bash
export USE_TESTCONTAINERS=1
pytest -m integration
```

### Smoke tests – what are they?

A “smoke test” is a tiny, high-confidence check to see if the system basically works. In this project,
`tests/budgetbuddy/api/test_transaction.py::test_root_ok` is a smoke test: it ensures the app starts and the root
endpoint responds.

## Linting & type checking

Ruff:

```bash
ruff check .
ruff format .
```

Mypy:

```bash
mypy
```

## Tips

- Keep routers thin; put business logic in `services/` and low-level DB in `db/repository/`.
- Mark DB-touching tests as `@pytest.mark.integration` so you can run quick unit-only loops.
- Prefer environment configuration via `.env`/env vars over hard-coding credentials.

## Troubleshooting

- Tests skipped with a message about TEST_DATABASE_URL: ensure Postgres is running or set `USE_TESTCONTAINERS=1`.
- Migration autogenerate finds no changes: ensure models are imported in Alembic env (we import `Base` and dependent
  models via their package modules).
- Cannot import packages in Alembic: run from project root so `src/` is on the import path (env.py adds it
  automatically).
