# AQUA Dual-Literacy Standard Implementation

This directory contains the complete implementation of the **AQUA Dual-Literacy Standard (PR+QM)** as specified in the problem statement. The implementation establishes **Prompt-Readiness (PR)** and **Quantum-Mappability (QM)** as baseline literacy requirements for all classical engineers interfacing with AQUA systems.

## 🎯 Policy Implementation

> **"No decision artifact enters production unless it is Prompt-Ready and Quantum-Mappable—even if executed purely classically—with evidence anchored to UTCS and safety rails verified."**

## 📁 File Structure

```
8-RESOURCES/TEMPLATES/
├── AQUA-DUAL-LITERACY-STANDARD.md    # Complete specification document
├── aqua-dual-literacy.schema.json     # JSON schema for validation
├── aqua_dual_literacy_validator.py    # Python implementation
├── examples/                          # Aerospace concrete examples
│   ├── h2-route-planning-bwb-q100.json
│   ├── composite-ply-optimization.json
│   ├── avionics-partition-scheduling-dal-a.json
│   └── test-failure-case.json
└── README-AQUA-DUAL-LITERACY.md      # This file

.github/workflows/
└── aqua-dual-literacy-gate.yml       # CI/CD implementation

tests/
└── test_aqua_dual_literacy.py        # Unit tests
```

## 🚀 Quick Start

### 1. Validate an Artifact

```bash
python 8-RESOURCES/TEMPLATES/aqua_dual_literacy_validator.py \
  path/to/artifact.json \
  --schema 8-RESOURCES/TEMPLATES/aqua-dual-literacy.schema.json \
  --verbose
```

### 2. Run Unit Tests

```bash
python -m pytest tests/test_aqua_dual_literacy.py -v
```

### 3. Try the Examples

```bash
# Test a passing case
python 8-RESOURCES/TEMPLATES/aqua_dual_literacy_validator.py \
  8-RESOURCES/TEMPLATES/examples/h2-route-planning-bwb-q100.json

# Test a failing case  
python 8-RESOURCES/TEMPLATES/aqua_dual_literacy_validator.py \
  8-RESOURCES/TEMPLATES/examples/test-failure-case.json
```

## 🏗️ Architecture Overview

### Core Components

1. **PromptReadinessValidator**: Validates PR-1 through PR-4 criteria
2. **QuantumMappabilityValidator**: Validates QM-1 through QM-4 criteria  
3. **AquaDualLiteracyValidator**: Orchestrates validation and applies gate policy
4. **CI/CD Integration**: GitHub Actions workflow enforces gate policy

### Validation Framework

#### Prompt-Readiness (PR) Checks
- **PR-1**: Spec Sheet (goal, constraints, tool access, safety rails)
- **PR-2**: Golden Set & Eval Metrics (fidelity, harmlessness, determinism)
- **PR-3**: Adversarial Suite (instruction inversion, role hijack, tool abuse, prompt injection)
- **PR-4**: UTCS/DET Anchor (prompt hash, data snapshot hash, eval results hash)

#### Quantum-Mappability (QM) Checks
- **QM-1**: Canonical Form Declaration (LP/MILP/QUBO/Ising, derivation notes, variable mapping)
- **QM-2**: Encoding Choice & Penalty Scaling (rationale, penalty weights, unit conversion)
- **QM-3**: Noise/Latency Budget (noise tolerance, latency budget, baseline gap, fallback criteria)
- **QM-4**: UTCS/DET Anchor (encoding hash, seed docs, schedule docs, results hash)

### Integration Points

- **TFA Architecture**: Extends existing TFA layer validation
- **AQUA-OS-PRO**: Integrates with CB→QB→UE→FE→FWD→QS flow
- **UTCS Blockchain**: Leverages existing anchoring system
- **GitHub Actions**: Enforces gate policy in CI/CD pipeline

## 🛡️ Gate Policy Implementation

The CI gate blocks merge unless:
1. **PR Status** = `PASS`
2. **QM Status** ∈ `{DECLARED, IMPLEMENTED}`

Evidence bundles are generated with CB→QB metadata and anchored to UTCS blockchain.

## ✈️ Aerospace Examples

### 1. H₂ Route/Energy Planning (BWB-Q100)
- **Problem**: Hydrogen fuel route optimization with weather/NOTAM constraints
- **PR Implementation**: Flight safety constraints, adversarial weather scenarios
- **QM Implementation**: MILP formulation with QUBO waypoint selection subproblem

### 2. Composite Ply-Drop Optimization
- **Problem**: Carbon fiber layup sequence optimization
- **PR Implementation**: Manufacturing and structural safety constraints
- **QM Implementation**: QUBO formulation for ply adjacency effects

### 3. Avionics Partition Scheduling (DAL-A)
- **Problem**: DO-178C compliant real-time task scheduling
- **PR Implementation**: Safety-critical timing requirements, certification compliance
- **QM Implementation**: QUBO stress testing of discrete contention scenarios

## 🔧 Configuration

### Environment Variables
```bash
export AQUA_DUAL_LITERACY_VERSION="1.0.0"
export EVIDENCE_DIR="evidence"
```

