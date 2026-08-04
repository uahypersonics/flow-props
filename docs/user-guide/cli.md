# CLI

The command-line interface is exposed through `flow-props`.

## Overview

```bash
flow-props --help
```

Available subcommands:

- `profiles`
- `bl`
- `entropy`
- `wall`

## Profiles

Extract wall-normal profiles at selected stations:

```bash
flow-props profiles \
  --input solution.vtu \
  --stations 10,50,100 \
  --j-max 80 \
  --output profiles.json
```

## Boundary-Layer Properties

Compute $\delta$, $\delta^*$, $\theta$, and $H$:

```bash
flow-props bl \
  --input solution.vtu \
  --stations 10,50,100 \
  --criterion velocity_ratio \
  --threshold 0.99 \
  --output bl.json
```

For an enthalpy-based edge criterion:

```bash
flow-props bl \
  --input solution.vtu \
  --stations 10,50,100 \
  --criterion enthalpy_ratio \
  --threshold 0.99
```

For a derivative-based criterion:

```bash
flow-props bl \
  --input solution.vtu \
  --stations 10,50,100 \
  --criterion velocity_gradient \
  --gradient-threshold 0.0
```

## Entropy-Layer Thickness

```bash
flow-props entropy \
  --input solution.vtu \
  --stations 10,50,100 \
  --threshold 0.25 \
  --output entropy.json
```

## Wall Quantities

```bash
flow-props wall \
  --input solution.vtu \
  --mu-wall 1.8e-5 \
  --output wall.json
```

Add freestream and thermal inputs if you want $C_f$, $q_w$, and $St$:

```bash
flow-props wall \
  --input solution.vtu \
  --mu-wall 1.8e-5 \
  --output wall.json
```

## Template Config Files

Each command can print a starter TOML block:

```bash
flow-props bl --init
flow-props entropy --init
flow-props wall --init
flow-props profiles --init
```