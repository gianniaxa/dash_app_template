import dash
from dash import html

dash.register_page(__name__, path="/theme/tailwind", name="Theme: Tailwind")

# Tailwind CSS via CDN — no Bootstrap components used on this page
TAILWIND_CSS = "https://cdn.jsdelivr.net/npm/tailwindcss@3.4.17/base.css"
TAILWIND_CDN = "https://cdn.tailwindcss.com"

layout = html.Div([
    html.Link(rel="stylesheet", href=TAILWIND_CSS),
    html.Script(src=TAILWIND_CDN),

    html.Div([
        # Header
        html.Div([
            html.H1("Tailwind CSS Theme", className="text-3xl font-bold text-gray-900 mb-1"),
            html.P(
                "Pure Tailwind CSS — no Bootstrap. Utility-first, fully customizable.",
                className="text-gray-500 text-lg mb-8",
            ),
            html.Hr(className="border-gray-200 mb-8"),
        ]),

        # KPI Cards
        html.Div([
            html.Div([
                html.P("Total Positions", className="text-sm font-medium text-gray-500"),
                html.P("142", className="text-3xl font-bold text-blue-600 mt-1"),
                html.P("Job Level ≥ 8", className="text-xs text-gray-400 mt-1"),
            ], className="bg-white rounded-xl shadow p-6"),
            html.Div([
                html.P("Candidates Assigned", className="text-sm font-medium text-gray-500"),
                html.P("318", className="text-3xl font-bold text-green-600 mt-1"),
                html.P("Across all positions", className="text-xs text-gray-400 mt-1"),
            ], className="bg-white rounded-xl shadow p-6"),
            html.Div([
                html.P("Ready Now", className="text-sm font-medium text-gray-500"),
                html.P("74", className="text-3xl font-bold text-yellow-500 mt-1"),
                html.P("Succession ready", className="text-xs text-gray-400 mt-1"),
            ], className="bg-white rounded-xl shadow p-6"),
            html.Div([
                html.P("Interests Expressed", className="text-sm font-medium text-gray-500"),
                html.P("89", className="text-3xl font-bold text-purple-600 mt-1"),
                html.P("By employees", className="text-xs text-gray-400 mt-1"),
            ], className="bg-white rounded-xl shadow p-6"),
        ], className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8"),

        # Table
        html.Div([
            html.Table([
                html.Thead(
                    html.Tr([
                        html.Th("Position", className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider"),
                        html.Th("Department", className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider"),
                        html.Th("Level", className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider"),
                        html.Th("Candidates", className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider"),
                        html.Th("Status", className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider"),
                    ]),
                    className="bg-gray-50 border-b border-gray-200",
                ),
                html.Tbody([
                    html.Tr([
                        html.Td("Head of Engineering", className="px-4 py-3 text-sm text-gray-900"),
                        html.Td("Technology", className="px-4 py-3 text-sm text-gray-500"),
                        html.Td("10", className="px-4 py-3 text-sm text-gray-500"),
                        html.Td("3", className="px-4 py-3 text-sm text-gray-500"),
                        html.Td(html.Span("Ready Now", className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full"), className="px-4 py-3"),
                    ], className="border-b border-gray-100 hover:bg-gray-50"),
                    html.Tr([
                        html.Td("VP Finance", className="px-4 py-3 text-sm text-gray-900"),
                        html.Td("Finance", className="px-4 py-3 text-sm text-gray-500"),
                        html.Td("12", className="px-4 py-3 text-sm text-gray-500"),
                        html.Td("2", className="px-4 py-3 text-sm text-gray-500"),
                        html.Td(html.Span("1-2 Years", className="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded-full"), className="px-4 py-3"),
                    ], className="border-b border-gray-100 hover:bg-gray-50"),
                    html.Tr([
                        html.Td("Director HR", className="px-4 py-3 text-sm text-gray-900"),
                        html.Td("HR", className="px-4 py-3 text-sm text-gray-500"),
                        html.Td("9", className="px-4 py-3 text-sm text-gray-500"),
                        html.Td("4", className="px-4 py-3 text-sm text-gray-500"),
                        html.Td(html.Span("3+ Years", className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-600 rounded-full"), className="px-4 py-3"),
                    ], className="border-b border-gray-100 hover:bg-gray-50"),
                    html.Tr([
                        html.Td("Head of Sales", className="px-4 py-3 text-sm text-gray-900"),
                        html.Td("Sales", className="px-4 py-3 text-sm text-gray-500"),
                        html.Td("8", className="px-4 py-3 text-sm text-gray-500"),
                        html.Td("1", className="px-4 py-3 text-sm text-gray-500"),
                        html.Td(html.Span("Ready Now", className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full"), className="px-4 py-3"),
                    ], className="hover:bg-gray-50"),
                ]),
            ], className="w-full"),
        ], className="bg-white rounded-xl shadow overflow-hidden mb-8"),

        # Form
        html.Div([
            html.H2("Express Interest", className="text-lg font-semibold text-gray-900 mb-4"),
            html.Div([
                html.Div([
                    html.Label("Position", className="block text-sm font-medium text-gray-700 mb-1"),
                    html.Select([
                        html.Option("Select a position...", value=""),
                        html.Option("Head of Engineering", value="1"),
                        html.Option("VP Finance", value="2"),
                        html.Option("Director HR", value="3"),
                    ], className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"),
                ], className="flex-1"),
                html.Div([
                    html.Label("Motivation (optional)", className="block text-sm font-medium text-gray-700 mb-1"),
                    html.Textarea(
                        placeholder="Why are you interested?",
                        rows=2,
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500",
                    ),
                ], className="flex-1"),
            ], className="flex gap-4 mb-4"),
            html.Div([
                html.Button("Submit Interest", className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700"),
                html.Button("Cancel", className="ml-2 border border-gray-300 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-50"),
            ]),
        ], className="bg-white rounded-xl shadow p-6 mb-8"),

        # Info
        html.Div([
            html.P(
                "This page uses Tailwind CSS via CDN — no Bootstrap components. "
                "The navbar above still uses Bootstrap (from the global stylesheet).",
                className="text-sm text-blue-800",
            ),
        ], className="bg-blue-50 border border-blue-200 rounded-lg p-4"),

    ], className="max-w-6xl mx-auto px-6 py-8"),
])
