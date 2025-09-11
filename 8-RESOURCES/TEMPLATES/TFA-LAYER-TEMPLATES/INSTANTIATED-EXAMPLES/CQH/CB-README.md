# CB · CLASSICAL BIT (CQH-CRYOGENICS-QUANTUM-INTERFACES-HYDROGEN-CELLS)

**Layer:** BITS  
**LLC Code:** CB  
**Canonical Meaning:** CLASSICAL BIT  
**Domain:** CQH - Cryogenics, Quantum Interfaces & Hydrogen Cells  
**Path:** `2-DOMAINS-LEVELS/CQH-CRYOGENICS-QUANTUM-INTERFACES-HYDROGEN-CELLS/TFA/BITS/CB/`

## Overview

This directory contains artifacts and implementations for the CLASSICAL BIT within the CQH-CRYOGENICS-QUANTUM-INTERFACES-HYDROGEN-CELLS domain. Classical bits serve as the fundamental binary computation layer for safety interlocks, cryo‑plant state words, quantum‑classical handshakes, and hydrogen cell BMS fault/status.

## Purpose

Classical bits in the CQH domain handle:
- **Interlock matrices** (valves, pumps, heaters) with provable safe sequences
- **Cryostat stage statuses** (T, P, valve position) aggregated into state words
- **Q‑bridge control registers** for qubit reset/measure/ready handshakes
- **Hydrogen BMS fault words** and inhibit lines

## Directory Structure

```
CB/
├── README.md                    # This file
├── specifications/
│   ├── bit-definitions.yaml    # Classical bit specifications
│   ├── logic-gates.json        # Gate configurations
│   └── state-machines.xml      # State machine definitions
├── implementations/
│   ├── cryo-pfc/         # Plant/fault control matrices (VHDL/C)
│   ├── qbridge-control/         # Quantum interface control regs (C++/C)
│   └── bms-safety/         # H2 cell BMS fault words (C)
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

### 1. InterlockMatrix
- **Purpose:** Ensures ordered, safe actuation across cryo plant elements
- **Implementation:** `implementations/cryo-pfc/interlock_matrix.vhd`
- **SafeOrderingProof:** Model‑checked (property set P1..P7)

### 2. QBridgeCR
- **Purpose:** Classical control register block for qubit reset/measure/ready lines
- **Implementation:** `implementations/qbridge-control/qbridge_cr.hpp`
- **Latency_us:** ≤ 25

### 3. BMSFaultWord
- **Purpose:** Aggregated H2‑cell faults + inhibits
- **Implementation:** `implementations/bms-safety/fault_word.c`
- **HazardCoverage:** ≥ 99%

## Interfaces

### Upward Interface (to COMPONENTS layer)
- **CC (Configuration Cell):** `BITFIELD_IF` tables for plant items and quantum channels
- **CI (Configuration Item):** Register schemas exported in `documentation/interface-specs.md`
- **Protocol:** `TFA-BIT-V1` ABI + C headers

### Lateral Interface (to QUBITS layer)
- **QB (Qubit):** Control bits synchronize qubit reset/measure/ready with QIR adapters
- **Protocol:** `QCE-PROTO v0.3` (shared memory or SPI‑lite for embedded prototypes)

### Downward Interface (from SYSTEMS layer)
- **SI (System Integration):** Maps to **AFDX/ARINC 429** (flight), **CAN‑FD** (lab rigs) buses
- **DI (Domain Interface):** Hooks for cryo PLCs and BMS controllers

## Technical Specifications

```yaml
bit_specifications:
  word_size: 32
  endianness: little
  error_correction: "CRC‑16 on frames; duplication + voter on safety lines"
  
  timing:
    clock_frequency_mhz: 50
    setup_time_ns: 3.2
    hold_time_ns: 1.6
    
  reliability:
    mtbf_hours: 200000
    bit_error_rate: 1.0e-12
    redundancy_level: "DWC with majority voter; cold‑spare controllers"
```

## Usage Examples

### Basic Bit Operation

```python
from implementations.qbridge_control.qbridge_cr import ControlReg

# Create CQH cryo bit
cr = ControlReg(name="qb_handshake")
cr.set(True)

# Request quantum measurement
if cryo.ready and qubit.iface_idle():
    cr.request_measure().set(True)
```

### State Machine Example

```python
from models.state_machines import FSM

fsm = FSM()
fsm.add_state("IDLE", bits="0001")
fsm.add_state("COOLDOWN", bits="0010")
fsm.add_state("READY", bits="0100")
fsm.add_transition("IDLE", "COOLDOWN", condition="T<4K && P in range && leaks==0")
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
  * UE (Unit Elements) for valve/pump IO primitives and timebases
  * FE (Federation Elements) for cross‑lab federation and auditability
* **External:**
  * FreeRTOS/Zephyr for embedded control
  * QIR adapter library for quantum runtime bridging
  * CANopen/AFDX stacks for as applicable

## Compliance

* **Standards:**
  * DO‑178C / DO‑254: depending on target (SW/HW)
  * IEC 61508: functional safety for plant interlocks
* **Certification:**
  * DAL A for interlocks preventing hazardous energy release
  * DAL B for status/monitoring paths

## Maintenance

* **Owner:** CQH Domain Team
* **Review Cycle:** Quarterly
* **Last Updated:** 2025‑09‑11
* **Version:** v1.0.0

## Related Documentation

* [TFA Architecture Overview](../../../META/README.md)
* [CQH Domain Specification](../../../../README.md)
* [QB Quantum Interface](../../QUBITS/QB/README.md)
* [System Integration Guide](../../SYSTEMS/SI/README.md)