TEKNIA — Universal Token Compensation System

Layer: UTCS / AQUA-OS • Scope: Incentives & Provenance • Status: Spec v1.0

“TEKNIA is not a cryptocurrency. It is a compliance-by-design incentive layer that turns verified aerospace outcomes into auditable value.”

Quick links:
   •   TFA overview: ../8-RESOURCES/TFA-ARCHITECTURE.md
   •   AQUA app/API entry: ../services/aqua-webhook/README_AQUA.md
   •   Quantum–Classical Bridge: ../docs/quantum-classical-bridge.md
   •   Templates (schemas): ../8-RESOURCES/TEMPLATES/TEKNIA-SCHEMAS/
   •   Contracts (UTCS): ./teknia-contracts/

⸻

1) Principles (authoritative)

| Principle                | Why it matters                                                                                                                        |
|--------------------------|---------------------------------------------------------------------------------------------------------------------------------------|
| Real-world asset–backed  | Units bound to measurable outcomes (e.g., 1 CO2_SAVED = 1 kg CO₂ avoided; 1 QTIME = 1 hour quantum compute).                         |
| Regulatory-first         | Utility tokens with verifiable provenance; designed to align with EASA/FAA/NATO guidance (no investment promise, no speculative utility). |
| Federated & trustless    | Rewards only issue when FE (Federation Entanglement) consensus validates outcomes; no single issuer.                                 |
| Cross-segment parity     | Same rules across AIR / SPACE / GROUND / DEFENSE / CROSS programs.                                                                   |

Legal note: this spec is not legal advice; deployments must pass jurisdictional review.

⸻

2) Role in the AQUA-OS TFA Platform

graph LR
    A[QS-Ledger (immutable states)] -->|Outcome proofs| B[TEKNIA Contracts]
    B --> C{Distribution Rules}
    C --> D[FE-Scheduler rewards]
    C --> E[PRO fuel-savings rewards]
    C --> F[FWD forecast-accuracy rewards]
    C --> G[DEFENSE threat-response rewards]
    D --> H[UTCS Chain]
    E --> H
    F --> H
    G --> H
    H --> I[Wallets: OEMs · Regulators · Contractors]

   •   Inputs: QS proofs (hashes, oracles, attestations).
   •   Logic: On-chain policies (per domain/token).
   •   Outputs: Utility tokens to entitled wallets; events back to AQUA for audit dashboards.

⸻

3) Folder layout

6-UTCS-BLOCKCHAIN/
└── teknia-contracts/
    ├── TokenMinter.sol
    ├── FECompensation.sol
    ├── QSProof.sol
    ├── DefenseCompensation.sol
    ├── interfaces/
    │   ├── IProofVerifier.sol
    │   └── ITekniaIssuer.sol
    ├── scripts/           # deployment & verification
    └── README.md          # build, test, audit notes
8-RESOURCES/
└── TEMPLATES/
    └── TEKNIA-SCHEMAS/
        ├── token.schema.json
        ├── policy.schema.json
        └── examples/
            ├── eee_co2_saved.json
            ├── qb_quantum_bandwidth.json
            └── defense_swarm_response.json
.github/
└── workflows/
    └── teknia-validator.yml


⸻

4) Contract interfaces (canonical)

// interfaces/ITekniaIssuer.sol
interface ITekniaIssuer {
    function quoteMint(bytes32 qsHash, bytes calldata policyData) external view returns (uint256 amount);
    function mintWithProof(
        address to,
        bytes32 qsHash,
        bytes calldata proof,       // oracle attest / EIP-712 bundle / ZK proof
        bytes calldata policyData   // domain token policy snapshot
    ) external returns (uint256 amountMinted);
    event TekniaMinted(address indexed to, bytes32 indexed qsHash, string tokenCode, uint256 amount);
}

