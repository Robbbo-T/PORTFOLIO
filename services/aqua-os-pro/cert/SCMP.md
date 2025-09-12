---
title: Software Configuration Management Plan (SCMP)
program: {{PROGRAM}}
system: AQUA-OS PRO
software_level: {{DAL}}
version: v1.0
date: {{YYYY-MM-DD}}
---

## 1. CM Objectives
Ensure integrity, identification, control, status accounting, and delivery of all life-cycle data.

## 2. Items Under Configuration
- **Baselined:** Plans, standards, HLSR/LLR, design, code, tests, coverage, CM/SQA records, build scripts, SBOM, SAS.
- **Non-deliverable but controlled:** CI configs, scripts, experimental branches.

## 3. Identification & Versioning
- Naming convention; semantic versioning; signed tags; release manifests.
- Branch strategy: `main`, `release/*`, `hotfix/*`, protected merges with review gates.

## 4. Change Control
- CCB composition; change request workflow; impact analysis (safety/trace/timing); approval criteria.
- Emergency fix protocol & retroactive verification.

## 5. Build & Release
- Reproducible builds; pinned toolchain; artifact hashing; binary provenance (QS).
- Delivery packages; configuration index; archive & retention policy ({{YEARS}} years).

## 6. Status Accounting & Audits
- CM dashboards; periodic audits; discrepancy reporting; action tracking.

## 7. Access Control & Security
- Role-based permissions; signed commits; supply-chain controls (artifact attestation).

*Appendices:* Item list; baseline checklist; release form; retention schedule.