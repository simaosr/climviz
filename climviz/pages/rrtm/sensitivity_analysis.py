import dash_mantine_components as dmc
from dash import dcc
from dash_iconify import DashIconify

from climviz.helpers.layout import (
    create_grid,
)

from climviz.pages.rrtm.common import id_func, selectors

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
