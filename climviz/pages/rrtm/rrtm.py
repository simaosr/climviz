import dash
import dash_mantine_components as dmc
import numpy as np
import plotly.graph_objects as go
from dash import Input, Output, State, callback, ctx, dash_table, dcc, html
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from icecream import ic

from climviz.components.div_based import CustomMantineNumberInput
from climviz.components.dmc_based import indicator_card
from climviz.helpers.layout import (
    create_grid,
    graph_in_card,
    make_indicator_card,
    make_tabbed_content,
)
from climviz.helpers.utils import make_page_id_func
from climviz.models.rrtm import (
    absorber_vmr,
    calc_olr,
    find_equilibrium_surface_temperature,
    make_fig_atm_profile,
    make_fig_rad_profile,
)

from climviz.pages.rrtm.common import PAGE_DESC, PAGE_IMG, PAGE_NAME, id_func, selectors
from climviz.pages.rrtm.exploration import tab_content as tab1_content
from climviz.pages.rrtm.sensitivity_analysis import sensitivity_layout

# Check if RRTM model is available (in the climlab_rrtm package)
try:
    import climlab_rrtmg

    have_rrtm = True
except ImportError:
    have_rrtm = False


if have_rrtm:
    dash.register_page(
        __name__,
        path=f"/{PAGE_NAME}",
        name=PAGE_NAME,
        description=PAGE_DESC,
        image=PAGE_IMG,
    )

# Style for the page
dmc.add_figure_templates(default="mantine_light")


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
            id=id_func("rrtm-options"),
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
            id=id_func("saved-points"),
            data=[],
            storage_type="session",
        ),
        # Store last sensitivity analysis points
        dcc.Store(
            id=id_func("sensitivity-points"),
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


# Callback to update the sensitivity datasets list
@callback(
    Output(id_func("sensitivity-datasets-list"), "children"),
    Input(id_func("sensitivity-points"), "data"),
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
    Output(id_func("sensitivity-points"), "data", allow_duplicate=True),
    State(id_func("sensitivity-points"), "data"),
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
    Output(id_func("ind1"), "children"),
    Output(id_func("ind2"), "children"),
    Output(id_func("ind3"), "children"),
    Input(id_func("rrtm-options"), "data"),
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

    ind1_children = make_indicator_card(
        indicator=-rad.ASR[0],
        title="Incoming shortwave Radiation",
        unit="W/m²",
        hover_text="At the top of the atmosphere",
    )

    ind2_children = make_indicator_card(
        indicator=rad.OLR[0],
        title="Outgoing Longwave Radiation",
        unit="W/m²",
        hover_text="At the top of the atmosphere",
    )

    ind3_children = make_indicator_card(
        indicator=net_flux,
        title="Radiation Balance",
        unit="W/m²",
        hover_text="Net flux at the top of the atmosphere. \n"
        "Positive values indicate a net gain of energy, "
        "negative values indicate a net loss of energy.",
    )

    # fig4 = indicator_card("Incoming Shortwave Radiation (W/m²)", -rad.ASR[0])

    return fig1, fig2, ind3_children, ind1_children, ind2_children


@callback(
    Output(selectors["surface_temperature"].id, "value"),
    Input(id_func("find-eq-button"), "n_clicks"),
    State(id_func("rrtm-options"), "data"),
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
    Input(id_func("sensitivity-points"), "data"),
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
    Output(id_func("sensitivity-points"), "data"),
    Input(id_func("run-sensitivity"), "n_clicks"),
    State("param-selector-1", "value"),
    State("param-selector-2", "value"),
    State("param-1-min", "value"),
    State("param-1-max", "value"),
    State("param-2-min", "value"),
    State("param-2-max", "value"),
    State(id_func("n-1"), "value"),
    State(id_func("n-2"), "value"),
    State(id_func("rrtm-options"), "data"),
    State(id_func("dataset-name"), "value"),
    State(id_func("sensitivity-points"), "data"),
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
    Input(id_func("sensitivity-points"), "data"),
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
    Output(id_func("saved-points"), "data"),
    Input(id_func("save-point-button"), "n_clicks"),
    State(id_func("point-name"), "value"),
    State(id_func("rrtm-options"), "data"),
    State(id_func("saved-points"), "data"),
    prevent_initial_call=True,
)
def save_point(n_clicks, point_name, rrtm_options, saved_points):
    if saved_points is None:
        saved_points = {}

    saved_points[point_name] = rrtm_options

    return saved_points
