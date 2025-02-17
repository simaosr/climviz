import dash
import dash_mantine_components as dmc
from dash import dash_table
import numpy as np
import plotly.graph_objects as go
from climviz.helpers.layout import create_grid, make_tabbed_content, graph_in_card
from climviz.helpers.utils import make_page_id_func
from climviz.models.rrtm import (
    absorber_vmr,
    calc_olr,
    find_equilibrium_surface_temperature,
    make_fig_atm_profile,
    make_fig_rad_profile,
)
from dash import Input, Output, callback, dcc, html, State, ctx
from dash.exceptions import PreventUpdate
from icecream import ic
from dash_iconify import DashIconify

from climviz.components.div_based import CustomMantineNumberInput
from climviz.components.dmc_based import indicator_card

# Page initialization
PAGE_NAME = "RRTM"
dash.register_page(__name__, path=f"/{PAGE_NAME}", name=PAGE_NAME)
id_func = make_page_id_func(PAGE_NAME)

# Style for the page
dmc.add_figure_templates(default="mantine_light")

# Define possible parameters for the model run (and sensitivity analysis)
possible_params = {
    "co2_concentration": {
        "label": "CO2 Concentration (ppm)",
        "id": id_func("co2-concentration"),
        "value": 400.0,
        "min": 0.0,
        "max": 10000.0,
        "step": 1.0,
    },
    "ch4_concentration": {
        "label": "CH4 Concentration (ppm)",
        "id": id_func("ch4-concentration"),
        "value": 0.0,
        "min": 0.0,
        "max": 10000.0,
        "step": 1.0,
    },
    "rel_humidity": {
        "label": "Relative Humidity (-)",
        "id": id_func("rel-humidity"),
        "value": 0.8,
        "min": 0.0,
        "max": 1.0,
        "step": 0.01,
    },
    "surface_temperature": {
        "label": "Surface Temperature (K)",
        "id": id_func("surface-temperature"),
        "value": 275.0,
        "min": 250.0,
        "max": 290.0,
        "step": 1.0,
    },
}


fig = go.Figure()

# Create a dictionary of selectors for the parameters
selectors = {}
for param in possible_params:
    selectors[param] = CustomMantineNumberInput(
        id=id_func(param),
        label=possible_params[param]["label"],
        value=possible_params[param]["value"],
        min=possible_params[param]["min"],
        max=possible_params[param]["max"],
        step=possible_params[param]["step"],
        store_id=id_func("rrtm_options"),
    )

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


save_point_button = dmc.Button(
    "Save Current Point",
    id=id_func("save-point-button"),
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
            "content": graph_in_card("ind1", id_func),
            "size": 4,
        },
        {"content": graph_in_card("ind2", id_func), "size": 4},
        {"content": graph_in_card("ind3", id_func), "size": 4},
        {"content": graph_in_card("temp", id_func), "size": 4},
        {"content": graph_in_card("rad", id_func), "size": 8},
    ]
)

tab1_content = create_grid(
    [
        {"content": options_content, "size": 2},
        {
            "content": tab1_plots_grid,
            "size": 10,
        },
    ]
)

# Sensitivity Analysis Tab
sens_param_options = [{"label": s.label, "value": s.id} for s in selectors.values()]

param_selector_1 = dmc.Select(
    id="param-selector-1",
    data=sens_param_options,
    label="Parameter 1",
    value=selectors["co2_concentration"].id,
)
param_selector_2 = dmc.Select(
    id="param-selector-2",
    data=sens_param_options,
    label="Parameter 2",
    value=selectors["ch4_concentration"].id,
)

range_inputs_param_1 = dmc.SimpleGrid(
    cols=3,
    spacing="md",
    verticalSpacing="md",
    children=[
        dmc.NumberInput(id="param-1-min", label="Min", value=0),
        dmc.NumberInput(id="param-1-max", label="Max", value=1000),
        dmc.NumberInput(id=id_func("n-1"), label="# Points", value=5),
    ],
)

range_inputs_param_2 = dmc.SimpleGrid(
    cols=3,
    spacing="md",
    verticalSpacing="md",
    children=[
        dmc.NumberInput(id="param-2-min", label="Min", value=0),
        dmc.NumberInput(id="param-2-max", label="Max", value=1000),
        dmc.NumberInput(id=id_func("n-2"), label="# Points", value=5),
    ],
)

