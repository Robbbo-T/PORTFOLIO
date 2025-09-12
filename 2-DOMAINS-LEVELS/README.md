# 2-DOMAINS-LEVELS · Canonical Domains Index

> **Purpose**
> This directory contains the **15 aerospace domains** that make up the portfolio’s engineering backbone.
> Each domain is organized using the **TFA (Top Final Algorithm)** hierarchy with a **quantum–classical bridge** (CB/QB/UE/FE/FWD/QS).
> All work here **must** comply with the **STRICT TFA-ONLY** policy.

* 🔗 Architecture primer: [`8-RESOURCES/8-RESOURCES/TFA-ARCHITECTURE.md`](../8-RESOURCES/8-RESOURCES/TFA-ARCHITECTURE.md)
* 🔗 Quantum–classical bridge: [`docs/quantum-classical-bridge.md`](../docs/quantum-classical-bridge.md)
* 🔗 AQUA-OS PRO (example MAP/MAL app): [`services/aqua-os-pro/`](../services/aqua-os-pro/)

---

## ⚖️ STRICT TFA-ONLY (enforced)

* ✅ Use: `2-DOMAINS-LEVELS/<CODE-NAME>/TFA/<GROUP>/<LLC>/…`
* ❌ Never create **flat** LLC folders under the domain root.
* ✅ Include `TFA/META/` for identity, policies, ADRs, provenance.
* ✅ Quantum bridge layers must exist (CB/QB/UE/FE/FWD/QS).
* ✅ Terminology guard: don’t use deprecated forms (e.g., `Station~Envelop`, `Fine~Element`).

CI gates:
`.github/workflows/tfa_structure_validator.yml` · `quantum-layers-check.yml` · `link-and-quality.yml` · `dir-policy.yml` · `anchor_utcs.yml`

---

## 🗂️ Domain List (15)

| Code    | Domain (verbatim)                        | Path                                                                                               |
| ------- | ---------------------------------------- | -------------------------------------------------------------------------------------------------- |
| **AAA** | AERODYNAMICS-AND-AIRFRAMES-ARCHITECTURES | [`AAA-AERODYNAMICS-AND-AIRFRAMES-ARCHITECTURES/`](./AAA-AERODYNAMICS-AND-AIRFRAMES-ARCHITECTURES/) |
| **AAP** | AIRPORT-ADAPTABLE-PLATFORMS              | [`AAP-AIRPORT-ADAPTABLE-PLATFORMS/`](./AAP-AIRPORT-ADAPTABLE-PLATFORMS/)                           |
| **CCC** | COCKPIT-CABIN-AND-CARGO                  | [`CCC-COCKPIT-CABIN-AND-CARGO/`](./CCC-COCKPIT-CABIN-AND-CARGO/)                                   |
| **CQH** | CRYOGENICS-QUANTUM-AND-H2                | [`CQH-CRYOGENICS-QUANTUM-AND-H2/`](./CQH-CRYOGENICS-QUANTUM-AND-H2/)                               |
| **DDD** | DIGITAL-AND-DATA-DEFENSE                 | [`DDD-DIGITAL-AND-DATA-DEFENSE/`](./DDD-DIGITAL-AND-DATA-DEFENSE/)                                 |
| **EDI** | ELECTRONICS-DIGITAL-INSTRUMENTS          | [`EDI-ELECTRONICS-DIGITAL-INSTRUMENTS/`](./EDI-ELECTRONICS-DIGITAL-INSTRUMENTS/)                   |
| **EEE** | ECOLOGICAL-EFFICIENT-ELECTRIFICATION     | [`EEE-ECOLOGICAL-EFFICIENT-ELECTRIFICATION/`](./EEE-ECOLOGICAL-EFFICIENT-ELECTRIFICATION/)         |
| **EER** | ENVIRONMENTAL-EMISSIONS-AND-REMEDIATION  | [`EER-ENVIRONMENTAL-EMISSIONS-AND-REMEDIATION/`](./EER-ENVIRONMENTAL-EMISSIONS-AND-REMEDIATION/)   |
| **IIF** | INDUSTRIAL-INFRASTRUCTURE-FACILITIES     | [`IIF-INDUSTRIAL-INFRASTRUCTURE-FACILITIES/`](./IIF-INDUSTRIAL-INFRASTRUCTURE-FACILITIES/)         |
| **IIS** | INTEGRATED-INTELLIGENCE-SOFTWARE         | [`IIS-INTEGRATED-INTELLIGENCE-SOFTWARE/`](./IIS-INTEGRATED-INTELLIGENCE-SOFTWARE/)                 |
| **LCC** | LINKAGES-CONTROL-AND-COMMUNICATIONS      | [`LCC-LINKAGES-CONTROL-AND-COMMUNICATIONS/`](./LCC-LINKAGES-CONTROL-AND-COMMUNICATIONS/)           |
| **LIB** | LOGISTICS-INVENTORY-AND-BLOCKCHAIN       | [`LIB-LOGISTICS-INVENTORY-AND-BLOCKCHAIN/`](./LIB-LOGISTICS-INVENTORY-AND-BLOCKCHAIN/)             |
| **MMM** | MECHANICAL-AND-MATERIAL-MODULES          | [`MMM-MECHANICAL-AND-MATERIAL-MODULES/`](./MMM-MECHANICAL-AND-MATERIAL-MODULES/)                   |
| **OOO** | OS-ONTOLOGIES-AND-OFFICE-INTERFACES      | [`OOO-OS-ONTOLOGIES-AND-OFFICE-INTERFACES/`](./OOO-OS-ONTOLOGIES-AND-OFFICE-INTERFACES/)           |
| **PPP** | PROPULSION-AND-FUEL-SYSTEMS              | [`PPP-PROPULSION-AND-FUEL-SYSTEMS/`](./PPP-PROPULSION-AND-FUEL-SYSTEMS/)                           |

