import dash_mantine_components as dmc
from dash_iconify import DashIconify


# Card component with a title, and a value with an arrow depending if it is positive or negative
# make text red or green depending on the value
def indicator_card(title, value):
    arrow = "▲" if value > 0 else "▼"
    text_color = "red" if value < 0 else "green"

    return dmc.Card(
        [
            dmc.Title(title, order=4),
            dmc.Title(f"{arrow}{value:.2f}", style={"color": text_color}, order=2),
        ],
        withBorder=True,
        p="md",
        radius="md",
        style={"width": "100%", "textAlign": "center"},
    )
