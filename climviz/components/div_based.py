from typing import Callable
from dash import callback
from dash import html
from dash import Input
from dash import Output
from dash import State
import dash_mantine_components as dmc


class DivBasedComponent(html.Div):
    def __init__(
        self,
        children: list,
        callback_list: list,
        div_options: dict = None,
        update_function: Callable | None = None,
    ):
        if div_options is None:
            div_options = {}

        super().__init__(
            children,
            **div_options,
        )

        self.update_function = update_function
        self.callback_list = callback_list

        self.start_callback()

    def start_callback(self) -> None:
        if self.callback_list is not None and self.update_function is not None:
            callback(*self.callback_list, prevent_initial_call=True)(
                self.update_function
            )

    @property
    def update_function(self) -> Callable:
        return self._update_function

    @update_function.setter
    def update_function(self, func: Callable) -> None:
        if not isinstance(func, (Callable, None)):
            raise ValueError("Function must be a callable.")

        self._update_function = func

    @property
    def callback_list(self) -> list:
        return self._callback_list

    @callback_list.setter
    def callback_list(self, callback_list: list) -> None:
        if not isinstance(callback_list, (list, None)):
            raise ValueError("Callback list must be a list.")

        self._callback_list = callback_list


class SelectCompoment(DivBasedComponent):
    def __init__(
        self,
        id,
        select_data: dict,
        select_options: dict | None = None,
        div_options: dict | None = None,
        is_multi: bool = False,
    ):
        if select_options is None:
            select_options = {}

        if is_multi:
            select_func = dmc.Select
        else:
            select_func = dmc.MultiSelect

        children = [
            select_func(
                id=id,
                **select_data,
                label=select_data["label"],
                placeholder=select_data["placeholder"],
                value=select_data["value"],
                data=select_data["data"],
                w=select_options.pop("w", 200),
                mb=select_options.pop("mb", 10),
                **select_options,
            ),
        ]

        callback_list = None

        super().__init__(
            children=children, callback_list=callback_list, div_options=div_options
        )


class MultiSelectComponent(SelectCompoment):
    def __init__(
        self,
        id,
        select_data: dict,
        select_options: dict | None = None,
        div_options: dict | None = None,
    ):
        super().__init__(
            id=id,
            select_data=select_data,
            select_options=select_options,
            div_options=div_options,
            is_multi=True,
        )


class MantineComponent(DivBasedComponent):
    def __init__(
        self,
        mantine_component,
        callback_list: list,
        component_options: dict = None,
        div_options: dict = None,
        update_function: Callable | None = None,
    ):
        if component_options is None:
            component_options = {}

        wrapped_children = [mantine_component(**component_options)]

        super().__init__(
            children=wrapped_children,
            callback_list=callback_list,
            div_options=div_options,
            update_function=update_function,
        )


class CustomMantineNumberInput(MantineComponent):
    def __init__(
        self,
        id,
        label,
        value: float = 0.0,
        min: float = 0.0,
        max: float = 1e6,
        step: int = 1,
        size: str = "sm",
        store_id: str | None = None,
        custom_key: str | None = None,
        **kwargs,
    ):
        callback_list = [
            Output(store_id, "data", allow_duplicate=True),
            State(store_id, "data"),
            Input(id, "value"),
        ]

        self.id = id
        self.value = value
        self.min = min
        self.max = max
        self.label = label
        self.store_id = store_id
        self.custom_key = custom_key

        super().__init__(
            mantine_component=dmc.NumberInput,
            component_options={
                "id": id,
                "label": label,
                "value": value,
                "min": min,
                "max": max,
                "step": step,
                "size": size,
                **kwargs,
            },
            callback_list=callback_list,
            update_function=self._update_function,
        )

    def _update_function(self, state, value):
        """
        Update the state of the component.
        """
        if self.custom_key is None:
            if self.id not in state:
                state[self.id] = {
                    "value": value,
                    "min": self.min,
                    "max": self.max,
                }
            else:
                state[self.id]["value"] = value
        else:
            if self.custom_key not in state:
                state[self.custom_key] = {}

            if self.id not in state[self.custom_key]:
                state[self.custom_key][self.id] = {
                    "value": value,
                    "min": self.min,
                    "max": self.max,
                }
            else:
                state[self.custom_key][self.id]["value"] = value

        return state


