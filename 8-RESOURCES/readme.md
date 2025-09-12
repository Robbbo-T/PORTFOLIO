# 8-RESOURCES · Resource Hub

> **Everything you need to bootstrap, extend, and audit the TFA V2 ecosystem.**
> Templates, reference docs, style guides, example datasets, and CI hooks—organized for fast reuse across AIR · SPACE · GROUND · DEFENSE · CROSS.

[← Back to Root README](../README.md) · [TFA Architecture](./TFA-ARCHITECTURE.md) · [Quantum–Classical Bridge](../docs/quantum-classical-bridge.md) · [AQUA-OS PRO Spec](../services/aqua-os-pro/AQUA-OS-PRO-SPEC.md)

---

## 📚 Index

1. [What lives here](#-what-lives-here)
2. [Template Packs](#-template-packs)
   2.1 [TFA-Layer Templates (SI/DI/…/QS)](#tfa-layer-templates) · 2.2 [CAx Lifecycle Templates](#cax-lifecycle-templates) · 2.3 [Segment Packs (AIR/SPACE/GROUND/DEFENSE/CROSS)](#segment-packs)
3. [MAP/MAL Resource Kits](#-mapmal-resource-kits)
4. [Schemas, Data & Sample Assets](#-schemas-data--sample-assets)
5. [Style & Conventions](#-style--conventions)
6. [CI Hooks & Validators](#-ci-hooks--validators)
7. [How to use](#-how-to-use)
8. [Quality Gates (Checklist)](#-quality-gates-checklist)
9. [FAQs](#-faqs)

---

## 📦 What lives here

* **Templates** for every TFA layer and CAx phase
  `./TEMPLATES/…`
* **Architecture guides** and reference docs
  [TFA-ARCHITECTURE.md](./TFA-ARCHITECTURE.md) · [Quantum–Classical Bridge](../docs/quantum-classical-bridge.md)
* **Schemas** used across services (AQUA-OS, OPTIMO-DT)
  Primary: [AQUA-OS PRO Route Schema](../services/aqua-os-pro/schemas/route_optimization.json)
* **Style guides** (naming, folders, metadata)
  See [TEMPLATES/META/README.md](./TEMPLATES/META/README.md)
* **Example assets** (Mermaid diagrams, icons, placeholder datasets)
  `./ASSETS/…` *(add as needed)*

---

## 🧩 Template Packs

### TFA-Layer Templates

Starter docs and stubs for every **LLC** code. Copy them into a domain’s `TFA/<GROUP>/<LLC>/` and fill placeholders.

* Systems

  * **SI**—System Integration → `TEMPLATES/TFA-LAYER-TEMPLATES/SYSTEMS-TEMPLATES/SI-SYSTEM-INTEGRATION/`
  * **DI**—Domain Interface → `TEMPLATES/TFA-LAYER-TEMPLATES/SYSTEMS-TEMPLATES/DI-DOMAIN-INTERFACE/`
* Stations

  * **SE**—Station Envelope → `TEMPLATES/TFA-LAYER-TEMPLATES/STATIONS-TEMPLATES/SE-STATION-ENVELOPE/`
* Components

  * **CV/CE/CC/CI/CP** → `TEMPLATES/TFA-LAYER-TEMPLATES/COMPONENTS-TEMPLATES/…`
* Bits & Qubits

  * **CB**—Classical Bit → `TEMPLATES/TFA-LAYER-TEMPLATES/BITS-TEMPLATES/CB-CLASSICAL-BIT/`
  * **QB**—Qubit → `TEMPLATES/TFA-LAYER-TEMPLATES/QUBITS-TEMPLATES/QB-QUBIT/`
* Elements & Waves & States

  * **UE/FE/FWD/QS** → `TEMPLATES/TFA-LAYER-TEMPLATES/ELEMENTS-TEMPLATES/…`, `WAVES-TEMPLATES/FWD-…/`, `STATES-TEMPLATES/QS-QUANTUM-STATE/`

> 🔎 Each template uses **placeholder tokens** like `{{PROGRAM}}`, `{{DOMAIN}}`, `{{LLC}}`. See [META guide](./TEMPLATES/META/README.md).

### CAx Lifecycle Templates

Process documentation and checklists across **CAB → CAV**:
`TEMPLATES/CAX-LIFECYCLE-TEMPLATES/` *(e.g., CAB-BRAINSTORMING, CAD-DESIGN, CAT-TESTING, CAV-VERIFICATION)*

### Segment Packs

Opinionated presets per **segment**:

* **AIR**: Aero & propulsion presets, route optimization, emissions KPIs
* **SPACE**: Mission design, constellation scheduling, quantum links
* **GROUND**: MRO/Robbbo-t diagnostics, logistics, safety
* **DEFENSE**: RMF/NIST/STIG checklists, classification boundaries, FE policies
* **CROSS**: Cross-sector adapters (ATM, energy, mobility), data interoperability

> DEFENSE & CROSS include **policy scaffolds**, **PTP/time-sync notes**, and **federation (FE)** patterns for multi-entidad/país.

---

## 🗺️ MAP/MAL Resource Kits

A **MAP** (Master Application Program) per domain + **MAL** (Main Application Layer) por capa bridge:

* **MAP Kits** (per domain AAA…PPP)
  `TEMPLATES/MAP/<DOMAIN>/` *(create from TFA templates; wire to APIs in DI)*
* **MAL Kits** (CB/QB/FWD/QS/FE/UE)
  `TEMPLATES/MAL/<LAYER>/` *(shared, horizontal services)*

**Examples / How they compose:**

* **AMPEL360 BWB-Q100 (AIR)**
  MAP-AAA, MAP-PPP, MAP-EDI, MAP-LCC + MAL-CB/QB/FWD/QS/FE
* **GAIA Quantum SAT (SPACE)**
  MAP-LCC, MAP-CQH, MAP-EDI, MAP-LIB, MAP-IIS + MAL-QB/FE/QS
* **Diagnostics & MRO Robbbo-t (GROUND)**
  MAP-MMM, MAP-EDI, MAP-IIS, MAP-LIB + MAL-FWD/QS/FE

Learn more: [Quantum–Classical Bridge](../docs/quantum-classical-bridge.md) · [AQUA-OS PRO Spec](../services/aqua-os-pro/AQUA-OS-PRO-SPEC.md)

---

## 🧾 Schemas, Data & Sample Assets

* **AQUA-OS PRO Route Schema**
  `services/aqua-os-pro/schemas/route_optimization.json` *(requests/responses, waypoints, performance envelopes, provenance QS/UTCS)*

* **Example program config (YAML)**

  ```yaml
  program: AMPEL360-BWB-Q100
  segments: [AIR]
  maps: [AAA, PPP, EDI, LCC]
  mals: [CB, QB, FWD, QS, FE]
  policies:
    ci_required: [tfa_structure_validator, quantum-layers-check]
    export_standards: [S1000D, MBSE]
  ```

* **Sample diagrams** (Mermaid)
  Place in `ASSETS/diagrams/` and embed in specs.

---

## 🎨 Style & Conventions

* **Naming**: `CODE-NAME-WITH-DASHES/` (e.g., `AAA-AERODYNAMICS-AND-AIRFRAMES-ARCHITECTURES`)
* **LLC folders only** under `TFA/<GROUP>/<LLC>/` (no flat LLC under domain root)
* **Template files**: `specification.template.yaml`, `README.template.md`
* **Placeholders**: `{{UPPER_SNAKE}}` for required; `[optional]` for optional blocks
* **Doc badges**: MIT, TFA-V2, Layers, CI validators
* **Compliance**: S1000D exports, DO-178C/254 traces collected in **QS** + **UTCS** anchors

> Style reference: [TEMPLATES/META/README.md](./TEMPLATES/META/README.md)

---

## 🧪 CI Hooks & Validators

* Structure: `.github/workflows/tfa_structure_validator.yml`
* Quantum layers & terminology guard: `.github/workflows/quantum-layers-check.yml`
* Links & Quality: `.github/workflows/link-and-quality.yml`
* UTCS Anchors: `.github/workflows/anchor_utcs.yml`

All template packs are **CI-aware**: copying them preserves structure & required sections.

---

## ⚡ How to use

### 1) Scaffold & Validate

```bash
make scaffold     # create missing TFA trees
make check        # validate TFA + quantum layers + links
```

### 2) Start with a TFA layer template

```bash
# Example: new SI under AAA
cp -r 8-RESOURCES/TEMPLATES/TFA-LAYER-TEMPLATES/SYSTEMS-TEMPLATES/SI-SYSTEM-INTEGRATION/* \
      2-DOMAINS-LEVELS/AAA-AERODYNAMICS-AND-AIRFRAMES-ARCHITECTURES/TFA/SYSTEMS/SI/
```

### 3) Wire a MAP & MAL

* Fill **DI** APIs in the domain MAP.
* Attach MAL services (CB/QB/FWD/QS/FE) per the program’s needs.

### 4) Run AQUA-OS PRO (if applicable)

See orchestrator and validator:
`services/aqua-os-pro/core/aqua_pro_orchestrator.py` ·
`services/aqua-os-pro/validation/aqua_pro_validator.py`

---

## ✅ Quality Gates (Checklist)

* [ ] **TFA path**: `TFA/<GROUP>/<LLC>/` only
* [ ] **Spec completeness**: sections for Context · Contracts · Perf · Tests · Security · Compliance
* [ ] **DI contracts**: OpenAPI/Proto present & versioned
* [ ] **QS/UTCS**: provenance fields mapped (ids, hashes, anchors)
* [ ] **FE policies**: roles/tenants, sharing rules, consensus/CRDT notes
* [ ] **FWD metrics**: horizons, accuracy, baselines
* [ ] **QB/CB**: fallback path documented & tested
* [ ] **CI status**: all validators green

---

## ❓ FAQs

**Q: How do DEFENSE and CROSS differ?**
**A:** DEFENSE adds RMF/NIST/STIG guidance, classification boundaries, and FE policies for multi-org operations. CROSS ships adapters and data contracts to link with ATM, energy, mobility, etc.

**Q: Where do I start for a new program (e.g., AMPEL360)?**
**A:** Copy relevant **MAP** templates (AAA/PPP/EDI/LCC), add **MAL** packs (CB/QB/FWD/QS/FE), wire DI contracts, then validate with CI. Use **AQUA-OS PRO** for route cycles and **OPTIMO-DT** for digital-thread continuity.

**Q: Can I reuse MALs across programs?**
**A:** Yes. MALs are horizontal services (CB/QB/FWD/QS/FE/UE) designed for reuse across domains and segments.

---

### Related

* [Root README](../README.md)
* [TFA Architecture](./TFA-ARCHITECTURE.md)
* [Quantum–Classical Bridge](../docs/quantum-classical-bridge.md)
* [AQUA-OS PRO Spec](../services/aqua-os-pro/AQUA-OS-PRO-SPEC.md)

---

*This folder is the accelerator for building coherent, auditable, multi-program aerospace systems—**quantum-ready**, **federated**, and **standards-aligned**.*
