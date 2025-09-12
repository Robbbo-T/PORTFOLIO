---
title: Plan for Software Aspects of Certification (PSAC)
program: {{PROGRAM}}            # e.g., AMPEL360 BWB-Q100 / GAIA Quantum SAT / Robbbo-t
system: AQUA-OS Predictive Route Optimizer (PRO)
software_level: {{DAL}}         # DAL A/B/C/D per safety assessment
authority: {{AUTHORITY}}        # FAA/EASA/Military Airworthiness Authority
supplier: {{ORG}}
version: v1.0
date: {{YYYY-MM-DD}}
---

## 1. Purpose & Scope
This PSAC defines how {{ORG}} will comply with **DO-178C** for {{PROGRAM}}'s AQUA-OS PRO software.
Scope includes MAP/MAL integration across TFA layers: **SI, DI, SE, CB, QB, FWD, QS, FE** and segment(s) {{SEGMENTS}} (AIR / SPACE / GROUND / DEFENSE / CROSS).

## 2. System Overview
- **Function:** 10-minute route optimization loop (30s cadence), aero/environment aware, quantum-classical hybrid.
- **Architecture:** MAP (domain master programs) + MAL (bridge layers). Deterministic **CB** path with **QB** acceleration; **FE** federation; **FWD** nowcast; **QS** provenance.
- **Operational Context:** {{CONOPS_SUMMARY}}

## 3. Certification Basis
- Standard: **DO-178C** (+ supplements: DO-330 if TQL tools; DO-331/DO-332/DO-333 if Model-/OO-/Formal-based).
- Level allocation rationale: link to safety assessment (ARP4754A/ARP4761): {{REFERENCE_HAZARD_ASSESSMENT}}

## 4. Software Life Cycle & Data
- Plans: **SDP**, **SVP**, **SCMP**, **SQAP** (this set).
- Standards: coding, modeling, requirements, reviews (referenced in SDP §6).
- Life-cycle data produced: High/Low-level requirements, design, code, test cases & procedures, results, coverage, problem reports, QA/CM records, configuration indices, accomplishment summary.

## 5. Development Environment & Partitioning
- Target platform(s): {{CPU/OS/RTOS/Partioning}}; time partitioning & memory protection strategy; DAL mixing strategy (if any).
- Toolchain: {{COMPILERS/LINKERS}}, static analyzers, req/test/cov tools; intended qualification status (see TQP ref).

## 6. Verification Strategy (Summary)
- Requirements-based testing at all levels; data/control coupling analysis; robustness testing; coverage goals ({{COVERAGE}} e.g., MC/DC for DAL A/B).
- Independence matrix (role separation) maintained in **SVP**.

## 7. Configuration & Quality Assurance (Summary)
- **CM**: Git + signed releases + baselines; CCB controls (see **SCMP**).
- **SQA**: Process/product assurance, audits, non-conformance handling (see **SQAP**).

## 8. Compliance Objectives
- Mapping to DO-178C Tables A-1…A-7 by {{DAL}} maintained in `psac-objectives-matrix.xlsx`.
- Deviations/alternates (if any): {{NONE/DETAIL}}

## 9. Deliverables & Milestones
- Review gates: PSAC approval → Plan set approval → SRR/PDR/CDR → SOI-1/2/3/4.
- Data delivery list: plans, standards, requirements, tests, coverage reports, CM/SQA records, SAS.

## 10. Suppliers & Subcontractors
- Roles, oversight, audits, acceptance criteria, independence obligations.

## 11. Assumptions & Open Items
- Assumptions: {{LIST}}
- Open items/risk register link: {{URL/ID}}

*Appendices:* Glossary; Acronyms; Objective matrix snapshot; Tool list (intended TQL).