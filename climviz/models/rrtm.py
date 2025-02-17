# %%
#
import climlab
import matplotlib.pyplot as plt
import numpy as np
import scipy
import scipy.integrate as sp
import xarray as xr
from climlab.utils.thermo import pseudoadiabat

from pydantic import BaseModel
from pydantic import Field

import plotly.graph_objects as go


class RRTMModelOptions(BaseModel):
    """
    Options for the RRTM model
    """

    # Set the relative humidity (with max and min values)
    rel_humidity: float = Field(default=0.8, ge=0.0, le=1.0)
    # Set the stratospheric temperature
    strat_temperature: float = 195.0
    # Set the minimum specific humidity
    min_spec_humid: float = 5e-06
    # set the surface temperature
    surf_temperature: float = Field(default=280.0, ge=200.0, le=320.0)
    # concentrations of various gases
    absorver_vmr: dict = {
        "CO2": 0.0,
        "CH4": 0.0,
        "N2O": 0.0,
        "O2": 0.0,
        "CFC11": 0.0,
        "CFC12": 0.0,
        "CFC22": 0.0,
        "CCL4": 0.0,
        "O3": 0.0,
    }

    class Config:
        extra = "forbid"


# %%


def convert_pressure_to_altitude(pressure, Tstrat=200):
    """
    Convert pressure to altitude using the hypsometric equation.
    """
    R = 287.0
    g = 9.8
    Z = -Tstrat * R / g * np.log(pressure / 1013.0)
    return Z


def generate_idealized_temp_profile(SST, plevs, Tstrat=190):
    """
    Generate an idealized temperature profile with specified SST and Tstrat.
    """
    solution = sp.odeint(pseudoadiabat, SST, np.flip(plevs))
    temp = solution.reshape(-1)
    temp[np.where(temp < Tstrat)] = Tstrat
    return np.flip(temp)  # need to re-invert the pressure axis


def make_idealized_column(SST, num_lev=100, Tstrat=195):
    # Set up a column state
    state = climlab.column_state(num_lev=num_lev, num_lat=1)
    # Extract the pressure levels
    plevs = state["Tatm"].domain.axes["lev"].points
    # Set the SST
    state["Ts"][:] = SST
    # Set the atmospheric profile to be our idealized profile
    state["Tatm"][:] = generate_idealized_temp_profile(
        SST=SST, plevs=plevs, Tstrat=Tstrat
    )
    return state


def find_equilibrium_surface_temperature(
    absorber_vmr: dict,
    Tstrat: float = 195.0,
    rel_humidity: float = 0.8,
    options_dict: dict | None = None,
):
    def obj(Ts):
        state, h2o, rad = calc_olr(Ts, absorber_vmr, RH=rel_humidity, Tstrat=Tstrat)
        net_flux = rad.ASR - rad.OLR
        return net_flux[0]

    Ts_eq = scipy.optimize.root_scalar(obj, x0=275.0, bracket=[250, 300]).root

    return Ts_eq


def calc_olr(
    SST,
    absorber_vmr,
    return_spectral_olr=False,
    RH=0.8,
    Tstrat=195,
    qStrat=5e-06,
):
    #  Couple water vapor to radiation
    ## climlab setup
    # create surface and atmosperic domains
    state = make_idealized_column(SST, Tstrat=Tstrat)
    # state = create_simple_column(num_lev=30, surface_temp=SST, t_strat=Tstrat)

    #  fixed relative humidity
    #  Note we pass the qStrat parameter here, which sets a minimum specific humidity
    #  Set RH=0. and qStrat=0. for fully dry column
    h2o = climlab.radiation.water_vapor.FixedRelativeHumidity(
        state=state,
        relative_humidity=RH,
        qStrat=qStrat,
    )

    rad = climlab.radiation.rrtm.RRTMG(
        state=state,
        specific_humidity=h2o.q,
        icld=0,  # Clear-sky only!
        return_spectral_olr=return_spectral_olr,
        absorber_vmr=absorber_vmr,
    )
    rad.compute_diagnostics()

    net_flux = rad.ASR - rad.OLR
    # print(f"Ts: {SST}, net_flux: {net_flux[0]} (ASR: {rad.ASR}, OLR: {rad.OLR})")
    # print(f"{RH=}")
    # print(f"{Tstrat=}")
    # print(f"{absorber_vmr=}")

    return state, h2o, rad


