"""
User form component template.

Provides a form with Name, Nationality (dropdown), Email, and Birthday (date picker).

Usage:
------
from components.form import make_user_form

layout = html.Div([
    make_user_form(form_id="user-form"),
])
"""

from dash import dcc, html
import dash_bootstrap_components as dbc

NATIONALITIES = [
    "Austrian",
    "Belgian",
    "Dutch",
    "French",
    "German",
    "Italian",
    "Polish",
    "Portuguese",
    "Spanish",
    "Swedish",
    "Swiss",
    "Other",
]


def make_user_form(form_id: str) -> dbc.Form:
    """
    Creates a user entry form with Name, Nationality, Email, and Birthday.

    Parameters
    ----------
    form_id : str
        Prefix used for all field IDs. E.g. form_id="user-form" produces
        IDs: "user-form-name", "user-form-nationality", "user-form-email",
        "user-form-birthday", "user-form-submit", "user-form-feedback".
    """
    return dbc.Form(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Name"),
                            dbc.Input(
                                id=f"{form_id}-name",
                                type="text",
                                placeholder="e.g. Anna Müller",
                            ),
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Nationality"),
                            dcc.Dropdown(
                                id=f"{form_id}-nationality",
                                options=[{"label": n, "value": n} for n in NATIONALITIES],
                                placeholder="Select nationality...",
                                clearable=True,
                            ),
                        ],
                        md=6,
                    ),
                ],
                className="mb-3",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Email"),
                            dbc.Input(
                                id=f"{form_id}-email",
                                type="email",
                                placeholder="e.g. anna@example.com",
                            ),
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Birthday"),
                            dcc.DatePickerSingle(
                                id=f"{form_id}-birthday",
                                placeholder="Select date...",
                                display_format="DD.MM.YYYY",
                                style={"width": "100%"},
                            ),
                        ],
                        md=6,
                    ),
                ],
                className="mb-4",
            ),
            dbc.Button("Save", id=f"{form_id}-submit", color="primary"),
            html.Div(id=f"{form_id}-feedback", className="mt-3"),
        ],
        id=form_id,
    )
