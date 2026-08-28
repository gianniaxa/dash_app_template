"""
Chart component templates using Plotly Express.

Provides reusable factory functions for common chart types.
All functions return a dcc.Graph component ready to drop into any layout.

Usage:
------
from components.charts import make_bar_chart, make_line_chart, make_pie_chart

graph = make_bar_chart(df, x="month", y="revenue", title="Revenue by Month")
"""

import pandas as pd
import plotly.express as px
from dash import dcc


def make_bar_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    color: str | None = None,
    title: str = "",
    graph_id: str = "bar-chart",
    barmode: str = "group",
) -> dcc.Graph:
    """
    Creates a bar chart.

    Parameters
    ----------
    df : pd.DataFrame
    x : str
        Column for the x-axis.
    y : str
        Column for the y-axis (numeric).
    color : str, optional
        Column to use for color grouping.
    title : str
        Chart title.
    graph_id : str
        Unique component ID.
    barmode : str
        "group" (side-by-side) or "stack". Default "group".
    """
    fig = px.bar(
        df,
        x=x,
        y=y,
        color=color,
        title=title,
        barmode=barmode,
        template="plotly_white",
    )
    fig.update_layout(
        xaxis_title=x.replace("_", " ").title(),
        yaxis_title=y.replace("_", " ").title(),
        legend_title_text=color.replace("_", " ").title() if color else "",
    )
    return dcc.Graph(id=graph_id, figure=fig)


def make_line_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    color: str | None = None,
    title: str = "",
    graph_id: str = "line-chart",
    markers: bool = True,
) -> dcc.Graph:
    """
    Creates a line chart.

    Parameters
    ----------
    df : pd.DataFrame
    x : str
        Column for the x-axis.
    y : str
        Column for the y-axis (numeric).
    color : str, optional
        Column to split into multiple lines.
    title : str
        Chart title.
    graph_id : str
        Unique component ID.
    markers : bool
        Show data point markers. Default True.
    """
    fig = px.line(
        df,
        x=x,
        y=y,
        color=color,
        title=title,
        markers=markers,
        template="plotly_white",
    )
    fig.update_layout(
        xaxis_title=x.replace("_", " ").title(),
        yaxis_title=y.replace("_", " ").title(),
        legend_title_text=color.replace("_", " ").title() if color else "",
    )
    return dcc.Graph(id=graph_id, figure=fig)


def make_pie_chart(
    df: pd.DataFrame,
    names: str,
    values: str,
    title: str = "",
    graph_id: str = "pie-chart",
    hole: float = 0.0,
) -> dcc.Graph:
    """
    Creates a pie (or donut) chart.

    Parameters
    ----------
    df : pd.DataFrame
    names : str
        Column for slice labels.
    values : str
        Column for slice sizes (numeric).
    title : str
        Chart title.
    graph_id : str
        Unique component ID.
    hole : float
        0.0 = pie chart, 0.3–0.6 = donut chart. Default 0.0.
    """
    fig = px.pie(
        df,
        names=names,
        values=values,
        title=title,
        hole=hole,
        template="plotly_white",
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return dcc.Graph(id=graph_id, figure=fig)
