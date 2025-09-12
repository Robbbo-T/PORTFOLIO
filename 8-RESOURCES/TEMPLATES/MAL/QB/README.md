# MAL-QB (Qubit Service)

Shared Qubit service for quantum strategies and experiments across all domains.

## Purpose

MAL-QB provides the bridge interface for quantum computing operations that are shared across domains.

## Key Operations

- QAOA/VQE algorithm coordination
- Quantum annealing orchestration
- Quantum simulator management
- Hybrid quantum-classical workflows

## Configuration Template

```yaml
mal_qb:
  service_type: "qubit"
  quantum_resources:
    simulators: ["qasm", "cirq", "pennylane"]
    hardware: ["ibm", "rigetti", "ionq"]
  algorithm_support:
    qaoa: true
    vqe: true
    annealing: true
  
# Integration points  
integration:
  classical_bridge: "MAL-CB"
  federation: "MAL-FE"
  state_management: "MAL-QS"
```

## Usage

Copy this template to your domain and configure for specific quantum computing needs.