# Config Files

Each CLI subcommand can read its inputs from a TOML configuration file.

## Why Use Config Files

Config files are useful when:

- you want reproducible post-processing runs
- your station lists are long
- you want to version-control analysis inputs

## Pattern

Each command reads one top-level section:

- `[profiles]`
- `[bl]`
- `[entropy]`
- `[wall]`

## Example

```toml
[bl]
input = "solution.vtu"
grid_file = ""
stations = [10, 50, 100]
j_max = 80
criterion = "velocity_ratio"
threshold = 0.99
u_edge = 0.0
rho_edge = 0.0
output = "bl.json"
```

Run it with:

```bash
flow-props bl --config analysis.toml
```

## Notes

- command-line arguments override config values
- if `u_edge`, `rho_edge`, `temp_edge`, or `pressure_edge` are `0`, the code auto-detects edge values from the profile tail
- `j_max = 0` means use the full wall-normal extent