// interfaces/IProofVerifier.sol
interface IProofVerifier {
    function verify(bytes32 qsHash, bytes calldata proof) external view returns (bool ok, string memory err);
}

   •   TokenMinter.sol implements ITekniaIssuer (generic issuance).
   •   FECompensation.sol applies FE consensus weights/splits.
   •   QSProof.sol registers QS verifiers (oracles, EIP-712 signers, optional ZK).
   •   DefenseCompensation.sol adds multisig + export-control gates.

Security posture: no custodial balances; mint only on verified QS; optional rate-limits; emergency pause.

⸻

5) Schemas (machine-enforced)

token.schema.json (excerpt)

{
  "$id": "teknia.token.schema.json",
  "type": "object",
  "required": ["domain", "token", "unit", "formula", "validator"],
  "properties": {
    "domain": { "type": "string", "pattern": "^[A-Z]{3}(-[A-Z0-9-]+)?$" },
    "token": { "type": "string", "pattern": "^[A-Z0-9_]{3,32}$" },
    "unit":  { "type": "string" },
    "formula": { "type": "string" },
    "validator": { "type": "string" },
    "caps": {
      "type": "object",
      "properties": { "daily": {"type":"number"}, "program": {"type":"number"} }
    }
  }
}

Example: examples/eee_co2_saved.json

{
  "domain": "EEE",
  "token": "CO2_SAVED",
  "unit": "kg",
  "formula": "fuel_before_kg - fuel_after_kg",
  "validator": "services/aqua-os-pro/validation/eee_co2_validator.py",
  "caps": { "daily": 500000, "program": 50000000 }
}


⸻

6) Issuance flows

6.1 Mint (standard)

sequenceDiagram
    participant MAP/MAL
    participant AQUA
    participant QS as QS-Ledger
    participant ORA as Proof Oracle
    participant TK as TEKNIA Contracts

    MAP/MAL->>AQUA: Submit outcome (domain, token, metrics)
    AQUA->>QS: Record state + hash
    AQUA->>ORA: Request proof(attest QS hash, policy)
    ORA-->>AQUA: Proof(attestation / EIP-712 / ZK)
    AQUA->>TK: mintWithProof(to, qsHash, proof, policyData)
    TK-->>AQUA: TekniaMinted event
    AQUA-->>Dash: Update balances & audit log

Preconditions
   •   QS hash is present and anchored (optional UTCS testnet).
   •   Policy matches policy.schema.json and CI passes.
   •   Defense mints require multisig approval.

6.2 Redeem / Burn (optional profile)
   •   Programs may define sinks (e.g., pay for audits, compute, or carbon offset settlement).
   •   Implement as burnForService(serviceId, amount) with service registry.

⸻

7) CI/CD and governance

.github/workflows/teknia-validator.yml (excerpt)

name: teknia-validator
on:
  pull_request:
    paths:
      - '8-RESOURCES/TEMPLATES/TEKNIA-SCHEMAS/**'
      - '6-UTCS-BLOCKCHAIN/teknia-contracts/**'
      - '**/QS/**'
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Schema lint
        run: python scripts/jsonschema_check.py 8-RESOURCES/TEMPLATES/TEKNIA-SCHEMAS/token.schema.json
      - name: Static analysis (solc)
        run: make teknia-audit
      - name: Policy checks
        run: python services/aqua-webhook/tools/policy_guard.py --defense-profile --cross-profile
      - name: QS linkage
        run: python services/aqua-webhook/tools/qshash_guard.py

Governance hooks
   •   Changes to token semantics/policies → PR with approvals under 7-GOVERNANCE/ and recorded vote file.
   •   Defense profile enforces: SBOM, signing, export-control lists, multisig.

⸻

8) Programs & tokens (ready patterns)

