# AQUA Dual-Literacy Standard (PR+QM)

**Version:** 1.0  
**Status:** Active  
**Scope:** Universal baseline literacy for all classical engineers interfacing with AQUA systems  
**Policy:** "No decision artifact enters production unless it is **Prompt-Ready** and **Quantum-Mappable**—even if executed purely classically—with evidence anchored to UTCS and safety rails verified."

---

## Executive Summary

The AQUA Dual-Literacy Standard establishes **Prompt-Readiness (PR)** and **Quantum-Mappability (QM)** as baseline literacy requirements for all classical engineers. These serve as **interfaces and accelerators** that sit on top of classical methods, treating them as two new "control laws" every engineer should speak.

This standard integrates with the existing CB→QB→UE→FE→FWD→QS flow architecture and UTCS evidence anchoring system.

---

## 1. Core Parallel Framework

### Specification as Control
- **Prompting:** "spec → behavior" via language interface + evaluation harness
- **Quantum:** "Hamiltonian/Ising/QUBO → behavior" via encodings and schedules
- Both are *interfaces that drive solvers*. Bad spec → brittle behavior.

### Encodings Are Everything
- Prompt tokens, tools, and retrieval schemas ↔ variable encoding, penalty weights, mixers/ansätze
- Encoding quality dominates outcome quality

### Robustness & Assurance
- Prompt jailbreaks/drift ↔ quantum noise/barren plateaus
- Guardrails (tests, adversarial probes) and mitigation (RL/evals ↔ error mitigation) are first-class

### Artifacts Are Code
- Prompts and circuits belong in version control with CI, diffs, and UTCS/DET evidence
- Treat both as **design inputs** with traceability (LLC → QS)

### Human-in-the-Loop Optimization
- Iterative prompt tuning ↔ parameter sweeps (β, γ) and warm starts
- Same loop, different knobs

---

## 2. Prompt-Readiness (PR) Framework

### PR-1: Spec Sheet Validation
**Required Elements:**
- **Goal:** Clear, measurable objective statement
- **Constraints:** Safety rails, operational limits, compliance requirements
- **Tool Access:** Enumerated capabilities and permissions
- **Safety Rails:** Fail-safe mechanisms and fallback behaviors

**Validation Criteria:**
```yaml
goal:
  type: string
  required: true
  min_length: 10
  pattern: "^[A-Z].*\\.$"  # Must start with capital, end with period

constraints:
  type: array
  required: true
  min_items: 1
  items:
    type: object
    required: [type, description, enforcement]
    properties:
      type: 
        enum: [safety, operational, compliance, resource]
      description: string
      enforcement:
        enum: [hard_limit, soft_limit, advisory]

tool_access:
  type: object
  required: [available_tools, permissions, rate_limits]

safety_rails:
  type: object
  required: [primary_failsafe, secondary_failsafe, escalation_path]
```

### PR-2: Golden Set & Eval Metrics
**Required Elements:**
- **Golden Dataset:** Reference inputs/outputs for validation
- **Eval Metrics:** Quantitative success measures
- **Fidelity Measures:** Accuracy and consistency metrics
- **Harmlessness Checks:** Safety and ethics validation
- **Determinism Window:** Acceptable variance bounds

**Validation Criteria:**
```yaml
golden_set:
  type: object
  required: [inputs, expected_outputs, test_cases]
  properties:
    test_cases:
      type: array
      min_items: 5
      
eval_metrics:
  type: object
  required: [fidelity, harmlessness, determinism]
  properties:
    fidelity:
      type: object
      required: [accuracy_threshold, consistency_threshold]
      properties:
        accuracy_threshold:
          type: number
          minimum: 0.8
        consistency_threshold:
          type: number
          minimum: 0.9
```

### PR-3: Adversarial Suite
**Required Elements:**
- **Instruction Inversion:** Attempts to reverse/bypass instructions
- **Role Hijack:** Attempts to change system role/behavior
- **Tool Abuse:** Misuse of available tools/capabilities
- **Prompt Injection:** Malicious prompt insertion attempts

**Validation Criteria:**
```yaml
adversarial_tests:
  type: object
  required: [instruction_inversion, role_hijack, tool_abuse, prompt_injection]
  properties:
    instruction_inversion:
      type: array
      min_items: 3
    role_hijack:
      type: array
      min_items: 3
    tool_abuse:
      type: array
      min_items: 3
    prompt_injection:
      type: array
      min_items: 3

pass_criteria:
  type: object
  required: [max_failure_rate, escalation_required]
  properties:
    max_failure_rate:
      type: number
      maximum: 0.05  # 5% max failure rate
```

