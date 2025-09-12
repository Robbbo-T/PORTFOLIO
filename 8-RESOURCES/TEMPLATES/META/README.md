# META Templates — Project Canon, Provenance & Governance

**Purpose:** The **META** layer carries the *authoritative* documentation, decisions, provenance, and guardrails that make every TFA domain **auditable, reproducible, and governable**.

> Use these templates to create `TFA/META/` in any domain (e.g., `2-DOMAINS-LEVELS/AAA-.../TFA/META/`). CI expects a META root with README, policies, ADRs, and QS/UTCS hooks.

---

## 0) Quick Links

* **TFA Architecture (overview):** `8-RESOURCES/TFA-ARCHITECTURE.md`
* **Quantum–Classical Bridge:** `docs/quantum-classical-bridge.md`
* **AQUA-OS PRO (reference spec):** `services/aqua-os-pro/AQUA-OS-PRO-SPEC.md`
* **Schemas (route loop):** `services/aqua-os-pro/schemas/route_optimization.json`
* **CI Validators:** `.github/workflows/`

---

## 1) What “META” Covers

* **Canonical READMEs** (domain, segment, program)
* **Policies** (security, safety/ROE, export-controls, cadence)
* **ADR / DECISIONS** (Architectural Decision Records)
* **Glossary & Ontology bindings** (LLC terms, code lists)
* **Compliance mappings** (DO-178C, S1000D, MBSE, defense ROE)
* **QS Provenance & UTCS anchoring** (hashes, anchors, attestations)
* **Links registry** (internal/external specs, playbooks)
* **Badges & Status** (release/train, readiness, classification)

---

## 2) Folder Skeleton (copy under `TFA/META/`)

```
META/
├─ README.md                       # Domain/Program canonical entrypoint
├─ METADATA.yaml                   # Machine-readable identity & refs
├─ POLICIES/
│  ├─ security.policy.yaml         # mTLS, RBAC/ABAC, signing, classification
│  ├─ safety.policy.yaml           # envelopes, ROE, degraded modes
│  ├─ cadence.policy.yaml          # ticks, budgets, backpressure
│  └─ compliance.map.yaml          # standard-to-artifact crosswalk
├─ DECISIONS/
│  ├─ ADR-0000-template.md         # decision template
│  └─ ADR-YYYYMMDD-key-decision.md
├─ QS/
│  ├─ PROVENANCE.md                # what to hash/sign/anchor
│  └─ exports/                     # signed manifests (hashlists, attest)
├─ GLOSSARY.md                     # terms, LLC codes, controlled vocab
├─ LINKS.md                        # curated hyperlinks (stable URIs)
├─ CHANGELOG.md                    # human-readable changes
└─ BADGES/
   └─ status.badge.yaml            # rendered by CI (readiness, CI pass)
```

---

## 3) Templates (copy/paste starters)

### 3.1 `METADATA.yaml`

```yaml
domain:
  code: ${DOMAIN_CODE}        # e.g., AAA
  name: ${DOMAIN_NAME}        # e.g., AERODYNAMICS-AND-AIRFRAMES-ARCHITECTURES
program:
  id: ${PROGRAM_ID}           # e.g., AMPEL360-BWB-Q100
  segment: ${SEGMENT}         # AIR | SPACE | GROUND | DEFENSE | CROSS
classification: ${CLASS}      # PUBLIC | ORG | DEF-RESTRICTED
owners:
  - name: ${OWNER_NAME}
    role: Domain Lead
    contact: mailto:${EMAIL}
ci:
  required:
    - tfa_structure_validator
    - quantum-layers-check
    - link-and-quality
    - dir-policy
provenance:
  qs: enabled
  utcs_anchor: optional       # on/off per program policy
links:
  tfa_arch: 8-RESOURCES/8-RESOURCES/TFA-ARCHITECTURE.md
  bridge: docs/quantum-classical-bridge.md
```

### 3.2 `POLICIES/security.policy.yaml`

```yaml
authn: mTLS
authz: RBAC
roles: [dev, ops, auditor, defense-c2]
key_management:
  rotation_days: 90
  storage: HSM|KMS
classification:
  default: ${CLASS}
  export_controls: true
attestation:
  signing: ed25519
  hash: keccak256
```

### 3.3 `DECISIONS/ADR-0000-template.md`

```md
# ADR-XXXX: <Title>
- **Status:** Proposed | Accepted | Deprecated
- **Date:** YYYY-MM-DD
- **Context:** <Problem, constraints, drivers>
- **Decision:** <Chosen option>
- **Consequences:** <Tradeoffs, risks, debt>
- **Provenance:** QS hash(s), UTCS anchor (if any)
- **Links:** Specs, tickets, PRs
```

### 3.4 `QS/PROVENANCE.md`

