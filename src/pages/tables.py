import dash
from dash import html
import dash_bootstrap_components as dbc

from components.table_aggrid import make_aggrid
from components.table_datatable import make_datatable
from utils.data_loader import load_csv

dash.register_page(__name__, path="/tables", name="Tables")

data = load_csv("users.csv")

layout = dbc.Container(
    [
        html.H1("Tables", className="mb-1"),
        html.P(
            "Side-by-side comparison of Dash AG Grid and Dash DataTable. "
            "Both tables show the same data and support sorting, filtering, and pagination.",
            className="text-muted mb-5",
        ),

        # --- AG Grid ---
        html.H4("Dash AG Grid", className="mb-1"),
        html.P(
            [
                "External library ",
                html.Code("dash-ag-grid"),
                ". Better performance, richer feature set (grouping, pivoting, cell renderers). "
                "Recommended for complex or large datasets.",
            ],
            className="text-muted mb-3",
        ),
        make_aggrid(
            table_id="table-aggrid-demo",
            data=data,
            page_size=5,
            height="320px",
        ),

        html.Hr(className="my-5"),

        # --- DataTable ---
        html.H4("Dash DataTable", className="mb-1"),
        html.P(
            [
                "Built into ",
                html.Code("dash"),
                ", no extra dependency. Simpler to set up, sufficient for most standard use cases.",
            ],
            className="text-muted mb-3",
        ),
        make_datatable(
            table_id="table-datatable-demo",
            data=data,
            page_size=5,
        ),
    ],
    className="py-4",
)
