# CQH · META (Canonical) — Cryogenics, Quantum & H₂

**Domain code:** `CQH`
**Canonical location:** `2-DOMAINS-LEVELS/CQH-CRYOGENICS-QUANTUM-AND-H2/TFA/META/`

> If this file currently lives outside `TFA/META`, please relocate to comply with the **STRICT TFA-ONLY** policy.

**What this governs:** All canonical decisions, policies, provenance, interfaces, and compliance for **cryogenic systems**, **quantum compute stacks**, and **hydrogen infrastructure** across AIR/SPACE/GROUND (and DEFENSE where applicable).

---

## 0) Quick Links

* **TFA Architecture:** `8-RESOURCES/8-RESOURCES/TFA-ARCHITECTURE.md`
* **Quantum–Classical Bridge:** `docs/quantum-classical-bridge.md`
* **AQUA-OS PRO (spec):** `services/aqua-os-pro/AQUA-OS-PRO-SPEC.md`
* **Route Schema:** `services/aqua-os-pro/schemas/route_optimization.json`
* **CI Workflows:** `.github/workflows/`

  * `tfa_structure_validator.yml` · `quantum-layers-check.yml` · `link-and-quality.yml` · `dir-policy.yml` · `anchor_utcs.yml`

---

## 1) Scope (CQH)

* **Cryogenic plant & distribution:** LN₂/LHe systems, valves, lines, vents, boil-off control, insulation/Vacuum-Jacketed Piping, purges.
* **Quantum stacks:** QPU fridges, control electronics, wiring, shielding, calibration/fidelity, QEC envelopes.
* **Hydrogen systems:** LH₂ tanks, pumps, sensors, embrittlement policies, leak detection, purging & inerting, refuel/defuel ops.
* **Safety & ROE:** hazard zones, ignition source control, inerting envelopes, degraded modes, emergency venting.
* **Mission integration:** AIR (H₂ aircraft), SPACE (GAIA Quantum SAT ground/space chain), GROUND (test stands, MRO robotics).

---

## 2) Identity & Program Context

* **Domain:** `CQH — CRYOGENICS-QUANTUM-AND-H2`
* **Segments:** `SPACE`, `AIR`, `GROUND` (optional: `DEFENSE`, `CROSS`)
* **Typical MAP (Master Application Program):** `MAP-CQH`
* **MAL (Main Application Layers) used:** `MAL-QB`, `MAL-CB`, `MAL-FWD`, `MAL-QS`, `MAL-FE`
* **Example programs using CQH:**

  * **GAIA Quantum SAT** (SPACE): Cryo/QPU ground segment, entangled links, on-orbit thermal envelopes.
  * **AMPEL360 BWB-Q100** (AIR): H₂ storage & distribution, cryo safety envelopes, PRO loop integration.
  * **Diagnostics & MRO Robbbo-t** (GROUND): Safe maintenance workflows around cryo/H₂ assets.

---

## 3) META Tree (expected)

```
TFA/META/
├─ README.md
├─ METADATA.yaml
├─ POLICIES/
│  ├─ security.policy.yaml
│  ├─ safety.policy.yaml
│  ├─ cadence.policy.yaml
│  └─ compliance.map.yaml
├─ DECISIONS/
│  ├─ ADR-0000-template.md
│  └─ ADR-YYYYMMDD-chosen-architecture.md
├─ QS/
│  ├─ PROVENANCE.md
│  └─ exports/
├─ GLOSSARY.md
├─ LINKS.md
├─ CHANGELOG.md
└─ BADGES/
   └─ status.badge.yaml
```

Use the canonical starters in `8-RESOURCES/TEMPLATES/META/`.

---

## 4) Policies (CQH summary)

**Security (`POLICIES/security.policy.yaml`):**

* mTLS + RBAC/ABAC; HSM/KMS keys (90-day rotation).
* Signed artifacts (ed25519); hash = keccak256.
* Classified ops (set `classification: ORG|DEF-RESTRICTED` per program).

**Safety / ROE (`POLICIES/safety.policy.yaml`):**

* Hazard zoning (H₂ dispersion models), O₂ depletion alarms.
* Purge/inert requirements (N₂/He), ESD/ignition controls, grounding/bonding.
* Degraded modes (loss of cooling, vent path blockage), emergency vent stacks and safe-to-fail behaviors.
* QPU thermal ramp profiles & shock limits.

**Cadence (`POLICIES/cadence.policy.yaml`):**

* **AQUA-OS PRO** loop ≤ **300 ms** p95 per domain; **30 s** cadence; 10-min route horizon.
* Cryo plant telemetry ingest ≥ 10 Hz; QPU calibration windows tracked as envelopes.

