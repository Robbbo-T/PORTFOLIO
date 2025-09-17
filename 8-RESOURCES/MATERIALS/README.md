# Blockchain Material Passports

Deterministic control programs that depend on advanced materials now rely on a unified "material passport" dataset anchored into the UTCS ledger. This package delivers the canonical YAML format, integration notes for S1000D Issue 6 deliverables, and CI guards that keep provenance data auditable without leaking intellectual property.

## Executive Summary
- **Traceability & authenticity**: every graphene/CNT lot travels with a signed Material Passport. Only the hash of evidence packets (tests, custody, recycling) is anchored on-chain.
- **Transparent supply chain**: lifecycle events – `PRODUCTION → TEST → INSTALL → SERVICE → RECYCLE` – are sealed with role-aware actors (supplier, lab, integrator, recycler).
- **Regulatory compliance**: immutable anchors cover REACH, RoHS, conflict-minerals, and safety dossiers. Sensitive payloads remain encrypted off-chain.

## Dataset: `material_passports.yaml`
The YAML dataset lives at `8-RESOURCES/MATERIALS/material_passports.yaml` and aligns with S1000D Issue 6 metadata and UTCS anchors. Key fields:

```yaml
version: 1
issue: "6.0"
passports:
  - mp_id: "MP-GR-2025-000123"           # unique material-passport identifier
    material:
      type: "graphene"                   # graphene | cnt | hybrid
      form: "flake"
      grade: "A1"
    batch:
      batch_id: "GR-FLK-2309-001"
      supplier: { name: "NanoSup SA", did: "did:org:nanosup" }
    lifecycle:
      - kind: "PRODUCTION"               # hashed on-chain transaction ID in `tx`
    chain_anchor:
      chain: "besu-permnet"
      passport_sha256: "0x…"             # SHA-256 hash of the canonical passport payload
      status: "ACTIVE"                   # ACTIVE | RETIRED | RECYCLED
```

For CNT entries the `properties.residual_metal_ppm` block is mandatory to capture catalyst carryover. Safety declarations must confirm REACH compliance before release.

## S1000D Issue 6 Integration
- **Data Modules** referencing these materials expose `hazardous_materials`, `material_passport_ref`, and `chain_anchor.tx` metadata fields.
- **BREX/BRDP rules** enforce the presence of `safety_hazmat` and a valid `passport_sha256` whenever graphene/CNT appears in a DM.
- **Traceability bridge**: UTCS anchors referenced in `chain_anchor.tx` connect CSDB records to permissioned blockchain proofs while keeping documents off-chain.

## CI Acceptance Criteria
The CI helper `scripts/material_passport_ci.py` validates the dataset:
1. `chain_anchor.passport_sha256` must equal the SHA-256 hash of the canonical passport payload (excluding the hash field itself).
2. Any lifecycle event with `kind: INSTALL` must declare `link.dmcode` (Issue 6 DM code) and `link.assembly_pnr`.
3. CNT materials **must** include a populated `properties.residual_metal_ppm` mapping.
4. Publishing is blocked whenever `safety_hazmat.reach_compliant` is `false`.

Run locally with:

```bash
python scripts/material_passport_ci.py 8-RESOURCES/MATERIALS/material_passports.yaml
```

The script also surfaces summary stats (active vs retired passports, actor DID coverage, and lifecycle completeness) for audit dashboards.

## Architecture Flow (PlantUML)
`docs/architecture/material_trace.puml` captures the supplier → lab → integrator workflow. Render it locally with PlantUML to embed in domain specs or audits.

## Cross-Linking from MAL Manifests
MAL controllers reference the passports via the `material_passport_refs` block in `manifest.yaml`. CI cross-checks that references map to valid passport IDs, ensuring deterministic controllers always cite the ledger-backed provenance they depend on.
