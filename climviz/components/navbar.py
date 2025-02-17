import dash_mantine_components as dmc
from dash import dcc, html
from dash_iconify import DashIconify
import dash
from dash.dependencies import Input, Output


def unique_list(i_list):
    # initialize a null list
    u_list = []

    # traverse for all elements
    for x in i_list:
        # check if exists in unique_list or not
        if x not in u_list:
            u_list.append(x)
    return u_list


class Navbar:
    def __init__(
        self,
        i_report_parts,
        i_icons,
        i_report_name,
        i_report_logo,
        i_report_bug=None,
    ):
        self.i_report_parts = i_report_parts
        standalone_links = []
        for x in i_report_parts:
            try:
                i_report_parts[x]["navbar_menu"]
            except KeyError:
                standalone_links.append(x)
        self.standalone_links = standalone_links

        nav_tree = {}
        for x in unique_list(
            i_report_parts[x]["navbar_menu"]
            for x in i_report_parts
            if x not in standalone_links
        ):
            submenus = []
            for rep in i_report_parts:
                try:
                    if i_report_parts[rep]["navbar_menu"] == x:
                        try:
                            submenus.append(i_report_parts[rep]["navbar_submenu"])
                        except KeyError:
                            submenus.append("not_defined")
                            self.i_report_parts[rep]["navbar_submenu"] = "not_defined"
                except KeyError:
                    pass
            nav_tree[x] = unique_list(submenus)
        self.nav_tree = nav_tree
        self.i_icons = i_icons
        self.i_report_name = i_report_name
        self.i_report_logo = i_report_logo
        self.i_report_bug = i_report_bug

    def create_menu_target(self, name, href=None):
        try:
            if self.i_icons[name]:
                out = dmc.NavLink(
                    label=name,
                    href=href,
                    icon=DashIconify(icon=self.i_icons[name], width=17, color="grey"),
                    style={"padding": "7px", "width": "auto"},
                    styles={
                        "icon": {"margin-right": "3px"},
                        "label": {
                            "color": "grey",
                            "font-weight": "500",
                            "font-size": "16px",
                        },
                    },
                )
        except KeyError:
            out = dmc.NavLink(
                label=name,
                href=href,
                style={"padding": "7px", "width": "auto"},
                styles={
                    "icon": {"margin-right": "3px"},
                    "label": {
                        "color": "grey",
                        "font-weight": "500",
                        "font-size": "16px",
                    },
                },
            )
        return out

    def create_menu_item(self, name, href):
        try:
            if self.i_icons[name]:
                out = dmc.MenuItem(
                    name,
                    href=href,
                    icon=DashIconify(icon=self.i_icons[name]),
                )
        except KeyError:
            out = dmc.MenuItem(name, href=href)
        return out

    def create_links(self):
        links = []
        for menu in self.nav_tree:
            dropdown = []
            for submenu in self.nav_tree[menu]:
                if not ((submenu == "not_defined") & (len(self.nav_tree[menu]) == 1)):
                    try:
                        if self.i_icons[submenu]:
                            dropdown.append(
                                dmc.MenuLabel(
                                    dmc.Group(
                                        [
                                            DashIconify(
                                                icon=self.i_icons[submenu],
                                                width=13,
                                                color="grey",
                                            ),
                                            dmc.Text(
                                                "Other"
                                                if submenu == "not_defined"
                                                else submenu
                                            ),
                                        ],
                                        spacing=2,
                                    )
                                )
                            )
                    except KeyError:
                        dropdown.append(
                            dmc.MenuLabel(
                                "Other" if submenu == "not_defined" else submenu
                            )
                        )
                dropdown.extend(
                    [
                        self.create_menu_item(
                            name=self.i_report_parts[rep]["label"], href=rep
                        )
                        for rep in [
                            x
                            for x in self.i_report_parts
                            if x not in self.standalone_links
                        ]
                        if (
                            (self.i_report_parts[rep]["navbar_menu"] == menu)
                            & (self.i_report_parts[rep]["navbar_submenu"] == submenu)
                        )
                    ]
                )
            links.append(
                dmc.Menu(
                    [
                        dmc.MenuTarget(self.create_menu_target(menu)),
                        dmc.MenuDropdown(dropdown),
                    ],
                    trigger="hover",
                    offset=0,
                    transition="scale",
                    transitionDuration=150,
                )
            )
        for single in self.standalone_links:
            links.append(
                self.create_menu_target(
                    name=self.i_report_parts[single]["label"], href=single
                )
            )
        return dmc.Group(links, spacing=5)

    def create_navbar(self):
        if self.i_report_bug is not None:
            bug_report = dcc.Link(
                dmc.Tooltip(
                    dmc.ActionIcon(
                        DashIconify(
                            icon="material-symbols:bug-report-outline",
                            width=25,
                        ),
                        n_clicks=0,
                    ),
                    label="Report Issue",
                    withArrow=True,
                    arrowSize=3,
                    openDelay=500,
                    position="bottom",
                    transitionProps={
                        "transition": "scale",
                        "duration": 150,
                        "timingFunction": "ease",
                    },
                ),
                href=self.i_report_bug,
                target="_blank",
            )
        else:
            bug_report = html.Div()
        return dmc.Header(
            height=40,
            children=[
                dmc.Grid(
                    [
                        dmc.Col(
                            [
                                dmc.Group(
                                    [
                                        dcc.Link(
                                            dmc.Avatar(
                                                DashIconify(
                                                    icon=self.i_report_logo, height=35
                                                ),
                                                radius="sm",
                                                size=30,
                                                styles={
                                                    "placeholder": {
                                                        "background-color": "#fee600"
                                                    }
                                                },
                                            ),
                                            href="/",
                                        ),
                                        dmc.Anchor(
                                            self.i_report_name,
                                            size=24,
                                            style={
                                                "margin": "0px",
                                                "padding": "0px",
                                                "font-weight": "500",
                                                "color": "black",
                                            },
                                            href="/",
                                            underline=False,
                                        ),
                                    ],
                                    spacing=5,
                                    style={"margin-left": "2vh"},
                                )
                            ],
                            style={"margin": "0px", "padding": "0px"},
                            span="content",
                        ),
                        dmc.Col([], span=1),
                        dmc.Col(
                            [self.create_links()],
                            span="content",
                            style={"margin": "0px", "padding": "0px"},
                        ),
                        dmc.Col(
                            [
                                dmc.Grid(
                                    [
                                        dmc.Col(
                                            [dmc.Group([bug_report])],
                                            span="content",
                                            style={
                                                "padding": "0px",
                                                "margin-right": "2vh",
                                            },
                                        )
                                    ],
                                    justify="flex-end",
                                )
                            ],
                            span="auto",
                        ),
                    ],
                    align="center",
                    style={"margin": "0px", "padding": "0px"},
                    columns=24,
                )
            ],
            style={"margin-bottom": "3px"},
        )
