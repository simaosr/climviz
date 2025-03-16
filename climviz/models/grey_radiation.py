from functools import lru_cache
from pathlib import Path
import numpy as np
import xarray as xr
from numpy import cos, deg2rad
import climlab
import plotly.graph_objects as go


def grey_radiation(
    n_layers: int = 1,
) -> climlab.GreyRadiationModel:
    model = climlab.GreyRadiationModel(num_levels=n_layers)
    return model


def zstar(lev):
    return -np.log(lev / climlab.constants.ps)


@lru_cache
def get_ncep_data():
    ## The NOAA ESRL server is shutdown! January 2019
    ## This will try to read the data over the internet.
    ncep_filename = "air.mon.1981-2010.ltm.nc"
    ##  to read over internet
    ncep_url = "https://psl.noaa.gov/thredds/fileServer/Datasets/ncep.reanalysis.derived/pressure/"
    path = ncep_url

    path = Path(__file__).parent.parent / "data"

    ##  Open handle to data
    ncep_air = xr.open_dataset(path / ncep_filename, decode_times=False)
    ncep_air = ncep_air.rename({"lev": "level"})
    return ncep_air


def plotly_plot_soundings(
    result_list, name_list, plot_obs=False, fixed_range=True, show: bool = False
):
    fig = go.Figure()
    if plot_obs:
        ncep_air = get_ncep_data()
        #  Take global, annual average and convert to Kelvin
        weight = cos(deg2rad(ncep_air.lat)) / cos(deg2rad(ncep_air.lat)).mean(dim="lat")
        Tglobal = (ncep_air.air * weight).mean(dim=("lat", "lon", "time"))

        fig.add_trace(
            go.Scatter(x=Tglobal, y=zstar(Tglobal.level), mode="lines", name="Observed")
        )
    for i, state in enumerate(result_list):
        Tatm = state["Tatm"]
        lev = Tatm.domain.axes["lev"].points
        Ts = state["Ts"]
        fig.add_trace(go.Scatter(x=Tatm, y=zstar(lev), mode="lines", name=name_list[i]))
        fig.add_trace(go.Scatter(x=Ts, y=[0.0], mode="markers", name=name_list[i]))
    fig.update_layout(
        xaxis_title="Temperature (K)",
        yaxis_title="Pressure (hPa)",
        legend_title="Legend",
    )

    if show:
        fig.show()

    return fig


if __name__ == "__main__":
    # Create a model
    model = grey_radiation()

    model.integrate_converge(verbose=True)
    model.do_diagnostics()
    result = model.state

    # Plot the result
    plotly_plot_soundings([result], ["Grey Radiation Model"], plot_obs=True, show=True)
