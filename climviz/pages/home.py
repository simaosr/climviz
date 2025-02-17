import dash
from dash import dcc
from dash import html
import plotly.express as px
import plotly.graph_objects as go
from dash import callback, clientside_callback, Output, Input

import dash_mantine_components as dmc

from climviz.helpers.layout import create_grid

dash.register_page(__name__, path="/")


# make grid layoyt showing all the pages in the app, one in each card style
layout = create_grid(
    [
        {
            "content": dcc.Link(
                href=f"/{page['name']}",
                children=[
                    dmc.Card(
                        children=[dmc.Text(page["name"])],
                        withBorder=True,
                    )
                ],
            ),
            "size": 4,
        }
        for page in dash.page_registry.values()
        if page["path"] != "/"
    ]
)

layout = dmc.Container(
    children=[
        dmc.Text("Welcome to the Climate Visualization Tool"),
        layout,
    ],
    style={"textAlign": "center"},
)
