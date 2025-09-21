# Copilot Instructions — Amedeo Aerospace Portfolio (TFA)

## Identity & Mission
You assist on this repository implementing the **Top Final Algorithm (TFA)** across 15 domains with a quantum–classical bridge (CB/QB/UE/FE/FWD/QS). You must prefer idempotent, secure, verifiable outputs that pass our CI validators on the first try.

## Grounding (read first)
- docs/quantum-classical-bridge.md
- 0-STRATEGY/MASTER-PROJECT-FRAMEWORK/WORKFLOWS/README.md
- services/aqua-webhook/README.md (AQUA API & CI hooks)
- 8-RESOURCES/llc-map.yaml (authoritative LLC codes)
- 8-RESOURCES/TEMPLATES/TFA-LAYER-TEMPLATES/**/README.md

## TFA Rules (hard)
- **STRICT TFA-ONLY**: Never create flat folders under `2-DOMAINS-LEVELS/<DOMAIN>/`.
- Place artifacts under `TFA/<GROUP>/<LLC>/` using canonical LLC codes:
  SI, DI, SE, CV, CE, CC, CI, CP, CB, QB, UE, FE, FWD, QS.
- Use exact domain names (e.g., `AAA-AERODYNAMICS-AND-AIRFRAMES-ARCHITECTURES`).

## Quantum–Classical Bridge
- Layers: CB→QB→UE/FE→FWD→QS.
- Use FE for cross-domain orchestration; QS for quantum state artifacts.

## AQUA / Governance
- AQUA validates manifests, verifies **FE EIP-712** signatures, coordinates **UTCS anchoring** and **TEKNIA payouts**.
- Generate manifests that match schemas in `8-RESOURCES/TEMPLATES/...`.
- Do not propose mainnet actions; CI prepares payloads; multisig humans approve.

## Idempotency & CI
- Prefer commands and code that are **idempotent**.
- Ensure outputs would pass:
  - `.github/workflows/tfa_structure_validator.yml`
  - `.github/workflows/quantum-layers-check.yml`

## Security & Compliance
- No secrets or private keys in code or examples.
- For DEFENSE/CROSS contexts: assume partitioned data, SBOM, signed builds.

## Style of answers
- Show **relative paths** and **ready-to-commit** file diffs or snippets.
- Include **validation/run steps** (how to `make scaffold`, `make check`).
- Use canonical vocabulary; **avoid deprecated terms** (e.g., `Fine Element`, `Station Envelop`).

## Quick templates Copilot can emit
- TFA scaffolds per domain under `2-DOMAINS-LEVELS/<DOMAIN>/TFA/...`.
- Artifact manifest examples conforming to `artifact-manifest.schema.json`.
- FE EIP-712 stub (link to docs/eip712.md).
- GitHub Action snippets that validate structure or link quality.

## Domain Architecture (15 domains)
The repository contains these canonical domains:
- AAA-AERODYNAMICS-AND-AIRFRAMES-ARCHITECTURES
- AAP-AIRPORTS-PLATFORMS-AND-HYDROGEN-ENABLERS  
- CCC-COCKPIT-CABIN-AND-CARGO
- CQH-CRYOGENICS-QUANTUM-AND-H2
- DDD-DIGITAL-AND-DATA-DEFENSE
- EDI-ELECTRONICS-DIGITAL-INSTRUMENTS
- EEE-ECOLOGICAL-EFFICIENT-ELECTRIFICATION
- EER-ENVIRONMENTAL-EMISSIONS-AND-REMEDIATION
- IIF-INDUSTRIAL-INFRASTRUCTURE-FACILITIES
- IIS-INTEGRATED-INTELLIGENCE-SOFTWARE
- LCC-LINKAGES-CONTROL-AND-COMMUNICATIONS
- LIB-LOGISTICS-INVENTORY-AND-BLOCKCHAIN
- MMM-MECHANICS-MATERIALS-AND-MANUFACTURING
- OOO-OS-ONTOLOGIES-AND-OFFICE-INTERFACES
- PPP-PROPULSION-AND-FUEL-SYSTEMS

## TFA Layer Hierarchy
Each domain follows this strict hierarchy:
```
2-DOMAINS-LEVELS/<DOMAIN>/TFA/
├── SYSTEMS/
│   ├── SI/  # System Integration
│   └── DI/  # Domain Interface
├── STATIONS/
│   └── SE/  # Station Envelope
├── COMPONENTS/
│   ├── CV/  # Component Vendor
│   ├── CE/  # Component Equipment
│   ├── CC/  # Configuration Cell
│   ├── CI/  # Configuration Item
│   └── CP/  # Component Part
├── BITS/
│   └── CB/  # Classical Bit
├── QUBITS/
│   └── QB/  # Qubit
├── ELEMENTS/
│   ├── UE/  # Unit Element
│   └── FE/  # Federation Entanglement
├── WAVES/
│   └── FWD/ # Future/Waves Dynamics
├── STATES/
│   └── QS/  # Quantum State
└── META/
    └── README.md
```

## Terminology Enforcement
**APPROVED TERMS** (use these):
- "Federation Entanglement" (for FE)
- "Station Envelope" (for SE)

**FORBIDDEN TERMS** (never use):
- "Fine Element" (deprecated)
- "Station Envelop" (typo)

CI will fail if forbidden terms are detected in any files.

## Validation Commands
Before proposing changes, ensure they pass:
```bash
make check           # Run all validations
make validate        # TFA structure only
python scripts/validate_tfa.py  # Direct validation
```

## AQUA Integration
When working with manifests:
- Reference AQUA webhook at `services/aqua-webhook/`
- Use POST `/api/v1/manifests/validate` for validation
- Include EIP-712 signature blocks for FE manifests
- Ensure UTCS anchoring compatibility

## Example Scaffold Command
```bash
# Scaffold AAA domain with complete TFA structure
make scaffold DOMAIN=AAA-AERODYNAMICS-AND-AIRFRAMES-ARCHITECTURES
```

## TeknIA Token Integration
For blockchain/token work:
- Use UTCS-MI identifiers for asset references
- Implement ARP4754A-compliant safety patterns
- Include S1000D-style technical data packaging
- Emit QAL Bus events for all operations