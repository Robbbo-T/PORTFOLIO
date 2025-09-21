---

id: ASIT-GENESIS-0000-00-00-00-000-OV
REV: 0
llc: GENESIS
title: "ASI-T · Genesis — Foundational Components"
status: BASELINE
classification: "INTERNAL / EVIDENCE-REQUIRED"
version: "1.0.0"
release\_date: 2025-09-21
maintainer: "ASI-T Architecture Team"
provenance:
policy\_hash: "sha256\:POLICY"
model\_sha: "sha256\:MODEL"
data\_manifest\_hash: "sha256\:DATA"
operator\_id: "UTCS\:OP\:ID"
canonical\_hash: "sha256\:CANONICAL-BLOB"
licenses:
code: "Apache-2.0"
docs: "CC-BY-4.0"
bridge: "CB→QB→UE→FE→FWD→QS"
ethics\_guard: "MAL-EEM"

---

# ASI‑T Genesis — Foundational Components

The **Genesis** layer crystallizes the universal rules of the ASI‑T ecosystem: canonical path grammar, ethics & empathy guardrails, deterministic evidence (QS/UTCS), quantum‑extensible hooks, and CI/CD enforcement. Everything downstream must inherit or reference these contracts.

> Non‑negotiable: **TFA‑Only** path grammar, **MAL‑EEM** guardrails, **QS/UTCS provenance**, **FCR‑1/FCR‑2** follow‑up rules, and **MOD‑BASE / MOD‑STACK** conventions.

---

## 0) QUICK START (Maintainers & CI)

1. Clone repo and run the bootstrap checks:

   ```bash
   make genesis.check    # path grammar + headers + license + FCR
   make genesis.ci       # run full CI locally (same as GitHub Actions)
   ```
2. Author artifacts under **canonical roots** only (see §2). Deviation → CI FAIL.
3. Every PR must attach: **UTCS evidence pack** (QS blob), **policy/model/data hashes**, and **FCR chain**.

---

## 1) UNIVERSAL INJECTION PROMPT (UIX) — SSoT

**ASI‑T · Universal Injection Prompt (v1)** is the **single source of truth** for all agent actions. All tools/agents must import and validate against UIX before executing any step.

**Canonical path:** `ASI-T/GENESIS/UIX/ASI-T-Universal-Injection-Prompt.v1.md`

UIX enforces:

* **Ethics & empathy guardrails (MAL‑EEM):** red‑team resilient, never assist harm; log rationale snippets.
* **Strict TFA path grammar:** reject non‑conforming paths with **actionable errors**.
* **QS/UTCS provenance hooks:** automatic evidence anchoring per action.
* **FCR rules:** require FCR‑1 (intent + scope) then FCR‑2 (diff + evidence) before merge.

> Any agent invocation **must fail closed** if UIX import or validation is missing.

---

## 2) CANONICAL ROOTS & PATH GRAMMAR

Roots (read‑only by design; extend via MOD‑STACK):

```
ASI-T/
  GENESIS/                  # this module (SSoT)
    UIX/                    # universal injection prompt + specs
    POLICIES/               # ethics, empathy, safety
    SCHEMAS/                # JSON/YAML contracts used across repos
    TEMPLATES/              # commit/PR/FCR templates, headers
    EVIDENCE/               # QS/UTCS blob spec + examples
    CI/                     # CI workflows and local runners
    SCRIPTS/                # validators and generators
  MOD-BASE/                 # minimal runnable base (BasIC UE)
  MOD-STACK/                # curated stacks built on MOD-BASE
```

**Grammar (enforced):**

* Directories use **ALLCAPS LAYER CODES** (`SYSTEMS/ STATIONS/ COMPONENTS/ BITS/ QUBITS/ ELEMENTS/ WAVES/ STATES`).
* Subfolders use **LLC codes** (e.g., `SI/ DI/ SE/ CV/ CE/ CC/ CI/ CP`), then UTCS‑MI file IDs.
* Filenames begin with **UTCS‑MI 13‑field identifier** + suffix. Example:
  `GP-AM-AMPEL-0100-72-00-00-000-OV-A.md`

**Typical error on violation:**

```
[E1001] PathGrammarError: expected LAYER/LLC/UTCS-ID; found "docs/misc".
Action: move into TFA tree or declare MOD-STACK mapping in genesis.config.yaml
```

---

## 3) ETHICS & EMPATHY GUARDRAILS (MAL‑EEM)

Baseline principles:

