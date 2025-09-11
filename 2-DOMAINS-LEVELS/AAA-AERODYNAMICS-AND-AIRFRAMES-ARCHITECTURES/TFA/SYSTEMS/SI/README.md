# AAA · SYSTEMS · SI (System Integration)

**Scope**: Integrate aerodynamic & airframe subsystems into a coherent system: geometry → mesh → CFD/FEA → loads → performance → certification artifacts.

**LLC**: SI (Lifecycle Level Context: System Integration)  
**Upstream**: CAD/MBSE (CAD-DESIGN-MBSE), COMPONENTS/CE|CI, DI (Domain Interfaces)  
**Downstream**: STATIONS/SE (envelope checks), ELEMENTS/FE (federation runs), STATES/QS (superposition-derived models)

## Responsibilities
- Canonicalize inputs (units: SI m-kg-s-K; angles rad; pressure Pa).
- Orchestrate pipelines (mesh, CFD, loads, margins).
- Validate against `schemas/` and `integration-plan.yaml`.
- Emit `performance_summary` for FE orchestration and UTCS anchoring.

## Interfaces
- **Internal API**: `openapi.yaml` (validate, run, summarize).
- **Data contracts**: JSON Schemas under `schemas/`.
- **Events**: `artifact.*`, `utcs.anchor.requested` via AQUA.

## Acceptance
- All interfaces listed in `integration-plan.yaml` present & green.
- Test harness passes baseline cases (subsonic/transonic).
- Interface matrix coverage ≥ 95%; CI green.