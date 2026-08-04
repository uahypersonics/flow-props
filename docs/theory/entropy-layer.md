# Entropy Layer

For hypersonic flows, the entropy layer can be an important outer-layer feature distinct from the viscous boundary layer.

## Entropy Difference

`flow_props` computes a profile-based entropy difference relative to an edge reference state:

$$
\Delta s = c_p \ln\left(\frac{T}{T_e}\right) - R \ln\left(\frac{p}{p_e}\right)
$$

where $T_e$ and $p_e$ are taken from the profile edge unless the user supplies reference values explicitly.

## Current Criterion

The current implementation uses a normalized wall-based criterion:

$$
\frac{\Delta s}{\Delta s_w} = \text{threshold}
$$

with a default threshold of $0.25$.

That means the reported `delta_entropy` is the first wall-normal location where the normalized entropy difference decays to $25\%$ of its wall value.

## Interpretation

This makes the entropy-layer thickness a profile-reduction quantity, much like the boundary-layer edge location. It is useful for comparing how quickly the entropy excess decays with downstream position.