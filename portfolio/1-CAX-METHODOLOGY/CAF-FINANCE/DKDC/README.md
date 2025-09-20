# DKDC - Deep Knowledge & Development Context
# Consensed Sharing Protocol (v0.1)

This directory contains the implementation of the DKDC protocol for secure, auditable sharing of user context across LLMs/agents/tools.

## Structure

- `schemas/` - JSON-LD context graphs and policy schemas
- `api/` - REST API endpoints for consense and token management  
- `engine/` - Policy engine and CCT token implementation
- `parcels/` - Context parcelization and redaction
- `audit/` - DET integration and audit trails
- `examples/` - Usage examples and documentation
- `tests/` - Validation tests

## Overview

DKDC defines a secure way to share Deep Knowledge & Development Context using:
- **Consense**: Combined consent + consensus mechanism
- **CCT**: Context Capability Tokens (SD-JWT format)
- **Parcels**: Minimal context bundles with provenance
- **DET**: Digital Evidence Twin anchoring for auditability

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run API server
python api/server.py

# Run tests
pytest tests/
```

## Integration with TFA

This implementation follows TFA (Three-Faceted Architecture) principles:
- UTCS-MI compatible identifiers
- S1000D-style documentation
- DO-178C compliance patterns
- DET anchoring for audit trails