# TFA Layer Template — **SYSTEMS/SI (System Integration)**

**Purpose:** Orchestrate **cross-domain** flows, enforce **cadence & budgets**, and bind **SYSTEMS ⇆ STATIONS/COMPONENTS/BRIDGE layers** so programs ship **deterministically** with auditability (QS) and CI enforcement.

> SI is the conductor: it sequences DI, CB/QB/UE/FE/FWD, and QS; applies safety/policy; and guarantees “one loop, one truth” per cycle (e.g., AQUA-OS PRO 10-minute route loop with 30-second cadence).

---

## 0) Quick Links

* TFA Architecture: `8-RESOURCES/8-RESOURCES/TFA-ARCHITECTURE.md`
* Quantum–Classical Bridge: `docs/quantum-classical-bridge.md`
* Reference App (AQUA-OS PRO): `services/aqua-os-pro/AQUA-OS-PRO-SPEC.md`
* Route schema: `services/aqua-os-pro/schemas/route_optimization.json`
* Templates root: `8-RESOURCES/TEMPLATES/`

---

## 1) When to Use **SI**

Use this layer anytime a **MAP** (Master Application Program, one per domain) must:

* Coordinate **multiple TFA layers** (DI, CB/QB, FWD, FE, QS) within a time budget.
* Merge mission policies, safety envelopes (SE), and **program cadences** (e.g., 30s tick).
* Provide a **single authoritative output** (e.g., `/traj/proposed`, `/schedule/entangled`) per cycle.
* Guarantee **rollback & provenance** via QS (and optional UTCS anchoring).

**Examples**

* **MAP-AAA** (Aerodynamics): Close aero-aware route loop for **AMPEL360 BWB-Q100**.
* **MAP-LCC** (Comms): Time-sync C2 network and publish cross-fleet state.
* **MAP-IIS** (Software): Govern agentic pipelines across MAL-QB/MAL-FWD.

---

## 2) Folder Skeleton (copy into `TFA/SYSTEMS/SI/`)

```
SYSTEMS/SI/
├─ README.md                          # this file (explain, wire, test)
├─ specification.template.yaml        # SI contract, SLAs, cadences, topics
├─ interface.template.py              # abstract SI interface + dataclasses
├─ pipeline.template.yaml             # orchestration DAG/state machine
├─ policies/
│  ├─ cadence.policy.yaml             # tick, budgets, backpressure
│  ├─ safety.policy.yaml              # ROE/limits, degraded modes
│  └─ security.policy.yaml            # mTLS, RBAC/ABAC, audit
├─ adapters/
│  ├─ mal_qb.client.template.py       # MAL-QB client (quantum)
│  ├─ mal_fwd.client.template.py      # MAL-FWD client (nowcast)
│  └─ fe_bus.client.template.py       # FE pub/sub (federation)
├─ tests/
│  ├─ test_contract.py                # API contract & schema
│  ├─ test_cadence_budget.py          # 30s ticks, ≤300ms step
│  ├─ test_degraded_modes.py          # loss of QB/FWD/FE => graceful SI
│  └─ fixtures/
│      └─ cycle_ctx.sample.json       # sample cycle context
└─ examples/
   └─ si_loop_demo.py                 # minimal loop driver
```

---

## 3) Contract (API) — minimal & stable

### 3.1 Python Interface (reference)

```python
# interface.template.py
from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Literal

@dataclass
class SICadence:
    tick_seconds: int = 30
    step_budget_ms: int = 300  # per-domain step (PRO reference)

@dataclass
class SICycleCtx:
    utcs_id: str                # e.g., "AAA/SI/REQ-0101"
    program: str                # e.g., "AMPEL360-BWB-Q100"
    segment: Literal["AIR","SPACE","GROUND","DEFENSE","CROSS"]
    t_start: float
    metadata: Dict[str, Any]    # mission mode, ROE, classification

@dataclass
class SIOutput:
    status: Literal["success","degraded","error"]
    topics: Dict[str, Any]      # e.g., {"/traj/proposed": {...}}
    metrics: Dict[str, Any]     # latencies, fallback flags
    provenance: Dict[str, Any]  # QS hooks

class SIInterface:
    def initialize(self, cadence: SICadence, cfg: Dict[str, Any]) -> None: ...
    def step(self, ctx: SICycleCtx, inputs: Dict[str, Any]) -> SIOutput: ...
    def reconcile(self, last: SIOutput, now: SIOutput) -> SIOutput: ...
    def get_status(self) -> Dict[str, Any]: ...
```