### PR-4: UTCS/DET Anchor
**Required Elements:**
- **Prompt Hash:** SHA-256 hash of final prompt specification
- **Data Snapshot Hash:** Hash of training/reference data
- **Eval Results Hash:** Hash of evaluation results
- **UTCS Anchor:** Blockchain anchor for immutability

---

## 3. Quantum-Mappability (QM) Framework

### QM-1: Canonical Form Declaration
**Required Elements:**
- **Problem Type:** LP/MILP/QUBO/Ising classification
- **Derivation Notes:** Mathematical transformation documentation
- **Variable Mapping:** Classical → quantum variable correspondence
- **Constraint Translation:** How constraints map to quantum penalties

**Validation Criteria:**
```yaml
canonical_form:
  type: object
  required: [problem_type, derivation_notes, variable_mapping]
  properties:
    problem_type:
      enum: [LP, MILP, QUBO, ISING, MAXCUT, TSP, CUSTOM]
    derivation_notes:
      type: string
      min_length: 50
    variable_mapping:
      type: object
      required: [classical_vars, quantum_vars, mapping_function]
```

### QM-2: Encoding Choice & Penalty Scaling
**Required Elements:**
- **Encoding Rationale:** Why this encoding was chosen
- **Penalty Weights:** Relative importance of constraints
- **Unit Conversion:** Dimensionless transformation approach
- **Scaling Justification:** Mathematical basis for penalty scaling

**Validation Criteria:**
```yaml
encoding:
  type: object
  required: [rationale, penalty_weights, unit_conversion, scaling_justification]
  properties:
    penalty_weights:
      type: object
      patternProperties:
        "^.*$":
          type: number
          minimum: 0
    unit_conversion:
      type: object
      required: [method, validation_tests]
```

### QM-3: Noise/Latency Budget
**Required Elements:**
- **Noise Tolerance:** Acceptable error rates from quantum noise
- **Latency Budget:** Maximum acceptable execution time
- **Classical Baseline Gap:** Acceptable performance gap vs classical
- **Fallback Criteria:** When to revert to classical solution

**Validation Criteria:**
```yaml
performance_budget:
  type: object
  required: [noise_tolerance, latency_budget, baseline_gap, fallback_criteria]
  properties:
    noise_tolerance:
      type: number
      minimum: 0
      maximum: 0.1  # 10% max noise tolerance
    latency_budget:
      type: number
      minimum: 1    # minimum 1ms
    baseline_gap:
      type: number
      minimum: -0.5  # allow 50% worse than classical
      maximum: 2.0   # up to 200% better than classical
```

### QM-4: UTCS/DET Anchor
**Required Elements:**
- **Encoding Hash:** SHA-256 hash of encoding specification
- **Seed Documentation:** Random seeds used for reproducibility
- **Schedule Documentation:** Quantum annealing/gate schedules
- **Results Hash:** Hash of quantum execution results

---

## 4. CI Gate Implementation

### Gate Logic
```python
def aqua_dual_literacy_gate(artifact_metadata):
    pr_status = validate_prompt_readiness(artifact_metadata)
    qm_status = validate_quantum_mappability(artifact_metadata)
    
    if pr_status != "PASS":
        raise ValidationError(f"PR check failed: {pr_status}")
    
    if qm_status not in ["DECLARED", "IMPLEMENTED"]:
        raise ValidationError(f"QM check failed: {qm_status}")
    
    # Store evidence
    evidence_bundle = create_evidence_bundle(artifact_metadata, pr_status, qm_status)
    store_evidence_with_utcs_anchor(evidence_bundle)
    
    return "GATE_PASS"
```

### Evidence Storage Format
```yaml
evidence_bundle:
  timestamp: "2024-01-15T10:30:00Z"
  artifact_id: "AQUA/BWB-Q100/ROUTE-OPT"
  pr_status: "PASS"
  qm_status: "DECLARED"
  cb_qb_metadata:
    classical_solution_hash: "sha256:abc123..."
    quantum_enhancement_hash: "sha256:def456..."
    bridge_flow_version: "1.2.3"
  utcs_anchor: "utcs://anchor/abc123def456"
  evidence_hash: "sha256:evidence123..."
```

