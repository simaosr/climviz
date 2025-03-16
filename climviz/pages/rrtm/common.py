from climviz.components.div_based import CustomMantineNumberInput
from climviz.helpers.utils import make_page_id_func

PAGE_NAME = "RRTM"
PAGE_DESC = "Radiative Transfer Model (RRTM) for Earth's atmosphere"
PAGE_IMG = "image_rrtm.png"
id_func = make_page_id_func(PAGE_NAME)

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
        store_id=id_func("rrtm-options"),
    )
