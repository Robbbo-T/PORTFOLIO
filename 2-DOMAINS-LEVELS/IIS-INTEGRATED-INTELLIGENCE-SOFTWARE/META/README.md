# IIS · INTEGRATED-INTELLIGENCE-SOFTWARE · META

> **Purpose**
> This folder captures the **identity, policies, decisions, provenance, and contracts** for the **IIS** domain.
> It governs how intelligence services (agents, models, orchestration, guardrails) implement **TFA V2** and the **quantum–classical bridge** across the program.

* 🔗 TFA Architecture primer: [`../../../8-RESOURCES/8-RESOURCES/TFA-ARCHITECTURE.md`](../../../8-RESOURCES/8-RESOURCES/TFA-ARCHITECTURE.md)
* 🔗 Quantum–Classical Bridge: [`../../../docs/quantum-classical-bridge.md`](../../../docs/quantum-classical-bridge.md)
* 🔗 AQUA-OS PRO (MAL reference app): [`../../../services/aqua-os-pro/`](../../../services/aqua-os-pro/)
* 🔗 Layer templates:

  * SI: [`../../../8-RESOURCES/TEMPLATES/TFA-LAYER-TEMPLATES/SYSTEMS/SI/README.md`](../../../8-RESOURCES/TEMPLATES/TFA-LAYER-TEMPLATES/SYSTEMS/SI/README.md)
  * QB: [`../../../8-RESOURCES/TEMPLATES/TFA-LAYER-TEMPLATES/QUBITS/QB/README.md`](../../../8-RESOURCES/TEMPLATES/TFA-LAYER-TEMPLATES/QUBITS/QB/README.md)
  * META: [`../../../8-RESOURCES/TEMPLATES/META/README.md`](../../../8-RESOURCES/TEMPLATES/META/README.md)

---

## 📇 What lives in `META/`

```
META/
├─ README.md                  # This file
├─ METADATA.yaml              # Domain card (segments, owners, classification)
├─ POLICIES/                  # Security, safety, export, model/agent governance
├─ DECISIONS/                 # ADRs (Architecture Decision Records)
├─ LINKS.md                   # Inter-domain references & dependencies
├─ GLOSSARY.md                # Controlled vocabulary (CI-enforced)
└─ QS/PROVENANCE/             # Model lineage, run attestations, UTCS anchors
```

**Minimal `METADATA.yaml` skeleton**

```yaml
domain: IIS
name: INTEGRATED-INTELLIGENCE-SOFTWARE
segments: [AIR, SPACE, GROUND, DEFENSE, CROSS]
classification: ORG|DEF-RESTRICTED        # drop DEF-RESTRICTED if not applicable
owners:
  - map_owner_iis@org.example
  - ml_ops_lead@org.example
ci_gates:
  required:
    - tfa_structure_validator
    - quantum-layers-check
    - link-and-quality
    - dir-policy
    - model-governance-lint
contracts:
  di_spec: ../TFA/SYSTEMS/DI/CONTRACTS/
  si_points: ../TFA/SYSTEMS/SI/INTEGRATION.md
  data_plane: ../TFA/ELEMENTS/UE/DATA-PLANE.md
  guardrails: ../TFA/STATES/QS/GUARDRAILS.md
```

---

## 🧭 Domain scope (IIS)

* Multi-agent orchestration, planning/execution graphs, RL/NMPC controllers, perception & decision services.
* Model registry & lineage, feature store, prompt/graph templates, safety & policy enforcement.
* Provides **MAP-IIS** (domain “brain”) and consumes/provides **MAL** services (CB/QB/FWD/QS/FE/UE).

**Program examples using IIS**

* **AMPEL360 BWB-Q100 (AIR)** — closed-loop guidance: aero-aware PRO cycles, envelope guards, pilot-in-the-loop HMIs.
* **GAIA Quantum SAT (SPACE)** — constellation tasking, cross-link scheduling, on-orbit inference, UTCS anchoring.
* **Diagnostics & MRO Robbbo-t (GROUND)** — autonomous triage, repair planning, toolpath generation, QS provenance.

---

## 🧬 TFA tree for IIS (where specs/impls live)

```
../TFA/
├─ SYSTEMS/      ├─ SI/  (integration & orchestration)
│                └─ DI/  (APIs: OpenAPI/Proto/JSON Schema)
├─ STATIONS/     └─ SE/  (compute envelopes: CPU/GPU/QPU, latency, power)
├─ COMPONENTS/   ├─ CV/ CE/ CC/ CI/ CP/ (runtimes, SDKs, adapters)
├─ BITS/         └─ CB/  (deterministic planners/solvers)
├─ QUBITS/       └─ QB/  (QAOA/VQE adapters, sampling strategies)
├─ ELEMENTS/     ├─ UE/  (data plane, feature store, prompts)
│                └─ FE/  (federated/entangled coordination)
├─ WAVES/        └─ FWD/ (nowcasts, forecasts, simulators-in-the-loop)
└─ STATES/       └─ QS/  (guardrails, policies, attestations, lineage)
```

---

## 🆔 UTCS IDs & requirement indexing (IIS)

Use **UTCS** IDs to tag specs/impl/tests:

```
IIS/<LAYER>/REQ-1xyz
# examples:
IIS/SI/REQ-1001   IIS/DI/REQ-1002   IIS/SE/REQ-1003
IIS/CB/REQ-1004   IIS/QB/REQ-1005   IIS/FWD/REQ-1006
IIS/QS/REQ-1007   IIS/FE/REQ-1008
```

Index → Layer: `01:SI, 02:DI, 03:SE, 04:CB, 05:QB, 06:FWD, 07:QS, 08:FE`.

---

