---
id: ASIT-GENESIS-STYLEGUIDE-0001-OV
rev: 0
llc: CV # Configuration & Validation
title: "ASI-T · Copilot Agent Styleguide (CAx + LLC Bridges)"
configuration: baseline
classification: "INTERNAL / EVIDENCE-REQUIRED"
version: "1.0.0"
release_date: 2025-09-22
maintainer: "ASI-T Architecture Team"
provenance:
  policy_hash: "sha256:3a7bd3e2360a3d4b8b8e9e7e2c3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f"
  model_sha: "sha256:5e884898da28047151d0e56f8dc6292773603d0d6aabbddc8a3f6a7b8c9d0e1f"
  data_manifest_hash: "sha256:2c1743a391305fbf367df8e4f069f9f9b828b9d2b1e6a7b8c9d0e1f2a3b4c5d6"
  operator_id: "UTCS:OP:core"
  canonical_hash: "sha256:6b1b36cbb04b41490bfc0ab2bfa26f86e3b3a7b8c9d0e1f2a3b4c5d6e7f8g9h0"
licenses:
  code: "Apache-2.0"
  docs: "CC-BY-4.0"
bridge: "CB→QB→UE→FE→FWD→QS"
ethics_guard: "MAL-EEM"
---

# 📑 ASI-T · Copilot Agent Styleguide (CAx + LLC Bridges)

## 1. Golden Rules
- **UIX.v1 required** in each agent before acting.  
- **TFA-Only path grammar**: `TFA/<LAYER>/<LLC>/...`.  
- **MAL-EEM**: ética + empatía, fail-closed.  
- **QS/UTCS deterministic evidence** in every PR.  
- **FCR-1 + FCR-2** para todo merge.  
- **Revisiones**:
  - `rev: 0` = baseline → filename estable sin letra.  
  - `rev ≥ 1` = `_revisions/REV_<letter>/HOV_<MSN_RANGE>_<PHASES>/…`.  

## 2. File & Path Grammar
```text
TFA/
└── <LAYER>/
    └── <LLC>/
        ├── <UTCS-ID>.md
        └── _revisions/
            └── REV_A/
                └── HOV_MSN1-3_CAD-CAM/<UTCS-ID>.md
```
**Regex de validación (POSIX ERE):**
```regex
^TFA/(SYSTEMS|STATIONS|COMPONENTS|BITS|QUBITS|ELEMENTS|WAVES|STATES)/[A-Z]{2}/(_revisions/REV_[A-Z]/HOV_[A-Z0-9_-]+/)?(ASIT-[A-Z0-9-]+-[0-9]{4}-[A-Z]{2})\.md$
```

## 3. UTCS-MI Front-Matter Template
```yaml
---
id: <DOMAIN-PROGRAM-BLOCKS-ID>
rev: <int>    # 0=baseline; ≥1 revisiones documentadas
llc: <SI|DI|SE|CV|CE|CC|CI|CP>
title: "<Title>"
configuration: baseline
# ... (resto de campos)
hov:              # obligatorio en rev ≥ 1
  msn_range: "MSN1-3"
  phases: ["CAD","CAE","CAI"]
  label: "MSN1-3 diseño+ingeniería+embedding"
bridge: "CB→QB→UE→FE→FWD→QS"
ethics_guard: "MAL-EEM"
---
```

## 4. HOV Phases (CAx canónicos)
La lista canónica de fases se mantiene en `ASI-T/GENESIS/cax_phases.list`. Debe respetarse el orden cronológico.
1. `STRATEGY`
2. `CAX-METHODOLOGY`
3. `CAB`
4. `CAIR`
5. `CAD`
6. `CAE`
7. `CAI` *(HW·SW·AI embedding)*
8. `CAV`
9. `CAT`
10. `CAM`
11. `CA-PRO`
12. `CAO`
13. `CAF`
14. `CAS0`
15. `CAEPOST`

## 5. Error Codes
- `[E1001]` PathGrammarError
- `[E2001]` SchemaError
- `[E2107]` HOVNotAllowed
- `[E2108]` HOVMissing
- `[E2110]` HOVPhasesInvalid
- `[E2111]` HOVPathMismatch
- `[E6001]` ProvenanceDrift

## 6. Formatting Instructions
- **Filenames**: `UTCS-ID.md`.
- **Revisions**: `_revisions/REV_<letter>/HOV_<msn_range>_<phases>/UTCS-ID.md`.
- **Front-matter**: YAML delimitado por `---`.
- **Markdown body**: `#` → títulos, `##` → secciones, `###` → subsecciones.
- **Code fences**: ` ```yaml/json/bash `.
- **Blockquotes** `>` para normas críticas.
- **Lists**: `-` (bullets) o numeradas si hay orden.

## 7. Commit / PR Template
```text
feat(docs): Finaliza Styleguide con validación CAx y glosario completo

FCR-1: <link>
FCR-2: <link>
UTCS: ASIT-GENESIS-STYLEGUIDE-0001-OV
Evidence: EVIDENCE/blobs/<id>.yaml
Signed-off-by: <name <email>>
```

## 8. Glossary of Acronyms
- **ASI-T**: Aerospace Super-Intelligence Transformers.
- **CAx**: Computer-Aided X. Conjunto de 15 fases canónicas que modelan el ciclo de vida digital.
- **FCR**: Follow-up Chain Rules.
- **HOV**: Head-Of-Versions.
- **LLC**: Layer Logic Code.
- **MAL-EEM**: Master Application Layer — Ethics & Empathy Module.
- **MSN**: Manufacturer Serial Number.
- **QS**: Quantum State / Quantum Seal.
- **TFA**: Top Final Algorithm / Traceable Federated Architecture.
- **UIX**: Universal Injection Prompt.
- **UTCS**: Universal Traceability & Configuration System.
- **UTCS-MI**: UTCS Metadata Identifier.

### CAx Canónicos (Detalle)
- **STRATEGY**: Estrategia inicial del programa.
- **CAX-METHODOLOGY**: Metodología CAx a emplear.
- **CAB**: Brainstorming, Assessment & Setting.
- **CAIR**: Airworthiness & Certification Requirements (Requisitos de Aeronavegabilidad).
- **CAD**: Design (Diseño).
- **CAE**: Engineering (Ingeniería).
- **CAI**: Embedding HW·SW·AI (Integración de hardware, software e IA).
- **CAV**: Verification & Validation.
- **CAT**: Testing & Treatment.
- **CAM**: Manufacturing (Fabricación).
- **CA-PRO**: Production, Prototyping & Procurement.
- **CAO**: Organization (Gestión organizativa, PLM/PDM).
- **CAF**: Finance (Finanzas).
- **CAS0**: Sustainment & Supply (Sostenimiento y Cadena de Suministro).
- **CAEPOST**: End-of-Life (Fin de vida).