**Compliance map (`POLICIES/compliance.map.yaml`):**

* Aviation: DO-178C/DO-254/ARP4754A (where applicable).
* Ground/Process: IEC 61511/61508, ATEX/IECEx zones, API 2000 (venting), CGA/NFPA hydrogen.
* Space: ECSS thermal/vacuum, ISO 14644 (cleanliness), launcher safety.
* Information security: FIPS 140-3 (if mandated), Common Criteria profiles.

---

## 5) Decision Log (ADRs)

Keep material choices here (examples):

* **ADR-2025-01-QAOA-Fallback:** QAOA primary on `MAL-QB` with deterministic CB fallback under 220 ms.
* **ADR-2025-02-Vent-Policy:** Dual vent path with monitored backpressure; auto-isolation on ∆P slope.
* **ADR-2025-03-Cryo-Piping:** VJP spec and sensor class for leak-before-break detection.
* **ADR-2025-04-Calibration-Windows:** QPU calibration fenced via `SE` envelopes, exposed as QS states for schedulers.

Template: `TFA/META/DECISIONS/ADR-0000-template.md`.

---

## 6) Provenance & Anchoring (QS/UTCS)

**Where:** `TFA/META/QS/PROVENANCE.md`

* Hash/sign **inputs** (configs, models, env tiles) & **outputs** (topics like `/traj/proposed`, `/cryo/schedule`, `/qpu/calibration`).
* Emit **QS manifests** each PRO cycle with UTCS anchor (optional per program).

**QS manifest (example):**

```json
{
  "cycle": "AQUA/PRO/cycle_1757620...",
  "domain": "CQH",
  "inputs_hash": "0x...",
  "outputs_hash": "0x...",
  "signatures": ["ed25519:..."],
  "utcs_anchor": "0xTX"
}
```

---

## 7) Interfaces (CQH) — MAP/MAL view

**MAP-CQH** provides stable contracts; **MALs** deliver horizontal services.

* **DI (APIs):** REST/gRPC (OpenAPI/Protobuf); topics prefixed by domain:

  * `/cryo/telemetry/*`, `/cryo/safety/envelope`
  * `/h2/storage/status`, `/h2/leak/alerts`
  * `/qpu/calibration/window`, `/qpu/fidelity`
  * `/schedule/entangled` (via `MAL-FE`)

* **SI (integration):** Wires CQH envelopes into **AQUA-OS PRO** loop and OPTIMO-DT DTs.

* **CB/QB:** Deterministic solvers for cryo flow/network + QAOA/VQE search surfaces.

* **FWD:** Nowcasts for boil-off, thermal loads, leak dispersion, calibration success likelihood.

* **QS:** States for safety envelopes, calibration windows, asset readiness.

* **FE:** Cross-asset coordination (test stands ↔ aircraft ↔ ground QPU lab).

See reference schema: `services/aqua-os-pro/schemas/route_optimization.json`.

---

## 8) SLAs & Envelopes

* **AQUA-OS PRO:** ≤ **300 ms** p95 per domain; 30 s cadence.
* **Cryo telemetry:** ingest ≥ 10 Hz; end-to-end alerting ≤ 2 s.
* **Quantum cadence:** calibration windows advertised ≥ 60 s before close; schedule conflict rate < 1%.
* **Safety envelopes:** validated each tick; vent/backpressure margins logged to QS.

---

## 9) CI Gates (what must pass)

* TFA structure & terminology (no deprecated terms).
* Quantum layer presence (CB/QB/UE/FE/FWD/QS).
* Link & spec quality, directory policy.
* Optional: UTCS anchor job for QS manifests.

---

## 10) How To Use / Contribute

1. **Scaffold (idempotent):**

   ```bash
   make scaffold
   ```
2. **Fill META identity:**

   * `TFA/META/METADATA.yaml` (owners, segment, classification).
3. **Author policies & ADRs;** add links/glossary.
4. **Wire QS/UTCS** per program policy.
5. **Validate:**

   ```bash
   make check
   ```

**PR checklist (CQH META):** owners set · policies present · ≥1 ADR per material change · QS manifest defined · links resolvable · badges updated.

---

## 11) Contacts

* **Domain Lead (CQH/MAP):** *fill in*
* **Safety Officer:** *fill in*
* **Security/Keys:** *fill in*
* **Ops (Cryo/H₂/Quantum):** *fill in*

---

**License:** MIT (inherits project) · **Version:** META template v2.0 (TFA V2)
