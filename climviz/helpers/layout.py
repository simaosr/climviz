from dash import dcc
from dash import html
import dash_mantine_components as dmc


def create_grid(columns_dict: list[dict], grid_options: dict | None = None) -> dmc.Grid:
    if grid_options is None:
        grid_options = {}

    layout = dmc.Grid(
        children=[
            dmc.GridCol(col["content"], span=col["size"], **col.get("options", {}))
            for col in columns_dict
        ],
        **grid_options,
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
    return ["Footer"]


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
                    mt="md",
                    **content.get("extra_panel_args", {}),
                )
                for val, (name, content) in enumerate(content_dict.items())
            ],
        ],
        value=value,
        id=id,
    )


def div_in_card(
    id: str,
    div_options: dict | None = None,
    card_options: dict | None = None,
):
    default_card_options = {
        "withBorder": True,
        "shadow": "sm",
        "radius": "md",
        "padding": 0,
    }

    if div_options is None:
        div_options = {}

    if card_options is None:
        card_options = {}

    card_options = {**default_card_options, **div_options}

    return dmc.Card(
        children=[html.Div(id=id, **div_options)],
        **card_options,
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


def make_indicator_card(
    indicator: float, title: str, unit: str, hover_text: str | None = None
) -> dmc.Card:
    if indicator > 0.0:
        color = "green"
        # arrow up icon
        symbol = "↑"
    elif indicator == 0.0:
        color = "blue"
        symbol = "↔"
    else:
        color = "red"
        symbol = "↓"

    title_text = dmc.Text(title, size="xl")
    if hover_text is not None:
        title_text = dmc.Group(
            [
                title_text,
                dmc.HoverCard(
                    withArrow=True,
                    width=200,
                    children=[
                        dmc.HoverCardTarget("ⓘ"),
                        dmc.HoverCardDropdown(
                            dmc.Text(
                                hover_text,
                                size="sm",
                            )
                        ),
                    ],
                    position="top",
                ),
            ]
        )

    output = dmc.Card(
        children=[
            dmc.CardSection(
                dmc.Center(title_text),
            ),
            dmc.Group(
                [
                    dmc.Title(
                        f"{symbol} {abs(indicator):.2f} {unit}",
                        order=1,
                        c=color,
                    ),
                ],
                mt="md",
                justify="center",
            ),
        ],
        withBorder=True,
        shadow="sm",
        radius="md",
    )

    return output


def make_home_card(
    title: str, description: str, href: str, image: dmc.Image | None = None
) -> dmc.Card:
    return dmc.Card(
        children=[
            dmc.CardSection(image),
            dmc.Group(
                [
                    dmc.Text(title, fw=500),
                    # dmc.Badge("On Sale", color="pink"),
                ],
                justify="space-between",
                mt="md",
                mb="xs",
            ),
            dmc.Text(
                description,
                size="sm",
                c="dimmed",
            ),
            dmc.Button(
                html.A(dmc.Text("Go to model"), href=href),
                color="blue",
                fullWidth=True,
                mt="md",
                radius="md",
            ),
        ],
        withBorder=True,
        shadow="sm",
        radius="md",
        w=350,
    )
