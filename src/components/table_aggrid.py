"""
AG Grid table component template.

Usage example:
--------------
from components.table_aggrid import make_aggrid

layout = make_aggrid(
    table_id="my-table",
    data=df.to_dict("records"),
    column_defs=[
        {"field": "name", "headerName": "Name"},
        {"field": "age",  "headerName": "Age"},
    ],
)

# Or let column_defs be auto-generated from data keys:
layout = make_aggrid(table_id="my-table", data=df.to_dict("records"))
"""

import dash_ag_grid as dag


def make_aggrid(
    table_id: str,
    data: list[dict],
    column_defs: list[dict] | None = None,
    pagination: bool = True,
    page_size: int = 10,
    height: str = "400px",
) -> dag.AgGrid:
    """
    Creates a reusable AG Grid table.

    Parameters
    ----------
    table_id : str
        Unique component ID.
    data : list of dict
        Row data, typically from df.to_dict("records").
    column_defs : list of dict, optional
        AG Grid column definitions. If None, auto-generated from data keys.
        Example: [{"field": "name", "headerName": "Name", "sortable": True}]
    pagination : bool
        Enable pagination. Default True.
    page_size : int
        Rows per page when pagination is enabled. Default 10.
    height : str
        CSS height of the grid. Default "400px".
    """
    if column_defs is None and data:
        column_defs = [{"field": key, "headerName": key.replace("_", " ").title()} for key in data[0].keys()]

    return dag.AgGrid(
        id=table_id,
        rowData=data,
        columnDefs=column_defs or [],
        defaultColDef={
            "resizable": True,
            "sortable": True,
            "filter": True,
            "minWidth": 100,
        },
        dashGridOptions={
            "pagination": pagination,
            "paginationPageSize": page_size,
            "animateRows": True,
        },
        style={"height": height, "width": "100%"},
        className="ag-theme-alpine",
    )
