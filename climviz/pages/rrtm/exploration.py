import dash_mantine_components as dmc
from dash import dash_table, html
from dash_iconify import DashIconify

from climviz.helpers.layout import (
    create_grid,
    graph_in_card,
)

from climviz.pages.rrtm.common import id_func, selectors

# create temperature selector with the update button
temp_selector_with_button = dmc.Group(
    [
        selectors["surface_temperature"],
        dmc.ActionIcon(
            children=DashIconify(icon="material-symbols:target"),
            size="input-sm",
            id=id_func("find-eq-button"),
        ),
    ],
    align="end",
)


save_point_button = dmc.Stack(
    [
        dmc.Divider(label="Save", variant="dashed"),
        dmc.TextInput(
            id=id_func("point-name"),
            value="Point Name",
            size="sm",
        ),
        dmc.Button(
            "Save Current Point",
            id=id_func("save-point-button"),
        ),
    ]
)

# Component to visualzied saved points in a table
saved_points_content = dash_table.DataTable(
    id=id_func("saved-points-table"),
    columns=[{"name": col.label, "id": col.id} for col in selectors.values()],
    data=[],
)

options_content = html.Div(
    children=[
        html.H3("RRTM Model Inputs"),
        dmc.Divider(label="Atmosphere", variant="dashed"),
        dmc.Stack(
            children=[temp_selector_with_button],
        ),
        dmc.Divider(label="Pollutants", variant="dashed"),
        dmc.Stack(
            children=[
                selectors["co2_concentration"],
                selectors["ch4_concentration"],
                selectors["rel_humidity"],
            ],
            gap="md",
        ),
        dmc.Divider(label="Aerosols", variant="dashed"),
        dmc.Stack(
            children=[],
        ),
        dmc.Stack(
            children=[
                save_point_button,
            ],
        ),
    ]
)


tab1_plots_grid = create_grid(
    [
        {
            "content": html.Div(id=id_func("ind1")),  # graph_in_card("ind1", id_func),
            "size": 4,
        },
        {"content": html.Div(id=id_func("ind2")), "size": 4},
        {"content": html.Div(id=id_func("ind3")), "size": 4},
        {"content": graph_in_card("temp", id_func), "size": 4},
        {"content": graph_in_card("rad", id_func), "size": 8},
    ]
)

tab_content = create_grid(
    [
        {"content": options_content, "size": 2},
        {
            "content": tab1_plots_grid,
            "size": 10,
        },
    ]
)
