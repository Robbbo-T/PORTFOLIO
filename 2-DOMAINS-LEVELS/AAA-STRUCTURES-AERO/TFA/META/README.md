# AAA-STRUCTURES-AERO · TFA Hierarchy
**STRICT TFA-only.** All work lives under `TFA/<GROUP>/<LLC>/` — no flat LLC folders.  
**Scope:** Primary and secondary aircraft structures (e.g., fuselage, wing/empennage, control surfaces, doors, pylons, landing-gear attachments, pressurized barrels, frames, ribs, spars, skins, joints, composites/metallics).

> Owner: **Structures Domain Stewards** · Reviewers: **Chief Architect**, **Compliance Lead**  
> Last updated: 2025-09-10

---

## 1) What lives where (TFA map)

```

AAA-STRUCTURES-AERO/
└─ TFA/
├─ SYSTEMS/
│  ├─ SI/  # System Integration: DMU baselines, loads envelopes, interfaces
│  ├─ SE/  # Systems Engineering: requirements, SysML models, traceability
│  └─ DI/  # Digital Integration: PLM/ALM hooks, schemas, pipelines
├─ COMPONENTS/
│  ├─ CE/  # Component Engineering: designs, allowables, analyses
│  ├─ CC/  # Component Control: configs, revisions, EBOM/SBOM alignment
│  ├─ CI/  # Component Integration: joints/fasteners, stack-ups, tolerances
│  ├─ CP/  # Component Production: NC, routings, work instructions links
│  └─ CV/  # Component Verification: reports, review packs, conformity
├─ ELEMENTS/
│  └─ FE/  # Finite elements: meshing guides, FEMs, submodels, decks
├─ STATES/
│  └─ QS/  # Quality States (readiness gates, sign-offs, releases)
└─ META/
└─ README.md  # this file

```

**Rule of thumb**
- **Requirements & interfaces:** `SYSTEMS/SE`, `SYSTEMS/SI`  
- **Design & analysis artifacts (CAD/CAE/allowables):** `COMPONENTS/CE`  
- **FEM & solvers:** `ELEMENTS/FE`  
- **Readiness, reviews & releases:** `STATES/QS`

---

## 2) Domain scope & boundaries

**In-scope**
- Airframe primary/secondary structures (metallic & composite).
- Loads, strength, stiffness, stability, fatigue, damage tolerance, crashworthiness at structure level.
- Detail/joint design (riveted/bolted/bonded), allowables, margins of safety (MoS).
- Structural test (coupon → element → sub-component → full-scale) evidence threads.

**Out-of-scope (refer)**
- **Propulsion** mounts & nacelles details → `PPP-PROPULSION-FUEL`
- **Avionics/electrical harness** supports → `EDI-ELECTRONICS`
- **Flight controls actuation** structure interfaces → `LCC-CONTROLS-COMMS`
- **Ground handling/fixtures** → `AAP-GROUND-SUPPORT`

---

## 3) Interfaces (minimum contracts)

| Partner Domain            | Interface Artifact (example)                                    | Stored At                        |
|--------------------------|------------------------------------------------------------------|----------------------------------|
| OOO-OS-NAVIGATION        | Flight envelope / mission profiles                               | `SYSTEMS/SI/interfaces/`         |
| LCC-CONTROLS-COMMS       | Control surface hinge loads / actuator reaction loads            | `SYSTEMS/SI/interfaces/`         |
| PPP-PROPULSION-FUEL      | Pylon/engine mount loads & thermal zones                         | `SYSTEMS/SI/interfaces/`         |
| EEE-ENVIRONMENTAL        | Pressurization cycles & temperature/condensation environments    | `SYSTEMS/SE/reqs/`               |
| LIB-LOGISTICS-CHAIN      | Part genealogy & CoC (traceability)                              | `SYSTEMS/DI/data-contracts/`     |

> **Every interface** must have: owner, version, units, coordinate system, and change log.

---

## 4) Compliance & evidence threads (examples)