### 3.2 REST/gRPC Shape (if exposing service)

```yaml
# specification.template.yaml (snippet)
api:
  version: v1
  post /si/step:
    request:
      ctx: SICycleCtx
      inputs:
        di: {...}          # domain interface payloads
        env: {...}         # FWD nowcasts
        compute: {...}     # CB/QB results
    response:
      output: SIOutput
security:
  authn: mTLS
  authz: RBAC  # roles: {dev, ops, auditor, defense-c2}
sla:
  tick_seconds: 30
  step_budget_ms: 300
  degraded_modes: ["no-qb","no-fe","no-fwd","offline"]
topics:
  publish:
    - "/traj/proposed"
    - "/schedule/entangled"
    - "/state/qs"
```

---

## 4) Orchestration Responsibilities

* **Plan the tick**: open a cycle, **fan-out** to DI/CB/QB/FWD/FE, enforce **budgets**, **fan-in** results, and **publish**.
* **Budget control**: ensure each sub-call (MAL-QB, MAL-FWD, FE) fits into **≤300ms** (or configured). Use **timeouts & fallbacks**.
* **Safety & SE**: gate outputs by **Station Envelope** limits before publishing.
* **Degraded modes**: if QB unavailable ➜ **CB fallback**; if FE down ➜ publish to local bus + mark `status="degraded"`.
* **QS provenance**: sign & record hashes of inputs/outputs; optional **UTCS** anchor for auditability.

---

## 5) Cadence, Budgets, and Topics

**Defaults (AQUA-OS PRO reference):**

* Tick: **30 s**; Loop horizon: **10 min**; Step budget: **≤ 300 ms** per domain.
* Publish topics (examples):

  * `/traj/proposed` (AAA, LCC)
  * `/schedule/entangled` (FE)
  * `/env/nowcast` (FWD)
  * `/state/qs` (QS provenance events)

Policies live in `policies/cadence.policy.yaml`.

---

## 6) Integration with MALs & MAPs

* **MAP-<DOMAIN>** owns SI and calls **MAL services** for horizontal capabilities:

  * **MAL-QB** for quantum strategies (with CB fallback guarantees).
  * **MAL-FWD** for nowcasts / short-horizon predictions.
  * **MAL-FE** via **FE bus** for fleet/federation decisions.
  * **QS** for provenance export.
* SI must not embed vendor SDKs; interact through **adapters** in `adapters/`.

---

## 7) Performance Targets (by segment)

| Segment | p95 SI step | Notes                             |
| ------- | ----------- | --------------------------------- |
| AIR     | ≤ 200 ms    | Flight ops; strict loop integrity |
| SPACE   | ≤ 250 ms    | Longer links; batch fan-out       |
| GROUND  | ≤ 300 ms    | MRO/diagnostics tolerant          |
| DEFENSE | ≤ 220 ms    | C2 overlays + two-man rule        |
| CROSS   | ≤ 240 ms    | Multi-sector stitching            |

**Whole-loop** (e.g., PRO) remains within per-program SLA; SI enforces **preemption** & **fallbacks**.

---

## 8) Security & Governance

* **mTLS**, pinned CAs; **RBAC/ABAC** with roles `{dev, ops, auditor, defense-c2}`.
* **Policy gating**: ROE/safety in `policies/safety.policy.yaml`; defense enforces **two-man rule** paths.
* **Classification** in `ctx.metadata.classification` (PUBLIC|ORG|DEF-RESTRICTED).
* **Audit**: every publish carries **QS provenance**; export controls captured in `policies/security.policy.yaml`.

