# Quantum–Classical Bridge (TFA V2)

> Hybrid computation, federation, wave dynamics, and audit-grade state across **15 domains** and **5 segments** (AIR · SPACE · GROUND · **DEFENSE** · **CROSS**), aligned to the **TFA** hierarchy and the **OPTIMO-DT** digital thread.

* **Scope**: This document specifies the **Bridge stack** (CB/QB/UE/FE/FWD/QS), its **MAL** services, contracts, safety, CI checks, and program-scale usage with **MAPs**.
* **Audience**: Domain leads (MAP owners), platform engineers (MAL owners), systems/MBSE, DevSecOps, mission ops.

---

## 1) Layer Stack Overview

| Order | Code    | Name                    | Group    | Core Role                               | Typical Tech                    |
| ----: | ------- | ----------------------- | -------- | --------------------------------------- | ------------------------------- |
|     1 | **CB**  | Classical Bit           | BITS     | Deterministic compute, solvers, control | HPC, Python/C/Rust, RTOS        |
|     2 | **QB**  | Qubit                   | QUBITS   | Quantum strategies/experiments          | QAOA/VQE, annealing, simulators |
|     3 | **UE**  | Unit Element            | ELEMENTS | Canonical primitives & unit ops         | Typed kernels, safety wrappers  |
|     4 | **FE**  | Federation Entanglement | ELEMENTS | Multi-asset coordination, policy        | Multi-agent, consensus, C2      |
|     5 | **FWD** | Future/Waves Dynamics   | WAVES    | Nowcasts, predictive/retrodictive       | Filtering, PDEs, ML forecasting |
|     6 | **QS**  | Quantum State           | STATES   | State, provenance, evidence             | Signed states, UTCS anchoring   |

**Flow**: `CB → QB → UE/FE → FWD → QS` (not strictly linear; layers may short-circuit via contracts).

* **MAP** = Master Application Program per domain (e.g., **MAP-AAA**, **MAP-PPP**).
* **MAL-x** = Main Application Layer service per Bridge layer (e.g., **MAL-CB**, **MAL-QB**).

> Browse domains: [`../2-DOMAINS-LEVELS/`](../2-DOMAINS-LEVELS/) · OPTIMO-DT: see [`../8-RESOURCES/`](../8-RESOURCES/) templates and thread.

---

## 2) MAL Services (Interfaces & Contracts)

Each MAL exposes a **stable service contract** (gRPC/HTTP+JSON or message bus) with a common envelope plus a type-specific payload.

### 2.1 Common Envelope (all MALs)

```json
{
  "trace_id": "uuid",
  "tfa": { "domain": "AAA", "map": "MAP-AAA", "layer": "CB|QB|UE|FE|FWD|QS" },
  "segment": "AIR|SPACE|GROUND|DEFENSE|CROSS",
  "intent": "optimize|schedule|nowcast|commit_state|...",
  "security": { "actor": "urn:role:MAP-AAA", "scopes": ["compute:run","state:write"] },
  "provenance": { "parent_state": "qs://...", "inputs": ["uri://..."] },
  "deadline_ms": 300,
  "quality": { "precision": "high", "energy_budget": "normal" }
}
```

### 2.2 MAL-CB (Classical)

* **Purpose**: Deterministic solvers, control loops, real-time kernels.
* **Key ops**: `solve`, `simulate`, `control_step`.
* **SLO**: P50 ≤ 120 ms (domain op), P99 ≤ 300 ms; RT variants for flight/robotics.
* **Fallback**: Always available; acts as **QB** fallback.

### 2.3 MAL-QB (Quantum)

* **Purpose**: Dispatch quantum strategies; select provider/simulator; return result + confidence.
* **Key ops**: `optimize_qaoa`, `estimate_vqe`, `anneal`, `simulate`.
* **SLO**: P50 ≤ 900 ms (sim/local), provider-backed as-available with **deadline enforcement**.
* **Safety**: **Two-man rule** policy option for DEFENSE; experiment gating.

### 2.4 MAL-UE (Unit Element)

* **Purpose**: Typed, reusable primitives (geometry ops, unit conversions, safety-checked kernels).
* **Key ops**: `transform`, `aggregate`, `validate_units`.

### 2.5 MAL-FE (Federation)

* **Purpose**: Multi-asset scheduling, deconfliction, coalition policy, cross-org data sharing.
* **Key ops**: `negotiate`, `allocate`, `schedule`, `publish_topology`.
* **Profiles**: **Ops-Safe**, **Regulated**, **Defense-C2** (adds ROE, mission phases).

### 2.6 MAL-FWD (Waves)

