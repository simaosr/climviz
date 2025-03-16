import dash
import dash_mantine_components as dmc
from dash import (
    Dash,
    dcc,
    _dash_renderer,
    Input,
    Output,
    clientside_callback,
    callback,
    State,
)
from dash_iconify import DashIconify

from climviz.helpers.layout import create_appshell, make_navbar


# Initialize the Dash app
_dash_renderer._set_react_version("18.2.0")

app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=dmc.styles.ALL,
    suppress_callback_exceptions=True,
)

# Style for the page
dmc.add_figure_templates(default="mantine_light")

theme_toggle = dmc.Switch(
    offLabel=DashIconify(
        icon="radix-icons:sun", width=15, color=dmc.DEFAULT_THEME["colors"]["yellow"][8]
    ),
    onLabel=DashIconify(
        icon="radix-icons:moon",
        width=15,
        color=dmc.DEFAULT_THEME["colors"]["yellow"][6],
    ),
    id="color-scheme-toggle",
    persistence=True,
    color="grey",
)

# Prepare navbar to list all possible pages
possible_pages = dash.page_registry
navbar_items = [
    dmc.NavLink(
        label=page["name"],
        href=page["path"],
    )
    for page in possible_pages.values()
]
header_items = [
    dmc.Group(
        [
            # dmc.Burger(id="burger", size="md", opened=False),
            dmc.Title("ClimViz", c="blue"),
            theme_toggle,
        ],
        h="100%",
        px="md",
    )
]


# Define the layout of the app
app.layout = create_appshell(
    header=header_items,
    content=dash.page_container,
    navbar=make_navbar(navbar_items),
    footer=dmc.Center(
        dmc.Text(
            "Climate Models Visualization Tool - Simão Rodrigues",
            c="blue",
        )
    ),
    aside=None,
    extra=dcc.Store(id="models_options", storage_type="session", data={}),
)

clientside_callback(
    """ 
    (switchOn) => {
       document.documentElement.setAttribute('data-mantine-color-scheme', switchOn ? 'dark' : 'light');  
       return window.dash_clientside.no_update
    }
    """,
    Output("color-scheme-toggle", "id"),
    Input("color-scheme-toggle", "checked"),
)


@callback(
    Output("appshell", "navbar"),
    Input("main-burger", "opened"),
    State("appshell", "navbar"),
)
def navbar_is_open(opened, navbar):
    navbar["collapsed"] = {"mobile": not opened}
    return navbar


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
