"""Tests for flow_props.profiles profile extraction."""

import numpy as np
import pytest
from cfd_io.dataset import Dataset, Field, StructuredGrid

from flow_props.profiles import (
    PROFILE_METHOD_WALL_NORMAL_INTERP,
    extract_profiles,
)


def _make_dataset(ni: int = 10, nj: int = 20) -> Dataset:
    """Build a minimal 2D structured Dataset for testing."""
    x = np.zeros((ni, nj, 1))
    y = np.zeros((ni, nj, 1))
    for i in range(ni):
        for j in range(nj):
            x[i, j, 0] = float(i)
            y[i, j, 0] = float(j) * 0.01  # small wall-normal spacing
    z = np.zeros_like(x)
    grid = StructuredGrid(x=x, y=y, z=z)

    uvel = np.zeros((ni, nj, 1))
    for j in range(nj):
        uvel[:, j, 0] = float(j) / nj  # linear velocity profile

    flow = {"uvel": Field(data=uvel, association="node")}
    return Dataset(grid=grid, flow=flow, attrs={"format": "test"})


def _make_skewed_dataset(ni: int = 12, nj: int = 20) -> Dataset:
    """Build a skewed structured Dataset with an analytic linear field."""
    x = np.zeros((ni, nj, 1))
    y = np.zeros((ni, nj, 1))
    for i in range(ni):
        for j in range(nj):
            x[i, j, 0] = float(i) + 0.2 * float(j)
            y[i, j, 0] = 0.01 * float(j)
    z = np.zeros_like(x)
    grid = StructuredGrid(x=x, y=y, z=z)

    uvel = np.zeros((ni, nj, 1))
    for i in range(ni):
        for j in range(nj):
            x_val = x[i, j, 0]
            y_val = y[i, j, 0]
            uvel[i, j, 0] = x_val + 2.0 * y_val

    flow = {"uvel": Field(data=uvel, association="node")}
    return Dataset(grid=grid, flow=flow, attrs={"format": "test"})


def _make_rotated_vector_dataset(ni: int = 12, nj: int = 20, angle_deg: float = 35.0) -> Dataset:
    """Build a rotated orthogonal Dataset with known tangential and normal velocity."""
    # build a straight wall with a constant local basis at the chosen angle
    angle_rad = np.deg2rad(angle_deg)
    tangent = np.array([np.cos(angle_rad), np.sin(angle_rad)], dtype=float)
    normal = np.array([-np.sin(angle_rad), np.cos(angle_rad)], dtype=float)

    streamwise_spacing = 1.0
    normal_spacing = 0.01

    x = np.zeros((ni, nj, 1))
    y = np.zeros((ni, nj, 1))
    uvel = np.zeros((ni, nj, 1))
    vvel = np.zeros((ni, nj, 1))

    for i in range(ni):
        for j in range(nj):
            eta_value = normal_spacing * float(j)

            # build rotated grid coordinates from the local tangent and normal basis
            position = float(i) * streamwise_spacing * tangent + eta_value * normal
            x[i, j, 0] = position[0]
            y[i, j, 0] = position[1]

            # build a velocity field with known local tangential and normal components
            u_tangent = 1.0 + 2.0 * eta_value
            u_normal = -0.5 * eta_value
            velocity = u_tangent * tangent + u_normal * normal
            uvel[i, j, 0] = velocity[0]
            vvel[i, j, 0] = velocity[1]

    z = np.zeros_like(x)
    grid = StructuredGrid(x=x, y=y, z=z)
    flow = {
        "uvel": Field(data=uvel, association="node"),
        "vvel": Field(data=vvel, association="node"),
    }
    return Dataset(grid=grid, flow=flow, attrs={"format": "test"})


