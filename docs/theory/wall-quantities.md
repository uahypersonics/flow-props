# Wall Quantities

`flow_props` computes near-wall quantities directly from the CFD dataset and grid geometry.

## Wall Shear Stress

The wall shear stress is evaluated as:

$$
\tau_w = \mu_w \left.\frac{\partial u}{\partial \eta}\right|_w
$$

The current implementation uses a one-sided second-order finite-difference approximation at the wall.

## Skin-Friction Coefficient

$$
C_f = \frac{\tau_w}{\tfrac{1}{2}\rho_\infty u_\infty^2}
$$

This requires freestream density and velocity.

## Wall Heat Flux

$$
q_w = -k_w \left.\frac{\partial T}{\partial \eta}\right|_w
$$

As with shear stress, the wall-normal derivative is approximated with a one-sided finite-difference stencil.

## Stanton Number

The package reports:

$$
St = \frac{q_w}{\rho_\infty u_\infty c_p (T_\infty - T_w)}
$$

This is a practical working definition for the current package implementation.