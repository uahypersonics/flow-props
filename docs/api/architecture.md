# Architecture

`flow_props` follows a narrow pipeline:

1. `cfd-io` reads a CFD dataset
2. `flow_props.profiles.extract_profiles` slices wall-normal profiles at chosen stations
3. reduction modules compute derived quantities from those profiles

## Module Layout

- `profiles.py`: wall-normal profile extraction
- `bl.py`: boundary-layer edge detection and integral thicknesses
- `entropy_layer.py`: entropy-layer thickness
- `wall.py`: wall shear and thermal quantities
- `config.py`: TOML section loading for the CLI
- `cli.py`: Typer-based command-line interface

## Design Intent

The package is deliberately lightweight.

- it does not own CFD file I/O
- it assumes `cfd-io` has already constructed a dataset
- it focuses on profile-based property extraction rather than general field operations

That separation keeps `flow_props` easy to reason about and consistent with the rest of the workspace.