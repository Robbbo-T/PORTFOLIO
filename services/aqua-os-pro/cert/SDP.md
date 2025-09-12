---
title: Software Development Plan (SDP)
program: {{PROGRAM}}
system: AQUA-OS PRO
software_level: {{DAL}}
version: v1.0
date: {{YYYY-MM-DD}}
---

## 1. Organization & RACI
- **Roles**: Chief SW Engineer, Requirements Lead, Design Lead, Coding Lead, Integration Lead, Safety Lead, Tool Lead.
- **Independence**: Dev vs. V&V vs. SQA/CM (no reporting overlap).
- **RACI** table maintained in `org-raci.xlsx`.

## 2. Life-Cycle Model
- Iterative V-model with continuous integration.
- Gate reviews: SRR → PDR → CDR → TRR → QR → FR.

## 3. Requirements Engineering
- Sources: system safety, aero/perf models, ops constraints, standards.
- **HLSR/LLR** method; **derived requirements** capture/approval; bi-directional trace (Req ↔ Test ↔ Code).
- Data formats: Markdown + ReqIF/CSV; repository locations under `2-DOMAINS-LEVELS/*/TFA`.

## 4. Design
- Architectural decomposition: MAP (domain) + MAL (CB/QB/FWD/QS/FE).
- Interfaces in **DI** (OpenAPI/Proto); **SE** resource envelopes (CPU/RAM/latency).
- Design notations: UML/SysML (if used); state/sequence canvases; timing budgets.

## 5. Coding Standards & Methods
- Languages: {{PY/C/C++/Rust}} per component.
- Standards: MISRA-C/C++; Python style (PEP8 + safety addenda); Rust Clippy gates.
- Prohibited features (DAL-dependent): dynamic memory at runtime (if prohibited), recursion, undefined behavior.
- Static analysis + code review rules; security patterns (zero-trust, secret hygiene).

## 6. Build & Integration
- Deterministic builds, pinned toolchain; SBOM generation.
- Integration order: SI ➜ DI ➜ SE ➜ CB/QB ➜ FWD ➜ QS/FE.
- Hardware-in-the-Loop (HIL) / Processor-in-the-Loop (PIL) strategy: {{DETAILS}}.

## 7. Resource & Timing
- **Cadence** 30s, **loop SLA** ≤300ms per domain; WCET budgets per component; scheduling policy; watchdogs.

## 8. Data & Models
- Performance models (aero/propulsion); environmental tiles (FWD); config parameters (PDIF).
- Model control & validation; numeric determinism (CB path).

## 9. Safety & Security
- Defensive coding, error handling, safe states; crypto policy; key management; data classification across **FE** federation.

## 10. Tool Strategy
- Tool list + intended TQL (DO-330): compilers, static analyzers, requirements/test/coverage tools.
- TQP reference: `TQP.md` (separate).

## 11. Deliverables
- Standards, HLSR/LLR, design docs, code, integration notes, SBOM, release notes, SAS references.

*Appendices:* Naming, folder conventions (TFA); templates references; sample diagrams.