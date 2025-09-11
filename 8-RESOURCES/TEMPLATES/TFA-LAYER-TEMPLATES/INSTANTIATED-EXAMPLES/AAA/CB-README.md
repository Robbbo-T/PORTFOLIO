# CB · CLASSICAL BIT (AAA-AERODYNAMICS-AND-AIRFRAMES-ARCHITECTURES)

**Layer:** BITS  
**LLC Code:** CB  
**Canonical Meaning:** CLASSICAL BIT  
**Domain:** AAA - Aerodynamics and Airframes Architectures  
**Path:** `2-DOMAINS-LEVELS/AAA-AERODYNAMICS-AND-AIRFRAMES-ARCHITECTURES/TFA/BITS/CB/`

## Overview

This directory contains artifacts and implementations for the CLASSICAL BIT within the AAA-AERODYNAMICS-AND-AIRFRAMES-ARCHITECTURES domain. Classical bits serve as the fundamental binary computation layer for HPC CFD/FEA kernels, discrete I/O for aeroelastic sensing/actuation, and flight-loads monitoring flags.

## Purpose

Classical bits in the AAA domain handle:
- Bit-parallel masks for **mesh nodes, boundary conditions, and partition flags** in CFD/FEA
- **Rounding/exception flags** coordination for fixed/floating-point pipelines
- **Glitch-filtered latching** of discrete sensors/actuators in aero/flight-control benches
- **FDIR fault words** for aeroelastic/loads monitoring and test automation

## Directory Structure

```
CB/
├── README.md                    # This file
├── specifications/
│   ├── bit-definitions.yaml    # Classical bit specifications
│   ├── logic-gates.json        # Gate configurations
│   └── state-machines.xml      # State machine definitions
├── implementations/
│   ├── hpc-bitset/         # SIMD/TBB-accelerated bitset kernels (C++)
│   ├── fpga-rtl/         # Discrete latch + debouncing (SystemVerilog)
│   └── rtos-hal/         # GPIO/IRQ HAL for benches (C/RTOS)
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

### 1. BitSet64 Kernel
- **Purpose:** High‑throughput masking over millions of mesh nodes/edges
- **Implementation:** `implementations/hpc-bitset/bitset64.cpp`
- **Throughput_Gb_s:** ≥ 256

### 2. DiscreteLatch
- **Purpose:** Glitch‑filtered latch for sensor discretes (spoilers, flaps rig, AoA vane bench I/O)
- **Implementation:** `implementations/fpga-rtl/discrete_latch.sv`
- **Debounce_ns:** ≥ 100

### 3. SECDED‑ECC
- **Purpose:** Single‑error‑correct/dual‑error‑detect on scratch buffers used by HPC kernels
- **Implementation:** `implementations/hpc-bitset/secded.hpp`
- **Code:** Hamming(72,64) SECDED

## Interfaces

### Upward Interface (to COMPONENTS layer)
- **CC (Configuration Cell):** Exposes `BITFIELD_IF` structures for mesh/solver params and I/O maps
- **CI (Configuration Item):** Memory‑mapped register schema for benches; schema artifacts in `documentation/interface-specs.md`
- **Protocol:** `TFA-BIT-V1` ABI + Cap'n Proto schema for host↔bench messages

### Lateral Interface (to QUBITS layer)
- **QB (Qubit):** QCE shim packs/unpacks bitstrings to quantum measurement registers for hybrid (VQE/QAOA) aero‑loads prototypes
- **Protocol:** `QCE-PROTO v0.3` (shared memory ring + optional RDMA channel)

### Downward Interface (from SYSTEMS layer)
- **SI (System Integration):** Maps bit I/O to **ARINC 429/664 simulation buses** in HIL benches
- **DI (Domain Interface):** Stable ABI for solver kernels (CFD/FEA) and aeroelastic pipelines

## Technical Specifications

```yaml
bit_specifications:
  word_size: 64
  endianness: little
  error_correction: "SECDED (Hamming 72,64) on buffers; TMR on FPGA latches"
  
  timing:
    clock_frequency_mhz: 3200
    setup_time_ns: 1.2
    hold_time_ns: 0.6
    
  reliability:
    mtbf_hours: 500000
    bit_error_rate: 1.0e-15
    redundancy_level: "TMR critical paths; hot‑spare worker threads"
```

## Usage Examples

### Basic Bit Operation

```python
from implementations.hpc_bitset.bitset64 import BitSet64

# Create AAA solver bit
mesh_mask = BitSet64(name="bc_inlet_nodes")
mesh_mask.set(True)

# Apply mask to action flag
if solver.ready and mesh_mask.any():
    action_flag = BitSet64(name="advance_timestep").set(True)
```

### State Machine Example

```python
from models.state_machines import FSM

fsm = FSM()
fsm.add_state("INIT", bits="0001")
fsm.add_state("RUN", bits="0010")
fsm.add_state("PAUSE", bits="0100")
fsm.add_transition("INIT", "RUN", condition="solver_ready && io_ok")
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
  * UE (Unit Elements) for GPIO primitives and timing units
  * FE (Federation Elements) for artifact governance and build graph
* **External:**
  * Boost::dynamic_bitset for high‑level bitsets
  * oneTBB for parallel primitives
  * RTEMS/FreeRTOS for bench HAL

## Compliance

* **Standards:**
  * DO‑178C: Software considerations in airborne systems
  * DO‑254: Design assurance for airborne electronic hardware
* **Certification:**
  * DAL B for control‑path‑adjacent benches
  * DAL C for monitoring/analysis utilities

## Maintenance

* **Owner:** AAA Domain Team
* **Review Cycle:** Quarterly
* **Last Updated:** 2025‑09‑11
* **Version:** v1.0.0

## Related Documentation

* [TFA Architecture Overview](../../../META/README.md)
* [AAA Domain Specification](../../../../README.md)
* [QB Quantum Interface](../../QUBITS/QB/README.md)
* [System Integration Guide](../../SYSTEMS/SI/README.md)