dataset_name_selector = dmc.TextInput(
    id=id_func("dataset-name"),
    label="Dataset Name",
    placeholder="Enter a name for the dataset",
    value="Dataset 1",
)


run_button = dmc.Button("Run Sensitivity Analysis", id=id_func("run-sensitivity"))

param_selector_desc = dmc.Blockquote(
    """Select the parameters to vary in the sensitivity analysis and the range of values to vary them over.
    Press the run button to see the sensitivity analysis results.""",
    icon=DashIconify(icon="tabler:info-circle", width=30),
    color="blue",
)

sensitivity_datasets_list = dmc.List(
    id=id_func("sensitivity-datasets-list"),
    children=[],
)

sensitivity_controls = dmc.Stack(
    [
        param_selector_1,
        range_inputs_param_1,
        param_selector_2,
        range_inputs_param_2,
        dataset_name_selector,
        run_button,
        param_selector_desc,
        dmc.Divider(label="Saved Datasets", variant="dashed"),
        sensitivity_datasets_list,
    ]
)

sensitivity_plots = create_grid(
    [
        {
            "content": dcc.Graph(
                id=id_func(
                    "sensitivity-contour-1",
                ),
            ),
            "size": 6,
        },
        {
            "content": dcc.Graph(id=id_func("sensitivity-contour-2")),
            "size": 6,
        },
        {
            "content": dcc.Graph(id=id_func("sensitivity-contour-3")),
            "size": 6,
        },
        {
            "content": dcc.Graph(id=id_func("sensitivity-contour-4")),
            "size": 6,
        },
    ]
)

sensitivity_layout = create_grid(
    [
        {"content": sensitivity_controls, "size": 2},
        {"content": sensitivity_plots, "size": 10},
    ]
)

# About this model content
about_content = html.Div(
    children=[
        html.H3("About this model"),
        html.P(
            "The RRTMG is a fast and accurate radiative transfer model for the calculation of longwave and shortwave radiative fluxes in the atmosphere."
        ),
        html.P(
            "Clim-viz uses the implementation of the model based on the work of climlab, a python package for climate modeling."
        ),
    ]
)

# DATA TAB CONTENT

saved_points_datatable = dash_table.DataTable(
    id=id_func("saved-points-table"),
    columns=[
        {"name": "CO2 Concentration (ppm)", "id": "CO2 Concentration (ppm)"},
        {"name": "CH4 Concentration (ppm)", "id": "CH4 Concentration (ppm)"},
        {"name": "Relative Humidity (-)", "id": "Relative Humidity (-)"},
        {"name": "Surface Temperature (K)", "id": "Surface Temperature (K)"},
    ],
    data=[],
)
sensitivity_points_datatable = dash_table.DataTable(
    id=id_func("sensitivity-points-table"),
    columns=[
        {"name": "param1_label", "id": "param1_label"},
        {"name": "param2_label", "id": "param2_label"},
        {"name": "param1_value", "id": "param1_value"},
        {"name": "param2_value", "id": "param2_value"},
        {"name": "OLR", "id": "OLR"},
        {"name": "ASR", "id": "ASR"},
        {"name": "Net Flux", "id": "Net Flux"},
        {
            "name": "Equilibrium Surface Temperature",
            "id": "Equilibrium Surface Temperature",
        },
    ],
    data=[],
    editable=False,
    style_table={"height": "600px", "overflowY": "auto"},
    export_format="csv",
)


data_content = dmc.Stack(
    children=[
        dmc.Title("Sensitivity Points", order=2),
        sensitivity_points_datatable,
        dmc.Title("Saved Points", order=2),
        saved_points_datatable,
        dcc.Store(
            id=id_func("rrtm_options"),
            data={
                s.id: {
                    "value": s.value,
                    "min": s.min,
                    "max": s.max,
                }
                for s in selectors.values()
            },
            storage_type="session",
        ),
        # Store saved points
        dcc.Store(
            id=id_func("saved_points"),
            data=[],
            storage_type="session",
        ),
        # Store last sensitivity analysis points
        dcc.Store(
            id=id_func("sensitivity_points"),
            data={},
            storage_type="session",
        ),
        dcc.Location(id=id_func("url-page"), refresh=False),
    ]
)


