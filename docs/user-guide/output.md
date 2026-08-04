# Output Formats

The current CLI writes JSON outputs for easy inspection and scripting.

## Profiles Output

`flow-props profiles` writes a list of profile dictionaries.

Each item contains:

- `x`
- `y`
- `eta`
- one array for each available flow variable

## Boundary-Layer Output

`flow-props bl` writes one object per station with:

- `station`
- `delta`
- `delta_star`
- `theta`
- `H`

## Entropy-Layer Output

`flow-props entropy` writes one object per station with:

- `station`
- `delta_entropy`

## Wall Output

`flow-props wall` writes a dictionary of surface arrays. Depending on the inputs you provide, it may contain:

- `tau_w`
- `cf`
- `qw`
- `st`

## Post-Processing Strategy

These JSON outputs are intended to be lightweight interchange products. They are easy to:

- inspect directly
- read into Python for plotting
- archive with the CFD case inputs