| Program         | Segment         | Token(s)                                   | Source of Truth                |
|-----------------|-----------------|--------------------------------------------|-------------------------------|
| AMPEL360        | BWB-Q100AIR     | CO2_SAVED, FUEL_SAVED                      | PRO results → QS              |
| GAIA Quantum SAT| SPACEQUANTUM    | BANDWIDTH, LATENCY_SLAM                    | AL-QB + LCC telemetry → QS    |
| ARES-X UAS      | SWARMDEFENSE    | SWARM_DEFENSE, EW_RESPONSE                 | FE Scheduler + DDD sensors → QS|
| H2-CORRIDOR-X   | CROSSH2         | DELIVERED, CO2_REDUCTION, REGULATORY_COMPLIANCE | LIB + EER + EEE → QS     |
| ROBBBO-T MRO    | GROUNDMRO       | TASK, MTBF_IMPROVEMENT                     | MMM + IIS diagnostics → QS    |
Splits (example FE policy): OEM 60% · Operator 25% · Regulator 10% · Community 5%.

⸻

9) Security & compliance
   •   No speculation: contracts reject non-RWA types.
   •   Proof-before-mint: QSProof verifier must attest qsHash.
   •   Rate limits & caps: per program/token to mitigate abuse.
   •   Audits: mandatory static analysis + external audit before mainnet.
   •   Privacy: store PII off-chain; only hashes on UTCS.
   •   Defense: air-gapped CI, artifact signing, multisig, export-control checks.

require(QSProof(verifier).verify(qsHash), "Unverified QS");
require(tokenType == keccak256("REAL_WORLD_ASSET"), "Utility only");


⸻

10) Minimal AQUA endpoints (integration contract)
   •   POST /api/v1/teknia/quote → {amount} for a qsHash + policy
   •   POST /api/v1/teknia/mint → triggers mintWithProof (governance-guarded)
   •   GET /api/v1/teknia/wallet/{addr} → balances & last events
   •   POST /api/v1/teknia/burn → optional sinks (audits/compute)

All calls logged as audit events: teknia.mint.requested, teknia.minted, teknia.burned.

⸻

11) Tokenomics (reference)

| Parameter   | Choice / Value                  | Rationale                                         |
|-------------|---------------------------------|---------------------------------------------------|
| Type        | Utility / RWA-backed            | Aligns with compliance; maps to verified outcomes  |
| Supply      | Dynamic (policy-gated)          | Mint on proof; burn on redemption                  |
| Peg         | ISO 14064 (CO₂) or USD index    | Stability for contracts & accounting               |
| Redemption  | Audits, compute, quantum time   | Keeps value inside ecosystem                       |
Accounting mapping: treat as earned incentives / liabilities until redemption (deployment-specific; consult finance).

⸻

12) Implementation roadmap

| Phase      | Action                                   | Outcome                                 |
|------------|------------------------------------------|-----------------------------------------|
| Q4 2025    | Publish schemas + contract stubs; wire CI| Templates usable across 15 domains      |
| Q1 2026    | Pilot AMPEL360 (fuel savings)            | Verified CO₂ tokens on UTCS testnet     |
| Q2 2026    | EU ETS integration (bridge oracle)       | Carbon credit settlement path           |
| Q3 2026    | NATO defense market (air-gapped)         | Mission-tied rewards with multisig      |
| 2027       | Cross-sector clearing                    | H₂ ↔ bandwidth ↔ audit credits          |
⸻

13) Ready-to-commit artifacts (ask to generate)
   •   teknia-contracts/*.sol minimal, compilable stubs
   •   TEKNIA-SCHEMAS/*.json + validators
   •   teknia-validator.yml workflow
   •   policy_guard.py & qshash_guard.py utilities
   •   Example FE split policies per domain

⸻

14) Adoption checklist
1.Define token(s) via TEKNIA-SCHEMAS (with caps & validators).
2.Ensure QS writes outcome hashes (UTCS testnet optional).
3.Configure FE splits & defense profile as needed.
4.Run CI; deploy contracts to testnet; execute a mint dry-run.
5.Enable AQUA endpoints and dashboards.

⸻

Contact: see 0-STRATEGY/GOVERNANCE.md (Owner: A. Pelliccia).
License: MIT (contracts & schemas).
Compliance: Deployment owners remain responsible for jurisdictional alignment.

⸻

