# Dash App Template

A minimal multi-page Dash application with reusable component templates, ready to run via Docker Compose.

## Structure

```
dash_app_template/
├── Dockerfile
├── docker-compose.yml
└── src/
    ├── app.py               # App entry point, navbar, router
    ├── pyproject.toml       # Dependencies (managed by uv)
    ├── pages/
    │   ├── page1.py         # /page-1
    │   ├── page2.py         # /page-2
    │   └── tables.py        # /tables — AG Grid vs DataTable comparison
    └── components/
        ├── modal.py         # Reusable Bootstrap modal
        ├── table_aggrid.py  # Reusable AG Grid table
        └── table_datatable.py # Reusable Dash DataTable
```

## Getting Started

**Requirements:** Docker + Docker Compose

```bash
docker compose up --build
```

App runs at `http://localhost:8050`.

The `src/` directory is mounted as a volume, so code changes are picked up automatically without rebuilding the image.

## Dependencies

Managed via `uv` and defined in `src/pyproject.toml`. To add a new package locally:

```bash
cd src
uv add <package>
```

Then rebuild the Docker image to apply the change:

```bash
docker compose up --build
```

## Pages

| Route | Description |
|---|---|
| `/page-1` | Blank starter page |
| `/page-2` | Blank starter page |
| `/tables` | Side-by-side comparison of AG Grid and DataTable |

## Components

### Modal (`components/modal.py`)

```python
from components.modal import make_modal, register_modal_toggle

# In layout:
make_modal(
    modal_id="my-modal",
    title="My Modal",
    body=html.P("Content here."),
    footer=[
        dbc.Button("Save",   id="btn-save",          color="primary"),
        dbc.Button("Cancel", id="btn-cancel-my-modal", color="secondary"),
    ],
)

# Register toggle callback once, outside layout:
register_modal_toggle(
    app=app,
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
    data=df.to_dict("records"),
    column_defs=[
        {"field": "name", "headerName": "Name"},
        {"field": "age",  "headerName": "Age"},
    ],
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

## Packages

| Package | Version | Purpose |
|---|---|---|
| `dash` | 4.3.0 | Core framework + DataTable |
| `dash-bootstrap-components` | 2.0.4 | Navbar, Modal, layout |
| `dash-ag-grid` | 35.3.0 | AG Grid table |
| `gunicorn` | 26.0.0 | Production WSGI server |
