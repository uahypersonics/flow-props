"""Wall-normal interpolated profile extraction."""

from __future__ import annotations

import numpy as np
from cfd_io.dataset import Dataset, StructuredGrid

from flow_props.profiles.geometry import (
    add_rotated_velocity_components,
    build_eta_from_path,
    compute_wall_basis,
)


def extract_profiles_wall_normal_interp(
    ds: Dataset,
    stations: list[int],
    n_eta: int | None,
    eta_max: float | None,
) -> list[dict[str, np.ndarray]]:
    """Extract profiles by interpolating along wall-normal rays."""
    # validate inputs
    if ds.grid.shape[2] != 1:
        raise ValueError("wall_normal_interp currently supports only nk=1 structured grids")

    ni = ds.grid.shape[0]
    nj = ds.grid.shape[1]

    # default interpolation count to the full grid-line count
    if n_eta is None or n_eta <= 0:
        n_eta = nj

    results: list[dict[str, np.ndarray]] = []
    for station in stations:
        # check station bounds
        if station < 0 or station >= ni:
            raise IndexError(f"station i={station} out of range [0, {ni})")

        # build a reference grid-line profile for distance defaults and wall values
        grid_x = ds.grid.x[station, :nj, 0]
        grid_y = ds.grid.y[station, :nj, 0]
        grid_eta = build_eta_from_path(grid_x, grid_y)

        # default interpolation extent to the full grid-line extent
        eta_limit = eta_max if eta_max is not None and eta_max > 0.0 else float(grid_eta[-1])
        eta_samples = np.linspace(0.0, eta_limit, n_eta)

        # build the wall basis from local wall geometry
        wall_point = np.array([ds.grid.x[station, 0, 0], ds.grid.y[station, 0, 0]], dtype=float)
        tangent, normal = compute_wall_basis(ds.grid, station)

        # initialize sample arrays with the wall point
        x_values = [float(wall_point[0])]
        y_values = [float(wall_point[1])]
        eta_values = [float(eta_samples[0])]
        flow_values: dict[str, list[float]] = {}
        for name, field in ds.flow.items():
            if field.association != "node":
                raise ValueError("wall_normal_interp currently supports node-associated fields only")
            flow_values[name] = [float(field.data[station, 0, 0])]

        # march outward along the wall normal and interpolate from nearby cells
        seed_i = min(station, ni - 2)
        seed_j = 0
        for eta_value in eta_samples[1:]:
            sample_point = wall_point + eta_value * normal
            cell_info = find_local_cell(ds.grid, sample_point[0], sample_point[1], seed_i, seed_j)

            if cell_info is None:
                break

            cell_i, cell_j, xi, eta_local = cell_info
            seed_i = cell_i
            seed_j = cell_j

            x_values.append(float(sample_point[0]))
            y_values.append(float(sample_point[1]))
            eta_values.append(float(eta_value))

            for name, field in ds.flow.items():
                sampled_value = bilinear_sample(field.data[:, :, 0], cell_i, cell_j, xi, eta_local)
                flow_values[name].append(float(sampled_value))

        # build profile container
        profile: dict[str, np.ndarray] = {
            "x": np.asarray(x_values, dtype=float),
            "y": np.asarray(y_values, dtype=float),
            "eta": np.asarray(eta_values, dtype=float),
        }
        for name, values in flow_values.items():
            profile[name] = np.asarray(values, dtype=float)

        # add local tangential and normal velocity components when available
        add_rotated_velocity_components(profile, tangent, normal)

        results.append(profile)

    return results


def find_local_cell(
    grid: StructuredGrid,
    x_point: float,
    y_point: float,
    seed_i: int,
    seed_j: int,
    max_radius: int = 3,
) -> tuple[int, int, float, float] | None:
    """Find a nearby grid cell that contains a sample point."""
    ni = grid.shape[0]
    nj = grid.shape[1]

    # search expanding neighborhoods around the current seed cell
    for radius in range(max_radius + 1):
        i_min = max(0, seed_i - radius)
        i_max = min(ni - 2, seed_i + radius)
        j_min = max(0, seed_j - radius)
        j_max = min(nj - 2, seed_j + radius)

        for cell_j in range(j_min, j_max + 1):
            for cell_i in range(i_min, i_max + 1):
                local_coords = invert_bilinear_cell(grid, cell_i, cell_j, x_point, y_point)
                if local_coords is None:
                    continue
                return cell_i, cell_j, local_coords[0], local_coords[1]

    return None