absorber_vmr = {
    "CO2": 0.0,
    "CH4": 0.0,
    "N2O": 0.0,
    "O2": 0.0,
    "CFC11": 0.0,
    "CFC12": 0.0,
    "CFC22": 0.0,
    "CCL4": 0.0,
    "O3": 0.0,
}


def make_fig_atm_profile(state):
    # Convert state to xarray
    state_xr = state["Tatm"].to_xarray()

    # convert pressure to altitude
    altitude = convert_pressure_to_altitude(state_xr["lev"]) / 1000.0

    fig = go.Figure(
        go.Scatter(
            x=state_xr,
            y=altitude,
            mode="lines",
            name="Temperature",
            line=dict(color="blue"),
        ),
        layout=go.Layout(
            title="Temperature Profile",
            xaxis=dict(title="Temperature (K)"),
            yaxis=dict(title="Altitude (km)"),
        ),
    ).update_xaxes(range=[170, 310])

    return fig


def make_fig_rad_profile(state, rad):
    # Convert state to xarray
    state_xr = state["Tatm"].to_xarray()

    # convert pressure to altitude
    altitude = convert_pressure_to_altitude(state_xr["lev"]) / 1000.0

    # Plot radiation profile
    fig2 = go.Figure(
        layout=go.Layout(
            title="Radiation Profile",
            xaxis=dict(title="Radiation (W/m^2)"),
            yaxis=dict(title="Altitude (km)"),
        ),
    ).update_xaxes(range=[-600, 600])

    for values, label in zip(
        [
            rad.LW_flux_up,
            rad.SW_flux_up,
        ],
        [
            "LW Flux Up",
            "SW Flux Up",
        ],
    ):
        fig2.add_trace(
            go.Scatter(
                x=values,
                y=altitude,
                mode="lines",
                name=label,
            )
        )

    for values, label in zip(
        [
            -rad.LW_flux_down,
            -rad.SW_flux_down,
        ],
        [
            "LW Flux Down",
            "SW Flux Down",
        ],
    ):
        fig2.add_trace(
            go.Scatter(
                x=values,
                y=altitude,
                mode="lines",
                name=label,
            )
        )

    return fig2


if __name__ == "__main__":
    # %%
    state = make_idealized_column(300)

    # Plot the profile
    fig, ax = plt.subplots(dpi=100)
    state["Tatm"].to_xarray().plot(ax=ax, y="lev", yincrease=False)
    ax.set_xlabel("Temperature (K)")
    ax.set_ylabel("Pressure (hPa)")
    ax.grid()

    # Plot the profile
    fig, ax = plt.subplots(dpi=100)
    state["Tatm"].to_xarray().plot(ax=ax, y="lev", yincrease=False)
    ax.set_xlabel("Temperature (K)")
    ax.set_ylabel("Altityde (km)")
    ax.grid()
    plt.show()

    n = 20

    OLRS = np.zeros((n, n))
    temparray = np.linspace(280, 290, n)
    co2array = np.linspace(280, 1200, n)

    for idx1, temp in enumerate(temparray):
        for idx2, co2 in enumerate(co2array):
            state, h2o, rad = calc_olr(temp, co2, absorber_vmr)

            OLRS[idx1, idx2] = rad.OLR

    # %%

    da = xr.DataArray(
        OLRS,
        dims=["temp", "co2"],
        coords={"temp": temparray, "co2": co2array},
    )

    fig, ax = plt.subplots(dpi=100)

    p = da.plot.contourf(ax=ax, cmap="viridis", levels=20, add_colorbar=False)

    fig.colorbar(p, label="OLR (W m$^{-2}$)")

    ax.set_xlabel("$CO_{2}$ (ppmv)")
    ax.set_ylabel("SST (K)")

    plt.show()

    # %%
