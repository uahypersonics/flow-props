# Wall Quantities

Module: `flow_props.wall`

## Purpose

This module computes surface quantities from the first few wall-normal points in the CFD dataset.

## Main Functions

- `wall_shear_stress`
- `skin_friction`
- `wall_heat_flux`
- `stanton_number`
- `run_wall`

## Implementation Notes

- the current implementation uses a one-sided second-order finite-difference stencil at the wall
- `run_wall` always returns `tau_w`
- `cf`, `qw`, and `st` are included only when the required inputs are provided