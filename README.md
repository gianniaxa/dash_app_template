# Dash App Template

A reusable multi-page Dash application template. Clone it, describe your app, and let the agents build it for you.

## How to use this template

This template is designed around a two-step AI-assisted workflow using [opencode](https://opencode.ai):

### Step 1 — Define your app with the spec agent

```
/spec
```

The `spec` agent interviews you about your app — pages, data, components, auth, deployment — and writes a completed `SPEC.md`.

### Step 2 — Build the app with the build agent

```
/build
```

The `build` agent reads `SPEC.md` and implements the full app by extending and adapting this template.

---

## Prerequisites

### Required

| Tool | Version | Notes |
|---|---|---|
| [Docker Desktop](https://www.docker.com/products/docker-desktop/) | 4.x+ | Includes Docker Compose |
| [Git](https://git-scm.com/) | any | For cloning the repo |

### Windows users

Docker Desktop on Windows requires either **WSL 2** (recommended) or Hyper-V.

- **WSL 2 setup:** [docs.microsoft.com/en-us/windows/wsl/install](https://docs.microsoft.com/en-us/windows/wsl/install)
- In Docker Desktop → Settings → General → enable "Use the WSL 2 based engine"

### Optional (local development without Docker)

| Tool | Version | Notes |
|---|---|---|
| [Python](https://www.python.org/downloads/) | 3.13+ | |
| [uv](https://docs.astral.sh/uv/getting-started/installation/) | latest | Fast Python package manager |

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies and run locally
cd src
uv sync
uv run python app.py
```

---

## Getting Started

```bash
git clone https://github.com/gianniaxa/dash_app_template.git
cd dash_app_template
docker compose up --build
```

App runs at `http://localhost:8050`.

The `src/` directory is mounted as a volume, so code changes are picked up automatically without rebuilding the image.

---

## Structure

```
dash_app_template/
├── AGENTS.md                   # Project conventions (read by all agents)
├── SPEC.md                     # App specification (written by spec agent)
├── opencode.json               # opencode config
├── Dockerfile
├── docker-compose.yml
├── secrets/
│   └── env.secrets.example     # Copy to .env.secrets and fill in credentials
└── src/
    ├── app.py                  # App entry point, navbar, router, auth gate
    ├── pyproject.toml          # Dependencies (managed by uv)
    ├── auth/                   # Authentication module
    │   ├── __init__.py
    │   ├── saml_auth.py        # Flask Blueprint: /auth/login, /auth/saml/acs/, /auth/logout
    │   ├── saml_settings.py    # IdP URLs, role names, SAML config per stage
    │   └── session.py          # Session helpers: is_authenticated(), get_user(), get_roles()
    ├── data/
    │   ├── users.csv           # User dummy data
    │   └── sales.csv           # Sales dummy data
    ├── pages/
    │   ├── login.py            # /login — sign-in page
    │   ├── home.py             # /        — landing page with logo + component cards
    │   ├── form.py             # /form    — user entry form + live table
    │   ├── tables.py           # /tables  — AG Grid vs DataTable comparison
    │   ├── charts.py           # /charts  — bar, line, donut chart (tabbed)
    │   └── modal_demo.py       # /modal   — modal example
    ├── components/
    │   ├── form.py             # Reusable user form
    │   ├── modal.py            # Reusable Bootstrap modal
    │   ├── table_aggrid.py     # Reusable AG Grid table
    │   ├── table_datatable.py  # Reusable Dash DataTable
    │   └── charts.py           # Reusable Plotly chart components
    ├── assets/
    │   └── icons/
    │       └── logo.svg        # App logo (auto-served at /assets/icons/logo.svg)
    ├── utils/
    │   ├── data_loader.py      # load_csv() / save_csv()
    │   └── db.py               # get_engine() for PostgreSQL / MSSQL
    └── tests/
        ├── conftest.py         # pytest fixtures (mongomock)
        ├── test_data_loader.py # Unit tests
        └── test_mongo_integration.py  # Integration tests
```

---

## Pages

| Route | Description |
|---|---|
| `/` | Home — landing page with logo and component overview |
| `/form` | User entry form — saves to `users.csv`, live table below |
| `/tables` | Side-by-side comparison of AG Grid and Dash DataTable |
| `/charts` | Sales charts — bar, line, donut (3 tabs) |
| `/modal` | Modal example with open/close button |

---

## Components

### Form (`components/form.py`)

```python
from components.form import make_user_form

make_user_form(form_id="my-form")
# Field IDs: my-form-name, my-form-nationality, my-form-email,
#            my-form-birthday, my-form-submit, my-form-feedback
```

### Modal (`components/modal.py`)

```python
from components.modal import make_modal, register_modal_toggle

make_modal(
    modal_id="my-modal",
    title="My Modal",
    body=html.P("Content here."),
    footer=[
        dbc.Button("Save",   id="btn-save",            color="primary"),
        dbc.Button("Cancel", id="btn-cancel-my-modal", color="secondary"),
    ],
)

# Register toggle callback once at module level:
register_modal_toggle(
    modal_id="my-modal",
    open_trigger_id="btn-open-my-modal",
    close_trigger_id="btn-cancel-my-modal",
)
```

### AG Grid (`components/table_aggrid.py`)

```python
from components.table_aggrid import make_aggrid

make_aggrid(
    table_id="my-grid",
    data=df.to_dict("records"),   # or load_csv("users.csv")
    page_size=10,
)
```

Column definitions are auto-generated from data keys if `column_defs` is omitted.

### DataTable (`components/table_datatable.py`)

```python
from components.table_datatable import make_datatable

make_datatable(
    table_id="my-table",
    data=df.to_dict("records"),
    page_size=10,
)
```

### Charts (`components/charts.py`)

```python
from components.charts import make_bar_chart, make_line_chart, make_pie_chart

make_bar_chart(df, x="month", y="revenue", title="Revenue by Month")
make_line_chart(df, x="month", y="revenue", color="product")
make_pie_chart(df, names="category", values="revenue", hole=0.4)
```

---

## Authentication

Authentication is handled by the `src/auth/` module and is transparent to pages and components.

### Local (default — no login required)

When `SSO_ENABLED` is not set, the app auto-signs in as `local-dev` with all roles. No credentials needed.

```bash
docker compose up --build
# → opens directly on the app, no login prompt
```

### SSO / SAML (production)

Set `SSO_ENABLED=true` in your environment or `secrets/.env.secrets`:

```
SSO_ENABLED=true
STAGE=dev         # dev | preprod | prod
FLASK_SECRET_KEY=<random string>
SP_ENTITY_ID=my-app
```

Configure your IdP URLs and role group names in `src/auth/saml_settings.py`.

`python3-saml` must be added to `pyproject.toml` (commented out by default — requires `libxml2-dev` and `libxmlsec1-dev` system packages):

```bash
cd src
uv add python3-saml
```

### Using auth in pages

```python
from auth.session import is_authenticated, get_user, get_roles, has_role

user = get_user()           # "C123456" or "local-dev"
roles = get_roles()         # ["APP-ADMIN-DEV", ...]
has_role("APP-ADMIN-DEV")   # True / False
```

---



```python
from utils.data_loader import load_csv, save_csv

data = load_csv("users.csv")                        # list[dict] for Dash components
df   = load_csv("users.csv", as_dataframe=True)    # pd.DataFrame

save_csv("users.csv", {"name": "Anna", ...})        # append a row
```

---

## Database (`utils/db.py`)

```python
from utils.db import get_engine

engine = get_engine()  # reads DB_TYPE, DB_HOST, DB_NAME, DB_USER, DB_PASSWORD from env
```

Supports `postgresql` and `mssql`. Copy `secrets/env.secrets.example` to `secrets/.env.secrets` and fill in credentials for local use.

---

## Running tests

```bash
cd src
uv sync --group dev
uv run pytest tests/ -v
```

---

## Dependencies

Managed via `uv` and defined in `src/pyproject.toml`. To add a new package:

```bash
cd src
uv add <package>
```

Then rebuild:

```bash
docker compose up --build
```

| Package | Version | Purpose |
|---|---|---|
| `dash` | 4.3.0 | Core framework + DataTable |
| `dash-bootstrap-components` | 2.0.4 | Navbar, Modal, layout |
| `dash-ag-grid` | 35.3.0 | AG Grid table |
| `plotly` | 6.9.0 | Interactive charts |
| `pandas` | 3.0.5 | Data loading and aggregation |
| `sqlalchemy` | 2.0.51 | Database connections |
| `python-dotenv` | 1.2.3 | Load secrets from `.env.secrets` |
| `gunicorn` | 26.0.0 | Production WSGI server |

**Dev only:**

| Package | Version | Purpose |
|---|---|---|
| `pytest` | 9.1.1 | Test runner |
| `mongomock` | 4.3.0 | In-memory MongoDB for integration tests |
| `pymongo` | 4.17.0 | MongoDB client (used by mongomock) |
