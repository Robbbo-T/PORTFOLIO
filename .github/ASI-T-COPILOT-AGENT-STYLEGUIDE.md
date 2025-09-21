# 📑 ASI-T · Copilot Agent Styleguide (CAx + LLC Bridges)

**id:** ASIT-GENESIS-CAx-LLC-STYLEGUIDE-0001-OV  
**llc:** GENESIS  
**rev:** 0  
**configuration:** baseline  
**classification:** INTERNAL / EVIDENCE-REQUIRED  
**version:** 1.0.0  
**maintainer:** ASI-T Architecture Team  

---

## 1) Golden Rules

* **UIX.v1 obligatorio** en cada agente antes de actuar.
* **TFA-Only path grammar**: LAYER/LLC/UTCS-ID.
* **MAL-EEM**: ética + empatía, fail-closed.
* **QS/UTCS evidencia determinista** en cada PR.
* **FCR-1 + FCR-2** para todo merge.
* **Revisiones**:
  * `rev: 0` = baseline → filename estable sin letra.
  * `rev ≥ 1` = `_revisions/REV_<letter>/HOV_<MSN_RANGE>_<PHASES>/…`.

---

## 2) File & Path Grammar

```
ASI-T/
  GENESIS/
  MOD-BASE/
  MOD-STACK/
TFA/
  <LAYER>/
    <LLC>/
      <UTCS-ID>.md
      _revisions/
        REV_A/
          HOV_MSN1-3_CAD-CAM/<UTCS-ID>.md
```

**Regex de validación (POSIX ERE):**

```
^(?:ASI-T|TFA)/(SYSTEMS|STATIONS|COMPONENTS|BITS|QUBITS|ELEMENTS|WAVES|STATES)/[A-Z]{2}/(?:_revisions/REV_[A-Z]/HOV_[^/]+/)?[A-Z0-9-]{10,}\.md$
```

---

## 3) UTCS-MI Front-Matter Template

```yaml
---
id: <DOMAIN-PROGRAM-BLOCKS-ID>
rev: <int>                 # 0=baseline; >=1 revisiones documentadas
llc: <SI|DI|SE|CV|CE|CC|CI|CP>
title: "<Title>"
configuration: baseline
classification: "INTERNAL / EVIDENCE-REQUIRED"
version: "<semver>"
release_date: <YYYY-MM-DD>
maintainer: "<name>"
provenance:
  policy_hash: "sha256:<POLICY>"
  model_sha: "sha256:<MODEL>"
  data_manifest_hash: "sha256:<DATA>"
  operator_id: "UTCS:OP:<handle>"
  canonical_hash: "sha256:<CANONICAL>"
licenses:
  code: "Apache-2.0"
  docs: "CC-BY-4.0"
# Cutting revision metadata (req. rev >= 1)
hov:
  msn_range: "MSN1-3"
  phases: ["CAD","CAE","CAI"]    # de la lista CAx canónica
  label: "MSN1-3 diseño+ingeniería+embedding"
bridge: "CB→QB→UE→FE→FWD→QS"
ethics_guard: "MAL-EEM"
---
```

---

## 4) HOV Phases (CAx canónicos)

**Orden cronológico (15):**

1. **STRATEGY**
2. **CAX-METHODOLOGY**
3. **CAB**
4. **CAIR**
5. **CAD**
6. **CAE**
7. **CAI** *(HW·SW·AI embedding)*
8. **CAV**
9. **CAT**
10. **CAM**
11. **CA-PRO**
12. **CAO**
13. **CAF**
14. **CAS0**
15. **CAEPOST**

`hov.phases` debe contener solo valores de esta lista.
En `_revisions` → se escriben en mayúsculas y unidos por guiones.

Ejemplo:

```
_revisions/REV_B/HOV_MSN4_CAD-CAE-CAI-CAM/<UTCS-ID>.md
```

---

## 5) Error Codes