---

## 9) QS Provenance (+ optional UTCS)

Every `SIOutput` must include:

```json
{
  "provenance": {
    "qs_hash": "keccak256(output|inputs|ctx)",
    "inputs_hash": "keccak256(inputs)",
    "utcs_anchor": "optional_tx_hash",
    "signatures": ["ed25519:..."]
  }
}
```

QS artifacts are written under `TFA/STATES/QS/`. CI can anchor UTCS via `.github/workflows/anchor_utcs.yml`.

---

## 10) Tests (what CI expects)

* **Contract**: request/response schema parity with `specification.template.yaml`.
* **Cadence & Budget**: simulate tick; assert **p95 ≤ budget** and **timeouts trigger fallbacks**.
* **Degraded Modes**: cut QB/FWD/FE; SI must degrade cleanly and still publish.
* **SE Guards**: outputs violating envelopes are **blocked** with reason codes.
* **Deterministic merge**: `reconcile()` is associative & idempotent for repeated inputs.
* **Provenance**: QS hashes present and stable.

Run:

```bash
pytest SYSTEMS/SI/tests -q
```

---

## 11) Minimal Example (AQUA-OS PRO flavored)

### 11.1 Cadence Policy

```yaml
# policies/cadence.policy.yaml
tick_seconds: 30
step_budget_ms: 300
timeouts:
  qb_ms: 220
  fwd_ms: 120
  fe_ms: 150
backpressure:
  drop_old_env: true
  max_queue: 2
```

### 11.2 Pseudocode

```python
cad = SICadence(tick_seconds=30, step_budget_ms=300)
si = MySIImplementation()                      # implements SIInterface
si.initialize(cadence=cad, cfg={"program":"AMPEL360-BWB-Q100"})

ctx = SICycleCtx(
    utcs_id="AAA/SI/REQ-0101",
    program="AMPEL360-BWB-Q100",
    segment="AIR",
    t_start=time.time(),
    metadata={"mode":"nominal","classification":"ORG"}
)

inputs = {
  "di": {...},               # domain interface inputs
  "env": mal_fwd.nowcast(...),
  "compute": mal_qb.optimize(...),  # QB or CB fallback under budget
}

out = si.step(ctx, inputs)
assert out.status in ("success","degraded")
publish("/traj/proposed", out.topics["/traj/proposed"])
record_qs(out.provenance)
```

---

## 12) Defense & Cross Notes

* **Defense**: add **two-man rule** for high-impact publishes; require dual signatures in `provenance.signatures`. Maintain **ROE trail** in QS.
* **Cross**: SI stitches AIR/SPACE/GROUND with **FE** consensus; keep reconciliation **policy-free** in SI (policies live in `policies/*` and FE).

---

## 13) PR Checklist (SI)

* [ ] `specification.template.yaml` filled (UTCS ID, SLA, topics).
* [ ] `pipeline.template.yaml` defines fan-out/fan-in and error paths.
* [ ] Adapters implemented for MAL-QB / MAL-FWD / FE bus.
* [ ] Cadence & safety policies authored; CI passes budget tests.
* [ ] Degraded modes exercised; deterministic `reconcile()` verified.
* [ ] QS provenance recorded (+ UTCS anchor if enabled).
* [ ] No vendor secrets; mTLS certs via secure mounts.

---

## 14) FAQ

* **Is SI the same as DI?** No. **DI** exposes domain boundaries; **SI** orchestrates **within the domain** across layers and services.
* **What if QB is slow/unavailable?** SI must enforce timeout, **accept CB fallback**, and continue cycle.
* **Can SI publish multiple truths?** No — **exactly one** authoritative output per topic per cycle; later corrections go through `reconcile()`.

---

**License:** MIT (inherit project) • **Owner:** MAP-<DOMAIN> / Governance
**Version:** Template v2.0 (TFA V2)
