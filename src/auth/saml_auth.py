"""
Flask Blueprint for authentication.

Two modes controlled by the SSO_ENABLED environment variable:

  SSO_ENABLED=true   → real SAML flow via python3-saml
  (not set)          → local dev bypass, session written directly

Routes
------
GET  /auth/login     → start SSO flow (or dev bypass)
POST /auth/saml/acs/ → SAML Assertion Consumer Service (SSO only)
GET  /auth/logout    → clear session, redirect to the signed-out page
"""

import os
from urllib.parse import urlparse

from flask import Blueprint, redirect, request, session, abort

from auth.session import _write_session
from auth.saml_settings import (
    SSO_ENABLED,
    STAGE,
    SSO_HOSTS,
    ACS_URLS,
    LOCAL_DEV_USER_ID,
    LOCAL_DEV_ROLES,
    build_saml_settings,
)

auth_routes = Blueprint("auth", __name__, url_prefix="/auth")

# ---------------------------------------------------------------------------
# SSO mode — load SAML settings once at startup
# ---------------------------------------------------------------------------
if SSO_ENABLED:
    _saml_settings = build_saml_settings()

    def _init_saml_auth(req):
        from onelogin.saml2.auth import OneLogin_Saml2_Auth
        return OneLogin_Saml2_Auth(req, _saml_settings)

    def _prepare_request(flask_request):
        """Adapt Flask request for python3-saml (handles reverse proxy)."""
        return {
            "https": "on" if flask_request.scheme == "https" else "off",
            "http_host": flask_request.headers.get("X-Host", flask_request.host),
            "server_port": 443,
            "script_name": flask_request.path,
            "get_data": flask_request.args.copy(),
            "post_data": flask_request.form.copy(),
        }

    @auth_routes.route("/login", methods=["GET"])
    def login():
        auth = _init_saml_auth(_prepare_request(request))
        login_url = auth.login()
        # Remember the request ID so acs() can verify InResponseTo
        session["AuthNRequestID"] = auth.get_last_request_id()
        # Validate redirect host to prevent open redirect
        if urlparse(login_url).netloc != SSO_HOSTS[STAGE]:
            abort(400)
        return redirect(login_url)

    @auth_routes.route("/saml/acs/", methods=["POST"])
    def acs():
        auth = _init_saml_auth(_prepare_request(request))
        request_id = session.pop("AuthNRequestID", None)
        auth.process_response(request_id=request_id)

        if auth.get_errors():
            abort(401)

        attributes = auth.get_attributes()
        user_id = auth.get_nameid()
        roles = attributes.get("memberof", [])

        _write_session(user_id=user_id, roles=roles)
        return redirect("/")

# ---------------------------------------------------------------------------
# Local dev bypass — skips SSO entirely
# ---------------------------------------------------------------------------
else:
    @auth_routes.route("/login", methods=["GET"])
    def login():
        _write_session(user_id=LOCAL_DEV_USER_ID, roles=LOCAL_DEV_ROLES)
        return redirect("/")


# ---------------------------------------------------------------------------
# Shared: logout (both modes)
# ---------------------------------------------------------------------------
@auth_routes.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect("/logout")
