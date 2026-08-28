"""
SAML SSO configuration.

All environment-specific URLs and role group names live here.
Change only this file when adapting to a new environment or IdP.

Environment variables
---------------------
STAGE           : "dev" | "preprod" | "prod" (default: "dev")
SSO_ENABLED     : "true" to activate real SAML flow (default: disabled = local bypass)
FLASK_SECRET_KEY: Required. Signs Flask session cookies.
"""

import os

STAGE = os.environ.get("STAGE", "dev")
SSO_ENABLED = os.environ.get("SSO_ENABLED", "").lower() == "true"

# ---------------------------------------------------------------------------
# IdP metadata URLs — replace with your IdP's federation metadata endpoint
# ---------------------------------------------------------------------------
IDP_METADATA_URLS: dict[str, str] = {
    "dev":     "https://idp.dev.example.com/federation_metadata",
    "preprod": "https://idp.acc.example.com/federation_metadata",
    "prod":    "https://idp.example.com/federation_metadata",
}

# ---------------------------------------------------------------------------
# Assertion Consumer Service (ACS) return URLs
# Must be registered with your IdP as allowed redirect targets.
# The path must match the route in saml_auth.py, including the blueprint's
# "/auth" url_prefix — the IdP posts the assertion straight to this URL.
# ---------------------------------------------------------------------------
ACS_PATH = "/auth/saml/acs/"

APP_HOSTS: dict[str, str] = {
    "dev":     "app.dev.example.com",
    "preprod": "app.acc.example.com",
    "prod":    "app.example.com",
}

ACS_URLS: dict[str, str] = {
    stage: f"https://{host}{ACS_PATH}" for stage, host in APP_HOSTS.items()
}

# ---------------------------------------------------------------------------
# SSO host — validated against the IdP redirect to prevent open redirect
# ---------------------------------------------------------------------------
SSO_HOSTS: dict[str, str] = {
    "dev":     "idp.dev.example.com",
    "preprod": "idp.acc.example.com",
    "prod":    "idp.example.com",
}

# ---------------------------------------------------------------------------
# SAML SP entity ID — must match what is registered with the IdP
# ---------------------------------------------------------------------------
SP_ENTITY_ID = os.environ.get("SP_ENTITY_ID", "my-app")

# ---------------------------------------------------------------------------
# Role group names — returned by the IdP in the "memberof" SAML attribute.
# Add as many roles as your app needs.
# ---------------------------------------------------------------------------
ROLES: dict[str, dict[str, str]] = {
    "admin": {
        "dev":     "APP-ADMIN-DEV",
        "preprod": "APP-ADMIN-PPD",
        "prod":    "APP-ADMIN-PRD",
    },
    "user": {
        "dev":     "APP-USER-DEV",
        "preprod": "APP-USER-PPD",
        "prod":    "APP-USER-PRD",
    },
}

# ---------------------------------------------------------------------------
# Local dev bypass user — used when SSO_ENABLED is not set
# ---------------------------------------------------------------------------
LOCAL_DEV_USER_ID = "local-dev"
LOCAL_DEV_ROLES = [ROLES["admin"][STAGE], ROLES["user"][STAGE]]


def get_role(name: str) -> str:
    """Return the stage-specific group name for a role. E.g. get_role('admin')"""
    return ROLES[name][STAGE]


def build_saml_settings() -> dict:
    """
    Build the settings dict for python3-saml by fetching IdP metadata.
    Called once at startup when SSO_ENABLED is true.
    """
    from onelogin.saml2.idp_metadata_parser import OneLogin_Saml2_IdPMetadataParser

    metadata_url = IDP_METADATA_URLS[STAGE]
    data = OneLogin_Saml2_IdPMetadataParser.parse_remote(
        metadata_url, validate_cert=True
    )
    data["strict"] = True
    data["debug"] = STAGE == "dev"
    data["sp"]["entityId"] = SP_ENTITY_ID
    data["sp"]["assertionConsumerService"] = {
        "url": ACS_URLS[STAGE],
        "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
    }
    return data