* **Do no harm**, comply with law & certification regimes; adversarial requests → document and refuse with cause.
* **Human‑on‑the‑loop:** critical merges require human signoff with name, time, and purpose.
* **Transparency:** store explainability traces (XAI notes) alongside artifacts in **EVIDENCE/**.

**Policy file:** `GENESIS/POLICIES/mal-eem.policy.md`

---

## 4) DETERMINISTIC EVIDENCE (QS/UTCS)

Each artifact must ship a **QS blob** and a **UTCS proof**:

```yaml
# EVIDENCE/specs/qs_blob.example.yaml
version: 1
artifact_id: <UTCS-ID>
created_at: <UTC>
hashes:
  canonical: <sha256>
  content: <sha256>
  deps_tree: <sha256>
provenance:
  operator_id: <UTCS:OP:ID>
  toolchain: ["python3.11", "nastran2024R2", "qiskit1.3"]
  policy_hash: <sha256:POLICY>
  model_sha: <sha256:LLM/MODEL>
notes: "XAI rationale + key decisions"
```

**Anchor file:** `EVIDENCE/anchors/UTCS/<date>/<artifact_id>.utcs.json`

---

## 5) IDENTITY, ATTESTATION & ANOMALY SCORING (Quantum‑Safe)

* **Operator IDs:** `OPERATORS/operators.yaml` (UTCS namespace). Require signed key attestations.
* **Attestation flow:** sign QS blob → register UTCS anchor → attach to PR.
* **Anomaly baseline:** simple z‑score over artifact deltas + rule‑based detectors (path, schema, ethics).

---

## 6) AUTOMATED VALIDATION (CI/CD)

### 6.1 GitHub Actions (reference workflow)

```yaml
# GENESIS/CI/workflows/genesis.yml
name: genesis
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - name: Install
        run: |
          pip install -r GENESIS/CI/requirements.txt
      - name: Path grammar & headers
        run: python GENESIS/SCRIPTS/check_paths.py
      - name: Schema validation
        run: python GENESIS/SCRIPTS/validate_schemas.py
      - name: FCR enforcer
        run: python GENESIS/SCRIPTS/fcr_enforcer.py
      - name: Evidence lint
        run: python GENESIS/SCRIPTS/evidence_lint.py
```

### 6.2 Local make targets

```
make genesis.check   # fast checks
make genesis.ci      # reproduce CI
```

---

## 7) CHANGE REQUESTS — FCR Rules

* **FCR‑1 (Intent):** purpose, scope, impacted paths, safety notes.
* **FCR‑2 (Diff+Evidence):** code diff, test results, QS blob, UTCS anchor, signoffs.

`TEMPLATES/FCR/fcr1.md` and `TEMPLATES/FCR/fcr2.md` are required in every PR.

**Commit message template:**

```
feat(GENESIS): short summary

FCR-1: <link>
FCR-2: <link>
UTCS: <anchor-id>
Evidence: EVIDENCE/blobs/<id>.yaml
Co-authored-by: <name <email>>
Signed-off-by: <name <email>>
```

---

## 8) MOD‑BASE (BasIC UE) & MOD‑STACK

* **MOD‑BASE** provides the minimal Unit Element (**BasIC UE**) to exercise UIX + CI + QS/UTCS.
* **MOD‑STACK** are curated stacks (domain packs) built on MOD‑BASE; they must declare mapping to TFA trees.

```
MOD-BASE/
  UE/
    baseline.md
    demo.inputs/
    demo.outputs/
```

---

## 9) SCHEMAS & CONTRACTS

**Genesis configuration**

```yaml
# GENESIS/SCHEMAS/genesis.config.schema.yaml (excerpt)
$schema: "https://json-schema.org/draft/2020-12/schema"
title: ASI-T Genesis Config
type: object
required: [version, stacks, enforcement]
properties:
  version: { type: string }
  stacks:
    type: array
    items:
      type: object
      required: [name, root, mapping]
      properties:
        name: { type: string }
        root: { type: string, pattern: "^(ASI-T|TFA|DOMAINS)/" }
        mapping: { type: object }
  enforcement:
    type: object
    properties:
      path_grammar: { type: boolean }
      utcs_required: { type: boolean }
      fcr_required: { type: boolean }
```

**Artifact manifest (QS layer)**

```json
// GENESIS/SCHEMAS/artifact-manifest.schema.json (excerpt)
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "QS Artifact Manifest",
  "type": "object",
  "required": ["id", "hashes", "provenance"],
  "properties": {
    "id": { "type": "string" },
    "hashes": {
      "type": "object",
      "required": ["canonical", "content"],
      "properties": {
        "canonical": { "type": "string", "pattern": "^[a-f0-9]{64}$" },
        "content": { "type": "string", "pattern": "^[a-f0-9]{64}$" }
      }
    },
    "provenance": {
      "type": "object",
      "required": ["operator_id", "policy_hash", "model_sha"],
      "properties": {
        "operator_id": { "type": "string" },
        "policy_hash": { "type": "string" },
        "model_sha": { "type": "string" }
      }
    }
  }
}
```

---

## 10) OPERATOR REGISTRY

File: `OPERATORS/operators.yaml`

```yaml
- id: UTCS:OP:robbo-t
  name: Amedeo Pelliccia
  role: "CQ‑extensible engineer"
  pubkey: <ed25519:base58>
  attestations: ["UIX.v1", "MAL‑EEM@2025-09"]
```

---

## 11) POLICY HASHES & REPRODUCIBILITY

* Policies in `POLICIES/` are hashed on release; changes require new policy\_hash.
* Repro builds must regenerate **canonical\_hash** and match prior value for identical inputs.

---

## 12) EXAMPLE PR CHECKLIST (TEMPLATES/PR\_CHECKLIST.md)

* [ ] Paths follow TFA grammar
* [ ] UTCS‑MI header present
* [ ] UIX referenced
* [ ] FCR‑1 and FCR‑2 attached
* [ ] Evidence pack added (QS + UTCS)
* [ ] Ethics check (MAL‑EEM) complete
* [ ] Operator attestation signed

---

## 13) CONTACT

**Core team:** `ASI-T/GENESIS/OPERATORS/operators.yaml`

---

**Last updated:** 2025‑09‑21
**Maintainer:** ASI‑T Architecture Team