def invert_bilinear_cell(
    grid: StructuredGrid,
    cell_i: int,
    cell_j: int,
    x_point: float,
    y_point: float,
    max_iter: int = 12,
    tol: float = 1.0e-10,
) -> tuple[float, float] | None:
    """Invert the bilinear map for one structured cell."""
    p00 = np.array([grid.x[cell_i, cell_j, 0], grid.y[cell_i, cell_j, 0]], dtype=float)
    p10 = np.array([grid.x[cell_i + 1, cell_j, 0], grid.y[cell_i + 1, cell_j, 0]], dtype=float)
    p01 = np.array([grid.x[cell_i, cell_j + 1, 0], grid.y[cell_i, cell_j + 1, 0]], dtype=float)
    p11 = np.array([grid.x[cell_i + 1, cell_j + 1, 0], grid.y[cell_i + 1, cell_j + 1, 0]], dtype=float)

    # initialize at the cell center
    xi = 0.5
    eta = 0.5
    target = np.array([x_point, y_point], dtype=float)

    # solve the inverse bilinear map with Newton iterations
    for _ in range(max_iter):
        mapped = bilinear_point(p00, p10, p01, p11, xi, eta)
        residual = mapped - target
        if np.linalg.norm(residual) <= tol:
            break

        jacobian = bilinear_jacobian(p00, p10, p01, p11, xi, eta)
        determinant = jacobian[0, 0] * jacobian[1, 1] - jacobian[0, 1] * jacobian[1, 0]
        if abs(determinant) <= tol:
            return None

        delta = np.linalg.solve(jacobian, residual)
        xi -= float(delta[0])
        eta -= float(delta[1])

    # accept local coordinates that lie inside the cell with a small tolerance
    if -1.0e-8 <= xi <= 1.0 + 1.0e-8 and -1.0e-8 <= eta <= 1.0 + 1.0e-8:
        return min(max(xi, 0.0), 1.0), min(max(eta, 0.0), 1.0)

    return None


def bilinear_point(
    p00: np.ndarray,
    p10: np.ndarray,
    p01: np.ndarray,
    p11: np.ndarray,
    xi: float,
    eta: float,
) -> np.ndarray:
    """Evaluate the bilinear physical map at one local coordinate."""
    return (
        (1.0 - xi) * (1.0 - eta) * p00
        + xi * (1.0 - eta) * p10
        + (1.0 - xi) * eta * p01
        + xi * eta * p11
    )


def bilinear_jacobian(
    p00: np.ndarray,
    p10: np.ndarray,
    p01: np.ndarray,
    p11: np.ndarray,
    xi: float,
    eta: float,
) -> np.ndarray:
    """Evaluate the bilinear map Jacobian at one local coordinate."""
    d_dxi = (1.0 - eta) * (p10 - p00) + eta * (p11 - p01)
    d_deta = (1.0 - xi) * (p01 - p00) + xi * (p11 - p10)
    return np.column_stack((d_dxi, d_deta))


def bilinear_sample(
    field: np.ndarray,
    cell_i: int,
    cell_j: int,
    xi: float,
    eta: float,
) -> float:
    """Sample one nodal field inside a structured cell."""
    value00 = float(field[cell_i, cell_j])
    value10 = float(field[cell_i + 1, cell_j])
    value01 = float(field[cell_i, cell_j + 1])
    value11 = float(field[cell_i + 1, cell_j + 1])
    return (
        (1.0 - xi) * (1.0 - eta) * value00
        + xi * (1.0 - eta) * value10
        + (1.0 - xi) * eta * value01
        + xi * eta * value11
    )
