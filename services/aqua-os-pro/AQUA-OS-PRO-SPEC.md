# AQUA-OS · Predictive Route Optimizer (PRO) — Product Specification

**Status:** Active · **Spec v1.2** · **Owner:** MAP-IIS / Platform Team
**Scope:** Route optimization loop across **15 TFA domains** and **5 segments** (AIR · SPACE · GROUND · DEFENSE · CROSS) using the **Quantum–Classical Bridge** (CB/QB/UE/FE/FWD/QS).
**Codebase:** [`services/aqua-os-pro/`](./)

---

## 0) Executive Summary

**PRO** is the host platform’s flight/mission path optimizer. It runs a **10-minute plan loop** with a **30-second cadence**, blending **classical solvers (CB)** with **quantum strategies (QB)**, fusing **nowcasts (FWD)**, coordinating **fleet constraints (FE)**, and committing **audit-grade states (QS)**.

* **Design goals**

  * Aero/mission aware routes with **≤ 300 ms** domain step latency (ops mode).
  * **Deterministic classical baseline** with **QB acceleration** when profitable.
  * **Federated deconfliction** (assets, airspace, spectrum, power, crew).
  * **Provable lineage** via **QS states** (+ optional **UTCS** anchoring).

* **Non-goals**

  * Building a full ATC, C2, or mission planner UI (separate products).
  * Long-range (> 24 h) strategic planning (handled by MAP-Program tools).

---

## 1) Architecture (MAP/MAL on TFA)

**PRO** is a **MAP-IIS** orchestrated application that binds to **MAL** services of the **Bridge**:

```mermaid
flowchart LR
  subgraph MAPs (Domains)
    AAA[MAP-AAA] --- PPP[MAP-PPP] --- EDI[MAP-EDI] --- LCC[MAP-LCC] --- IIS[MAP-IIS (Owner)]
  end
  subgraph MALs (Bridge)
    CB[MAL-CB (classical)] --- QB[MAL-QB (quantum)]
    UE[MAL-UE (units/primitives)] --- FWD[MAL-FWD (nowcasts)]
    FE[MAL-FE (federation)] --- QS[MAL-QS (state)]
  end
  PRO[AQUA-OS PRO] --> CB
  PRO --> QB
  PRO --> FWD
  PRO --> FE
  PRO --> QS
  MAPs --- PRO
```

* **MAPs (per domain)** provide models/constraints (e.g., **MAP-AAA** aerodynamic envelopes, **MAP-PPP** TSFC, **MAP-LCC** comms corridors).
* **MALs (per Bridge layer)** expose stable compute/state services used by PRO:

  * **MAL-CB**: classical solvers, control kernels
  * **MAL-QB**: QAOA/VQE/annealing provider selection with deadlines
  * **MAL-FWD**: nowcast tiles, scenario rolls
  * **MAL-FE**: fleet scheduling, deconfliction, coalition policy
  * **MAL-QS**: state commits, lineage, evidence (UTCS-anchor optional)
  * **MAL-UE**: typed units & safe primitives

**Host platform fit:** TFA trees enforce traceability; **OPTIMO-DT** keeps Org→Process→Technical→AI aligned.
See: [`../../docs/quantum-classical-bridge.md`](../../docs/quantum-classical-bridge.md)

---

## 2) Control Loop

**Cadence:** 30 s (ops loop) · **Refresh:** 10 min (full plan) · **Deadline per step:** 300 ms

**Stage A — Sense**

* Ingest MET tiles, traffic, NOTAMs, spectrum, power, terrain, constraints.
* Query **FWD** for short-horizon fields; normalize via **UE**.

**Stage B — Decide**

* Baseline solve with **CB** (deterministic, feasible).
* If **QB** budget allows and potential gain > threshold, run **QB**; pick better plan under deadline.

**Stage C — Coordinate**

* Send plan candidates to **FE** for deconfliction, allocation, sequencing, coalition policy.

**Stage D — Commit**

* Write outputs (`/traj/proposed`, `/traj/approved`) and **QS** state with evidence bundle; optionally anchor to **UTCS**.

---

## 3) Interfaces & Contracts

### 3.1 Common Envelope (all MAL calls)

```json
{
  "trace_id": "uuid",
  "tfa": { "domain": "AAA", "map": "MAP-AAA", "layer": "CB|QB|UE|FE|FWD|QS" },
  "segment": "AIR|SPACE|GROUND|DEFENSE|CROSS",
  "intent": "optimize|nowcast|schedule|commit_state",
  "security": { "actor": "urn:role:MAP-IIS", "scopes": ["compute:run","state:write"] },
  "deadline_ms": 300,
  "provenance": { "parent_state": "qs://...", "inputs": ["uri://..."] }
}
```

