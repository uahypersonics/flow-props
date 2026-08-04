"""Public profile extraction API."""

from __future__ import annotations

import numpy as np
from cfd_io.dataset import Dataset, StructuredGrid

from flow_props.profiles.grid_line import extract_profiles_grid_line
from flow_props.profiles.wall_normal import extract_profiles_wall_normal_interp

# --------------------------------------------------
# public configuration template
# --------------------------------------------------

PROFILE_METHOD_GRID_LINE = "grid_line"
PROFILE_METHOD_WALL_NORMAL_INTERP = "wall_normal_interp"

TEMPLATE = """\
[profiles]
method = "grid_line"          # grid_line | wall_normal_interp

# station selection: pick exactly ONE of the three modes below
# mode 1 (default): wall x-coordinate range (inclusive start/end, positive step)
x_s = 0.05
x_e = 0.50
dx = 0.05

# mode 2: i-index range (inclusive start/end, positive step)
# i_s = 10
# i_e = 100
# di = 10

# mode 3: explicit list of i-station indices
# stations = [10, 50, 100]

n_eta = 0                       # samples for wall_normal_interp (0 = use full grid-line count)
eta_max = 0.0                   # max wall-normal distance for wall_normal_interp (0 = use full grid-line extent)
output = "profiles.dat"         # output file (.dat or .json)
"""


# --------------------------------------------------
# public API
# --------------------------------------------------


def extract_profiles(
    ds: Dataset,
    stations: list[int],
    method: str = PROFILE_METHOD_GRID_LINE,
    n_eta: int | None = None,
    eta_max: float | None = None,
) -> list[dict[str, np.ndarray]]:
    """Extract wall-normal profiles at specified i-stations."""
    # validate inputs
    if not isinstance(ds.grid, StructuredGrid):
        raise TypeError("extract_profiles requires a StructuredGrid")

    # dispatch to the requested extraction method
    if method == PROFILE_METHOD_GRID_LINE:
        return extract_profiles_grid_line(ds, stations)
    if method == PROFILE_METHOD_WALL_NORMAL_INTERP:
        return extract_profiles_wall_normal_interp(ds, stations, n_eta, eta_max)

    raise ValueError(f"unsupported profile extraction method: {method}")
