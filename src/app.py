import os
from datetime import timedelta

import dash
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc
from flask import redirect, request, session

from auth import auth_routes, is_authenticated
from auth.saml_settings import SSO_ENABLED

# ---------------------------------------------------------------------------
# Dash app
# ---------------------------------------------------------------------------
app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)

server = app.server

# ---------------------------------------------------------------------------
# Flask / session config
# ---------------------------------------------------------------------------
server.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-in-prod")
server.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=60)
server.config["SESSION_COOKIE_HTTPONLY"] = True
if SSO_ENABLED:
    # The IdP returns the assertion via a cross-site POST to the ACS route.
    # "Lax" would withhold the cookie there, losing the AuthNRequestID that
    # acs() needs for the InResponseTo check. "None" requires Secure.
    server.config["SESSION_COOKIE_SAMESITE"] = "None"
    server.config["SESSION_COOKIE_SECURE"] = True
else:
    server.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    if os.environ.get("STAGE") in ("preprod", "prod"):
        server.config["SESSION_COOKIE_SECURE"] = True

# ---------------------------------------------------------------------------
# Auth blueprint
# ---------------------------------------------------------------------------
server.register_blueprint(auth_routes)

# ---------------------------------------------------------------------------
# Auth gate — redirect unauthenticated requests to /login
# Exempt: /login page, /auth/* routes, and Dash's internal /_dash-* endpoints
# ---------------------------------------------------------------------------
EXEMPT_PREFIXES = ("/login", "/logout", "/auth/", "/_dash-", "/assets/")

@server.before_request
def require_login():
    if any(request.path.startswith(p) for p in EXEMPT_PREFIXES):
        return
    if not is_authenticated():
        return redirect("/login")

# ---------------------------------------------------------------------------
# Navbar
# ---------------------------------------------------------------------------
navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.NavbarBrand(
                [
                    html.Img(
                        src="/assets/icons/logo.svg",
                        height="30px",
                        className="me-2",
                    ),
                    "My App",
                ],
                href="/",
            ),
            dbc.Nav(
                [
                    dbc.NavItem(dbc.NavLink("Home",   href="/")),
                    dbc.NavItem(dbc.NavLink("Form",   href="/form")),
                    dbc.NavItem(dbc.NavLink("Tables", href="/tables")),
                    dbc.NavItem(dbc.NavLink("Charts", href="/charts")),
                    dbc.NavItem(dbc.NavLink("Modal",  href="/modal")),
                    dbc.NavItem(
                        dbc.NavLink(
                            "Logout",
                            href="/auth/logout",
                            # Flask route, not a Dash page — bypass client-side routing
                            external_link=True,
                            className="text-danger",
                        )
                    ),
                ],
                navbar=True,
            ),
        ]
    ),
    color="dark",
    dark=True,
    className="mb-4",
)

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
app.layout = html.Div(
    [
        dcc.Location(id="url"),
        navbar,
        dash.page_container,
    ]
)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
