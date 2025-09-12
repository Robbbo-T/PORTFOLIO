---
title: Software Verification Plan (SVP)
program: {{PROGRAM}}
system: AQUA-OS PRO
software_level: {{DAL}}
version: v1.0
date: {{YYYY-MM-DD}}
---

## 1. Strategy
- Requirements-based verification: reviews, analyses, tests at unit/integration/system level.
- **Coverage targets**: {{STATEMENT/DECISION/MC-DC}} per {{DAL}}; coupling (data/control) analysis; robustness testing.
- **Independence**: V&V team separate from development; SQA independent of both.

## 2. Verification Levels
- **Reviews/Analyses:** Plans, standards, HLSR/LLR, design, code.
- **Unit Tests:** Deterministic CB units; QB adapters with oracle comparison to CB path; boundary/robustness.
- **Integration Tests:** DI contracts; timing under SE envelopes; FE coordination scenarios; FWD nowcast correctness.
- **System Tests:** End-to-end route loop; 10-min horizon stability; failure injection & fallbacks; QS provenance integrity.

## 3. Test Cases & Procedures
- Structure & templates; parameterization; expected results; trace to requirements.
- Randomization limits for reproducibility; seeds captured.

## 4. Test Environments
- SIL/PIL/HIL descriptions; simulators (weather/traffic/QPU sim).
- Tool qualification status where test outcome depends on tool correctness.

## 5. Structural Coverage
- Instrumentation approach; coverage collection & analysis; gap closure; dead code policy; deactivated code rationale.

## 6. Independence Matrix
- Who reviews what; dual-control on safety-significant artifacts; access separation.

## 7. Problem Reporting & Retest
- Defect lifecycle; severity; containment; regression scope; closure criteria.

## 8. Acceptance Criteria & Reporting
- Entry/exit criteria per level; pass/fail metrics; stability windows; SAS contributions.
- Artifacts: test specs, procedures, logs, results, coverage, anomalies, reports.

*Appendices:* Traceability schema; coverage mapping form; robustness checklist.