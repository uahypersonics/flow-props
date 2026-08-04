"""Geometry helpers for profile extraction."""

from __future__ import annotations

import numpy as np
from cfd_io.dataset import StructuredGrid

# --------------------------------------------------
# path helpers
# --------------------------------------------------


def build_eta_from_path(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Build cumulative wall-normal distance from a polyline path."""
    dx = np.diff(x, prepend=x[0])
    dy = np.diff(y, prepend=y[0])
    ds_local = np.sqrt(dx**2 + dy**2)
    eta = np.cumsum(ds_local)
    eta[0] = 0.0
    return eta


def compute_wall_basis(grid: StructuredGrid, station: int) -> tuple[np.ndarray, np.ndarray]:
    """Compute the local wall tangent and inward-pointing normal.

    Args:
        grid: Structured surface grid.
        station: Wall station index in the streamwise direction.

    Returns:
        Tuple ``(tangent, normal)`` of unit vectors.
    """
    ni = grid.shape[0]

    # build a wall tangent from neighboring wall nodes
    if station == 0:
        tangent = np.array(
            [grid.x[1, 0, 0] - grid.x[0, 0, 0], grid.y[1, 0, 0] - grid.y[0, 0, 0]],
            dtype=float,
        )
    elif station == ni - 1:
        tangent = np.array(
            [
                grid.x[ni - 1, 0, 0] - grid.x[ni - 2, 0, 0],
                grid.y[ni - 1, 0, 0] - grid.y[ni - 2, 0, 0],
            ],
            dtype=float,
        )
    else:
        tangent = np.array(
            [
                grid.x[station + 1, 0, 0] - grid.x[station - 1, 0, 0],
                grid.y[station + 1, 0, 0] - grid.y[station - 1, 0, 0],
            ],
            dtype=float,
        )

    # normalize the wall tangent before constructing the local basis
    tangent_norm = np.linalg.norm(tangent)
    if tangent_norm == 0.0:
        raise ValueError(f"cannot build wall tangent at station {station}")
    tangent /= tangent_norm

    # rotate tangent by 90 degrees to get a candidate normal
    normal = np.array([-tangent[1], tangent[0]], dtype=float)

    # orient the normal toward the interior using the first off-wall point
    interior = np.array(
        [grid.x[station, 1, 0] - grid.x[station, 0, 0], grid.y[station, 1, 0] - grid.y[station, 0, 0]],
        dtype=float,
    )
    if np.dot(normal, interior) < 0.0:
        normal *= -1.0

    return tangent, normal


# --------------------------------------------------
# basis helpers
# --------------------------------------------------


def compute_wall_normal(grid: StructuredGrid, station: int) -> np.ndarray:
    """Compute an inward-pointing wall normal at one station."""
    _, normal = compute_wall_basis(grid, station)
    return normal


def add_rotated_velocity_components(
    profile: dict[str, np.ndarray],
    tangent: np.ndarray,
    normal: np.ndarray,
) -> None:
    """Add local tangential and normal velocity components when possible.

    Args:
        profile: Extracted profile data.
        tangent: Unit wall-tangent vector.
        normal: Unit wall-normal vector.
    """
    # check whether one supported in-plane velocity pair is available
    velocity_pair = _find_velocity_component_pair(profile)
    if velocity_pair is None:
        return

    # project the Cartesian in-plane velocity onto the local wall basis
    streamwise_name, wall_normal_name = velocity_pair
    velocity_x = np.asarray(profile[streamwise_name], dtype=float)
    velocity_y = np.asarray(profile[wall_normal_name], dtype=float)
    profile["u_tangent"] = velocity_x * tangent[0] + velocity_y * tangent[1]
    profile["u_normal"] = velocity_x * normal[0] + velocity_y * normal[1]


def _find_velocity_component_pair(profile: dict[str, np.ndarray]) -> tuple[str, str] | None:
    """Return the first recognized in-plane velocity component pair."""
    candidate_pairs = (
        ("uvel", "vvel"),
        ("u", "v"),
        ("velx", "vely"),
        ("velocity_x", "velocity_y"),
    )

    # search common CFD naming conventions in order
    for x_name, y_name in candidate_pairs:
        if x_name in profile and y_name in profile:
            return x_name, y_name

    return None
