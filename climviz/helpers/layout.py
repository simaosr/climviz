from dash import dcc
from dash import html
import pandas as pd
from icecream import ic
import dash_mantine_components as dmc

import plotly.express as px


def create_grid(columns_dict):
    layout = html.Div(
        dmc.Grid(
            children=[
                dmc.GridCol(col["content"], span=col["size"], **col.get("options", {}))
                for col in columns_dict
            ],
        ),
        style={"padding": "1rem"},
    )

    return layout


def create_appshell(
    content,
    header: str | list | None = None,
    navbar: str | list | None = None,
    footer: str | list | None = None,
    aside: str | list | None = None,
    extra: str | list | None = None,
):
    children = []
    content_args = {}

    if header is not None:
        children.append(dmc.AppShellHeader(children=header))
        content_args["header"] = {"height": 60}

    if navbar is not None:
        children.append(
            dmc.AppShellNavbar(
                id="navbar",
                children=navbar,
                p="md",
            )
        )
        content_args["navbar"] = {
            "width": 300,
            "breakpoint": "sm",
            "collapsed": {"mobile": True},
        }

    children.append(dmc.AppShellMain(content))

    if aside is not None:
        children.append(dmc.AppShellAside(aside, p="md"))
        content_args["aside"] = {
            "width": 300,
            "breakpoint": "md",
            "collapsed": {"desktop": False, "mobile": True},
        }

    if footer is not None:
        children.append(dmc.AppShellFooter(footer, p="md"))
        content_args["footer"] = {"height": 60}

    if extra is not None:
        children.append(extra)

    layout = dmc.AppShell(
        children,
        **content_args,
        padding="md",
        id="appshell",
    )

    return dmc.MantineProvider(layout)


def make_footer() -> list:
    return ["footer"]


def make_header() -> list:
    return ["header"]


def make_navbar(content: list | None = None) -> list:
    if content is None:
        content = [dmc.Skeleton(height=28, mt="sm", animate=False) for _ in range(15)]
    else:
        content = content

    return [
        "Navbar",
        *content,
    ]


def make_tabbed_content(
    content_dict: dict, id: str = "tabs", value: str = "1"
) -> dmc.Tabs:
    return dmc.Tabs(
        [
            dmc.TabsList(
                [
                    dmc.TabsTab(
                        name,
                        value=str(content.get("value", val + 1)),
                        **content.get("extra_tab_args", {}),
                    )
                    for val, (name, content) in enumerate(content_dict.items())
                ]
            ),
            *[
                dmc.TabsPanel(
                    content["children"],
                    value=str(content.get("value", val + 1)),
                    **content.get("extra_panel_args", {}),
                )
                for val, (name, content) in enumerate(content_dict.items())
            ],
        ],
        value=value,
        id=id,
    )


def graph_in_card(
    name: str,
    id_func: callable,
    prefix: str = "rrtm_graph_",
    graph_options: dict | None = None,
    card_options: dict | None = None,
):
    default_card_options = {
        "withBorder": True,
        "shadow": "sm",
        "radius": "md",
        "padding": 0,
    }

    if graph_options is None:
        graph_options = {}

    if card_options is None:
        card_options = {}

    card_options = {**default_card_options, **card_options}

    return dmc.Card(
        children=[dcc.Graph(id_func(f"{prefix}{name}"), **graph_options)],
        **card_options,
    )