## 🧠 MAP/MAL model (how IIS powers intelligence)

* **MAP-IIS** = the intelligence “program brain”:
  roadmap, contracts, orchestration graphs, KPIs, safety gates, evaluation harnesses.
* **MAL services touched by IIS**

  * **MAL-CB**: classical planners (MILP, NMPC), validation solvers.
  * **MAL-QB**: quantum optimization for scheduling/routing; CB fallback.
  * **MAL-FWD**: simulators/nowcasts in the loop for short-horizon control.
  * **MAL-QS**: policy/guardrails, lineage, attestations, audit.
  * **MAL-FE**: multi-node/fleet coordination, conflict-free merges.
  * **MAL-UE**: datasets, features, embeddings, prompt/graph templates.

AQUA-OS example (as MAL service): [`../../../services/aqua-os-pro/`](../../../services/aqua-os-pro/)

---

## 📐 IIS policies, SLOs & compliance

**Strict rules (CI-enforced)**

* **TFA-ONLY**: never create flat LLC folders under the domain root.
* **Contracts first**: DI specs are versioned, reproducible, and validated in CI.
* **Governed AI**: each model/agent has owner, license, dataset card, evals, QS lineage & UTCS anchor.

**Illustrative SLOs**

* **Orchestration p95**: < **300 ms** per domain pass within PRO cadence (30 s).
* **Model-serve p99**: < **150 ms** (onboard edge profiles vary by SE envelope).
* **Planner (CB) p95**: < **250 ms**; **QB fallback** switch < **100 ms**.
* **Lineage latency**: < **2 s** to persist QS record & UTCS anchor.

**Compliance**

* DO-178C (software), DO-330 (tool qualification) when applicable.
* DO-326A/ED-202A (airworthiness security), SOC2-like controls for services.
* FIPS-validated crypto, GDPR/PIA where personal data exists (e.g., ops logs).

---

## 🧩 Interfaces & integration handshakes

* **DI** → `../TFA/SYSTEMS/DI/CONTRACTS/`
  OpenAPI (`*.yaml`), Protobuf (`*.proto`), JSON Schemas, versioned & tested.
* **SI** → `../TFA/SYSTEMS/SI/`
  `INTEGRATION.md`: sequence diagrams, retries/backoff, circuit-breakers, QoS.
* **SE** → `../TFA/STATIONS/SE/`
  Station envelopes: CPU/GPU/QPU quotas, thermal/power, offline modes.
* **QB/CB/FWD/QS/FE/UE** → see templates + bridge guide.

**Helpful references**

* Bridge guide: [`../../../docs/quantum-classical-bridge.md`](../../../docs/quantum-classical-bridge.md)
* SI template: [`../../../8-RESOURCES/TEMPLATES/TFA-LAYER-TEMPLATES/SYSTEMS/SI/README.md`](../../../8-RESOURCES/TEMPLATES/TFA-LAYER-TEMPLATES/SYSTEMS/SI/README.md)
* QB template: [`../../../8-RESOURCES/TEMPLATES/TFA-LAYER-TEMPLATES/QUBITS/QB/README.md`](../../../8-RESOURCES/TEMPLATES/TFA-LAYER-TEMPLATES/QUBITS/QB/README.md)

---

## 🗳️ Decisions (ADRs)

Place ADRs in `DECISIONS/` with incremental IDs:

```
DECISIONS/
├─ ADR-0001-agent-graph-runtime.md
├─ ADR-0002-qaoa-for-task-scheduling.md
├─ ADR-0003-guardrails-and-policy-engine.md
```

Every ADR must link impacted UTCS IDs and update **LINKS.md** for inter-domain impacts (e.g., IIS↔LCC control loops).

---

## 🔒 Provenance & QS (lineage, safety, audit)

Use `QS/PROVENANCE/` to store:

* `*.qs.json` lineage snapshots (model version, dataset hash, prompts, params).
* run attestations (supply-chain, evals, red-team results).
* UTCS anchors & export manifests for certification evidence.

AQUA-OS PRO schema integration:
`../../../services/aqua-os-pro/schemas/route_optimization.json`

---

## 🛡️ DEFENSE & 🌐 CROSS overlays (if applicable)

**DEFENSE**

* ABAC/RBAC + mTLS; keys in HSM/KMS; 90-day rotation.
* Redaction/export filters in `POLICIES/`; zero-trust posture; telemetry minimization.
* Model weights/data under classification rules; reproducible builds.

**CROSS**

* Federated learning & FE conflict-resolution notes in `LINKS.md`.
* Contracts for inter-program dependencies (AIR↔SPACE↔GROUND), e.g., GAIA SAT tasking → AIR ops.

---

## ✅ Done-Definition (IIS is integration-ready when…)

* [ ] `METADATA.yaml` complete (owners, segments, classification).
* [ ] `POLICIES/` present (security, governance, export, naming).
* [ ] DI contracts versioned & validated; SI integration doc present.
* [ ] **All** bridge layers created: CB/QB/UE/FE/FWD/QS.
* [ ] SE station envelopes codified with tests.
* [ ] ADRs for runtimes, guardrails, quantum adapters, data plane.
* [ ] QS lineage & UTCS anchors produced for models/agents.
* [ ] CI green: structure, bridge, links, dir policy, model governance.

---

## 🧪 Quick validation

```bash
# From repo root
make check
python3 services/aqua-os-pro/validation/aqua_pro_validator.py
make domains
```

---

## 📬 Contacts

* **MAP-IIS Owner**: `map_owner_iis@org.example`
* **ML Ops Lead**: `ml_ops_lead@org.example`

*Keep META concise, governed, and CI-validated. IIS is the connective tissue that lets every program think, decide, and prove.*
