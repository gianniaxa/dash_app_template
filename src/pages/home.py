import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/", name="Home")

layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                [
                    html.Img(
                        src="/assets/icons/logo.svg",
                        style={"width": "100px", "height": "100px"},
                        className="mb-4",
                    ),
                    html.H1("Dash App Template", className="mb-2"),
                    html.P(
                        "A reusable multi-page Dash application template. "
                        "Use the navigation above to explore the included component examples.",
                        className="text-muted lead mb-5",
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Card(
                                    dbc.CardBody([
                                        html.H5("Form", className="card-title"),
                                        html.P("User entry form with validation and live table update.", className="card-text text-muted"),
                                        dbc.Button("Go", href="/form", color="primary", size="sm"),
                                    ]),
                                    className="h-100",
                                ),
                                md=3,
                            ),
                            dbc.Col(
                                dbc.Card(
                                    dbc.CardBody([
                                        html.H5("Tables", className="card-title"),
                                        html.P("AG Grid vs Dash DataTable side by side.", className="card-text text-muted"),
                                        dbc.Button("Go", href="/tables", color="primary", size="sm"),
                                    ]),
                                    className="h-100",
                                ),
                                md=3,
                            ),
                            dbc.Col(
                                dbc.Card(
                                    dbc.CardBody([
                                        html.H5("Charts", className="card-title"),
                                        html.P("Bar, line, and donut charts with Plotly.", className="card-text text-muted"),
                                        dbc.Button("Go", href="/charts", color="primary", size="sm"),
                                    ]),
                                    className="h-100",
                                ),
                                md=3,
                            ),
                            dbc.Col(
                                dbc.Card(
                                    dbc.CardBody([
                                        html.H5("Modal", className="card-title"),
                                        html.P("Bootstrap modal with open/close callback.", className="card-text text-muted"),
                                        dbc.Button("Go", href="/modal", color="primary", size="sm"),
                                    ]),
                                    className="h-100",
                                ),
                                md=3,
                            ),
                        ],
                        className="g-3",
                    ),
                ],
                className="text-center",
            )
        )
    ],
    className="py-5",
)