> Tip: run `make domains` to print a one-line health snapshot per domain (layers present, TFA compliance).

---

## 🧬 TFA Tree (per domain)

Expected skeleton under each domain:

```
<DOMAIN>/TFA/
├─ SYSTEMS/      ├─ SI/ (SYSTEM INTEGRATION)   └─ DI/ (DOMAIN INTERFACE)
├─ STATIONS/     └─ SE/ (STATION ENVELOPE)
├─ COMPONENTS/   ├─ CV/ ├─ CE/ ├─ CC/ ├─ CI/ └─ CP/
├─ BITS/         └─ CB/ (CLASSICAL BIT)
├─ QUBITS/       └─ QB/ (QUBIT)
├─ ELEMENTS/     ├─ UE/ (UNIT ELEMENT) └─ FE/ (FEDERATION ENTANGLEMENT)
├─ WAVES/        └─ FWD/ (Future/Waves Dynamics)
├─ STATES/       └─ QS/ (QUANTUM STATE)
└─ META/         └─ README.md + policies + ADRs + provenance
```

Starter templates:
`8-RESOURCES/TEMPLATES/TFA-LAYER-TEMPLATES/` and `8-RESOURCES/TEMPLATES/META/`

---

## 🗺️ MAP/MAL Reference (how domains become programs)

* **MAP (Master Application Program):** one brain per domain (e.g., `MAP-AAA`, `MAP-PPP`).
  Defines domain strategy, contracts, and orchestration points exposed to programs.
* **MAL (Main Application Layer):** one horizontal service per bridge layer (CB/QB/FWD/QS/FE/UE).
  Example implementations live in `services/` (e.g., **AQUA-OS PRO**).

Learn more:

* AQUA-OS PRO (Predictive Route Optimizer): [`services/aqua-os-pro/`](../services/aqua-os-pro/)
* Bridge layers overview: [`docs/quantum-classical-bridge.md`](../docs/quantum-classical-bridge.md)

---

## 🛡️ Segment Coverage (AIR · SPACE · GROUND · **DEFENSE** · **CROSS**)

Declare coverage at `TFA/META/METADATA.yaml`:

