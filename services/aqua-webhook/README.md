# AQUA Webhook Service

> **Architectural Quality Unified Anchor** - Core webhook service for TFA V2 manifest validation, EIP-712 verification, and UTCS anchoring.

## Overview

AQUA provides the central webhook infrastructure for the TFA V2 ecosystem, enabling deterministic validation, cryptographic verification, and blockchain anchoring of Federation Entanglement (FE) manifests and other TFA artifacts.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   GitHub CI     │───▶│   AQUA Webhook   │───▶│ UTCS Blockchain │
│   (PR Checks)   │    │   Validation     │    │   (Anchoring)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                               │
                               ▼
                       ┌──────────────────┐
                       │  EIP-712 Verify  │
                       │  (Signatures)    │
                       └──────────────────┘
```

## Endpoints

### Health Check
- **GET** `/health` - Service health and status

### Manifest Validation
- **POST** `/api/v1/manifests/validate` - Validate TFA manifests and compute canonical hashes

### Manifest Submission
- **POST** `/manifests/submit` - Submit validated manifests with EIP-712 signatures

### UTCS Anchoring (CI Only)
- **POST** `/utcs/anchor` - Anchor manifest hashes to UTCS blockchain

## Features

### 🔒 **Security**
- HSTS + TLS enforcement in production
- EIP-712 signature verification for all submissions
- GitHub App token authentication for CI operations
- Validator registry integration

### ⚡ **Validation**
- JSON Schema validation for all TFA manifest types
- Business rule validation (quorum thresholds, member roles, etc.)
- Canonical hash computation for consistency
- Cross-reference validation

### 🔗 **Integration**
- GitHub Actions workflow integration
- UTCS blockchain anchoring
- Event bus emission for OPTIMO-DT
- Validator registry support

## Installation

### Development Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Set environment variables
export FLASK_ENV=development
export FLASK_SECRET_KEY=your-secret-key
export GITHUB_CI_TOKEN=your-ci-token
export AQUA_WEBHOOK_SECRET=your-webhook-secret

# Run development server
python app.py
```

### Production Deployment

```bash
# Use gunicorn for production
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## API Reference

### Validate Manifest

Validate a TFA manifest and compute its canonical hash.

```http
POST /api/v1/manifests/validate
Content-Type: application/json

{
  "manifest": {
    "type": "FE",
    "name": "Cross-Domain Federation",
    "version": "1.0.0",
    "members": [
      {"domain": "AAA", "role": "coordinator"},
      {"domain": "CQH", "role": "participant"}
    ],
    "orchestration_rules": {
      "consensus_protocol": "proof-of-authority",
      "quorum_threshold": 0.67,
      "timeout_seconds": 300
    }
  },
  "domain": "AAA-AERODYNAMICS-AND-AIRFRAMES-ARCHITECTURES",
  "llc_path": "TFA/ELEMENTS/FE"
}
```

**Response:**
```json
{
  "valid": true,
  "canonical_hash": "0x1234567890abcdef...",
  "errors": [],
  "metadata": {
    "domain": "AAA-AERODYNAMICS-AND-AIRFRAMES-ARCHITECTURES",
    "llc_path": "TFA/ELEMENTS/FE",
    "manifest_type": "FE",
    "validation_timestamp": "2025-01-27T12:00:00Z"
  }
}
```

### Submit Manifest

Submit a validated manifest with EIP-712 signature for anchoring.

```http
POST /manifests/submit
Content-Type: application/json

{
  "manifest": { ... },
  "canonical_hash": "0x1234567890abcdef...",
  "signature": {
    "r": "0x...",
    "s": "0x...",
    "v": 27,
    "signer": "0x742d35Cc6635C0532925a3b8D0D8c5b4c8d46AAB"
  },
  "metadata": {
    "pr_number": 123,
    "commit_sha": "abc123def456"
  }
}
```

**Response:**
```json
{
  "status": "accepted",
  "submission_id": "1234567890abcdef",
  "canonical_hash": "0x1234567890abcdef...",
  "signer": "0x742d35Cc6635C0532925a3b8D0D8c5b4c8d46AAB",
  "next_steps": "Queued for UTCS anchoring"
}
```

### Anchor to UTCS (CI Only)

Anchor manifest hash to UTCS blockchain. Requires valid GitHub CI token.

```http
POST /utcs/anchor
Authorization: Bearer your-ci-token
Content-Type: application/json

