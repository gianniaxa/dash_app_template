---
name: new-page
description: Use when creating a new Dash page, adding a route, or registering a new page file under src/pages/. Covers the correct file structure, dash.register_page convention, callback placement, and navbar registration.
---

# Creating a New Dash Page

## File location

All pages live under `src/pages/`. One file = one route.

```
src/pages/<name>.py
```

## Minimal page template

```python
import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/<route>", name="<Display Name>")

layout = dbc.Container(
    [
        html.H1("<Page Title>", className="mb-1"),
        html.P("Description.", className="text-muted mb-4"),
        # ... content
    ],
    className="py-4",
)
```

## Adding callbacks

Callbacks belong in the page file, **at module level** (not inside `layout`), using `@callback`:

```python
from dash import callback, Input, Output

@callback(
    Output("my-output", "children"),
    Input("my-input", "value"),
)
def update(value):
    return f"You entered: {value}"
```

Never use `@app.callback` — use `@callback` (imported from `dash`).

## Loading data

Always use `utils/data_loader.py`:

```python
from utils.data_loader import load_csv

data = load_csv("users.csv")           # list[dict] for tables
df   = load_csv("users.csv", as_dataframe=True)  # pd.DataFrame for charts
```

## Registering in the navbar

After creating the page file, add a NavLink in `src/app.py`:

```python
dbc.NavItem(dbc.NavLink("<Display Name>", href="/<route>")),
```

## Checklist

- [ ] File created at `src/pages/<name>.py`
- [ ] `dash.register_page(__name__, path="...", name="...")` at top
- [ ] `layout` defined
- [ ] Callbacks use `@callback`, placed at module level
- [ ] NavLink added in `src/app.py`