```yaml
domain: CQH
segments: [AIR, SPACE, GROUND, DEFENSE, CROSS]
classification: ORG|DEF-RESTRICTED
owners: [map_owner@org]
```

**DEFENSE** additions (when present):

* Policy pack required: safety, security, export controls in `TFA/META/POLICIES/`.
* Keys & crypto in HSM/KMS; 90-day rotation; mTLS + RBAC/ABAC.
* CI gate for restricted exports (strip non-cleared artifacts in release jobs).

**CROSS** additions:

* Inter-domain contracts documented in `TFA/META/LINKS.md`.
* FE (federation) flows must define CRDT/consensus semantics and conflict policy.

---

## 🔢 UTCS IDs & Requirement Pattern

Use UTCS IDs to tag specs/impls & test artifacts:

```
<DOMAIN>/<LAYER>/REQ-<NNNN>
# Example:
AAA/SI/REQ-0101
```

Layer index (for consistency in IDs):

| Index | Layer | Meaning                 |
| ----: | ----- | ----------------------- |
|    01 | SI    | System Integration      |
|    02 | DI    | Domain Interface        |
|    03 | SE    | Station Envelope        |
|    04 | CB    | Classical Bit           |
|    05 | QB    | Qubit                   |
|    06 | FWD   | Future/Waves Dynamics   |
|    07 | QS    | Quantum State           |
|    08 | FE    | Federation Entanglement |

---

## 🚀 Common Tasks

### 1) Scaffold or repair domain trees

```bash
make scaffold
```

### 2) Validate domain structure & bridge layers

```bash
make check
# or run CI locally if desired
```

### 3) Create a new requirement (example)

* Add spec under the correct layer, e.g.
  `AAA-AERODYNAMICS-AND-AIRFRAMES-ARCHITECTURES/TFA/SYSTEMS/SI/AQUA-OS-PRO-SPEC.md`
* Reference UTCS ID in the doc header and in code stubs.

### 4) Wire into AQUA-OS PRO loop (optional)

* See orchestrator & schema:
  `services/aqua-os-pro/core/aqua_pro_orchestrator.py`
  `services/aqua-os-pro/schemas/route_optimization.json`

---

## ✅ Done-Definition (per domain)

A domain is **integration-ready** when:

* [ ] `TFA/META/` present with **METADATA**, **POLICIES**, **ADRs**, **QS/PROVENANCE**
* [ ] All TFA groups exist; no flat LLC folders
* [ ] Quantum bridge layers visible (CB/QB/UE/FE/FWD/QS)
* [ ] DI contracts (OpenAPI/Protobuf) versioned & linted
* [ ] SI integration points documented and testable
* [ ] CI passes: structure, bridge layers, links, dir policy
* [ ] (If DEFENSE) restricted policies and export filters applied

---

## 🔍 Health & Status

Print a fast status of layers present per domain:

```bash
make domains
```

Run comprehensive validation (AQUA-OS PRO example):

```bash
python3 services/aqua-os-pro/validation/aqua_pro_validator.py
```

---

## 🧩 How this directory fits the whole ecosystem

* **Domains** provide **stable contracts** (MAP) and **layered services** (MAL).
* **Bridge layers** ensure **quantum–classical** portability & deterministic fallbacks.
* **OPTIMO-DT** binds organization/process/technical/MLOps into a single **Digital Thread**.
* **UTCS** anchors provenance for audit and verifiable state transitions.
* **CI** prevents structural drift and enforces terminology and layers across the fleet.

Together, this yields a **coherent, intelligent, multi-sector** platform capable of supporting
programs like **AMPEL360 BWB-Q100** (AIR), **GAIA Quantum SAT** (SPACE), and **Diagnostics & MRO Robbbo-t** (GROUND), with **DEFENSE** and **CROSS** overlays where needed.

---

## 🤝 Contributing

Follow repo-level guidance in [`CONTRIBUTING.md`](../CONTRIBUTING.md).
For domain-specific changes, open an ADR in `TFA/META/DECISIONS/` and reference the UTCS IDs impacted.

**License:** MIT (inherits project)