### 3.2 Route Optimization Schema (IO)

* **Canonical schema**: [`./schemas/route_optimization.json`](./schemas/route_optimization.json)

  * `route_request`: origin/destination, envelopes, weights, quantum config
  * `route_response`: waypoints, fuel/time/emissions, confidence, QS/provenance

### 3.3 gRPC (reference sketch)

```proto
service ProService {
  rpc Optimize(OptimizeRequest) returns (OptimizeResponse);
  rpc healthz(HealthRequest) returns (HealthResponse);
}

message OptimizeRequest { bytes envelope_json = 1; }
message OptimizeResponse { bytes route_response_json = 1; }
```

> HTTP+JSON is also supported via the same schema.

---

## 4) Configuration

```yaml
program: AMPEL360-BWB-Q100
segments: [AIR]
maps: [AAA, PPP, EDI, LCC, IIS]
mals: [CB, QB, FWD, FE, QS, UE]

policy:
  cadence_seconds: 30
  refresh_minutes: 10
  step_deadline_ms: 300
  quantum:
    enabled: true
    strategy: QAOA
    budget_ms: 800
    min_advantage_pct: 2.0
    fallback: MAL-CB.solve
  federation:
    profile: ops-safe   # ops-safe | regulated | defense-c2
    max_assets: 500
  qs:
    anchor_utcs: false
    evidence:
      - schema_ref
      - runlog_uri
```

---

## 5) Performance & SLOs

| Layer              | Target P50 | Target P95 | Notes                                  |
| ------------------ | ---------: | ---------: | -------------------------------------- |
| **CB**             |   ≤ 120 ms |   ≤ 300 ms | Deterministic, bounded                 |
| **QB** (sim/local) |   ≤ 400 ms |   ≤ 900 ms | Enforced by `budget_ms`; must fallback |
| **FWD**            |   ≤ 200 ms |   ≤ 600 ms | Tile count ≤ 1e4                       |
| **FE**             |   ≤ 150 ms |   ≤ 400 ms | Topology ≤ 500 assets                  |
| **QS commit**      |    ≤ 80 ms |   ≤ 200 ms | Anchor async                           |

**System-level goals**

* **Cadence** stable at 30 s (ops), jitter < 5%
* **Cycle walltime** (all domains parallelized): typical 70–120 ms
* **SLA compliance** ≥ 99.5% (rolling 24 h)

---

## 6) Safety, Security, Compliance

* **Zero-Trust MALs**: mTLS, mutual attestation, signed envelopes.
* **RBAC/ABAC**: scopes audited in QS.
* **Defense profile**: ROE policy overlays, mission phase guards, **two-man rule** for high-impact `QB`/`FE` actions.
* **Standards**: S1000D exports; MBSE sync (OPTIMO-DT); DO-178C/DO-254 alignment via MAP-owners.
* **Data hygiene**: units via **UE**, schema versioning, redaction for FE exchanges.

---

## 7) Failure Modes & Fallbacks

* **QB timeout** → **CB** baseline is used; rationale recorded in `quantum_metrics.fallback_reason`.
* **FWD missing tiles** → last-good snapshot + uncertainty inflation.
* **FE overload** → local deconfliction + delayed global merge.
* **QS unavailable** → write-ahead log; later `commit_state` with preserved lineage.
* **Any step > deadline** → mark `sla_compliance=false`; trigger observability event.

---

## 8) Observability

* **OpenTelemetry** traces per `trace_id`.
* Metrics: `cycle_ms`, `sla_ok`, `quantum_used`, `fallback_used`, `tiles/sec`, `fe_conflicts`, `qs_commit_ms`.
* **QS** holds canonical evidence bundle; optional **UTCS** anchor.

---

## 9) Deployment & Host Platform

* **Modes**: `dev (sim)`, `staging`, `ops`
* **Packaging**: container + Helm/K8s (recommended), RT variant for edge (AIR/GROUND).
* **Hardware**: CPU baseline; optional GPU; quantum via providers/simulators (MAL-QB).
* **CI**:

  * Structure: `.github/workflows/tfa_structure_validator.yml`
  * Quantum layers: `.github/workflows/quantum-layers-check.yml`
  * Links/quality: `.github/workflows/link-and-quality.yml`
  * Anchors: `.github/workflows/anchor_utcs.yml`

---

## 10) Test & Validation

* **Validator**: [`./validation/aqua_pro_validator.py`](./validation/aqua_pro_validator.py)

  * TFA coverage (spec+impl per domain/layer)
  * Schema validity + sample roundtrip
  * Quantum–classical bridge presence and terminology guards