layout = make_tabbed_content(
    id=id_func("rrtm-tabs"),
    value="1",
    content_dict={
        "Exploration": {
            "children": tab1_content,
            "extra_tab_args": {
                "leftSection": DashIconify(icon="fluent-mdl2:explore-data")
            },
        },
        "Sensitivity Analysis": {
            "children": sensitivity_layout,
            "extra_tab_args": {"leftSection": DashIconify(icon="hugeicons:trade-up")},
        },
        "Data": {
            "children": data_content,
            "extra_tab_args": {"leftSection": DashIconify(icon="tabler:database")},
        },
        "About": {
            "children": [about_content],
            "extra_tab_args": {
                "ml": "auto",
                "leftSection": DashIconify(icon="tabler:info-circle"),
            },
        },
    },
)


# Callbacks
# @callback(
#     Output(id_func("rrtm-tabs"), "value"),
#     Input(id_func("url-page"), "search"),  # Get tab from the query string
# )
# def update_tab_from_url(query_string):
#     """Update tab selection based on URL query parameter."""
#     if ctx.triggered_id == id_func("url-page"):
#         params = (
#             dict(q.split("=") for q in query_string.lstrip("?").split("&") if "=" in q)
#             if query_string
#             else {}
#         )
#         return params.get("tab", "1")  # Default tab
#     raise PreventUpdate  # Prevent unnecessary updates


# @callback(Output(id_func("url-page"), "search"), Input(id_func("rrtm-tabs"), "value"))
# def update_url_from_tab(tab):
#     """Update URL query parameter when the tab changes."""
#     if ctx.triggered_id == id_func("rrtm-tabs"):
#         return f"?tab={tab}"
#     raise PreventUpdate  # Prevent unnecessary updates


# Callback to update the sensitivity datasets list
@callback(
    Output(id_func("sensitivity-datasets-list"), "children"),
    Input(id_func("sensitivity_points"), "data"),
)
def update_sensitivity_datasets_list(sensitivity_points):
    # Add dataset name and button to delete the dataset from the stored data
    # Add the icon next to the name of the dataset
    return [
        dmc.Group(
            [
                dmc.ActionIcon(
                    DashIconify(icon="tabler:trash"),
                    color="red",
                    variant="light",
                    id={"type": "delete-btn", "index": i},
                ),
                dmc.Text(item),
            ],
        )
        for i, item in enumerate(sensitivity_points)
    ]


# Callback to delete a sensitivity dataset when the delete button is clicked
@callback(
    Output(id_func("sensitivity_points"), "data", allow_duplicate=True),
    State(id_func("sensitivity_points"), "data"),
    Input({"type": "delete-btn", "index": dash.ALL}, "n_clicks"),
    State({"type": "delete-btn", "index": dash.ALL}, "id"),
    prevent_initial_call=True,
)
def delete_item(sensitivity_points, n_clicks, ids):
    if not np.any(n_clicks):
        return dash.no_update

    ic(n_clicks)

    # Find which button was clicked
    triggered_idx = [id["index"] for i, id in enumerate(ids) if n_clicks[i]]

    # delete nth item in sensitivity_points (which is a dictionary)
    # delete the nth item in the dictionary

    # get the key for the nth item (to be deleted)
    key_to_delete = list(sensitivity_points.keys())[triggered_idx[0]]
    del sensitivity_points[key_to_delete]

    return sensitivity_points