```md
## What we sign & anchor
- Inputs: configs, policies, env tiles, models (hashlist)
- Outputs: authoritative topics (/traj/proposed, /schedule/entangled)
- Cycle context: UTCS ID, segment, classification

### Example manifest (JSON)
{
  "cycle": "AQUA/PRO/cycle_...",
  "inputs_hash": "0x...",
  "outputs_hash": "0x...",
  "signatures": ["ed25519:..."],
  "utcs_anchor": "0xTX (optional)"
}
```

---

## 4) How to Instantiate META for a Domain

1. **Create tree (idempotent):**

```bash
mkdir -p 2-DOMAINS-LEVELS/${DOMAIN_CODE}-${DOMAIN_NAME}/TFA/META
cp -r 8-RESOURCES/TEMPLATES/META/* 2-DOMAINS-LEVELS/${DOMAIN_CODE}-${DOMAIN_NAME}/TFA/META/
```

2. **Fill identity:**

* Edit `METADATA.yaml` (codes, owners, segment).
* Set `classification` and export control flags.

3. **Author policies:**

* Security, safety/ROE, cadence, compliance crosswalk.

4. **Record decisions:**

* Create ADRs for structural or algorithmic choices (e.g., “QB uses QAOA with CB fallback under 220ms”).

5. **Wire QS/UTCS:**

* Define what gets hashed/signed, and whether anchors are mandatory for the program.

6. **Run CI:**

```bash
make check   # structure + quantum layers + link quality
```

---

## 5) CI & Compliance Signals (what validators look for)

* `META/README.md` exists and links to **TFA Architecture** & **Bridge** docs.
* `METADATA.yaml` has **domain**, **program**, **segment**, **classification**.
* `POLICIES/*` present; **security** includes mTLS & RBAC; **safety** defines ROE/degraded modes; **cadence** aligns with program SLAs (e.g., PRO ≤300ms p95).
* `DECISIONS/` contains at least one ADR for any nontrivial change.
* `QS/PROVENANCE.md` describes hashing/signing and (if enabled) UTCS anchoring.
* `GLOSSARY.md` lists **LLC codes** and prohibits deprecated terms.
* `BADGES/status.badge.yaml` provides readiness gates (CI renders shield).

---

## 6) Defense & Cross Segment Notes

* **Defense:**

  * Enforce **two-man rule** for high-impact publishes (dual signatures in QS manifest).
  * Classification defaults `DEF-RESTRICTED`; ROE documented in `safety.policy.yaml`.
  * Additional roles: `defense-c2`, separated keys/attestation chains.

* **Cross:**

  * META must *stitch* AIR/SPACE/GROUND with **neutral policy wording**.
  * Keep domain-specific constraints in their own META; CROSS only references and reconciles.

---

## 7) Badges

Add/maintain `BADGES/status.badge.yaml`:

```yaml
readiness: green|yellow|red
ci:
  tfa_structure_validator: pass|fail
  quantum_layers_check: pass|fail
  link_and_quality: pass|fail
classification: ${CLASS}
last_update: YYYY-MM-DD
```

Rendered as shields via CI (see `.github/workflows/link-and-quality.yml`).

---

## 8) Glossary Hints (LLC & Guardrails)

* **SI / DI / SE / CV / CE / CC / CI / CP / CB / QB / UE / FE / FWD / QS** — canonical meanings per `TFA-ARCHITECTURE.md`.
* **Guard:** terms like `Fine~Element`, `Station~Envelop` are **rejected** by CI.
* Map synonyms to canonical tokens; keep a short “Deprecated” table.

---

## 9) Example META README Header (to reuse)

```md
# ${DOMAIN_CODE} · META (Canonical)
**Program:** ${PROGRAM_ID} · **Segment:** ${SEGMENT} · **Class:** ${CLASS}

- Architecture: 8-RESOURCES/TFA-ARCHITECTURE.md  
- Bridge: docs/quantum-classical-bridge.md  
- Policies: ./POLICIES/  
- Decisions: ./DECISIONS/  
- Provenance: ./QS/PROVENANCE.md
```

---

## 10) PR Checklist (META)

* [ ] `METADATA.yaml` populated (codes, owners, segment, class)
* [ ] Policies present & linked (security/safety/cadence/compliance)
* [ ] At least one **ADR** per material decision
* [ ] QS manifest defined (+ UTCS toggle decided)
* [ ] Glossary updated; no deprecated terms
* [ ] Badges reflect current CI & readiness
* [ ] Links in `LINKS.md` are resolvable (CI “link-and-quality” passes)

---

## 11) FAQ

* **Why keep META per domain?** To make each domain *individually auditable* and *program-ready* while sharing global patterns.
* **Where do we store private or export-restricted items?** Reference secure stores from META; never commit secrets.
* **How to reflect multi-segment programs (e.g., CROSS)?** Keep a META per domain and one CROSS META that references and reconciles.

---

**License:** MIT (inherits project) · **Owner:** Domain MAP · **Version:** Template v2.0 (TFA V2)