* **Orchestrator smoke**: [`./core/aqua_pro_orchestrator.py`](./core/aqua_pro_orchestrator.py)
* **Integration tests** (example path): `services/aqua-os-pro/tests/` (if present)

**Acceptance criteria**

1. 120 layer specs/impls present (15 domains × 8 layers).
2. Schema validates; sample route passes.
3. Loop meets **≤ 300 ms** step deadlines (P95) in `staging`.
4. Fallbacks verified (QB→CB, FWD missing tiles, QS backlog).
5. QS evidence bundle reproducible; optional UTCS anchor succeeds.
6. CI: all validators pass; no terminology violations.

---

## 11) Program-Scale Use Cases

### A) **AMPEL360 BWB-Q100** (AIR)

* Inputs: AAA perf envelopes, PPP TSFC, LCC comm corridors, EER emissions.
* Flow: CB baseline → QB refinement (if gain) → FE deconfliction → QS certification trail.
* Output: `/traj/proposed`, `/traj/approved`, QS state `qs://ampel360/...`

### B) **GAIA Quantum SAT** (SPACE)

* QB for link scheduling; FWD space weather; FE constellation ops; QS mission logs.

### C) **Diagnostics & MRO Robbbo-t** (GROUND)

* UE safety-checked action kernels; FE task allocation; QS maintenance ledger.

### D) **ARES-X UAS Swarm** (DEFENSE)

* FE with C2/ROE; QB for combinatorial routes; QS mission assurance (+ two-man rule).

### E) **H2-CORRIDOR-X** (CROSS)

* FE across air/road/port/grid; FWD energy/logistics flows; UTCS-anchored provenance.

---

## 12) Developer Guide

### Run locally (sim)

```bash
make scaffold
make check
python3 services/aqua-os-pro/core/aqua_pro_orchestrator.py
```

### Minimal optimize call (HTTP)

```json
POST /api/pro/optimize
{
  "route_request": {
    "utcs_id": "AAA/SI/REQ-0101",
    "domain": "AAA",
    "layer": "SI",
    "timestamp": "2025-09-10T12:00:00Z",
    "route_params": {
      "origin": {"latitude": 40.6, "longitude": -73.8, "identifier": "JFK", "type": "airport"},
      "destination": {"latitude": 34.0, "longitude": -118.2, "identifier": "LAX", "type": "airport"},
      "cruise_altitude": 35000,
      "optimization_weights": {"fuel": 0.4, "time": 0.4, "emissions": 0.2}
    },
    "quantum_config": {"enabled": true, "strategy": "qaoa", "shots": 1024}
  }
}
```

**Response (abridged)**

```json
{
  "route_response": {
    "status": "success",
    "processing_time_ms": 212.5,
    "optimized_route": { "waypoints": [...], "estimated_fuel": 12345.6 },
    "quantum_metrics": {"used_quantum": true, "quantum_advantage": 1.8},
    "provenance": {"qs_hash": "blake3:...", "processing_node": "aqua-pro-node-01"}
  }
}
```

---

## 13) Roadmap

* **v1.3**: Live tile streaming adapters; FE policy packs (regulated/defense-c2).
* **v1.4**: Quantum provider AB-tests; adaptive advantage thresholding.
* **v1.5**: Real-time dashboard + OpenTelemetry traces explorer.
* **v2.0**: Multi-program portfolio optimizer; cross-segment FE at scale.

---

## 14) Glossary

* **MAP**: Master Application Program (per domain, e.g., MAP-AAA).
* **MAL**: Main Application Layer (per Bridge layer, e.g., MAL-QB).
* **QS**: Quantum State (signed lineage + evidence).
* **UTCS**: Universal Token Classification System (anchoring).
* **FE**: Federation Entanglement (multi-asset coordination).
* **FWD**: Waves Dynamics (nowcasts/predictions).

---

## 15) References

* Bridge: [`../../docs/quantum-classical-bridge.md`](../../docs/quantum-classical-bridge.md)
* Schema: [`./schemas/route_optimization.json`](./schemas/route_optimization.json)
* Orchestrator: [`./core/aqua_pro_orchestrator.py`](./core/aqua_pro_orchestrator.py)
* Validator: [`./validation/aqua_pro_validator.py`](./validation/aqua_pro_validator.py)
* Templates: [`../../8-RESOURCES/TEMPLATES/`](../../8-RESOURCES/TEMPLATES/)
* CI: [`../../.github/workflows/`](../../.github/workflows/)
* Domains (MAPs): [`../../2-DOMAINS-LEVELS/`](../../2-DOMAINS-LEVELS/)

---