@callback(
    Output(id_func("rrtm_graph_temp"), "figure"),
    Output(id_func("rrtm_graph_rad"), "figure"),
    Output(id_func("rrtm_graph_ind1"), "figure"),
    Output(id_func("rrtm_graph_ind2"), "figure"),
    Output(id_func("rrtm_graph_ind3"), "figure"),
    Input(id_func("rrtm_options"), "data"),
)
def update_rrtm_graph(models_options):
    rrtm_options = models_options

    absorber_vmr_mod = absorber_vmr.copy()
    absorber_vmr_mod["CO2"] = (
        rrtm_options[selectors["co2_concentration"].id]["value"] / 1e6
    )
    absorber_vmr_mod["CH4"] = (
        rrtm_options[selectors["ch4_concentration"].id]["value"] / 1e6
    )
    sst = rrtm_options[selectors["surface_temperature"].id]["value"]
    rel_humidity = rrtm_options[selectors["rel_humidity"].id]["value"]

    state, h2o, rad = calc_olr(sst, absorber_vmr_mod, RH=rel_humidity)

    fig1 = make_fig_atm_profile(state)
    fig2 = make_fig_rad_profile(state, rad)

    net_flux = rad.OLR[0] - rad.ASR[0]
    # round to 2 decimal places
    net_flux = round(net_flux, 2)

    fig3 = go.Figure()
    fig3.add_trace(
        go.Indicator(
            mode="delta",
            value=rad.OLR[0],
            title={"text": "Outgoing Longwave Radiation (W/m²)"},
            domain={"x": [0, 1.0], "y": [0, 1.0]},
            delta={"reference": 0},
        )
    )
    fig3.update_layout(height=250)

    fig4 = go.Figure()
    fig4.add_trace(
        go.Indicator(
            mode="delta",
            title={"text": "Incoming Shortwave Radiation (W/m²)"},
            value=-rad.ASR[0],
            domain={"x": [0, 1.0], "y": [0, 1.0]},
            delta={"reference": 0},
        )
    )
    fig4.update_layout(height=250)

    fig5 = go.Figure()
    fig5.add_trace(
        go.Indicator(
            mode="delta",
            title={"text": "Radiation Balance (W/m²)"},
            value=net_flux,
            domain={"x": [0, 1.0], "y": [0, 1.0]},
            delta={"reference": 0},
        )
    )
    fig5.update_layout(height=250)

    # fig4 = indicator_card("Incoming Shortwave Radiation (W/m²)", -rad.ASR[0])

    return fig1, fig2, fig4, fig3, fig5


@callback(
    Output(selectors["surface_temperature"].id, "value"),
    Input(id_func("find-eq-button"), "n_clicks"),
    State(id_func("rrtm_options"), "data"),
    prevent_initial_call=True,
    allow_duplicate=True,
)
def eq_temperature_callback(n_clicks, options):
    rrtm_options = options

    absorber_vmr_mod = absorber_vmr.copy()
    absorber_vmr_mod["CO2"] = (
        rrtm_options[selectors["co2_concentration"].id]["value"] / 1e6
    )
    absorber_vmr_mod["CH4"] = (
        rrtm_options[selectors["ch4_concentration"].id]["value"] / 1e6
    )
    rel_humidity = rrtm_options[selectors["rel_humidity"].id]["value"]

    eq_temp = find_equilibrium_surface_temperature(
        absorber_vmr_mod, rel_humidity=rel_humidity
    )
    return eq_temp


# callback to create the sensitivity figures
@callback(
    Output(id_func("sensitivity-contour-1"), "figure"),
    Output(id_func("sensitivity-contour-2"), "figure"),
    Output(id_func("sensitivity-contour-3"), "figure"),
    Output(id_func("sensitivity-contour-4"), "figure"),
    Input(id_func("sensitivity_points"), "data"),
)
def create_sensitivity_figures(sensitivity_points):
    if len(sensitivity_points) == 0:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update

    # Get the last dataset
    sensitivity_points = list(sensitivity_points.values())[-1]

    values1 = [point["param1_value"] for point in sensitivity_points]
    values2 = [point["param2_value"] for point in sensitivity_points]
    Z1 = [point["OLR"] for point in sensitivity_points]
    Z2 = [point["ASR"] for point in sensitivity_points]
    Z3 = [point["Net Flux"] for point in sensitivity_points]
    Z4 = [point["Equilibrium Surface Temperature"] for point in sensitivity_points]

    fig1 = go.Figure(go.Contour(x=values1, y=values2, z=Z1))
    fig2 = go.Figure(go.Contour(x=values1, y=values2, z=Z2))
    fig3 = go.Figure(go.Contour(x=values1, y=values2, z=Z3))
    fig4 = go.Figure(go.Contour(x=values1, y=values2, z=Z4))

    for fig, title in zip(
        [fig1, fig2, fig3, fig4],
        ["OLR", "ASR", "Net Flux", "Equilibrium Surface Temperature"],
    ):
        # Change colormap to Blackbody
        fig.update_layout(
            coloraxis_colorscale="Blackbody",
            title=f"{title} Sensitivity Analysis",
            xaxis_title=sensitivity_points[0]["param1_label"],
            yaxis_title=sensitivity_points[0]["param2_label"],
            height=600,
            width=600,
        )

    return fig1, fig2, fig3, fig4