* **Purpose**: Nowcasts, scenario rolls, predictive/retrodictive fields.
* **Key ops**: `nowcast`, `forecast`, `retrodict`, `assimilate`.
* **Inputs**: Sensor streams, weather, mission telem, external feeds.

### 2.7 MAL-QS (State & Provenance)

* **Purpose**: Authoritative state transitions + evidence bundles.
* **Key ops**: `commit_state`, `query_lineage`, `export_evidence`.
* **Anchoring**: Optional **UTCS** anchors under `../6-UTCS-BLOCKCHAIN/`.

---

## 3) Schemas & Examples

### 3.1 Route Optimization (CB/QB → FWD → QS)

* Schema: [`../services/aqua-os-pro/schemas/route_optimization.json`](../services/aqua-os-pro/schemas/route_optimization.json)
* Orchestrator: [`../services/aqua-os-pro/core/aqua_pro_orchestrator.py`](../services/aqua-os-pro/core/aqua_pro_orchestrator.py)

```yaml
# MAL-QB selection policy
mal_qb:
  providers: [simulator_local, provider_alpha]
  strategy: "QAOA"
  budget_ms: 800
  fallback: "MAL-CB.solve"
```

```python
# Pseudocode orchestration (inside a MAP)
plan = MAL_CB.solve(model, constraints, deadline=0.12)
if need_quantum(plan) and budget_allows():
    q = MAL_QB.optimize_qaoa(plan.to_qubo(), deadline=0.8)
    plan = choose_better(plan, q)
field = MAL_FWD.nowcast(area, t_horizon=600)
schedule = MAL_FE.allocate(assets, plan, field)
state = MAL_QS.commit_state(program="AMPEL360", artifact=schedule)
```

### 3.2 QS State (signed, anchorable)

```json
{
  "id": "qs://ampel360/flightplan/2025-09-10T12:00Z",
  "hash": "blake3:...",
  "signatures": ["did:org:OEM#key1:..."],
  "lineage": ["qs://.../inputs/*"],
  "evidence": [
    {"type":"schema","uri":"git+file://.../route_optimization.json@abcd"},
    {"type":"runlog","uri":"s3://.../aqua-pro/run/123"}
  ],
  "utcs_anchor": "utcs://chain/tx/0xabc..."  // optional
}
```

---

## 4) Execution Model & Cadence

* **Loop**: `Sense → Decide (CB/QB/UE/FWD) → Coordinate (FE) → Commit (QS)` every **30s** (ops), **10-min** full refresh (planning), real-time micro-loops for control.
* **Deadlines**: Each call carries a `deadline_ms`; MALs **must** honor it.
* **Determinism**: All non-deterministic ops (QB/FWD) must attach seeds + confidence.
* **Isolation**: QB experiments run in sandboxes; FE uses policy envelopes.

**Performance targets (typical ops mode)**

| Layer          |    P50 |    P95 | Notes                 |
| -------------- | -----: | -----: | --------------------- |
| CB             | 120 ms | 300 ms | Deterministic         |
| QB (sim/local) | 400 ms | 900 ms | Falls back to CB      |
| FE             | 150 ms | 400 ms | Topology ≤ 500 assets |
| FWD            | 200 ms | 600 ms | Nowcast tiles ≤ 1e4   |
| QS commit      |  80 ms | 200 ms | Anchor async          |

---

## 5) Safety, Security & Compliance

* **Zero-Trust** MALs: mTLS, mutual attestation, signed envelopes.
* **RBAC/ABAC**: `security.scopes` audited in QS.
* **Defense profile** (DEFENSE segment): ROE, mission phase guards, **two-man rule** for `QB` and `FE` high-impact actions.
* **Regulatory**: Exports to **S1000D**, MBSE sync via OPTIMO-DT.
* **Data hygiene**: Typed units in UE, schema versioning, redaction policies on FE topics.
* **CI**: Terminology guards (rejects `Fine~Element`, `Station~Envelop`), structure/layer presence.

---

## 6) Integration with TFA & OPTIMO-DT

* **TFA** trees per domain enforce SI/DI interfaces that **bind** MAPs to MALs.
* **OPTIMO-DT** keeps **Organization → Process → Technical → AI** thread coherent across **AIR/SPACE/GROUND/DEFENSE/CROSS**.
* Templates: [`../8-RESOURCES/TEMPLATES/`](../8-RESOURCES/TEMPLATES/) · CI: [`../.github/workflows/`](../.github/workflows/)

Mermaid overview:

```mermaid
flowchart LR
  subgraph MAPs (Domains)
    AAA[MAP-AAA] --- PPP[MAP-PPP] --- EDI[MAP-EDI] --- LCC[MAP-LCC] --- IIS[MAP-IIS]
  end
  subgraph MALs
    CB[MAL-CB] --- QB[MAL-QB] --- UE[MAL-UE] --- FE[MAL-FE] --- FWD[MAL-FWD] --- QS[MAL-QS]
  end
  MAPs --> MALs
  MALs --> OPT[OPTIMO-DT]
  QS --> UTCS[UTCS Anchors]
```

