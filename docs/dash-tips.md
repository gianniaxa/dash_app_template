# Dash Tips & Tricks

A growing collection of Dash-specific patterns, gotchas, and solutions discovered during development.

---

## Layout & Styling

### Equal-height cards in a row

By default Bootstrap cards in the same `dbc.Row` will have different heights depending on their content. Add `className="h-100"` to each card to make them all match the tallest one.

```python
dbc.Col(
    dbc.Card(
        dbc.CardBody([...]),
        className="h-100",   # ← makes all cards in the row equal height
    ),
    md=3,
)
```

---

### Avoid double containers

`app.py` wraps `dash.page_container` — do not wrap it again in a `dbc.Container`. Each page should manage its own container. A double container causes unexpected width constraints.

```python
# app.py — correct
app.layout = html.Div([
    navbar,
    dash.page_container,   # no Container here
])

# each page — correct
layout = dbc.Container([...], className="py-4")
```

---

### Chart height

`dcc.Graph` has a default height of ~450px. Inside `dbc.Card` or `dbc.Tab` the chart can appear shorter than expected due to extra padding. Always set an explicit height via the Plotly figure:

```python
fig = px.bar(df, x="month", y="revenue", height=500)
```

Or pass it through the factory function:

```python
make_bar_chart(df, x="month", y="revenue", height=500)
```

---

## Callbacks

### Use `@callback`, not `@app.callback`

Since Dash 2.x, `@callback` (imported from `dash`) works without the app instance and is the recommended approach — especially in multi-page apps where the app object is not always in scope.

```python
from dash import callback, Input, Output

@callback(
    Output("my-output", "children"),
    Input("my-input", "value"),
)
def update(value):
    return value
```

---

### Register callbacks at module level, not inside `layout`

Callbacks defined inside a function or inside `layout` can be registered multiple times or not at all depending on page navigation. Always define them at the top level of the page module.

```python
# correct — module level
layout = html.Div([...])

@callback(...)
def my_callback(...):
    ...

# wrong — inside a function
def layout():
    @callback(...)   # ← do not do this
    def my_callback(...):
        ...
    return html.Div([...])
```

---

### `prevent_initial_call=True`

Without this, Dash fires every callback once on page load with `None` as input values. Add it to callbacks that should only run on user interaction (e.g. button clicks, form submissions).

```python
@callback(
    Output("output", "children"),
    Input("btn", "n_clicks"),
    prevent_initial_call=True,
)
def on_click(n):
    ...
```

---

### `dash.no_update`

Return `dash.no_update` for outputs you do not want to change in a given callback execution. Useful when a callback has multiple outputs but only some should update.

```python
@callback(
    Output("table", "rowData"),
    Output("feedback", "children"),
    Input("btn-submit", "n_clicks"),
    prevent_initial_call=True,
)
def submit(n_clicks):
    if error:
        return dash.no_update, "Something went wrong"
    return new_data, "Saved!"
```

---

### `ctx.triggered_id`

Use `dash.ctx.triggered_id` to identify which input triggered a callback — useful when multiple inputs share one callback (e.g. open/close buttons for a modal).

```python
from dash import ctx

@callback(
    Output("modal", "is_open"),
    Input("btn-open", "n_clicks"),
    Input("btn-close", "n_clicks"),
    prevent_initial_call=True,
)
def toggle(n_open, n_close):
    if ctx.triggered_id == "btn-open":
        return True
    return False
```

---

## Multi-page Apps

### `dash.register_page`

Every page file must call `dash.register_page(__name__, ...)`. The `path` sets the URL route, `name` appears in the browser tab.

```python
dash.register_page(__name__, path="/my-page", name="My Page")
```

The home page uses `path="/"`.

---

### Static assets

Anything placed under `src/assets/` is automatically served by Dash at `/assets/`. No configuration needed.

```python
html.Img(src="/assets/icons/logo.svg")
```

Supported: CSS, JS, images, SVGs, fonts.

---

## AG Grid

### Auto-generate column definitions

If `column_defs` is omitted, `make_aggrid()` auto-generates them from the data keys. Column headers are title-cased with underscores replaced by spaces.

```python
make_aggrid(table_id="my-grid", data=load_csv("users.csv"))
# columns: Name, Nationality, Email, Birthday
```

---

### Update table data via callback

To refresh an AG Grid after a form submission, return the new `rowData` from a callback:

```python
Output("my-grid", "rowData")
...
return load_csv("users.csv")
```
