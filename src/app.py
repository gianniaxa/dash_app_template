import dash
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc

app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)

server = app.server

navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.NavbarBrand("My App", href="/"),
            dbc.Nav(
                [
                    dbc.NavItem(dbc.NavLink("Form",   href="/form")),
                    dbc.NavItem(dbc.NavLink("Tables", href="/tables")),
                    dbc.NavItem(dbc.NavLink("Modal",  href="/modal")),
                ],
                navbar=True,
            ),
        ]
    ),
    color="dark",
    dark=True,
    className="mb-4",
)

app.layout = html.Div(
    [
        dcc.Location(id="url"),
        navbar,
        dbc.Container(dash.page_container),
    ]
)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
