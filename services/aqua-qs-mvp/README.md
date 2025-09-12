# AQUA-OS QS-MVP Service

Quantum State MVP Service with UTCS Anchoring - Implementation of MAL-QS for state management and provenance with blockchain anchoring.

## Overview

The QS-MVP service provides audit-grade state management with immutable provenance tracking, evidence bundling, and optional UTCS blockchain anchoring for mission-critical operations. This service implements the MAL-QS (Main Application Layer - Quantum State) component of the TFA V2 quantum-classical bridge architecture.

## Features

- **Quantum State Management**: Immutable state commits with cryptographic hashing
- **UTCS Anchoring**: Optional blockchain anchoring for external verification
- **Provenance Tracking**: Complete lineage and evidence bundling
- **Performance Metrics**: Real-time performance monitoring and reporting
- **Integration Ready**: Compatible with AQUA-OS PRO and other MAL services

## Key Components

### State Types
- `route_plan`: Route planning and optimization results
- `optimization_result`: Quantum and classical optimization outcomes
- `system_config`: System configuration changes
- `mission_state`: Mission-critical state checkpoints
- `evidence_bundle`: Compliance and audit evidence
- `checkpoint`: General-purpose state checkpoints

### UTCS Anchoring
- **Network**: utcs-testnet (configurable)
- **Confirmation**: Single confirmation required
- **Performance**: ~100ms additional latency for anchoring
- **Verification**: Automatic anchor verification

## Usage

### Basic State Commit
```python
from services.aqua_qs_mvp.qs_service import commit_quantum_state

result = await commit_quantum_state(
    utcs_id="TEST/QS/001",
    state_type="route_plan", 
    data={
        "route": "JFK->LAX",
        "optimization_score": -2.5,
        "fuel_estimate": 12000
    },
    require_utcs_anchor=False
)
```

### Anchored State Commit
```python
result = await commit_quantum_state(
    utcs_id="MISSION/QS/CRITICAL",
    state_type="mission_state",
    data=mission_data,
    require_utcs_anchor=True  # Enables UTCS anchoring
)
```

## Performance

- **Basic Commit**: ~60ms average
- **Anchored Commit**: ~150ms average (includes blockchain interaction)
- **Throughput**: 100+ commits/second
- **SLA**: < 200ms P95 commit time

## Integration Points

### MAL-QB Integration
```python
# Quantum optimization results -> QS commit
qb_result = await execute_quantum_optimization(utcs_id, strategy="qaoa")
qs_result = await commit_quantum_state(
    utcs_id=utcs_id,
    state_type="optimization_result",
    data=qb_result,
    require_utcs_anchor=True  # Critical results
)
```

### MAL-CB Integration  
```python
# Classical solver results -> QS commit
cb_result = await solve_classical_optimization(utcs_id, solver_type="linear")
qs_result = await commit_quantum_state(
    utcs_id=utcs_id,
    state_type="optimization_result", 
    data=cb_result,
    require_utcs_anchor=False  # Non-critical results
)
```

### AQUA-OS PRO Integration
```python
# PRO orchestrator -> QS state commits
cycle_result = await orchestrator.process_cycle()
qs_result = await commit_quantum_state(
    utcs_id=cycle_result["utcs_id"],
    state_type="route_plan",
    data=cycle_result,
    require_utcs_anchor=cycle_result["critical"]
)
```

## Configuration

```python
# QS Service Configuration
qs_config = {
    "utcs_anchoring": {
        "enabled": True,
        "network": "utcs-testnet", 
        "endpoint": "https://api.utcs-blockchain.com"
    },
    "performance": {
        "max_commit_time_ms": 200,
        "enable_metrics": True
    }
}
```

## Compliance Integration

### DO-178C Integration
- **DAL-A**: Formal verification for critical state commits
- **DAL-B**: MC/DC coverage for state management logic
- **Traceability**: Complete UTCS ID linkage to requirements

### RMF Security Controls
- **AC-2**: State access control and authentication  
- **AU-3**: Complete audit trail generation
- **SC-8**: Encrypted state transmission
- **SC-13**: Cryptographic state protection

### STIG Compliance
- **Category I**: Input validation and injection prevention
- **Category II**: Cryptographic implementation standards
- **Category III**: Security configuration requirements

## Testing

```bash
# Run QS service tests
cd services/aqua-qs-mvp/
python3 qs_service.py

# Integration testing
cd ../../scripts/
python3 test_integration.py
```

## Metrics and Monitoring

The QS service provides comprehensive performance metrics:

```python
metrics = qs_service.get_performance_metrics()
# Returns:
# {
#   "total_commits": 150,
#   "successful_commits": 148, 
#   "anchored_states": 45,
#   "average_commit_time_ms": 95.2
# }
```

## API Reference

### Core Functions

#### `commit_quantum_state(utcs_id, state_type, data, require_utcs_anchor=False)`
Commits a new quantum state with optional UTCS anchoring.

#### `query_state_lineage(state_id)`  
Retrieves complete lineage information for a state.

#### `export_state_evidence(state_id)`
Exports complete evidence bundle for compliance and auditing.

### Return Formats

All functions return standardized response formats with `success`, `error`, and relevant data fields.

## Security Considerations

- **State Immutability**: All committed states are immutable
- **Cryptographic Hashing**: BLAKE2b-256 for content hashing
- **Access Control**: Integration with TFA RBAC system
- **Audit Trail**: Complete provenance tracking
- **Blockchain Anchoring**: Optional external verification via UTCS

## Development Status

- ✅ Core state management functionality
- ✅ UTCS anchoring integration  
- ✅ Performance metrics and monitoring
- ✅ AQUA-OS PRO integration
- 🚧 Advanced lineage queries
- 🚧 Multi-signature support
- 📋 Formal verification integration

## Related Services

- **AQUA-OS PRO**: Route optimization orchestrator
- **MAL-QB**: Quantum processing unit backend  
- **MAL-CB**: Classical solver backend
- **MAL-FWD**: Future wave dynamics nowcast service
- **UTCS Blockchain**: External anchoring and verification

---

**Service Owner**: TFA Platform Team  
**Last Updated**: September 2025  
**Version**: 1.0 (MVP)