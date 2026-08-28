import dash
from dash import html
import dash_bootstrap_components as dbc

from auth.saml_settings import SSO_ENABLED

dash.register_page(__name__, path="/login", name="Login")

layout = dbc.Container(
    dbc.Row(
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.Img(
                            src="/assets/icons/logo.svg",
                            style={"width": "72px", "height": "72px"},
                            className="mb-4",
                        ),
                        html.H3("My App", className="mb-1"),
                        html.P(
                            "Sign in to continue.",
                            className="text-muted mb-4",
                        ),
                        dbc.Button(
                            "Sign in with SSO" if SSO_ENABLED else "Sign in (local dev)",
                            href="/auth/login",
                            color="primary",
                            size="lg",
                            className="w-100",
                        ),
                    ],
                    className="text-center p-4",
                ),
                className="shadow-sm",
            ),
            md=4,
        ),
        justify="center",
        align="center",
        style={"minHeight": "80vh"},
    ),
    fluid=True,
)