---

## 7) Program Patterns (Segments)

### AIR — **AMPEL360 BWB-Q100**

* **MAPs**: AAA, PPP, EDI, LCC, EEE, EER, DDD, IIS
* **Bridge**: Flight plan loops via **CB/QB**, **FWD** nowcasts, **FE** deconfliction, **QS** certification evidence.
* Config: [`../3-PROJECTS-USE-CASES/`](../3-PROJECTS-USE-CASES/)

### SPACE — **GAIA Quantum SAT**

* **MAPs**: LCC, CQH, EDI, LIB, IIS
* **Bridge**: QB experiments (links), FE constellation scheduling, FWD space weather, QS mission ledger.

### GROUND — **Diagnostics & MRO Robbbo-t**

* **MAPs**: MMM, EDI, IIS, LIB (+ CAS/CAV)
* **Bridge**: UE safety-checked robot kernels, FE tasking, QS maintenance record.

### **DEFENSE** — **ARES-X UAS Swarm**

* **MAPs**: DDD, LCC, EDI, MMM, IIS, LIB
* **Bridge**: FE with **C2/ROE**, QB for combinatorial mission planning, QS mission assurance; **two-man rule** gates.

### **CROSS** — **H2-CORRIDOR-X**

* **MAPs**: IIF, OOO, LIB, EEE, EER, IIS, LCC
* **Bridge**: FE cross-sector topology (air/road/port/grid), FWD supply/energy flows, QS provenance.

---

## 8) CI, Validation & Quality Gates

* **Structure**: `tfa_structure_validator.yml` — every domain has `TFA/…` with LLC buckets present.
* **Quantum Layers**: `quantum-layers-check.yml` — enforces **CB/QB/UE/FE/FWD/QS** presence and terminology.
* **Link & Quality**: `link-and-quality.yml` — broken links, linting, format.
* **UTCS Anchor**: `anchor_utcs.yml` — optional evidence anchoring.

> See [`../.github/workflows/`](../.github/workflows/) for exact jobs.

---

## 9) Local Dev & Emulation

```bash
# Create trees + templates
make scaffold

# Validate layers + terminology
make check

# Demo: AQUA-OS PRO orchestrator
python3 ../services/aqua-os-pro/core/aqua_pro_orchestrator.py
```

**Emulation tips**

* Set `MAL_QB_MODE=sim` to force local simulators.
* Use `DEADLINE_MS` to test time-bound fallbacks.
* Toggle **defense profile** with `PROFILE=defense` to enable ROE/two-man rule mocks.

---

## 10) Extension Patterns

* **Add a quantum strategy**: Implement `MAL-QB:<strategy>` + register in provider selector.
* **New FE topology**: Provide `negotiate/allocate` policies + schema version bump.
* **New QS state**: Add a `kind`, update validator, extend export adapters (S1000D/MBSE).
* **Observability**: Emit OpenTelemetry spans with `trace_id` → **QS** lineage.

---

## 11) FAQs

**Q: Do I need quantum hardware?**
A: No. **MAL-QB** supports simulators and **must** fall back to **MAL-CB** within deadlines.

**Q: How do MAPs stay portable across segments?**
A: MAPs bind only to **MAL contracts**; segment profiles (AIR/SPACE/…) are policy overlays, not code forks.

**Q: Where does evidence live?**
A: In **QS** states with hashes/signatures; optional **UTCS** anchors provide external immutability.

---

## 12) Glossary

* **MAP**: Master Application Program per domain (e.g., MAP-AAA).
* **MAL**: Main Application Layer service per Bridge layer (CB/QB/UE/FE/FWD/QS).
* **OPTIMO-DT**: Digital Thread backbone (Org, Process, Technical, AI).
* **UTCS**: Universal Token Classification System for anchoring/provenance.
* **ROE**: Rules of Engagement (Defense profile).

---

## 13) Pointers

* Readme (host platform view): [`../README.md`](../README.md)
* AQUA-OS PRO (implemented): [`../services/aqua-os-pro/`](../services/aqua-os-pro/)
* Templates: [`../8-RESOURCES/TEMPLATES/`](../8-RESOURCES/TEMPLATES/)
* Domains (MAPs): [`../2-DOMAINS-LEVELS/`](../2-DOMAINS-LEVELS/)
* CI Workflows: [`../.github/workflows/`](../.github/workflows/)
* UTCS: [`../6-UTCS-BLOCKCHAIN/`](../6-UTCS-BLOCKCHAIN/)

---
