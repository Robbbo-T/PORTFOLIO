# AAA/SI Integration Spec — Example

## Scope
Wing–fuselage–propulsion aerodynamic-structural integration, including control surface actuation.

## Interfaces (summary)
- Loads: steady/unsteady pressure fields → primary structure nodes
- Controls: aileron/flap actuation → hinge moments → aero response
- Thermal: skin heating envelope (Mach regime targets)
- Data: sensor buses (LCC), health telemetry (LIB)

## Verification
- CFD–FEA co-sim matrix
- Wind-tunnel correlation targets
- Flight test entry/exit criteria