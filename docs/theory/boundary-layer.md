# Boundary-Layer Quantities

`flow_props` computes several standard integral boundary-layer quantities from extracted wall-normal profiles.

## Boundary-Layer Thickness

The edge location $\delta$ is determined from a selected criterion.

### Velocity-Ratio Criterion

The default criterion defines the edge where:

$$
\frac{u}{u_e} = \text{threshold}
$$

with a default threshold of $0.99$.

### Enthalpy-Ratio Criterion

An alternative edge is based on total enthalpy:

$$
h_t = c_p T + \frac{1}{2}u^2
$$

and the edge is defined where:

$$
\frac{h_t}{h_{t,e}} = \text{threshold}
$$

### Velocity-Gradient Criterion

The third option identifies the edge where the wall-normal velocity gradient falls below a specified threshold.

## Displacement Thickness

The compressible displacement thickness is:

$$
\delta^* = \int \left(1 - \frac{\rho u}{\rho_e u_e}\right) d\eta
$$

## Momentum Thickness

The compressible momentum thickness is:

$$
\theta = \int \frac{\rho u}{\rho_e u_e}\left(1 - \frac{u}{u_e}\right)d\eta
$$

## Shape Factor

The reported shape factor is:

$$
H = \frac{\delta^*}{\theta}
$$

This is the standard integral diagnostic used to compare profile fullness and boundary-layer state.