---

## 5. Aerospace Concrete Examples

### 5.1 H₂ Route/Energy Planning (BWB-Q100)
```yaml
# PR Specification
prompt_spec:
  goal: "Optimize hydrogen fuel consumption for BWB-Q100 flight path considering wind patterns, NOTAMs, and regulatory constraints."
  constraints:
    - type: safety
      description: "Minimum fuel reserves per EASA requirements"
      enforcement: hard_limit
    - type: operational  
      description: "Maximum flight time 8 hours"
      enforcement: hard_limit
  tool_access:
    available_tools: [weather_api, notam_api, fuel_calculator, route_planner]
    permissions: [read_weather, read_notams, calculate_fuel, optimize_route]
    rate_limits: {weather_api: "100/hour", notam_api: "50/hour"}

# QM Specification  
quantum_mapping:
  problem_type: MILP
  derivation_notes: "Flight path optimization as mixed-integer linear program with waypoint selection (binary) and fuel flow (continuous) variables"
  variable_mapping:
    classical_vars: ["waypoint_selection[i]", "fuel_flow[t]", "altitude[t]"]
    quantum_vars: ["q_waypoint[i]", "q_fuel_continuous[t]"]
    mapping_function: "Binary waypoint decisions → QUBO; continuous variables retained in classical warm start"
```

### 5.2 Composite Ply-Drop Optimization
```yaml
# PR Specification
prompt_spec:
  goal: "Generate admissible carbon fiber layup sequences for wing panel optimization under manufacturing and structural constraints."
  constraints:
    - type: safety
      description: "Minimum factor of safety 1.5 for ultimate load"
      enforcement: hard_limit
    - type: operational
      description: "Maximum 24 plies total thickness"
      enforcement: hard_limit

# QM Specification
quantum_mapping:
  problem_type: QUBO
  derivation_notes: "Ply sequencing as quadratic unconstrained binary optimization with adjacency penalties"
  penalty_weights:
    structural_integrity: 1000.0
    manufacturing_complexity: 100.0
    weight_optimization: 10.0
```

### 5.3 Avionics Partition Scheduling (DAL-A)
```yaml
# PR Specification  
prompt_spec:
  goal: "Compile DO-178C requirement texts into verifiable temporal claims for critical avionics scheduling."
  constraints:
    - type: safety
      description: "DAL-A certification requirements must be maintained"
      enforcement: hard_limit
    - type: compliance
      description: "RTCA DO-178C traceability required"
      enforcement: hard_limit

# QM Specification
quantum_mapping:
  problem_type: QUBO
  derivation_notes: "Task scheduling with precedence constraints mapped to QUBO for stress testing discrete contention scenarios"
  noise_tolerance: 0.01  # 1% for safety-critical
  fallback_criteria: "Any solution gap > 5% reverts to classical solver"
```

---

## 6. Implementation Checklist

### Minimal, Standardizable Checklist
- **Intent:** ✓ documented prompt spec & cost function
- **Encoding:** ✓ token/tool schema & QUBO/Ising mapping notes  
- **Baselines:** ✓ classical solve + gap targets
- **Robustness:** ✓ adversarial prompts & noise scenarios
- **Assurance:** ✓ UTCS anchor + reproducible seeds/runs
- **Governance:** ✓ who approved, which LLC, which QS effectivity

### Integration Points
- **TFA Architecture:** Extends existing TFA layer validation
- **AQUA-OS-PRO:** Integrates with orchestrator service
- **UTCS Blockchain:** Leverages existing anchoring system
- **CB→QB Bridge:** Compatible with quantum-classical flow

---

## 7. Governance and Approval

### Approval Authority
- **LLC Mapping:** Each artifact must map to approved Lifecycle Category
- **QS Effectivity:** Quantum State effectivity dates must be declared
- **Engineering Authority:** Technical approval by qualified personnel
- **Safety Authority:** Safety approval for safety-critical applications

### Audit Trail
All PR+QM validations generate immutable audit records stored in QS with optional UTCS anchoring for external verification.

---

## 8. References

- TFA Architecture Specification
- AQUA-OS-PRO Service Specification  
- UTCS Blockchain Integration Guide
- CB→QB→UE→FE→FWD→QS Flow Documentation
- DO-178C Software Considerations in Airborne Systems
- EASA Certification Specifications