"""
Dash DataTable component template.

Usage example:
--------------
from components.table_datatable import make_datatable

layout = make_datatable(
    table_id="my-table",
    data=df.to_dict("records"),
    columns=[
        {"name": "Name", "id": "name"},
        {"name": "Age",  "id": "age"},
    ],
)

# Or let columns be auto-generated from data keys:
layout = make_datatable(table_id="my-table", data=df.to_dict("records"))
"""

from dash import dash_table


def make_datatable(
    table_id: str,
    data: list[dict],
    columns: list[dict] | None = None,
    pagination: bool = True,
    page_size: int = 10,
    sortable: bool = True,
    filterable: bool = True,
) -> dash_table.DataTable:
    """
    Creates a reusable Dash DataTable.

    Parameters
    ----------
    table_id : str
        Unique component ID.
    data : list of dict
        Row data, typically from df.to_dict("records").
    columns : list of dict, optional
        Column definitions. If None, auto-generated from data keys.
        Example: [{"name": "Name", "id": "name"}]
    pagination : bool
        Enable pagination. Default True.
    page_size : int
        Rows per page when pagination is enabled. Default 10.
    sortable : bool
        Allow column sorting. Default True.
    filterable : bool
        Show per-column filter inputs. Default True.
    """
    if columns is None and data:
        columns = [{"name": key.replace("_", " ").title(), "id": key} for key in data[0].keys()]

    return dash_table.DataTable(
        id=table_id,
        data=data,
        columns=columns or [],
        page_action="native" if pagination else "none",
        page_size=page_size,
        sort_action="native" if sortable else "none",
        filter_action="native" if filterable else "none",
        style_table={"overflowX": "auto"},
        style_header={
            "backgroundColor": "#343a40",
            "color": "white",
            "fontWeight": "bold",
        },
        style_cell={
            "padding": "8px 12px",
            "textAlign": "left",
            "fontFamily": "inherit",
        },
        style_data_conditional=[
            {
                "if": {"row_index": "odd"},
                "backgroundColor": "#f8f9fa",
            }
        ],
    )
