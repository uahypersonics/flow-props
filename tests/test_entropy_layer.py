"""Tests for flow_props.entropy_layer."""

import numpy as np
import pytest
from cfd_io.dataset import Dataset, Field, StructuredGrid

from flow_props.entropy_layer import (
    entropy_difference,
    entropy_layer_thickness,
    run_entropy,
)
from flow_props.profiles import PROFILE_METHOD_WALL_NORMAL_INTERP


def _make_entropy_dataset(ni: int = 5, nj: int = 21) -> Dataset:
    """Build a dataset with a controlled entropy profile."""
    x = np.zeros((ni, nj, 1))
    y = np.zeros((ni, nj, 1))
    for i in range(ni):
        for j in range(nj):
            x[i, j, 0] = float(i)
            y[i, j, 0] = float(j) / float(nj - 1)

    z = np.zeros_like(x)
    grid = StructuredGrid(x=x, y=y, z=z)

    eta = np.linspace(0.0, 1.0, nj)
    entropy_profile = 1.0 - eta
    pressure_profile = np.exp(-entropy_profile)
    temp_profile = np.ones_like(pressure_profile)

    pressure = np.zeros((ni, nj, 1))
    temp = np.zeros((ni, nj, 1))
    for j in range(nj):
        pressure[:, j, 0] = pressure_profile[j]
        temp[:, j, 0] = temp_profile[j]

    flow = {
        "pres": Field(data=pressure, association="node"),
        "temp": Field(data=temp, association="node"),
    }
    return Dataset(grid=grid, flow=flow, attrs={"format": "test"})


def test_entropy_difference_matches_reference_definition():
    temp = np.array([1.0, 1.0])
    pressure = np.array([np.exp(-1.0), 1.0])

    delta_s = entropy_difference(
        temp,
        pressure,
        temp_ref=1.0,
        pressure_ref=1.0,
        gamma=1.4,
        gas_constant=1.0,
    )

    np.testing.assert_allclose(delta_s, np.array([1.0, 0.0]), rtol=1e-12)


def test_entropy_layer_thickness_wall_fraction():
    eta = np.linspace(0.0, 1.0, 21)
    entropy_profile = 1.0 - eta
    pressure = np.exp(-entropy_profile)
    temp = np.ones_like(pressure)

    delta = entropy_layer_thickness(
        eta,
        temp,
        pressure,
        temp_ref=1.0,
        pressure_ref=1.0,
        threshold=0.25,
        gamma=1.4,
        gas_constant=1.0,
    )

    assert delta == pytest.approx(0.75, rel=1e-6)


def test_run_entropy_returns_station_results():
    ds = _make_entropy_dataset()

    results = run_entropy(
        ds,
        stations=[0, 3],
        threshold=0.25,
        gamma=1.4,
        gas_constant=1.0,
    )

    assert [item["station"] for item in results] == [0, 3]
    assert results[0]["delta_entropy"] == pytest.approx(0.75, rel=1e-6)


def test_run_entropy_accepts_wall_normal_interp_method():
    ds = _make_entropy_dataset()

    results = run_entropy(
        ds,
        stations=[0, 3],
        method=PROFILE_METHOD_WALL_NORMAL_INTERP,
        n_eta=21,
        eta_max=1.0,
        threshold=0.25,
        gamma=1.4,
        gas_constant=1.0,
    )

    assert [item["station"] for item in results] == [0, 3]
    assert results[0]["delta_entropy"] == pytest.approx(0.75, rel=1e-6)
