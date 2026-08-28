---
name: new-component
description: Use when creating a new reusable Dash component, adding a factory function to src/components/, or when asked to build a widget, table, chart, form, or modal that should be reusable across pages.
---

# Creating a New Reusable Component

## File location

All components live under `src/components/`. One file = one component type.

```
src/components/<name>.py
```

## Rules

- Export one or more **factory functions** named `make_<component>(...)`
- Each function returns a Dash component (or a `dbc` layout component)
- **No callbacks inside component files** — callbacks belong in the page that uses the component
- All component IDs must be derived from a parameter (e.g. `component_id: str`) to avoid ID collisions when the component is used on multiple pages

## Template

```python
"""
<Component name> component.

Usage:
------
from components.<name> import make_<name>

layout = make_<name>(component_id="my-<name>")
"""

from dash import html
import dash_bootstrap_components as dbc


def make_<name>(
    component_id: str,
    # ... other parameters
) -> dbc.<Component>:
    """
    Creates a reusable <description>.

    Parameters
    ----------
    component_id : str
        Prefix for all child IDs. E.g. "my-widget" produces
        IDs: "my-widget-input", "my-widget-output".
    """
    return dbc.Card(
        [
            # ... layout
        ],
        id=component_id,
    )
```

## Registering callbacks in the page

After placing the component in the layout, register its callbacks in the page file:

```python
from components.<name> import make_<name>
from dash import callback, Input, Output

layout = html.Div([
    make_<name>(component_id="my-widget"),
    html.Div(id="my-widget-output"),
])

@callback(
    Output("my-widget-output", "children"),
    Input("my-widget-input", "value"),
)
def handle_widget(value):
    ...
```

## Checklist

- [ ] File at `src/components/<name>.py`
- [ ] Factory function named `make_<name>(...)`
- [ ] All IDs derived from `component_id` parameter
- [ ] No `@callback` decorators inside the component file
- [ ] Docstring with usage example at the top of the file