def test_extract_profiles_single_station():
    ds = _make_dataset(ni=10, nj=20)
    profs = extract_profiles(ds, stations=[5])
    assert len(profs) == 1
    prof = profs[0]
    assert "x" in prof
    assert "y" in prof
    assert "eta" in prof
    assert "uvel" in prof
    assert prof["eta"][0] == 0.0
    assert len(prof["eta"]) == 20


def test_extract_profiles_multiple_stations():
    ds = _make_dataset(ni=10, nj=20)
    profs = extract_profiles(ds, stations=[0, 3, 9])
    assert len(profs) == 3


def test_extract_profiles_wall_normal_matches_grid_line_on_orthogonal_grid():
    ds = _make_dataset(ni=10, nj=20)
    profs = extract_profiles(
        ds,
        stations=[5],
        method=PROFILE_METHOD_WALL_NORMAL_INTERP,
        n_eta=20,
        eta_max=0.19,
    )
    prof = profs[0]

    np.testing.assert_allclose(prof["x"], np.full(20, 5.0), atol=1.0e-12)
    np.testing.assert_allclose(prof["y"], np.linspace(0.0, 0.19, 20), atol=1.0e-12)
    np.testing.assert_allclose(prof["eta"], np.linspace(0.0, 0.19, 20), atol=1.0e-12)
    np.testing.assert_allclose(prof["uvel"], np.linspace(0.0, 19.0 / 20.0, 20), atol=1.0e-12)


def test_extract_profiles_wall_normal_interpolates_skewed_grid_field():
    ds = _make_skewed_dataset()
    profs = extract_profiles(
        ds,
        stations=[5],
        method=PROFILE_METHOD_WALL_NORMAL_INTERP,
        n_eta=20,
        eta_max=0.19,
    )
    prof = profs[0]

    np.testing.assert_allclose(prof["x"], np.full(len(prof["x"]), 5.0), atol=5.0e-10)
    np.testing.assert_allclose(prof["y"], prof["eta"], atol=5.0e-10)
    np.testing.assert_allclose(prof["uvel"], prof["x"] + 2.0 * prof["y"], atol=5.0e-8)


def test_extract_profiles_grid_line_rotates_velocity_components():
    ds = _make_rotated_vector_dataset()
    prof = extract_profiles(ds, stations=[5])[0]

    expected_eta = np.linspace(0.0, 0.19, 20)
    expected_u_tangent = 1.0 + 2.0 * expected_eta
    expected_u_normal = -0.5 * expected_eta

    np.testing.assert_allclose(prof["eta"], expected_eta, atol=1.0e-12)
    np.testing.assert_allclose(prof["u_tangent"], expected_u_tangent, atol=1.0e-12)
    np.testing.assert_allclose(prof["u_normal"], expected_u_normal, atol=1.0e-12)


def test_extract_profiles_wall_normal_rotates_velocity_components():
    ds = _make_rotated_vector_dataset()
    prof = extract_profiles(
        ds,
        stations=[5],
        method=PROFILE_METHOD_WALL_NORMAL_INTERP,
        n_eta=20,
        eta_max=0.19,
    )[0]

    expected_eta = np.linspace(0.0, 0.19, 20)
    expected_u_tangent = 1.0 + 2.0 * expected_eta
    expected_u_normal = -0.5 * expected_eta

    np.testing.assert_allclose(prof["eta"], expected_eta, atol=1.0e-10)
    np.testing.assert_allclose(prof["u_tangent"], expected_u_tangent, atol=5.0e-8)
    np.testing.assert_allclose(prof["u_normal"], expected_u_normal, atol=5.0e-8)


def test_extract_profiles_bad_station():
    ds = _make_dataset(ni=10, nj=20)
    with pytest.raises(IndexError):
        extract_profiles(ds, stations=[99])


def test_extract_profiles_requires_structured():
    """Should raise TypeError for non-structured grids."""
    # pass an object that is not a StructuredGrid
    ds = Dataset(grid=None, flow={}, attrs={})
    with pytest.raises(TypeError):
        extract_profiles(ds, stations=[0])
