import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

from components.charts import make_bar_chart, make_line_chart, make_pie_chart
from utils.data_loader import load_csv

dash.register_page(__name__, path="/charts", name="Charts")

df = load_csv("sales.csv", as_dataframe=True)

# --- Aggregations ---

# Tab 1: Bar — total revenue per month
df_monthly = df.groupby("month", as_index=False)["revenue"].sum()

# Tab 2: Line — monthly revenue per product
df_by_product = df.sort_values("month")

# Tab 3: Pie — total revenue share by category
df_by_category = df.groupby("category", as_index=False)["revenue"].sum()

# --- Layout ---

layout = dbc.Container(
    [
        html.H1("Charts", className="mb-1"),
        html.P(
            "Sales data visualized with Plotly. Each tab shows a different chart type.",
            className="text-muted mb-4",
        ),
        dbc.Tabs(
            [
                dbc.Tab(
                    dbc.Card(
                        dbc.CardBody(
                            make_bar_chart(
                                df=df_monthly,
                                x="month",
                                y="revenue",
                                title="Total Revenue per Month",
                                graph_id="chart-bar",
                            )
                        ),
                        className="mt-3",
                    ),
                    label="Bar Chart",
                    tab_id="tab-bar",
                ),
                dbc.Tab(
                    dbc.Card(
                        dbc.CardBody(
                            make_line_chart(
                                df=df_by_product,
                                x="month",
                                y="revenue",
                                color="product",
                                title="Monthly Revenue by Product",
                                graph_id="chart-line",
                            )
                        ),
                        className="mt-3",
                    ),
                    label="Line Chart",
                    tab_id="tab-line",
                ),
                dbc.Tab(
                    dbc.Card(
                        dbc.CardBody(
                            make_pie_chart(
                                df=df_by_category,
                                names="category",
                                values="revenue",
                                title="Revenue Share by Category",
                                graph_id="chart-pie",
                                hole=0.4,
                            )
                        ),
                        className="mt-3",
                    ),
                    label="Donut Chart",
                    tab_id="tab-pie",
                ),
            ],
            active_tab="tab-bar",
        ),
    ],
    className="py-4",
)
