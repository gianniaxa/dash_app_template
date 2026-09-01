import dash
from dash import html
import dash_mantine_components as dmc

dash.register_page(__name__, path="/theme/mantine", name="Theme: Mantine")

# Mantine via dash-mantine-components
# Install: uv add dash-mantine-components

layout = dmc.MantineProvider(
    theme={"colorScheme": "light"},
    children=html.Div([
        dmc.Container([
            # Header
            dmc.Title("Mantine Theme", order=1, mb="xs"),
            dmc.Text(
                "dash-mantine-components — React Mantine UI library for Dash. Clean, modern, accessible.",
                c="dimmed",
                size="lg",
                mb="xl",
            ),
            dmc.Divider(mb="xl"),

            # KPI Cards
            dmc.SimpleGrid(
                cols={"base": 1, "sm": 2, "lg": 4},
                mb="xl",
                children=[
                    dmc.Card([
                        dmc.Text("Total Positions", size="sm", c="dimmed"),
                        dmc.Title("142", order=2, c="blue"),
                        dmc.Text("Job Level ≥ 8", size="xs", c="dimmed", mt=4),
                    ], withBorder=True, shadow="sm", radius="md", p="lg"),
                    dmc.Card([
                        dmc.Text("Candidates Assigned", size="sm", c="dimmed"),
                        dmc.Title("318", order=2, c="green"),
                        dmc.Text("Across all positions", size="xs", c="dimmed", mt=4),
                    ], withBorder=True, shadow="sm", radius="md", p="lg"),
                    dmc.Card([
                        dmc.Text("Ready Now", size="sm", c="dimmed"),
                        dmc.Title("74", order=2, c="yellow"),
                        dmc.Text("Succession ready", size="xs", c="dimmed", mt=4),
                    ], withBorder=True, shadow="sm", radius="md", p="lg"),
                    dmc.Card([
                        dmc.Text("Interests Expressed", size="sm", c="dimmed"),
                        dmc.Title("89", order=2, c="violet"),
                        dmc.Text("By employees", size="xs", c="dimmed", mt=4),
                    ], withBorder=True, shadow="sm", radius="md", p="lg"),
                ],
            ),

            # Table
            dmc.Card(
                mb="xl",
                withBorder=True,
                shadow="sm",
                radius="md",
                p=0,
                children=dmc.Table(
                    striped=True,
                    highlightOnHover=True,
                    withTableBorder=False,
                    data={
                        "head": ["Position", "Department", "Level", "Candidates", "Status"],
                        "body": [
                            ["Head of Engineering", "Technology", "10", "3",
                             dmc.Badge("Ready Now", color="green", variant="light")],
                            ["VP Finance", "Finance", "12", "2",
                             dmc.Badge("1-2 Years", color="yellow", variant="light")],
                            ["Director HR", "HR", "9", "4",
                             dmc.Badge("3+ Years", color="gray", variant="light")],
                            ["Head of Sales", "Sales", "8", "1",
                             dmc.Badge("Ready Now", color="green", variant="light")],
                        ],
                    },
                ),
            ),

            # Form
            dmc.Card(
                mb="xl",
                withBorder=True,
                shadow="sm",
                radius="md",
                p="lg",
                children=[
                    dmc.Title("Express Interest", order=3, mb="md"),
                    dmc.Grid([
                        dmc.GridCol(
                            dmc.Select(
                                label="Position",
                                placeholder="Select a position...",
                                data=[
                                    {"label": "Head of Engineering", "value": "1"},
                                    {"label": "VP Finance", "value": "2"},
                                    {"label": "Director HR", "value": "3"},
                                ],
                            ),
                            span=6,
                        ),
                        dmc.GridCol(
                            dmc.Textarea(
                                label="Motivation (optional)",
                                placeholder="Why are you interested?",
                                minRows=2,
                            ),
                            span=6,
                        ),
                    ], mb="md"),
                    dmc.Group([
                        dmc.Button("Submit Interest", color="blue"),
                        dmc.Button("Cancel", variant="default"),
                    ]),
                ],
            ),

            # Info
            dmc.Alert(
                "This page uses dash-mantine-components (Mantine UI). "
                "Install with: uv add dash-mantine-components",
                title="Mantine",
                color="blue",
                variant="light",
            ),
        ], py="xl"),
    ]),
)