{
  "canonical_hash": "0x1234567890abcdef...",
  "submission_id": "1234567890abcdef",
  "metadata": {
    "domain": "AAA",
    "llc_path": "TFA/ELEMENTS/FE",
    "pr_number": 123,
    "commit_sha": "abc123def456"
  }
}
```

**Response:**
```json
{
  "status": "anchored",
  "canonical_hash": "0x1234567890abcdef...",
  "anchor_tx_hash": "0xfedcba0987654321...",
  "utcs_block_number": 12345,
  "anchor_timestamp": "2025-01-27T12:00:00Z",
  "metadata": { ... }
}
```

## EIP-712 Signature Verification

AQUA implements EIP-712 typed structured data hashing for secure off-chain signing of TFA manifests.

### Domain Separator
```json
{
  "name": "TFA-FEDERATION-ENTANGLEMENT",
  "version": "2",
  "chainId": 1,
  "verifyingContract": "0x..."
}
```

### Primary Type: FederationManifest
```json
{
  "manifestType": "string",
  "name": "string", 
  "version": "string",
  "canonicalHash": "bytes32",
  "members": "FederationMember[]",
  "orchestrationRules": "OrchestrationRules",
  "nonce": "uint256"
}
```

### Example Signing (JavaScript)
```javascript
const domain = {
  name: 'TFA-FEDERATION-ENTANGLEMENT',
  version: '2',
  chainId: 1,
  verifyingContract: '0x...'
};

const types = {
  FederationManifest: [
    {name: 'manifestType', type: 'string'},
    {name: 'name', type: 'string'},
    {name: 'version', type: 'string'},
    {name: 'canonicalHash', type: 'bytes32'},
    {name: 'members', type: 'FederationMember[]'},
    {name: 'orchestrationRules', type: 'OrchestrationRules'},
    {name: 'nonce', type: 'uint256'}
  ],
  // ... other types
};

const signature = await signer._signTypedData(domain, types, message);
```

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `FLASK_ENV` | Flask environment | No | `production` |
| `FLASK_SECRET_KEY` | Flask secret key | Yes | - |
| `GITHUB_CI_TOKEN` | GitHub CI authentication token | Yes | - |
| `AQUA_WEBHOOK_SECRET` | Webhook secret for signatures | Yes | - |
| `PORT` | Server port | No | `5000` |

### Validator Registry

The service maintains a registry of authorized validators who can sign manifests. In production, this would be an on-chain registry contract.

Current placeholder validators:
- `0x742d35Cc6635C0532925a3b8D0D8c5b4c8d46AAB`
- `0x123d45Cc6635C0532925a3b8D0D8c5b4c8d46DDD`

## Schema Validation

AQUA validates manifests against JSON schemas specific to each LLC type:

- **FE** (Federation Entanglement): `schemas/federation_entanglement.json`
- **QS** (Quantum State): `schemas/quantum_state.json`
- **UE** (Unit Element): `schemas/unit_element.json`
- **CB** (Classical Bit): `schemas/classical_bit.json`
- **QB** (Qubit): `schemas/qubit.json`

### Business Rules Validation

Beyond schema validation, AQUA enforces business rules:

#### Federation Entanglement (FE)
- Minimum 2 members required
- Quorum threshold between 0.5 and 1.0
- At least one coordinator recommended
- Timeout values validated for practical ranges

#### Quantum State (QS)
- Valid representation types enforced
- State vector dimensions must be powers of 2
- Coherence time relationships validated
- Measurement protocol completeness

## Error Handling

### Validation Errors
```json
{
  "valid": false,
  "errors": [
    {
      "type": "schema_validation",
      "message": "Missing required field: members",
      "path": ["members"],
      "invalid_value": null
    }
  ],
  "canonical_hash": null
}
```

### Signature Errors
```json
{
  "error": "Invalid EIP-712 signature",
  "details": {
    "expected_signer": "0x742d35Cc...",
    "recovered_signer": "0x123d45Cc...",
    "canonical_hash": "0x1234567890abcdef..."
  }
}
```

## Security Considerations

### Production Deployment
- Always use HTTPS with valid TLS certificates
- Set strong, random secret keys
- Rotate CI tokens regularly
- Monitor for unusual validation patterns
- Implement rate limiting for public endpoints

### Signature Verification
- Signatures are verified using EIP-712 standard
- Validator registry prevents unauthorized submissions
- Canonical hashing ensures data integrity
- Nonce prevents replay attacks

## Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/

# Run with coverage
pytest --cov=. tests/
```

### Adding New LLC Types

1. Create JSON schema in `schemas/`
2. Add schema mapping in `manifest_schema.py`
3. Add business rules validation
4. Update API documentation

## Monitoring & Observability

### Health Metrics
- Validation success/failure rates
- Response times by endpoint
- Signature verification success rates
- UTCS anchoring success rates

### Logs
- All validation attempts (success/failure)
- Signature verification events
- UTCS anchoring transactions
- Error conditions and stack traces

## Support

For issues, questions, or contributions:
- Create GitHub issues in the PORTFOLIO repository
- Follow TFA V2 development guidelines
- Reference the canonical LLC mapping in `8-RESOURCES/llc-map.yaml`

## License

MIT License - see LICENSE file for details.