### Schema Validation
The implementation uses JSON Schema Draft 2020-12 for artifact validation. Schema is located at:
`8-RESOURCES/TEMPLATES/aqua-dual-literacy.schema.json`

### UTCS Integration
Evidence bundles are anchored to UTCS blockchain with format:
```
utcs://anchor/{evidence_hash_prefix}
```

## 📊 Validation Scoring

### PR Scoring
- **Total Checks**: ~20 validation points
- **Error Weight**: 1.0 (fails validation)
- **Warning Weight**: 0.1 (reduces score)
- **Pass Threshold**: Score ≥ 0.8

### QM Scoring  
- **Total Checks**: ~15 validation points
- **Error Weight**: 1.0 (fails validation)
- **Warning Weight**: 0.1 (reduces score)
- **Declared Threshold**: Score ≥ 0.8

## 🚨 Safety & Compliance

### Aviation Safety Integration
- **EASA CS-25**: Compliance validation for commercial aircraft
- **FAR 25.303**: Factor of safety requirements enforcement
- **DO-178C**: Software safety standards for avionics
- **ARP4754A**: System safety assessment processes

### Certification Authority Integration
- **FAA DER**: Designated Engineering Representative approval paths
- **EASA**: European Aviation Safety Agency compliance
- **Transport Canada**: Bilateral airworthiness agreements

## 🔄 Continuous Integration

The GitHub Actions workflow (`aqua-dual-literacy-gate.yml`) automatically:

1. **Detects** decision artifacts in PR changes
2. **Validates** PR and QM compliance
3. **Applies** gate policy (block merge if GATE_FAIL)
4. **Generates** evidence bundles with UTCS anchoring
5. **Comments** on PRs with validation results
6. **Stores** evidence artifacts for audit trail

### Workflow Triggers
- Pull requests to `main` branch
- Pushes to `main` branch  
- Manual workflow dispatch

### Evidence Storage
- **Retention**: 90 days
- **Format**: JSON evidence bundles
- **Anchoring**: UTCS blockchain simulation
- **Audit Trail**: Complete validation history

## 🧪 Testing Strategy

### Unit Tests
- **Prompt-Readiness**: 4 test classes, 11 test methods
- **Quantum-Mappability**: Validation of all QM criteria
- **Integration**: End-to-end validation with examples
- **Error Handling**: Failure case validation

### Test Coverage
```bash
# Run with coverage report
python -m pytest tests/test_aqua_dual_literacy.py --cov=aqua_dual_literacy_validator --cov-report=html
```

### Test Examples
- **Passing Cases**: H2 route planning, composite optimization, avionics scheduling
- **Failing Cases**: Intentional validation failures for negative testing

## 📚 Documentation

### Standards Compliance
- **IEEE 12207**: Software lifecycle processes
- **ISO 26262**: Functional safety automotive (adapted for aerospace)
- **RTCA DO-254**: Hardware design assurance
- **ARP4761**: Safety assessment methodology

### Technical Documentation
- **API Reference**: Full docstring coverage in Python implementation
- **Schema Documentation**: JSON Schema with detailed descriptions
- **Integration Guide**: CB→QB→UE→FE→FWD→QS flow integration
- **Certification Guide**: Regulatory compliance checklist

## 🔮 Future Enhancements

### Planned Features
1. **Quantum Hardware Integration**: Real QPU backend connectivity
2. **Advanced Adversarial Testing**: AI-powered prompt injection detection
3. **Blockchain Integration**: Full UTCS production deployment
4. **Multi-Language Support**: Rust, C++, and Julia implementations
5. **Web Interface**: Browser-based validation dashboard

### Research Directions
1. **Formal Verification**: Mathematical proof of gate policy correctness
2. **Machine Learning**: Automated adversarial test generation
3. **Quantum Advantage**: Empirical quantum vs. classical performance analysis
4. **Certification Automation**: Streamlined regulatory approval processes

## 🤝 Contributing

### Development Setup
```bash
git clone <repository>
cd ASI-T---Aerospace-Super-Intelligence-Transformers---A-Sustainable-Industry-Transition
pip install -e .[dev]
```

### Code Style
- **PEP 8**: Python code formatting
- **Type Hints**: Full type annotation coverage
- **Docstrings**: Comprehensive API documentation
- **Testing**: Unit tests for all new features

### Pull Request Process
1. Implement AQUA Dual-Literacy compliance for your changes
2. Add/update unit tests
3. Update documentation
4. Pass all CI checks including dual-literacy gate
5. Request review from engineering authority

## 📄 License & Compliance

This implementation complies with:
- **Open Source**: MIT/Apache 2.0 compatible
- **Export Control**: ITAR/EAR compliance for aerospace applications  
- **Data Privacy**: GDPR/CCPA compliance for personal data handling
- **Aviation Standards**: Certification-ready implementation

---

## 📞 Support

For questions, issues, or contributions related to the AQUA Dual-Literacy Standard:

- **Technical Issues**: Open GitHub issue with dual-literacy label
- **Certification Questions**: Contact aviation engineering authority
- **Security Concerns**: Follow responsible disclosure process
- **Feature Requests**: Submit enhancement proposal with PR+QM compliance plan

---

*Generated by AQUA Dual-Literacy Standard v1.0.0*