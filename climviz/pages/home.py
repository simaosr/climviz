import dash
import dash_mantine_components as dmc
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, callback, clientside_callback, dcc, html

from dash_iconify import DashIconify

from climviz.helpers.layout import create_grid, make_home_card

dash.register_page(__name__, path="/")


# make grid layoyt showing all the pages in the app, one in each card style
layout = create_grid(
    [
        {
            "content": make_home_card(
                page["name"],
                page.get("description", ""),
                href=f"/{page['name']}",
                image=dmc.Image(
                    src=dash.get_asset_url(page.get("image", "")),
                    h=160,
                    alt=page["name"],
                )
                if page.get("image", None)
                else None,
            ),
            "size": 4,
        }
        for page in dash.page_registry.values()
        if page["path"] != "/"
    ],
    grid_options={"justify": "space-around", "align": "stretch"},
)

layout = dmc.Container(
    children=[
        dmc.Blockquote(
            "Welcome to the Climate Visualization Tool."
            "Chose the model you want to visualize by chosing one card of selecting the model from the menu on the left.",
            icon=DashIconify(icon="codicon:info", width=30),
            color="blue",
            m="md",
        ),
        layout,
    ],
    fluid=True,
    style={"textAlign": "center"},
)
