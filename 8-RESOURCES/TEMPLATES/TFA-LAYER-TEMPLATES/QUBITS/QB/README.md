# TFA Layer Template — **QUBITS/QB (Qubit)**

**Purpose:** Standardize quantum optimization/estimation modules with **deterministic CB fallbacks**, enforced **deadlines**, and **provenance (QS)** — reusable by all domains (MAPs) via **MAL-QB**.

> This template is provider-agnostic (simulators & real QPUs) and enforces the TFA Bridge rules: **CB → QB → UE/FE → FWD → QS** with CI validation.

---

## 0) Quick Links

* Architecture: `8-RESOURCES/8-RESOURCES/TFA-ARCHITECTURE.md`
* Bridge details: `docs/quantum-classical-bridge.md`
* Reference app (AQUA-OS PRO): `services/aqua-os-pro/AQUA-OS-PRO-SPEC.md`
* Templates root: `8-RESOURCES/TEMPLATES/`

---

## 1) When to Use **QB**

Use this layer when a MAP (e.g., **MAP-AAA**, **MAP-PPP**, **MAP-IIS**) requires:

* Combinatorial optimization (routing, assignment, scheduling)
* Ground-state/energy estimation
* Variational circuit exploration with bounded runtime
* Quantum sampling for heuristics or calibration

**Mandatory:** define **deadline** and **CB fallback** for every QB call.

---

## 2) Folder Skeleton (copy into `TFA/QUBITS/QB/`)

```
QUBITS/QB/
├─ README.md                      # this file (explain, wire, test)
├─ specification.template.yaml    # contract & SLA for this QB module
├─ interface.template.py          # abstract interface + dataclasses
├─ provider-adapter.template.py   # adapter pattern for QPU/simulator
├─ fallback_cb.template.py        # deterministic classical fallback
├─ policies/
│  ├─ runtime.policy.yaml         # deadlines, shot caps, access classes
│  └─ security.policy.yaml        # mTLS, RBAC/ABAC, export rules
├─ tests/
│  ├─ test_contract.py            # API contract & schema tests
│  ├─ test_deadlines.py           # deadline/fallback behavior
│  ├─ test_noise_models.py        # robustness under noise
│  └─ fixtures/
│      └─ small_qubo.json         # MaxCut/Ising toy problems
└─ examples/
   ├─ maxcut_qaoa.ipynb           # tutorial (optional)
   └─ vqe_minH.py                 # simple VQE driver
```

---

## 3) Contract (API) — minimal, stable

### 3.1 Python Interface (reference)

```python
# interface.template.py
from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Literal

ProblemType = Literal["QUBO", "ISING", "CIRCUIT"]

@dataclass
class QBConfig:
    backend: str = "auto"         # "auto"|"sim"|"qpu:<vendor>"
    shots: int = 1024
    optimization_level: int = 1
    deadline_ms: int = 250        # hard deadline for QB part
    enable_error_mitigation: bool = True
    seed: Optional[int] = None

@dataclass
class QBProblem:
    type: ProblemType
    payload: Dict[str, Any]       # QUBO/ISING dict or circuit IR
    metadata: Dict[str, Any]

@dataclass
class QBResult:
    status: Literal["success","fallback","error"]
    bitstring: Optional[str]
    energy: Optional[float]
    metrics: Dict[str, Any]       # {latency_ms, queue_ms, depth, 1−fidelity, …}
    provenance: Dict[str, Any]    # QS hooks (hashes, inputs, signatures)

class QBInterface:
    def initialize(self, cfg: QBConfig) -> None: ...
    def optimize(self, problem: QBProblem) -> QBResult: ...
    def get_status(self) -> Dict[str, Any]: ...
```

### 3.2 REST/gRPC Shape (if exposing service)

```yaml
# specification.template.yaml (snippet)
api:
  version: v1
  post /qb/optimize:
    request:
      utcs_id: "AAA/QB/REQ-0105"
      config: QBConfig
      problem: QBProblem
    response:
      result: QBResult
security:
  authn: mTLS
  authz: RBAC  # roles: {dev, ops, auditor, defense-c2}
sla:
  deadline_ms: 250
  cb_fallback_max_ms: 100
  max_shots: 4096
```

---

## 4) **Deadline & Fallback** (non-negotiable)

* Each `optimize()` must **finish under `deadline_ms`**.
* If not feasible, **return immediately via CB fallback** (`fallback_cb.template.py`) with:

  * Same **signature** as QB (`QBResult.status = "fallback"`),
  * **Reason** and **exceeded\_ms** in `metrics`,
  * **Deterministic** output (seeded).
* Orchestrators (MAL-QB, PRO) may enforce extra budget (e.g., total ≤300 ms).

---

## 5) Problem Encodings

Supported **ProblemType**:

* **QUBO/ISING**: `{ "Q": [[i,j,coef], ...] }` or `{ "J": {...}, "h": {...} }`
* **CIRCUIT**: intermediate representation (IR) with gate list/depth; keep provider-agnostic (convert in adapter).

Keep payloads **small & documented**; add example fixtures in `tests/fixtures/`.

---

## 6) Provider Adapters (plug-in pattern)

`provider-adapter.template.py` exposes a **single thin API** and isolates vendor code:

