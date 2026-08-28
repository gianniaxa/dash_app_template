import dash
from dash import html
import dash_bootstrap_components as dbc

from components.modal import make_modal, register_modal_toggle

dash.register_page(__name__, path="/modal", name="Modal")

register_modal_toggle(
    modal_id="demo-modal",
    open_trigger_id="btn-open-demo-modal",
    close_trigger_id="btn-close-demo-modal",
)

layout = dbc.Container(
    [
        html.H1("Modal", className="mb-1"),
        html.P(
            "Example of a reusable modal component. Click the button to open it.",
            className="text-muted mb-4",
        ),
        dbc.Button("Open Modal", id="btn-open-demo-modal", color="primary"),
        make_modal(
            modal_id="demo-modal",
            title="Example Modal",
            body=html.P("This is the modal body. Put any content here."),
            footer=[
                dbc.Button("Save",  id="btn-save-demo-modal",  color="primary"),
                dbc.Button("Close", id="btn-close-demo-modal", color="secondary"),
            ],
        ),
    ],
    className="py-4",
)
