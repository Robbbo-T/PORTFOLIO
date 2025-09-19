# TFA Quantum-Bridge Package (CB/QB/UE/FE/FWD/QS)

This package implements the core JSON schemas, test stubs, and CI configuration for the TFA Quantum-Bridge architecture aligned with FADEC-X hybrid power management and ARP4761 hazard analysis.

## Package Structure

```
PORTFOLIO/
├── schemas/                    # JSON Schema definitions
│   ├── det_anchor.schema.json  # DET/QS anchor schema
│   ├── FADEC_X.spec.json      # FADEC-X hybrid power spec
│   └── arp4761.hazard.json    # ARP4761 hazard register schema
├── tests/                      # Test stubs for CI validation
│   ├── test_schema_spec.py     # Schema validation tests
│   ├── test_invariants.py     # System invariant tests
│   ├── test_safety_cage.py    # Safety cage trip tests
│   ├── test_qs_anchor.py       # QS anchor hash replay tests
│   ├── test_hazard_linkage.py  # Hazard traceability tests
│   └── test_brex_and_contracts.py # BREX/CAx placeholder tests
├── .ci/
│   └── Makefile               # CI test orchestration
└── ASSURANCE/ARP4761/
    └── hazard_register_hybrid_fc.yaml # Sample hazard register
```

## Schemas

### DET/QS Anchor Schema (`det_anchor.schema.json`)
- **Purpose**: Quantum State deterministic anchoring for audit trails
- **Key Features**: 
  - UTCS-MI code validation pattern
  - Event mode tracking with reasons and limits
  - SHA256 content hashing
  - Digital signatures (ed25519/ecdsa support)
  - Trace reference linking

### FADEC-X Spec Schema (`FADEC_X.spec.json`)
- **Purpose**: Hybrid power system configuration validation
- **Key Features**:
  - HVDC bus parameters with AFDI latency constraints
  - Surge protection thresholds and trip timing
  - Fuel cell power profiles and thermal limits
  - AMB (Air-Mixable Battery) reserve energy specs
  - Operating modes and trip table validation

### ARP4761 Hazard Schema (`arp4761.hazard.json`)
- **Purpose**: Aviation safety hazard register validation
- **Key Features**:
  - Hazard severity classification
  - Risk likelihood assessment
  - Control measures and residual risk tracking
  - Test and requirement traceability links

## CI Test Framework

The CI framework validates:

1. **Schema Compliance** (`make schema`): JSON schema validation with example data
2. **System Invariants** (`make invariants`): Property-based testing with Hypothesis
3. **Safety Cage** (`make trips`): Trip latency and protection response validation
4. **QS Anchoring** (`make qs`): Canonical hashing and content integrity
5. **Hazard Linkage** (`make arp`): Traceability between hazards, tests, and requirements
6. **BREX Contracts** (`make brex`): Placeholder for existing S1000D BREX validation

## Usage

### Running Tests
```bash
# Run all tests
make -f .ci/Makefile test

# Run specific test suites
make -f .ci/Makefile schema
make -f .ci/Makefile invariants
make -f .ci/Makefile trips
make -f .ci/Makefile qs
make -f .ci/Makefile arp
```

### Schema Validation Example
```python
import json, jsonschema
from pathlib import Path

# Load schema
schema = json.loads(Path("schemas/FADEC_X.spec.json").read_text())

# Validate FADEC-X configuration
config = {
    "hvdc": {"v_nom": 800, "v_min": 650, "v_max": 1050, "afdi_latency_ms": 2},
    "surge": {"s_min": 0.07, "trip_latency_ms": 50},
    "fuel_cell": {"p_cont_kw": 1500, "p_peak_kw": 3500, "peak_duration_s": 300, "ramp_kw_per_s": 300},
    "amb": {"reserve_energy_j": 1.0e6, "rundown_time_s": 60},
    "modes": ["NORMAL","ASSIST","DEGRADED"],
    "trip_table": [
        {"monitor":"AFDI","threshold":"TRIP","action":"isolate_bus_zone; fc_cmd=0; mode=DEGRADED","latency_ms":2}
    ]
}

jsonschema.validate(instance=config, schema=schema)
```

## Integration Points

- **UTCS Blockchain**: DET anchors provide blockchain integration points
- **QAL Bus**: Event traces and audit trails feed into QAL Bus infrastructure
- **S1000D Framework**: BREX validation connects to existing S1000D tooling
- **ARP4754A/ARP4761**: Safety analysis aligns with aviation safety standards

## Key Design Patterns

1. **Canonical Serialization**: JSON objects use `separators=(",",":")` and `sort_keys=True` for deterministic hashing
2. **UTCS Code Format**: `UTCS-MI-[A-Z]{3}-[A-Z0-9_.-]+` pattern for universal traceability
3. **Digital Signatures**: `DET:(ed25519|ecdsa):` prefix pattern for signature verification
4. **Property-Based Testing**: Hypothesis framework for invariant validation
5. **Hazard Traceability**: Bi-directional linking between hazards, tests, and requirements

## Status

✅ All schemas created and validated with example data
✅ Test framework implemented with passing tests
✅ CI Makefile configured for automated validation
✅ Hazard register template created with proper linkage
✅ Integration with existing PORTFOLIO structure complete

Ready for integration with production FADEC-X systems and ARP4761 safety analysis workflows.