```python
class ProviderAdapter:
    def __init__(self, provider_id: str, cfg: QBConfig): ...
    def submit(self, problem: QBProblem) -> Dict[str, Any]: ...
    def translate(self, problem: QBProblem) -> Any: ...
    def metrics(self) -> Dict[str, Any]: ...
```

* Supported kinds: `sim`, `qpu:<vendor>` (queue-aware).
* **Secrets** from env/volumes; never hard-code.
* Add **noise models** & **error mitigation** toggles (ZNE, readout mitigation).
* **Do not** let vendor APIs leak above adapter boundary.

---

## 7) Performance Targets (by segment)

| Segment | p95 QB time | Notes                               |
| ------- | ----------- | ----------------------------------- |
| AIR     | ≤ 120 ms    | Flight ops loop; strict cadence     |
| SPACE   | ≤ 200 ms    | Telemetry delays; larger QUBOs      |
| GROUND  | ≤ 250 ms    | MRO/diagnostics ok with higher p95  |
| DEFENSE | ≤ 150 ms    | C2/ROE overlays; two-man rule paths |
| CROSS   | ≤ 180 ms    | Inter-sector scheduling             |

**Total loop** (e.g., PRO) ≤ **300 ms** per domain; QB must **fit** and yield to fallback.

---

## 8) Security & Governance

* **mTLS everywhere**, pinned CAs.
* **RBAC/ABAC**: roles `{dev, ops, auditor, defense-c2}`; defense adds **two-man rule** for high-impact ops.
* **Data classification** labels in `metadata.classification` (e.g., `PUBLIC|ORG|DEF-RESTRICTED`).
* **Export controls** documented in `policies/security.policy.yaml`.
* Log **provider**, **queue time**, **region**, and **cost hints** to `metrics`.

---

## 9) QS Provenance (+ UTCS optional)

Every `QBResult` must include **provenance**:

```json
{
  "provenance": {
    "qs_hash": "keccak256(...)", 
    "inputs_hash": "keccak256(problem|cfg)",
    "utcs_anchor": "optional_tx_hash",
    "signatures": ["ed25519:..."]
  }
}
```

* QS artifacts live in `TFA/STATES/QS/`.
* Optional **UTCS** anchoring for regulated programs (see CI workflow `anchor_utcs.yml`).

---

## 10) Tests (what CI expects)

* **Contract tests**: request/response schema parity.
* **Deadline tests**: force timeouts → verify **CB fallback** correctness.
* **Noise tests**: inject noise; assert graceful degradation and metrics.
* **Determinism**: `seed` yields identical fallback outputs.
* **Golden**: tiny QUBO with known optimum (match energy/bitstring within tolerance).

Run locally:

```bash
pytest QUBITS/QB/tests -q
```

---

## 11) Minimal Example

### 11.1 Config (YAML)

```yaml
qb:
  backend: "auto"
  shots: 1024
  optimization_level: 1
  deadline_ms: 200
  enable_error_mitigation: true
```

### 11.2 Problem (QUBO MaxCut)

```json
{
  "type": "QUBO",
  "payload": { "Q": [[0,1,-1.0],[1,2,-1.0],[0,2,-1.0]] },
  "metadata": { "graph": "triangle", "classification": "ORG" }
}
```

### 11.3 Pseudocode

```python
cfg = QBConfig(deadline_ms=200)
qb = MyQBImplementation()          # implements QBInterface
qb.initialize(cfg)
res = qb.optimize(QBProblem(type="QUBO", payload=tri_qubo, metadata={}))
if res.status == "fallback":
    # System stayed deterministic under deadline
    pass
record_to_qs(res.provenance)
```

---

## 12) Integration with **MAL-QB** & MAPs

* **MAL-QB** is the shared service exposing `/qb/optimize`.
* MAPs (e.g., **MAP-AAA**, **MAP-PPP**, **MAP-IIS**) call MAL-QB; do **not** link vendor SDKs in MAPs.
* When used by **PRO**, QB must fit within **overall cadence** (30 s loop; ≤300 ms per domain step).

---

## 13) Defense & Cross Notes

* **Defense**: enforce **two-man rule** for ROE-gated QB runs; store ROE decision trail in **QS**.
* **Cross** (multi-sector): FE will stitch air/road/port/grid decisions; keep QB payloads **portable** and policy-free (policies live in **FE**).

---

## 14) PR Checklist (QB)

* [ ] `specification.template.yaml` filled with **UTCS ID** and SLA.
* [ ] `fallback_cb.template.py` present and referenced.
* [ ] Deadline honored; **metrics** include `{latency_ms, queue_ms, backend}`.
* [ ] `policies/*` updated for security/export.
* [ ] Tests: contract, deadline, noise, determinism, golden.
* [ ] QS provenance recorded (+ UTCS anchor if enabled).
* [ ] No vendor secrets in repo; adapters only.

---

## 15) FAQ

* **Can QB skip CB fallback?** No — every QB call must be safe under deadline.
* **Multiple providers?** Add adapters; select via `cfg.backend`.
* **Large problems?** Chunk, warm-start, or downgrade to CB with notice.

---

**License:** MIT (inherit project) • **Owner:** MAP-IIS / Governance
**Version:** Template v2.0 (TFA V2)
