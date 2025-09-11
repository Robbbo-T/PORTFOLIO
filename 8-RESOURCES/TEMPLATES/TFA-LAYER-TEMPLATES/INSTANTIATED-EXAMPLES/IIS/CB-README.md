# CB · CLASSICAL BIT (IIS-INTEGRATED-INTELLIGENCE-SOFTWARE)

**Layer:** BITS  
**LLC Code:** CB  
**Canonical Meaning:** CLASSICAL BIT  
**Domain:** IIS - Intelligent Systems Onboard AI  
**Path:** `2-DOMAINS-LEVELS/IIS-INTEGRATED-INTELLIGENCE-SOFTWARE/TFA/BITS/CB/`

## Overview

This directory contains artifacts and implementations for the CLASSICAL BIT within the IIS-INTEGRATED-INTELLIGENCE-SOFTWARE domain. Classical bits serve as the fundamental binary computation layer for safety gating for ML outputs, decision fences, watchdogs, and telemetry flags.

## Purpose

Classical bits in the IIS domain handle:
- **Hard safety gates**: allow/deny ML‑suggested actions under boolean invariants
- **Bitmask protocols** for feature availability and model health
- **Watchdog/fence bits** around inference windows and timing budgets
- **Telemetry flags** for explainability and post‑flight audits

## Directory Structure

```
CB/
├── README.md                    # This file
├── specifications/
│   ├── bit-definitions.yaml    # Classical bit specifications
│   ├── logic-gates.json        # Gate configurations
│   └── state-machines.xml      # State machine definitions
├── implementations/
│   ├── rt-safety-gates/         # Safety gating around ML outputs (C/C++)
│   ├── ml-runtime-bits/         # Bitmask protocols for inference runtime (C++/Rust)
│   └── diag-fdir/         # Diagnostics & FDIR flag aggregation (C)
├── models/
│   ├── boolean-networks.py     # Boolean network models
│   ├── state_machines.py       # FSM helpers (matches examples)
│   └── binary-optimization.jl  # Binary optimization algorithms
├── tests/
│   ├── unit/                   # Unit tests for bit operations
│   ├── integration/            # Integration with other layers
│   └── validation/             # Validation against requirements
└── documentation/
    ├── design-decisions.md     # Design rationale
    └── interface-specs.md      # Interface specifications
```

## Key Components

### 1. SafetyGateCtrl
- **Purpose:** Enforces boolean invariants before any ML‑driven actuator command propagates
- **Implementation:** `implementations/rt-safety-gates/safety_gate_ctrl.cpp`
- **FenceLatency_us:** ≤ 50

### 2. DecisionFence
- **Purpose:** Bitmask fence around model outputs; escalates to fallback when invariants fail
- **Implementation:** `implementations/ml-runtime-bits/decision_fence.rs`
- **FailSafeMode:** deterministic fallback engaged

### 3. HealthFlags
- **Purpose:** Aggregates model/IO health into a compact fault/status word for AP/FCC
- **Implementation:** `implementations/diag-fdir/health_flags.c`
- **Coverage:** ≥ 99% of declared hazards

## Interfaces

### Upward Interface (to COMPONENTS layer)
- **CC (Configuration Cell):** `BITFIELD_IF` for AP/FCC configuration items and ML runtime knobs
- **CI (Configuration Item):** ABI + schema for model registry and allowed action sets
- **Protocol:** `TFA-BIT-V1` ABI + gRPC for supervisory interfaces

### Lateral Interface (to QUBITS layer)
- **QB (Qubit):** Optional QCE hooks for quantum‑assisted monitors (e.g., V&V samplers) using classical bit taps
- **Protocol:** `QCE-PROTO v0.3` (observer‑only in flight)

### Downward Interface (from SYSTEMS layer)
- **SI (System Integration):** Bridges bits to AP/FCC shared memory and AFDX topics
- **DI (Domain Interface):** Deterministic RT fences around inference runtime

## Technical Specifications

```yaml
bit_specifications:
  word_size: 64
  endianness: little
  error_correction: "ECC RAM + software parity on shared memory; lockstep on critical cores"
  
  timing:
    clock_frequency_mhz: 1000
    setup_time_ns: 1.0
    hold_time_ns: 0.5
    
  reliability:
    mtbf_hours: 400000
    bit_error_rate: 1.0e-16
    redundancy_level: "Lockstep CPU + TMR on FPGA fences"
```

## Usage Examples

### Basic Bit Operation

```python
from implementations.rt_safety_gates.safety_gate_ctrl import SafetyGate

# Create IIS ML bit
gate = SafetyGate(name="ml_cmd_gate")
gate.set(False)

# Enable gate when invariants proven
if ap.mode in ("LNAV", "VNAV") and sensors.healthy():
    gate.set(True).set(True)
```

### State Machine Example

```python
from models.state_machines import FSM

fsm = FSM()
fsm.add_state("START", bits="0001")
fsm.add_state("CHECKS", bits="0010")
fsm.add_state("ALLOW", bits="0100")
fsm.add_transition("START", "CHECKS", condition="ml_healthy && invariants_ok && timing_budget_ok")
```

## Testing

```bash
# Run unit tests
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Validate against specifications
python tests/validation/spec_compliance.py
```

## Dependencies

* **Internal:**
  * UE (Unit Elements) for timing/deadline primitives
  * FE (Federation Elements) for audit trail federation
* **External:**
  * gRPC/Cap'n Proto for schemas
  * RTOS (Integrity/RTEMS) for deterministic execution
  * oneTBB/COZ runtime tools for (as applicable) for profiling

## Compliance

* **Standards:**
  * DO‑178C (SW), DO‑254 (if FPGA fences): ARP4754A/ARP4761 (system/safety), ED‑215/DO‑387 (AI safety guidance when adopted)
  * ARP4754A/ARP4761: Development & safety assessment processes
* **Certification:**
  * DAL A for safety gates directly influencing actuator commands
  * DAL B for monitoring/telemetry only

## Maintenance

* **Owner:** IIS Domain Team
* **Review Cycle:** Quarterly
* **Last Updated:** 2025‑09‑11
* **Version:** v1.0.0

## Related Documentation

* [TFA Architecture Overview](../../../META/README.md)
* [IIS Domain Specification](../../../../README.md)
* [QB Quantum Interface](../../QUBITS/QB/README.md)
* [System Integration Guide](../../SYSTEMS/SI/README.md)