def create_mantine_component(
    mantine_component,
    children: list,
    callback_list: list,
    component_options: dict = None,
    update_function: Callable | None = None,
):
    if component_options is None:
        component_options = {}

    component_instance = mantine_component(children=children, **component_options)

    if callback_list is not None and update_function is not None:
        callback(*callback_list)(update_function)

    return component_instance


# class SelectIndicatorCompoment(DivBasedComponent):
#     def __init__(
#         self,
#         id_func,
#         div_options=None,
#         label: str = "Color by",
#         id_label: str = "selection-color",
#         categories=None,
#     ):
#         children = [
#             dbc.Label(label),
#             dcc.Dropdown(
#                 [],
#                 "",
#                 id=id_func(id_label),
#                 multi=False,
#             ),
#         ]

#         callback_list = [
#             Output(id_func(id_label), "options"),
#             Output(id_func(id_label), "value"),
#             Input("store-data", "data"),
#             Input("url", "pathname"),
#         ]

#         if categories is None:
#             self.categories = [
#                 "variables",
#                 "objectives",
#                 "processed",
#                 "constraints",
#                 "observables",
#             ]
#         else:
#             self.categories = categories

#         super().__init__(children, callback_list, div_options)

#     def _update_function(self, stored_data, pathname):
#         if stored_data is not None:
#             selection_indicator = get_list_with_names_and_symbols(
#                 stored_data,
#                 self.categories,
#             )
#             return selection_indicator, ""

#         else:
#             return [], ""


# class SelectColorCompoment(DivBasedComponent):
#     def __init__(self, id_func, div_options=None, categories=None):
#         children = [
#             dbc.Label("Color by"),
#             dcc.Dropdown(
#                 [],
#                 "",
#                 id=id_func("selection-color"),
#                 multi=False,
#             ),
#         ]

#         callback_list = [
#             Output(id_func("selection-color"), "options"),
#             Output(id_func("selection-color"), "value"),
#             Input("store-data", "data"),
#             Input("url", "pathname"),
#         ]

#         if categories is None:
#             self.categories = [
#                 "variables",
#                 "objectives",
#                 "processed",
#                 "constraints",
#                 "observables",
#             ]
#         else:
#             self.categories = categories

#         super().__init__(children, callback_list, div_options)

#     def _update_function(self, stored_data, pathname):
#         if stored_data is not None:
#             selection_color = get_list_with_names_and_symbols(
#                 stored_data,
#                 self.categories,
#             )
#             return selection_color, ""

#         else:
#             return [], ""


# class SelectAxisComponent(DivBasedComponent):
#     def __init__(
#         self,
#         id_func,
#         axis_name: str = "x-axis",
#         axis_label: str = None,
#         categories=None,
#         div_options: dict = None,
#         default_index: int = 0,
#     ):
#         if axis_label is None:
#             axis_label = axis_name

#         self.default_index = default_index

#         id = id_func
#         children = [
#             dbc.Label(
#                 f"Select indicator ({axis_name})",
#                 html_for=f"crossfilter-{axis_label}-column",
#             ),
#             dcc.Dropdown(
#                 [],
#                 "",
#                 id=id(f"crossfilter-{axis_label}-column"),
#                 multi=False,
#                 clearable=False,
#             ),
#             dbc.RadioItems(
#                 options=[
#                     {"label": "Linear", "value": "Linear"},
#                     {"label": "Log", "value": "Log"},
#                 ],
#                 value="Linear",
#                 id=id(f"crossfilter-{axis_label}-type"),
#                 inline=True,
#             ),
#         ]
#         callback_list = [
#             Output(id(f"crossfilter-{axis_label}-column"), "options"),
#             Output(id(f"crossfilter-{axis_label}-column"), "value"),
#             Input("store-data", "data"),
#             Input("url", "pathname"),
#         ]

#         if categories is None:
#             self.categories = [
#                 "objectives",
#             ]
#         else:
#             self.categories = categories

#         super().__init__(children, callback_list, div_options)

#     def _update_function(self, stored_data, pathname):
#         if stored_data is not None:
#             selection = get_list_with_names_and_symbols(
#                 stored_data,
#                 self.categories,
#             )
#             return selection, selection[self.default_index]["value"]

#         else:
#             return [], ""
