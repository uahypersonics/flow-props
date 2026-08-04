# Profiles

Module: `flow_props.profiles`

## Purpose

This module extracts wall-normal slices from a structured CFD dataset.

## Main Function

### `extract_profiles(ds, stations, j_max=None)`

Returns a list of profile dictionaries, one per station.

Each profile contains:

- `x`
- `y`
- `eta`
- one array per flow variable in the dataset

## Notes

- the dataset must use a `StructuredGrid`
- `eta` is built from cumulative arc length along the wall-normal line
- `j_max` can truncate the wall-normal extent for focused near-wall analysis