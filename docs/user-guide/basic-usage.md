# Basic Usage

## Read A Dataset

`flow_props` expects a dataset that has already been read by `cfd-io`.

```python
import cfd_io

dataset = cfd_io.read_file("solution.vtu")
```

For split solution/grid formats, provide the separate grid file through `cfd-io`.

## Extract Profiles

```python
from flow_props import extract_profiles

profiles = extract_profiles(dataset, stations=[10, 50, 100], j_max=80)
print(profiles[0].keys())
```

Each extracted profile includes:

- `x`, `y`
- `eta`
- one array per flow field available in the input dataset

## Compute Boundary-Layer Properties

```python
from flow_props import run_bl

bl_results = run_bl(
    dataset,
    stations=[10, 50, 100],
    criterion="velocity_ratio",
    threshold=0.99,
)
```

Available edge criteria currently include:

- `velocity_ratio`
- `enthalpy_ratio`
- `velocity_gradient`

## Compute Entropy-Layer Thickness

```python
from flow_props import run_entropy

entropy_results = run_entropy(
    dataset,
    stations=[10, 50, 100],
    threshold=0.25,
)
```

## Compute Wall Quantities

```python
from flow_props import run_wall

wall_results = run_wall(
    dataset,
    mu_wall=1.8e-5,
    rho_inf=0.12,
    u_inf=2500.0,
    k_wall=0.03,
    cp=1005.0,
    T_wall=300.0,
    T_inf=220.0,
)
```

## Typical Workflow

In practice, a common pattern is:

```python
import cfd_io
from flow_props import run_bl, run_entropy, run_wall

dataset = cfd_io.read_file("solution.vtu")

bl_results = run_bl(dataset, stations=[20, 40, 60])
entropy_results = run_entropy(dataset, stations=[20, 40, 60])
wall_results = run_wall(dataset, mu_wall=1.8e-5)
```

That gives you station-wise layer quantities plus surface distributions from the same CFD input.
