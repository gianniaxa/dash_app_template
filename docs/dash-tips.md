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

---

## Security

### SSL/TLS verification — always on

Never disable SSL certificate verification when making HTTP requests. This applies everywhere in the codebase.

```python
# requests — correct
import requests
response = requests.get("https://api.example.com/data")       # verify=True is the default
response = requests.get("https://api.example.com/data", verify=True)  # explicit

# wrong — never do this
response = requests.get("https://api.example.com/data", verify=False)  # ← disables verification

# httpx — correct
import httpx
response = httpx.get("https://api.example.com/data")          # verify=True is the default

# python3-saml metadata fetch — correct
OneLogin_Saml2_IdPMetadataParser.parse_remote(url, validate_cert=True)
```

If a self-signed or internal CA certificate is needed (e.g. corporate proxy), pass the CA bundle path instead of disabling verification:

```python
requests.get("https://internal.example.com", verify="/path/to/ca-bundle.pem")
```

In Docker, mount the CA certificate and set the environment variable so Python libraries (`requests`, `httpx`) know where to find it — they use their own embedded CA bundle (`certifi`) and do not read the system store automatically:

```yaml
# docker-compose.yml
environment:
  - REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-bundle.pem
  - SSL_CERT_FILE=/etc/ssl/certs/ca-bundle.pem
volumes:
  - ./certs/my-ca.pem:/etc/ssl/certs/ca-bundle.pem
```

The mount makes the file available inside the container. The env variables tell Python where it is — without them, the file is present but ignored.

**Alternative: inject into the system CA store via Dockerfile**

If you prefer not to use env variables, you can bake the certificate into the image and update the system store. Python libraries still won't pick it up automatically, but you can update `certifi`'s own bundle as a final step:

```dockerfile
COPY certs/my-ca.pem /usr/local/share/ca-certificates/my-ca.crt
RUN apt-get update && apt-get install -y ca-certificates \
    && update-ca-certificates \
    && cat /usr/local/share/ca-certificates/my-ca.crt \
       >> $(python -c "import certifi; print(certifi.where())")
```

This appends your CA to `certifi`'s bundle so `requests` and `httpx` trust it without any env variables at runtime. Trade-off: the certificate is baked into the image and requires a rebuild to update.
