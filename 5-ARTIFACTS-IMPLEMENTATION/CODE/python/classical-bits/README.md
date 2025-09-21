# Classical Bits (CB) - CQEA Decision Kernel

## Overview

The Classical-Quantum Extensible Aerospace (CQEA) Decision Kernel provides a production-ready, audit-first system for aerospace decision making with quantum-ready hooks. This implementation follows the TFA V2 quantum-classical bridge architecture.

## Key Features

- **Adversarial-Resilient**: Non-destructive robustness testing with bounded perturbations
- **Quantum-Ready**: Clean hooks for QAOA/VQE with classical fallback
- **UTCS-Compatible**: Deterministic provenance and canonical evidence generation
- **MAL-CB Compliant**: P50 ≤ 120ms, P99 ≤ 300ms performance targets
- **Audit-First**: Complete traceability with SHA256 canonical hashing

## CQEA Decision Loop

1. **Model** — Physics/ops constraints → canonical form (LP/MILP/QUBO/Ising)
2. **Classical solve** — HPC/heuristics for baseline and bounds
3. **Quantum-ready map** — Optional loss/penalty shaping, encodings, noise-aware parameters
4. **Adversarial sandboxes** — Inject perturbations, spoofed data, timing faults for resilience
5. **Assurance** — UTCS evidence, deterministic hashing, cert-oriented reports

## Quick Start

### Python API Usage

```python
from cqea_kernel import create_kernel, RunConfig

# Create pre-configured kernel
kernel = create_kernel()

# Configure run
config = RunConfig(
    problem_id="AAA:DEMO:FUEL-OPT:2025-09-21",
    model_path="demo.yaml",
    solver="milp",  # or "heuristic", "qaoa_stub"
    seed=42,
    adversarial_mode=True
)

# Execute decision
model = {"variables": [], "constraints": []}
result, evidence = kernel.run(config, model)

print(f"Status: {result['status']}")
print(f"Objective: {result['metrics']['objective']}")
print(f"Hash: {evidence['canonical_hash']}")
```

### Command Line Usage

```bash
# Run from YAML manifest
python cqea_runner.py manifests/h2_energy_opt.yaml --verbose

# Output:
# ✅ CQEA run completed: AAA:AMP-BWB-Q100:ROUTE-ENERGY-OPT:2025-09-21
#    Execution time: 2.7ms
#    Status: OPTIMAL
#    Objective: 127.6
```

## Aerospace Use Cases

### 1. H₂ Energy Optimization (BWB-Q100)
Route-level energy optimization with hydrogen boil-off modeling:
- **Variables**: fuel_flow, altitude, speed, tank_pressure
- **Constraints**: Energy balance, thermal limits, payload requirements
- **Solver**: MILP for deterministic optimization
- **Manifest**: `manifests/h2_energy_opt.yaml`

### 2. Avionics Partition Scheduling (DO-178C DAL-A)
Critical timing partition optimization with jitter control:
- **Variables**: partition_1/2/3, hypervisor_overhead
- **Constraints**: Temporal isolation, resource limits, criticality separation
- **Solver**: Heuristic for real-time constraints
- **Manifest**: `manifests/avionics_scheduling.yaml`

### 3. Composite Layup Optimization
Ply-drop optimization under buckling/fatigue constraints:
- **Variables**: ply_angles, thickness
- **Constraints**: Buckling limits, fatigue life, manufacturing
- **Solver**: QAOA stub for quantum exploration
- **Manifest**: `manifests/composite_layup.yaml`

## YAML Manifest Format

```yaml
id: "DOMAIN:SYSTEM:PROBLEM:DATE"
bridge: "CB→QB→UE→FE→FWD→QS"

model:
  kind: "MILP|SCHEDULING|COMPOSITE"
  source: "models/problem.yaml"
  assumptions: ["constraint1", "constraint2"]

solver:
  name: "milp|heuristic|qaoa_stub"
  seed: 42

resilience:
  adversarial_mode: true
  tests: ["noise_test", "timing_test"]

assurance:
  outputs:
    - "reports/analysis.md"
    - "evidence/utcs_anchor.json"
```

## Solvers

### MILP Solver
- **Purpose**: Deterministic optimization with proven optimality
- **Performance**: Variables×2 + Constraints×1.5 ms
- **Use Cases**: Fuel optimization, resource allocation

### Heuristic Solver
- **Purpose**: Fast approximate solutions for real-time constraints
- **Performance**: Variables×0.5 ms (much faster than MILP)
- **Use Cases**: Scheduling, control loops

### QAOA Stub
- **Purpose**: Quantum-ready parameter preparation
- **Performance**: Variables×3 ms (includes circuit preparation)
- **Features**: β/γ parameter tuning, circuit depth optimization
- **Use Cases**: Combinatorial optimization, exploration

## Evidence Generation

All runs generate UTCS-compatible evidence with:
- **Canonical Hash**: SHA256 of deterministic payload
- **UTCS Fields**: ID, timestamps, bridge flow, determinism flag
- **Performance Metrics**: Duration, SLO compliance
- **Solver Metrics**: Objective value, solve time, iterations
- **Configuration**: Complete parameter preservation

## Testing

```bash
# Run CQEA-specific tests
pytest tests/test_cqea_kernel.py -v
pytest tests/test_cqea_runner.py -v

# Test all manifests
python cqea_runner.py manifests/h2_energy_opt.yaml
python cqea_runner.py manifests/avionics_scheduling.yaml
python cqea_runner.py manifests/composite_layup.yaml
```

## Integration with TFA V2

This implementation provides the **CB (Classical Bit)** layer in the TFA V2 quantum-classical bridge:

```
CB (Classical Bit) ← You Are Here
│
├─ QB (Qubit) ← Quantum enhancement hooks
├─ UE (Unit Element) ← Canonical primitives  
├─ FE (Federation Element) ← Multi-asset coordination
├─ FWD (Forward Wave Dynamics) ← Prediction
└─ QS (Quantum State) ← State management
```

The kernel serves as the deterministic baseline and fallback for quantum approaches, ensuring mission-critical reliability.
