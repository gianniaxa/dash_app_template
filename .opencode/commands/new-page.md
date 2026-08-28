---
description: Create a new Dash page with the correct structure, register it in the navbar, and follow project conventions.
---

Create a new Dash page for this project with the following specification:

$ARGUMENTS

Follow the `new-page` skill conventions:
- File goes in `src/pages/<name>.py`
- Use `dash.register_page(__name__, path="/<route>", name="<Display Name>")`
- Use `@callback` (not `@app.callback`) at module level
- Load data via `utils/data_loader.load_csv()` if needed
- Add a `dbc.NavItem(dbc.NavLink(...))` entry in `src/app.py`
