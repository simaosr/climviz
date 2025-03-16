from climviz.components.div_based import CustomMantineNumberInput
from climviz.helpers.layout import create_grid
from climviz.helpers.utils import make_page_id_func
import dash
import dash_mantine_components as dmc
from dash import dcc
from dash import html
from dash_iconify import DashIconify

PAGE_NAME = "grey_radiation"
id_func = make_page_id_func(PAGE_NAME)

dash.register_page(__name__, path=f"/{PAGE_NAME}", name=PAGE_NAME)

# Style for the page
dmc.add_figure_templates(default="mantine_light")

# Controls

info_desc = dmc.Blockquote(
    """Select the number of layers in the model.""",
    icon=DashIconify(icon="tabler:info-circle", width=30),
    color="blue",
)

number_of_layers = CustomMantineNumberInput(
    id=id_func("number_of_layers"),
    label="Number of Layers",
    min=1,
    max=10,
    step=1,
    store_id=id_func("store"),
)


save_button = dmc.Button("Save", id=id_func("save_button"))


controls_layout = dmc.Stack(
    [
        dmc.Title("Controls", order=3),
        number_of_layers,
        info_desc,
        save_button,
        dmc.Divider(label="Saved Datasets", variant="dashed"),
    ]
)


# Outputs


main_layout = create_grid(
    [
        {
            "content": [controls_layout],
            "size": 2,
        },
        {
            "content": [],
            "size": 10,
        },
    ]
)


layout = html.Div(
    [
        dcc.Store(id=id_func("store"), data={}),
        main_layout,
    ]
)
