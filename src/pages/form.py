import dash
from dash import html, Input, Output, State, callback
import dash_bootstrap_components as dbc

from components.form import make_user_form
from components.table_aggrid import make_aggrid
from utils.data_loader import load_csv, save_csv

dash.register_page(__name__, path="/form", name="Form")

FORM_ID = "user-form"

layout = dbc.Container(
    [
        html.H1("User Form", className="mb-1"),
        html.P(
            "Fill in the form to add a new user. The table below updates after each submission.",
            className="text-muted mb-4",
        ),
        make_user_form(form_id=FORM_ID),
        html.Hr(className="my-4"),
        html.H5("Users", className="mb-3"),
        make_aggrid(
            table_id="form-users-table",
            data=load_csv("users.csv"),
            page_size=10,
            height="400px",
        ),
    ],
    className="py-4",
)


@callback(
    Output("form-users-table", "rowData"),
    Output(f"{FORM_ID}-feedback", "children"),
    Output(f"{FORM_ID}-name", "value"),
    Output(f"{FORM_ID}-nationality", "value"),
    Output(f"{FORM_ID}-email", "value"),
    Output(f"{FORM_ID}-birthday", "date"),
    Input(f"{FORM_ID}-submit", "n_clicks"),
    State(f"{FORM_ID}-name", "value"),
    State(f"{FORM_ID}-nationality", "value"),
    State(f"{FORM_ID}-email", "value"),
    State(f"{FORM_ID}-birthday", "date"),
    prevent_initial_call=True,
)
def submit_user(n_clicks, name, nationality, email, birthday):
    # Validation
    missing = [label for label, val in [
        ("Name", name),
        ("Nationality", nationality),
        ("Email", email),
        ("Birthday", birthday),
    ] if not val]

    if missing:
        feedback = dbc.Alert(
            f"Please fill in: {', '.join(missing)}.",
            color="danger",
            dismissable=True,
        )
        return dash.no_update, feedback, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    save_csv("users.csv", {
        "name": name,
        "nationality": nationality,
        "email": email,
        "birthday": birthday,
    })

    feedback = dbc.Alert(
        f"{name} has been added successfully.",
        color="success",
        dismissable=True,
        duration=4000,
    )

    return load_csv("users.csv"), feedback, None, None, None, None
