"""
Modal component template.

Usage example:
--------------
from components.modal import make_modal, register_modal_toggle

# 1. In your layout, add the modal and a trigger button:
layout = html.Div([
    dbc.Button("Open Modal", id="btn-open-my-modal"),
    make_modal(
        modal_id="my-modal",
        title="My Modal Title",
        body=html.P("Modal body content goes here."),
        footer=[
            dbc.Button("Save",   id="btn-save",            color="primary"),
            dbc.Button("Cancel", id="btn-cancel-my-modal", color="secondary"),
        ],
    ),
])

# 2. Register the toggle callback once at module level (outside layout):
register_modal_toggle(
    modal_id="my-modal",
    open_trigger_id="btn-open-my-modal",
    close_trigger_id="btn-cancel-my-modal",
)
"""

from dash import Input, Output, callback
import dash_bootstrap_components as dbc
from dash import html


def make_modal(
    modal_id: str,
    title: str,
    body,
    footer=None,
    size: str = "lg",
    centered: bool = True,
) -> dbc.Modal:
    """
    Creates a reusable Bootstrap modal.

    Parameters
    ----------
    modal_id : str
        Unique ID for this modal. Used to wire up open/close callbacks.
    title : str
        Text shown in the modal header.
    body : dash component or list
        Content rendered inside the modal body.
    footer : list of dash components, optional
        Buttons or other elements in the modal footer.
        If None, a default Close button is rendered.
    size : str
        Bootstrap modal size: "sm", "lg", "xl". Default "lg".
    centered : bool
        Whether the modal is vertically centered. Default True.
    """
    if footer is None:
        footer = [dbc.Button("Close", id=f"{modal_id}-close-default", color="secondary")]

    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle(title)),
            dbc.ModalBody(body),
            dbc.ModalFooter(footer),
        ],
        id=modal_id,
        size=size,
        centered=centered,
        is_open=False,
    )


def register_modal_toggle(
    modal_id: str,
    open_trigger_id: str,
    close_trigger_id: str,
):
    """
    Registers a Dash callback to open and close a modal.
    Call once at module level in the page that uses the modal.

    Parameters
    ----------
    modal_id : str
        Must match the modal_id used in make_modal().
    open_trigger_id : str
        ID of the element that opens the modal (e.g. a Button).
    close_trigger_id : str
        ID of the element that closes the modal (e.g. a Cancel button).
    """

    @callback(
        Output(modal_id, "is_open"),
        Input(open_trigger_id, "n_clicks"),
        Input(close_trigger_id, "n_clicks"),
        prevent_initial_call=True,
    )
    def toggle_modal(n_open, n_close):
        from dash import ctx
        if ctx.triggered_id == open_trigger_id:
            return True
        return False

