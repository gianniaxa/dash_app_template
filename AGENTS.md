# Dash App Template — Project Context

## Purpose

This project is a reusable template for building Dash applications. The intended workflow is:

1. **Specify** — Run the `spec` agent (or `/spec`) to define your app through a guided interview. The agent writes a completed `SPEC.md`.
2. **Build** — Run the `build` agent (or `/build`) to implement the app based on `SPEC.md` and the conventions in this file.

```
/spec    →   SPEC.md is written
/build   →   App is implemented from SPEC.md
```

`SPEC.md` is the contract between the two agents. The spec agent must produce a complete spec. The build agent must implement exactly what is in the spec — nothing more, nothing less.

---

## What this project is

A minimal multi-page Dash application serving as a template for new Dash projects.
It demonstrates reusable component patterns, data loading, charts, forms, and testing.

## Stack

- **Python 3.13** with **uv** for dependency management
- **Dash 4.x** with `use_pages=True` for multi-page routing
- **dash-bootstrap-components** for layout and UI
- **Plotly** for charts
- **pandas** for data loading and aggregation
- **SQLAlchemy** for database connections (PostgreSQL / MSSQL)
- **pytest** + **mongomock** for testing
- **Gunicorn** as WSGI server
- **Docker + Docker Compose** for containerized runs

## Project structure

```
dash_app_template/
├── AGENTS.md
├── Dockerfile
├── docker-compose.yml
├── .gitignore
├── secrets/                        # Never committed — credentials here
│   └── env.secrets.example         # Copy to .env.secrets and fill in
└── src/
    ├── app.py                      # Dash app init, navbar, layout
    ├── pyproject.toml              # Dependencies (uv)
    ├── data/                       # CSV dummy data files
    │   ├── users.csv
    │   └── sales.csv
    ├── pages/                      # One file per route (Dash use_pages)
    │   ├── form.py                 # /form
    │   ├── tables.py               # /tables
    │   ├── charts.py               # /charts
    │   └── modal_demo.py           # /modal
    ├── components/                 # Reusable UI component factories
    │   ├── form.py
    │   ├── modal.py
    │   ├── table_aggrid.py
    │   ├── table_datatable.py
    │   └── charts.py
    ├── utils/
    │   ├── data_loader.py          # load_csv() / save_csv()
    │   └── db.py                   # get_engine() for PostgreSQL / MSSQL
    └── tests/
        ├── conftest.py             # pytest fixtures (mongomock)
        ├── test_data_loader.py     # Unit tests
        └── test_mongo_integration.py  # Integration tests with mongomock
```

## Key conventions

### Pages
- One file per page under `src/pages/`
- Always call `dash.register_page(__name__, path="/...", name="...")` at the top
- Register callbacks at module level (not inside layout) using `@callback`
- Add the route to the navbar in `src/app.py`

### Components
- Component files export factory functions: `make_<component>(...)` returning a Dash component
- All IDs are derived from a `component_id` parameter to avoid conflicts across pages
- No callbacks inside component files — callbacks belong in pages

### Data
- All CSV files live in `src/data/`
- Always use `load_csv()` / `save_csv()` from `utils/data_loader.py` — never read files directly in pages
- Database connections go through `utils/db.py` — never construct connection strings inline

### Secrets
- Local credentials go in `secrets/.env.secrets` (gitignored)
- `utils/db.py` loads this file automatically when present
- In production, inject env vars directly — the secrets file is not needed

### README.md

**After every change that affects the project, update `README.md` accordingly.**

This includes but is not limited to:
- Adding or removing a page → update the Pages table
- Adding or removing a component → update the Components section
- Adding a new package → update the Packages table
- Changing the project structure → update the Structure tree
- Changing how to run the app or tests → update Getting Started / Running tests

The README is the single source of truth for anyone new to the project. Keep it in sync.

## Running the app

### With Docker (recommended)
```bash
docker compose up --build
# App at http://localhost:8050
```

### Locally with uv
```bash
cd src
uv sync --group dev
uv run python app.py
# App at http://localhost:8050
```

## Running tests
```bash
cd src
uv run pytest tests/ -v
```
