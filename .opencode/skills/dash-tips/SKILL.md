---
name: dash-tips
description: Use when working on Dash layout, styling, callbacks, multi-page routing, AG Grid, or static assets. Contains known gotchas and patterns specific to this project such as equal-height cards, double container issues, chart height, callback placement, ctx.triggered_id, and no_update.
---

# Dash Tips & Tricks

Refer to `docs/dash-tips.md` for the full reference. Key patterns:

## Layout

- **Equal-height cards:** add `className="h-100"` to each `dbc.Card` in a row
- **No double containers:** `app.py` wraps `page_container` without a `dbc.Container` — each page manages its own
- **Chart height:** always set explicit `height` on Plotly figures (default ~450px looks short inside cards/tabs)

## Callbacks

- Use `@callback` (from `dash`), not `@app.callback`
- Define callbacks at **module level**, never inside `layout` or a layout function
- Use `prevent_initial_call=True` for button/form callbacks
- Use `dash.no_update` to skip outputs selectively
- Use `ctx.triggered_id` to distinguish between multiple inputs in one callback

## Multi-page

- Every page needs `dash.register_page(__name__, path="...", name="...")`
- Home page uses `path="/"`
- Static files go in `src/assets/` and are served at `/assets/` automatically

## AG Grid

- `column_defs` is auto-generated from data keys if omitted
- Refresh table data via `Output("grid-id", "rowData")` in a callback

For full examples and explanations, read `docs/dash-tips.md`.