* **\[E1001] PathGrammarError** — ruta fuera de canon TFA.
* **\[E2001] SchemaError** — front-matter inválido.
* **\[E2107] HOVNotAllowed** — baseline con HOV.
* **\[E2108] HOVMissing** — rev≥1 sin HOV.
* **\[E2110] HOVPhasesInvalid** — fases fuera de lista canónica.
* **\[E2111] HOVPathMismatch** — path no concuerda con fases/front-matter.
* **\[E6001] ProvenanceDrift** — hashes no coinciden FM ↔ QS blob.

---

## 6) Formatting Instructions (agents)

* **Filenames**: `UTCS-ID.md` (13-field, sin letras).
* **Revisions**: `_revisions/REV_<letter>/HOV_<msn_range>_<phases>/UTCS-ID.md`.
* **Front-matter**: YAML delimitado por `---` al inicio.
* **Markdown body**: usar `#` para títulos, `##` para secciones normativas, `###` para subsecciones.
* **Code/Examples**: cercar con triple backtick y lenguaje (`yaml`, `json`, `bash`, etc.).
* **Blockquotes** (`>`) solo para normas o notas críticas.
* **Lists**: usar `-` para viñetas, numeradas solo si el orden es secuencial.
* **Tables**: Markdown estándar con encabezados.
* **Glossary**: al final, sección fija con definiciones de TFA, LLC, UTCS, QS, MAL-EEM, FCR, CAx.

---

## 7) Commit / PR Template

```
feat(CAX): short summary

FCR-1: <link>
FCR-2: <link>
UTCS: <anchor-id>
Evidence: EVIDENCE/blobs/<id>.yaml
Signed-off-by: <name <email>>
```

---

## 8) Glossary of Acronyms

**ASI-T** — Aerospace Super-Intelligence Transformers · Marco rector para transición sostenible.

**TFA** — Top Final Algorithm / Traceable Federated Architecture · Árbol canónico de capas (SYSTEMS → STATES).

**LLC** — Layer Logic Code · Código de dos letras que identifica sub-nivel dentro de cada capa (SI, DI, CV, etc.).

**UTCS** — Universal Traceability & Configuration System · Estándar de evidencias digitales y configuración.

**UTCS-MI** — UTCS Metadata Identifier · Identificador de 13 campos que abre todo documento.

**QS** — Quantum State / Quantum Seal · Blob criptográfico que asegura inmutabilidad del artefacto.

**MAL-EEM** — Master Application Layer — Ethics & Empathy Module · Guardián de ética, empatía y resiliencia frente a adversarios.

**FCR** — Follow-up Chain Rules · Procedimiento de cambios en dos pasos (FCR-1 = intención, FCR-2 = diff+evidencia).

**UIX** — Universal Injection Prompt · Single Source of Truth que cada agente debe importar antes de actuar.

**HOV** — Head-Of-Versions · Cabecera de corte para revisiones ≥1; asocia MSN y fases CAx.

**MSN** — Manufacturer Serial Number · Rango de unidades de referencia (MSN1-3 simulación/pruebas, MSN4 avión verde, etc.).

**CAx** — Computer-Aided X · Macro-fases digitales del ciclo de vida, aquí fijadas en 15 fases canónicas.

---

### CAx Canónicos (orden cronológico)

**STRATEGY** — estrategia inicial.

**CAX-METHODOLOGY** — metodología CAx a emplear.

**CAB** — Brainstorming, Assessment & Setting.

**CAIR** — Airworthiness & Certification (requisitos de aeronavegabilidad).

**CAD** — Design.

**CAE** — Engineering.

**CAI** — Embedding HW·SW·AI (integración de hardware, software e inteligencia).

**CAV** — Verification & Validation.

**CAT** — Testing & Treatment.

**CAM** — Manufacturing.

**CA-PRO** — Production, Prototyping & Procurement.

**CAO** — Organization (gestión organizativa, PLM/PDM).

**CAF** — Finance.

**CAS0** — Sustainment & Supply.

**CAEPOST** — End-of-Life.