"""Tests for flow_props.wall wall quantities."""

import numpy as np
from cfd_io.dataset import Dataset, Field, StructuredGrid

from flow_props.wall import skin_friction, wall_heat_flux, wall_shear_stress


def _make_wall_dataset(ni: int = 20, nj: int = 30) -> Dataset:
    """Build a Dataset with a simple grid and linear velocity / temperature profiles."""
    dy = 0.001  # uniform wall-normal spacing
    x = np.zeros((ni, nj, 1))
    y = np.zeros((ni, nj, 1))
    for i in range(ni):
        for j in range(nj):
            x[i, j, 0] = float(i)
            y[i, j, 0] = float(j) * dy
    z = np.zeros_like(x)
    grid = StructuredGrid(x=x, y=y, z=z)

    # linear velocity: u = eta (slope = 1)
    uvel = np.zeros((ni, nj, 1))
    for j in range(nj):
        uvel[:, j, 0] = float(j) * dy

    # linear temperature: T = 300 + 1000 * eta
    temp = np.zeros((ni, nj, 1))
    for j in range(nj):
        temp[:, j, 0] = 300.0 + 1000.0 * float(j) * dy

    flow = {
        "uvel": Field(data=uvel, association="node"),
        "temp": Field(data=temp, association="node"),
    }
    return Dataset(grid=grid, flow=flow, attrs={"format": "test"})


def test_wall_shear_stress_shape():
    ds = _make_wall_dataset()
    tau = wall_shear_stress(ds, mu_wall=1e-5)
    assert tau.shape == (20,)


def test_wall_shear_stress_linear_profile():
    """For linear u = eta, du/deta = 1, so tau_w = mu * 1."""
    ds = _make_wall_dataset()
    mu = 1.0e-5
    tau = wall_shear_stress(ds, mu_wall=mu)
    # 2nd-order one-sided FD on a linear profile should be exact
    np.testing.assert_allclose(tau, mu, rtol=1e-6)


def test_skin_friction():
    ds = _make_wall_dataset()
    mu = 1e-5
    rho_inf = 1.0
    u_inf = 100.0
    cf = skin_friction(ds, mu, rho_inf, u_inf)
    expected_cf = mu / (0.5 * rho_inf * u_inf**2)
    np.testing.assert_allclose(cf, expected_cf, rtol=1e-6)


def test_wall_heat_flux_linear_temp():
    """For linear T profile with slope 1000, qw = -k * 1000."""
    ds = _make_wall_dataset()
    k = 0.025
    qw = wall_heat_flux(ds, k_wall=k)
    np.testing.assert_allclose(qw, -k * 1000.0, rtol=1e-6)
