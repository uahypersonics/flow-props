# Boundary Layer

Module: `flow_props.bl`

## Purpose

This module converts extracted profiles into integral boundary-layer quantities.

## Main Functions

- `boundary_layer_thickness`
- `enthalpy_boundary_layer_thickness`
- `velocity_gradient_thickness`
- `boundary_layer_edge`
- `displacement_thickness`
- `momentum_thickness`
- `shape_factor`
- `bl_properties`
- `run_bl`

## Edge Criteria

The public constants are:

- `BL_EDGE_VELOCITY_RATIO`
- `BL_EDGE_ENTHALPY_RATIO`
- `BL_EDGE_VELOCITY_GRADIENT`

These are used by `boundary_layer_edge` and `run_bl` to select how the boundary-layer edge is determined.