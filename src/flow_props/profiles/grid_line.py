"""Grid-line profile extraction."""

from __future__ import annotations

import numpy as np
from cfd_io.dataset import Dataset

from flow_props.profiles.geometry import (
    add_rotated_velocity_components,
    build_eta_from_path,
    compute_wall_basis,
)


def extract_profiles_grid_line(
    ds: Dataset,
    stations: list[int],
) -> list[dict[str, np.ndarray]]:
    """Extract profiles by following existing grid lines."""
    ni = ds.grid.shape[0]
    nj = ds.grid.shape[1]

    results: list[dict[str, np.ndarray]] = []
    for station in stations:
        # check station bounds
        if station < 0 or station >= ni:
            raise IndexError(f"station i={station} out of range [0, {ni})")

        # build the local wall basis used for component rotation
        tangent, normal = compute_wall_basis(ds.grid, station)

        # extract grid coordinates along the wall-normal line
        x = ds.grid.x[station, :nj, 0]
        y = ds.grid.y[station, :nj, 0]

        # build wall-normal distance from cumulative arc length
        eta = build_eta_from_path(x, y)

        # build profile container
        profile: dict[str, np.ndarray] = {"x": x, "y": y, "eta": eta}

        # copy all flow variables on this wall-normal line
        for name, field in ds.flow.items():
            profile[name] = field.data[station, :nj, 0]

        # add local tangential and normal velocity components when available
        add_rotated_velocity_components(profile, tangent, normal)

        results.append(profile)

    return results
