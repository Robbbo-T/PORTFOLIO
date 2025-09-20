# LLC Hierarchy (STRICT LLC (Lifecycle Level Context) Hierarchy

**UTCS**: `utcs:tfa:spec:llc-hierarchy:v2.1.0`  
**Status**: Authoritative Standard  
**Policy**: **STRICT**. This hierarchy is enforced by CI/CD validators. No deviations are permitted.

---

## 1. Introduction

The LLC codes are the canonical identifiers for every layer within the TFA (Top Final Algorithm) architecture. They provide a deterministic, traceable, and machine-readable structure for organizing all engineering artifacts across the 15 domains.

The hierarchy is organized into eight primary groups, which include the six layers of the quantum-classical bridge.

## 2. The Eight Primary Groups

| Group        | Description                                                              |
| :----------- | :----------------------------------------------------------------------- |
| **SYSTEMS**      | Manages high-level orchestration, interfaces, and system-wide contracts. |
| **STATIONS**     | Defines the physical and logical boundaries of operational environments. |
| **COMPONENTS**   | Provides a granular digital thread for hardware and software configuration.|
| **BITS**         | Contains the logic for classical, deterministic computation.             |
| **QUBITS**       | Manages quantum algorithms, problems, and orchestration.               |
| **ELEMENTS**     | Contains atomic, reusable functions and multi-agent coordination contracts.|
| **WAVES**        | Manages predictive models, simulations, and time-series dynamics.        |
| **STATES**       | Stores immutable, signed evidence and manages state provenance.          |

---

## 3. Detailed LLC Code Definitions

### 3.1 SYSTEMS Group

*   #### `SI/` - System Integration
    *   **Purpose**: Orchestration of multiple domains and services (MAP→MAL). Defines system-wide behavior, safety sequences, and data flows.
    *   **Key Artifacts**: `routes.map.yaml`, `thg.temporal.json`, `optimo-joins.yaml`.

*   #### `DI/` - Domain Interface
    *   **Purpose**: Defines the formal, versioned API contract for a single domain's services (the MALs). This is the boundary layer.
    *   **Key Artifacts**: `mal.contract.json`, `openapi.yaml`, input/output JSON schemas.

### 3.2 STATIONS Group

*   #### `SE/` - Station Envelope
    *   **Purpose**: Defines the safe operating limits (physical, electrical, environmental) for a specific station (e.g., test bench, integration lab, airport gate).
    *   **Key Artifacts**: `envelope.se.yaml`, `checks.se.tests.yaml`.

### 3.3 COMPONENTS Group

*   #### `CV/` - Component Vendor
    *   **Purpose**: Information about the supplier of a component.
    *   **Key Artifacts**: `<VENDOR_CODE>.vendor.yaml`.

*   #### `CE/` - Component Equipment
    *   **Purpose**: Defines a specific equipment model or type (e.g., "Power Control Unit Model X").
    *   **Key Artifacts**: `<PART_NUMBER>.equipment.yaml`.

*   #### `CC/` - Configuration Cell
    *   **Purpose**: A logical grouping of equipment that forms a functional unit.
    *   **Key Artifacts**: `<CELL_NAME>.cell.yaml`.

*   #### `CI/` - Configuration Item
    *   **Purpose**: A unique, specific instance of a component, linking hardware (`CE`) to its exact software/firmware load. This is the instantiable unit.
    *   **Key Artifacts**: `<INSTANCE_ID>.item.yaml`.

*   #### `CP/` - Component Part
    *   **Purpose**: An atomic, non-decomposable part with data for its Digital Material Passport (DMP).
    *   **Key Artifacts**: `<PART_NUMBER>.part.yaml`.

### 3.4 BITS Group (Quantum-Classical Bridge Layer)

*   #### `CB/` - Classical Bit
    *   **Purpose**: Contains the classical, deterministic algorithms, solvers, and computational logic.
    *   **Key Artifacts**: `algos/`, solver `contracts/`, performance `tests/`.

### 3.5 QUBITS Group (Quantum-Classical Bridge Layer)

*   #### `QB/` - Qubit
    *   **Purpose**: Manages quantum computing artifacts, including problem formulations and orchestration policies.
    *   **Key Artifacts**: `problems/` (QUBO/Ising models), `orchestration/` policies, fallback `tests/`.

### 3.6 ELEMENTS Group (Quantum-Classical Bridge Layer)

*   #### `UE/` - Unit Element
    *   **Purpose**: Contains fundamental, reusable, and testable software units (drivers, parsers, validators).
    *   **Key Artifacts**: `ue_manifest.yaml`, source code (`ue_*.py`), unit tests.

*   #### `FE/` - Federation Entanglement
    *   **Purpose**: Defines the rules and contracts for secure, multi-agent or multi-organization collaboration.
    *   **Key Artifacts**: `fe_coalition.schema.json`, governance `contracts/`.

### 3.7 WAVES Group (Quantum-Classical Bridge Layer)

*   #### `FWD/` - Forward/Waves Dynamics
    *   **Purpose**: Manages predictive analytics, simulations, and time-series/frequency-domain analysis.
    *   **Key Artifacts**: `fwd_metrics.yaml`, `thg.links.yaml`.

### 3.8 STATES Group (Quantum-Classical Bridge Layer)

*   #### `QS/` - Quantum State
    *   **Purpose**: The immutable, auditable evidence layer. Stores signed records of system operations and state transitions.
    *   **Key Artifacts**: `det_anchor.schema.json`, `anchors/DET-ANCHOR-*.json`.

---

## 4. Directory Structure Enforcement

The following directory structure is **mandatory** for all 15 domains. The CI pipeline will fail any commit that violates this structure.

```plaintext
<DOMAIN_NAME>/
└── TFA/
    ├── SYSTEMS/
    │   ├── SI/
    │   └── DI/
    ├── STATIONS/
    │   └── SE/
    ├── COMPONENTS/
    │   ├── CV/
    │   ├── CE/
    │   ├── CC/
    │   ├── CI/
    │   └── CP/
    ├── BITS/
    │   └── CB/
    ├── QUBITS/
    │   └── QB/
    ├── ELEMENTS/
    │   ├── UE/
    │   └── FE/
    ├── WAVES/
    │   └── FWD/
    ├── STATES/
    │   └── QS/
    └── META/
        └── README.md
