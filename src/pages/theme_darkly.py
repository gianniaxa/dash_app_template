import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/theme/darkly", name="Theme: Darkly")

# Darkly — dark Bootstrap theme (Bootswatch)
DARKLY_CSS = "https://cdn.jsdelivr.net/npm/bootswatch@5.3.3/dist/darkly/bootstrap.min.css"

_demo_cards = dbc.Row(
    [
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H5("Total Positions", className="card-title"),
                    html.H2("142", className="text-primary"),
                    html.P("Job Level ≥ 8", className="text-muted small mb-0"),
                ]),
                className="h-100",
            ),
            md=3,
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H5("Candidates Assigned", className="card-title"),
                    html.H2("318", className="text-success"),
                    html.P("Across all positions", className="text-muted small mb-0"),
                ]),
                className="h-100",
            ),
            md=3,
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H5("Ready Now", className="card-title"),
                    html.H2("74", className="text-warning"),
                    html.P("Succession ready", className="text-muted small mb-0"),
                ]),
                className="h-100",
            ),
            md=3,
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H5("Interests Expressed", className="card-title"),
                    html.H2("89", className="text-info"),
                    html.P("By employees", className="text-muted small mb-0"),
                ]),
                className="h-100",
            ),
            md=3,
        ),
    ],
    className="g-3 mb-4",
)

_demo_table = dbc.Table(
    [
        html.Thead(html.Tr([
            html.Th("Position"),
            html.Th("Department"),
            html.Th("Level"),
            html.Th("Candidates"),
            html.Th("Status"),
        ])),
        html.Tbody([
            html.Tr([html.Td("Head of Engineering"), html.Td("Technology"), html.Td("10"), html.Td("3"),
                     html.Td(dbc.Badge("Ready Now", color="success"))]),
            html.Tr([html.Td("VP Finance"), html.Td("Finance"), html.Td("12"), html.Td("2"),
                     html.Td(dbc.Badge("1-2 Years", color="warning", text_color="dark"))]),
            html.Tr([html.Td("Director HR"), html.Td("HR"), html.Td("9"), html.Td("4"),
                     html.Td(dbc.Badge("3+ Years", color="secondary"))]),
            html.Tr([html.Td("Head of Sales"), html.Td("Sales"), html.Td("8"), html.Td("1"),
                     html.Td(dbc.Badge("Ready Now", color="success"))]),
        ]),
    ],
    bordered=True,
    hover=True,
    responsive=True,
    striped=True,
    className="mb-4",
)

_demo_form = dbc.Card(
    dbc.CardBody([
        html.H5("Express Interest", className="card-title mb-3"),
        dbc.Row([
            dbc.Col([
                dbc.Label("Position"),
                dbc.Select(
                    options=[
                        {"label": "Head of Engineering", "value": "1"},
                        {"label": "VP Finance", "value": "2"},
                        {"label": "Director HR", "value": "3"},
                    ],
                    placeholder="Select a position...",
                ),
            ], md=6),
            dbc.Col([
                dbc.Label("Your Motivation (optional)"),
                dbc.Textarea(placeholder="Why are you interested?", rows=2),
            ], md=6),
        ], className="mb-3"),
        dbc.Button("Submit Interest", color="primary"),
        dbc.Button("Cancel", color="secondary", outline=True, className="ms-2"),
    ]),
    className="mb-4",
)

layout = html.Div([
    html.Link(rel="stylesheet", href=DARKLY_CSS),

    dbc.Container([
        dbc.Row(dbc.Col([
            html.H1("Darkly Theme", className="mb-1"),
            html.P(
                "Bootswatch Darkly — dark, modern. Good for dashboards and data-heavy tools.",
                className="text-muted lead mb-4",
            ),
            html.Hr(className="mb-4"),
        ])),
        _demo_cards,
        _demo_table,
        _demo_form,
        dbc.Alert(
            "This page loads its own Bootstrap theme via html.Link. "
            "The rest of the app is unaffected.",
            color="info",
        ),
    ], className="py-4"),
])