- **Airworthiness & methods:** structural strength & fatigue/damage-tolerance, composite substantiation, static/fatigue test plans, conformity records.  
- **Standards & formats (recommended):**  
  - Requirements/MBSE: SysML models with ID'd requirements and allocations.  
  - CAD exchange: STEP AP242; lightweight JT for DMU.  
  - FEA: NASTRAN/ABAQUS decks (`.bdf/.nas/.inp`), results (`.op2/.odb`) with run cards.  
  - Docs: S1000D DMC IDs for maintenance-relevant structure tasks (link only).  
- **Evidence storage pattern:** keep calculation notes, scripts, and solver inputs alongside reports; index in `CV/evidence/INDEX.md`.

> Map each certification objective → test/analysis → artifact link (one table per program).

---

## 5) Data conventions

- **Units:** SI (N, mm, MPa, kg, °C). If non-SI appears, include explicit conversion and rationale.  
- **CSYS:** Right-handed; define global and local part CSYS per assembly guide.  
- **File naming:**  
  - `AAA_<Area>_<Part>_<DocType>_v<MAJOR>.<MINOR>.<ext>` (e.g., `AAA_WING_RIB5_FEM_v1.3.bdf`)  
  - Analyses include load case & revision: `AAA_FUSE_SEC19_STATIC_LC12_MoS_v2.0.xlsx`  
- **Metadata header (YAML front-matter where possible):** author, owner, domain link, TFA path, loads set, material set, solver version, checksum.

---

## 6) Readiness gates (STATES/QS)

| Gate | Meaning                                  | Exit Criteria (all true)                                                  |
|------|-------------------------------------------|---------------------------------------------------------------------------|
| QS-0 | Draft / WIP                               | Owner assigned; TFA path valid; initial requirements linked               |
| QS-1 | Pre-review                                | CAD/mesh sanity; key interfaces stubbed; unit/CSYS checks pass            |
| QS-2 | Design/Analysis review ready              | Loads set frozen; MoS ≥ targets (or open risks logged); peer review done  |
| QS-3 | Verification complete                     | Reports signed; evidence indexed; test/analysis correlation if applicable |
| QS-4 | Released to downstream                    | Config frozen; PLM/BoM synced; change control active                      |
| QS-5 | In service / feedback loop                | Field data hooks live; CAPA pipeline established                          |

---

## 7) KPIs (track in `META/metrics.md`)

- **Weight/stiffness** vs. targets; **MoS** distribution by LC; **fatigue life** margins.  
- **NCRs** open → closure lead time; **interface churn** rate; **re-analysis cycle time**.  
- **Test correlation error** (strain/deflection); **data lineage completeness** (% artifacts linked).

---

## 8) Minimal checklists

### PR checklist (paste into PR)
- [ ] TFA path respected (`TFA/<GROUP>/<LLC>/…`)  
- [ ] Domain thread referenced (issue/RFC)  
- [ ] Units & CSYS declared; filenames follow convention  
- [ ] Interfaces updated & versioned (if touched)  
- [ ] Evidence indexed in `CV/evidence/INDEX.md`  
- [ ] QS gate updated; reviewers assigned (Structures Steward + Compliance)

### Analysis package (CE/FE)
- [ ] Loads & boundary conditions documented  
- [ ] Materials/allowables cited; laminate/stack details included (if composite)  
- [ ] Mesh quality checks captured  
- [ ] Solver version & run card saved; post-proc scripts included  
- [ ] MoS tables for all applicable LCs; sensitivities/assumptions listed

---

## 9) Templates & examples

- Report & calc note templates → `8-RESOURCES/TEMPLATES/`  
- Example FEM pack → `ELEMENTS/FE/examples/`  
- Interface contract template → `SYSTEMS/SI/interfaces/_template.md`  
- Evidence index starter → `COMPONENTS/CV/evidence/INDEX.md`  

---

## 10) Change control

- Breaking structural changes require RFC (`7-GOVERNANCE/COMMUNITY/RFC/`) and an ADR entry (`7-GOVERNANCE/DECISIONS/`).  
- Tag domain releases with `aaa-structures-aero-vX.Y`.

---

## 11) Contacts

- **Domain Steward (primary):** _TBD_  
- **Compliance Lead:** _TBD_  
- **Escalation:** Chief Architect (tie-break & safety override)

---
