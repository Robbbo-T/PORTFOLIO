# AAA — AERODYNAMICS-AND-AIRFRAMES-ARCHITECTURES

## Purpose & Scope
This META page captures domain-level decisions, authorship, and references for AAA. Scope: aerodynamic configuration, airframe architecture trade space, performance targets, and structural integration with other domains.

## Domain Steward
- Primary steward: [Team / Person Name]
- Contact: [email]

## Interfaces
- **Upstream:**
  - [0-STRATEGY](../../../../0-STRATEGY/) (requirements)
  - [1-CAX-METHODOLOGY](../../../../1-CAX-METHODOLOGY/) / *CAD-DESIGN (MBSE models)*
    - CAD-DESIGN template: [8-RESOURCES/TEMPLATES/CAX-LIFECYCLE-TEMPLATES/CAD-DESIGN/README.template.md](../../../../8-RESOURCES/TEMPLATES/CAX-LIFECYCLE-TEMPLATES/CAD-DESIGN/README.template.md)
- **Downstream:**
  - PPP (propulsion): [2-DOMAINS-LEVELS/PPP-PROPULSION-AND-FUEL-SYSTEMS/](../../../../2-DOMAINS-LEVELS/PPP-PROPULSION-AND-FUEL-SYSTEMS/)
  - CCC (cockpit/cabin interfaces): [2-DOMAINS-LEVELS/CCC-COCKPIT-CABIN-AND-CARGO/](../../../../2-DOMAINS-LEVELS/CCC-COCKPIT-CABIN-AND-CARGO/)
  - OPTIMO-DT (digital-thread ingest): [3-PROJECTS-USE-CASES/OPTIMO-DT/](../../../../3-PROJECTS-USE-CASES/OPTIMO-DT/)
- **Typical interface artifacts:** SysML models, interface-control documents (ICD), integration matrices — see **SI layer**: [TFA/SYSTEMS/SI](../SYSTEMS/SI/) · [README.md](../SYSTEMS/SI/README.md)

## Compliance & Standards
- Applicable: EASA CS-25 / FAA Part 25, ARP4754A, DO-178C (avionics SW), DO-254 (FPGA/hardware), AS9100, S1000D for maintenance data.
- Certification notes: Track traceability in OPTIMO-DT → [3-PROJECTS-USE-CASES/OPTIMO-DT/](../../../../3-PROJECTS-USE-CASES/OPTIMO-DT/) and register deviations in this META.

## Variants & Notable Items
- Variant families: BWB-Q100, BWB-Q250, AMPEL360e
- Notable: blended-wing-body aeroforms, distributed propulsion structural interfaces

## Quantum Layers Map (local decisions)
- **BITS/CB:** host classical solvers & config bits (CFD parameters) → [TFA/BITS/CB](../BITS/CB/) · [README.md](../BITS/CB/README.md)
- **QUBITS/QB:** reserved for quantum-accelerated aero optimizers (QAOA/VQE prototypes) → [TFA/QUBITS/QB](../QUBITS/QB/) · [README.md](../QUBITS/QB/README.md)
- **ELEMENTS/UE:** canonical geometric unit elements → [TFA/ELEMENTS/UE](../ELEMENTS/UE/) · [README.md](../ELEMENTS/UE/README.md)
- **ELEMENTS/FE:** federation elements for cross-domain optimization (e.g., aero-structures coupling) → [TFA/ELEMENTS/FE](../ELEMENTS/FE/) · [README.md](../ELEMENTS/FE/README.md)
- **WAVES/FWD:** FWD models used for predictive gust response → [TFA/WAVES/FWD](../WAVES/FWD/) · [README.md](../WAVES/FWD/README.md)
- **STATES/QS:** no active QS artifacts yet — record experiments here → [TFA/STATES/QS](../STATES/QS/) · [README.md](../STATES/QS/README.md)

## Local Decisions / Deviations
- Local decision log: record deviation IDs, reasons, and approval dates here.

## Links / Templates
- Template bucket: [`8-RESOURCES/TEMPLATES/DOMAIN-SPECIFIC-TEMPLATES/AAA-TEMPLATES/`](../../../../8-RESOURCES/TEMPLATES/DOMAIN-SPECIFIC-TEMPLATES/AAA-TEMPLATES/)
- Example artifacts: [`3-PROJECTS-USE-CASES/BWB-Q100-AIRCRAFT/`](../../../../3-PROJECTS-USE-CASES/BWB-Q100-AIRCRAFT/)

## Change log
- Created: [YYYY-MM-DD] by [author]
- Last updated: [YYYY-MM-DD] — brief note