# Callback for sensitivity analysis
@callback(
    Output(id_func("sensitivity_points"), "data"),
    Input(id_func("run-sensitivity"), "n_clicks"),
    State("param-selector-1", "value"),
    State("param-selector-2", "value"),
    State("param-1-min", "value"),
    State("param-1-max", "value"),
    State("param-2-min", "value"),
    State("param-2-max", "value"),
    State(id_func("n-1"), "value"),
    State(id_func("n-2"), "value"),
    State(id_func("rrtm_options"), "data"),
    State(id_func("dataset-name"), "value"),
    State(id_func("sensitivity_points"), "data"),
    prevent_initial_call=True,
    allow_duplicate=True,
)
def run_sensitivity(
    n_clicks,
    param1,
    param2,
    min1,
    max1,
    min2,
    max2,
    n_1,
    n_2,
    rrtom_options,
    dataset_name,
    current_sensitivity_points,
):
    values1 = np.linspace(min1, max1, n_1)
    values2 = np.linspace(min2, max2, n_2)
    Z1 = np.zeros((n_1, n_2))
    Z2 = np.zeros((n_1, n_2))
    Z3 = np.zeros((n_1, n_2))
    Z4 = np.zeros((n_1, n_2))

    rrtm_params = {param: val["value"] for param, val in rrtom_options.items()}

    sensitivity_points = []

    for i, v1 in enumerate(values1):
        for j, v2 in enumerate(values2):
            rrtm_params[param1] = v1 / 1e6 if "concentration" in param1 else v1
            rrtm_params[param2] = v2 / 1e6 if "concentration" in param2 else v2

            absorber_vmr_mod = absorber_vmr.copy()
            absorber_vmr_mod["CO2"] = (
                rrtm_params[selectors["co2_concentration"].id] / 1e6
            )
            absorber_vmr_mod["CH4"] = (
                rrtm_params[selectors["ch4_concentration"].id] / 1e6
            )

            _, _, rad = calc_olr(
                rrtm_params[selectors["surface_temperature"].id],
                absorber_vmr_mod,
                RH=rrtm_params[selectors["rel_humidity"].id],
                Tstrat=190.0,
            )
            Z1[j, i] = rad.OLR[0]
            Z2[j, i] = rad.ASR[0]
            Z3[j, i] = rad.OLR[0] - rad.ASR[0]
            Z4[j, i] = find_equilibrium_surface_temperature(
                absorber_vmr_mod, rel_humidity=rrtm_params[selectors["rel_humidity"].id]
            )

            sensitivity_points.append(
                {
                    "param1_value": v1,
                    "param2_value": v2,
                    "param1_label": param1,
                    "param2_label": param2,
                    "options": rrtm_params,
                    "OLR": Z1[j, i],
                    "ASR": Z2[j, i],
                    "Net Flux": Z3[j, i],
                    "Equilibrium Surface Temperature": Z4[j, i],
                }
            )

    current_sensitivity_points[dataset_name] = sensitivity_points

    return current_sensitivity_points


# Callback to update the sensitivity points datatable
@callback(
    Output(id_func("sensitivity-points-table"), "data"),
    Input(id_func("sensitivity_points"), "data"),
    prevent_initial_call=True,
)
def update_sensitivity_points_table(sensitivity_points):
    # Create a dictionary with the data for the datatable
    data = []

    # Get the last dataset
    sensitivity_points = list(sensitivity_points.values())[-1]

    for point in sensitivity_points:
        data.append(
            {
                "param1_label": point["param1_label"],
                "param2_label": point["param2_label"],
                "param1_value": point["param1_value"],
                "param2_value": point["param2_value"],
                "OLR": point["OLR"],
                "ASR": point["ASR"],
                "Net Flux": point["Net Flux"],
                "Equilibrium Surface Temperature": point[
                    "Equilibrium Surface Temperature"
                ],
            }
        )
    return data


@callback(
    Output(id_func("saved_points"), "data"),
    Input(id_func("save-point-button"), "n_clicks"),
    State(id_func("rrtm_options"), "data"),
    State(id_func("saved_points"), "data"),
    prevent_initial_call=True,
)
def save_point(n_clicks, rrtm_options, saved_points):
    if saved_points is None:
        saved_points = []

    saved_points.append(rrtm_options)
    return saved_points
