"""
Session helpers.

Thin wrappers around Flask's session object.
Pages and components should use these instead of accessing session directly,
so the rest of the app stays decoupled from the auth implementation.

Usage:
------
from auth.session import is_authenticated, get_user, get_roles

if not is_authenticated():
    ...

user = get_user()    # e.g. "C123456" or "local-dev"
roles = get_roles()  # e.g. ["ROLE_ADMIN"]
"""

from flask import session


def is_authenticated() -> bool:
    """Return True if the current request has a valid session."""
    return "user_id" in session


def get_user() -> str | None:
    """Return the current user's ID (e.g. employee number or username)."""
    return session.get("user_id")


def get_roles() -> list[str]:
    """Return the list of roles assigned to the current user."""
    return session.get("roles", [])


def has_role(role: str) -> bool:
    """Return True if the current user has the given role."""
    return role in get_roles()


def _write_session(user_id: str, roles: list[str]) -> None:
    """
    Internal helper used by saml_auth.py to write auth data into the session.
    Not intended to be called from pages or components.
    """
    session.clear()
    session.modified = True
    session.permanent = True
    session["user_id"] = user_id
    session["roles"] = roles
