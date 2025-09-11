# Federation Entanglement Manifest Templates

This directory contains templates for creating Federation Entanglement (FE) manifests that comply with TFA V2 architecture and support EIP-712 signatures for blockchain verification.

## Templates Available

### 1. `fe-manifest-minimal.yaml`
- **Use Case**: Simple two-member federations
- **Features**: Basic structure with required fields only
- **Best For**: Quick prototyping, initial federation setup

### 2. `fe-manifest-example.yaml`
- **Use Case**: Complex multi-domain federations
- **Features**: Full feature set including dependencies, interfaces, and governance
- **Best For**: Production federations, comprehensive integration

### 3. `fe-manifest-template-generator.py`
- **Use Case**: Automated template generation
- **Features**: Interactive CLI for creating custom templates
- **Best For**: Standardized federation creation workflow

## Quick Start

### Creating a New FE Manifest

1. **Copy Template**:
   ```bash
   cp fe-manifest-minimal.yaml ../../../2-DOMAINS-LEVELS/{YOUR_DOMAIN}/TFA/ELEMENTS/FE/your-federation.yaml
   ```

2. **Fill in Values**:
   - Replace all `{PLACEHOLDER}` values with actual data
   - Ensure all domain codes match existing domains
   - Set appropriate capabilities and endpoints

3. **Validate with AQUA**:
   ```bash
   # Using AQUA validation service
   curl -X POST https://robbbo-t.space/webhook/api/v1/manifests/validate \
     -H "Content-Type: application/json" \
     -d @validation-request.json
   ```

4. **Sign with EIP-712**:
   ```bash
   # Using signing script (requires private key)
   python scripts/sign_fe_manifest.py --manifest your-federation.yaml --key $PRIVATE_KEY
   ```

## Field Reference

### Required Fields

#### Basic Information
- `type`: Must be "FE" for Federation Entanglement
- `name`: Human-readable federation name
- `version`: Semantic version (e.g., "1.0.0")
- `members`: Array of federation members (minimum 2)
- `orchestration_rules`: Governance and consensus configuration

#### Member Configuration
- `domain`: Full domain identifier (e.g., "AAA-AERODYNAMICS-AND-AIRFRAMES-ARCHITECTURES")
- `role`: Member role ("coordinator", "participant", "observer", "validator")
- `weight`: Voting weight for consensus (integer, typically 1-5)
- `capabilities`: Array of capabilities provided by this member
- `endpoints`: Network endpoints for API access

#### Orchestration Rules
- `consensus_protocol`: Consensus mechanism ("proof-of-authority", "proof-of-stake", "byzantine-fault-tolerant", "simple-majority")
- `quorum_threshold`: Minimum fraction for consensus (0.5-1.0)
- `timeout_seconds`: Timeout for operations (10-86400 seconds)

### Optional Fields

#### Advanced Features
- `interfaces`: External interfaces exposed by federation
- `dependencies`: Dependencies on other TFA artifacts
- `metadata`: Additional metadata for governance and tracking

#### EIP-712 Signature Fields
- `nonce`: Incrementing nonce for replay protection
- `canonical_hash`: Computed by AQUA (read-only)
- `signature`: EIP-712 signature components (added by signing process)

## Validation Rules

### Schema Validation
All manifests must pass JSON schema validation against `services/aqua-webhook/schemas/federation_entanglement.json`.

### Business Rules
- Minimum 2 members required
- Exactly one coordinator recommended (warnings for 0 or multiple)
- Quorum threshold between 0.5 and 1.0
- Timeout values between 10 and 86400 seconds
- Valid domain identifiers from approved domain list

### Security Rules
- All endpoints must specify authentication requirements
- Signatures must be valid EIP-712 signatures
- Signers must be in approved validator registry

## Signing Process

### Manual Signing

1. **Generate Canonical Hash**:
   ```python
   from services.aqua_webhook.canonicalize import compute_canonical_hash
   canonical_hash = compute_canonical_hash(manifest)
   ```

2. **Create EIP-712 Message**:
   ```python
   from services.aqua_webhook.eip712_verify import create_eip712_message
   eip712_message = create_eip712_message(manifest, canonical_hash)
   ```

3. **Sign with Private Key**:
   ```python
   from services.aqua_webhook.eip712_verify import sign_federation_manifest
   signature = sign_federation_manifest(manifest, canonical_hash, private_key)
   ```

### Automated Signing

Use the provided signing script:

```bash
python scripts/sign_fe_manifest.py \
  --manifest path/to/manifest.yaml \
  --private-key $PRIVATE_KEY \
  --network testnet \
  --output signed-manifest.yaml
```

## Integration with CI/CD

### GitHub Actions Integration

The FE manifests automatically integrate with GitHub Actions workflows:

1. **TFA Structure Validation**: Validates TFA hierarchy compliance
2. **Schema Validation**: Validates against JSON schema
3. **AQUA Validation**: Sends to AQUA webhook for comprehensive validation
4. **UTCS Anchoring**: Anchors canonical hashes to blockchain
5. **OPTIMO-DT Update**: Updates digital thread with federation changes

### Workflow Files
- `.github/workflows/tfa_structure_validator.yml`: Basic structure validation
- `.github/workflows/quantum-layers-check.yml`: Enhanced validation with AQUA integration
- `.github/workflows/anchor_utcs.yml`: Blockchain anchoring

## Best Practices

### Naming Conventions
- **Federation Names**: Use descriptive names that indicate purpose and scope
- **Capabilities**: Use snake_case for capability identifiers
- **Versions**: Follow semantic versioning strictly

### Security Considerations
- **Private Keys**: Never commit private keys to repository
- **Endpoint Security**: Always require authentication for production endpoints
- **Signature Verification**: Verify signatures before accepting manifests

### Performance Optimization
- **Endpoint Timeout**: Set realistic timeout values based on expected response times
- **Retry Logic**: Configure appropriate retry policies for network operations
- **Caching**: Consider caching strategies for frequently accessed data

### Documentation
- **Purpose Documentation**: Clearly document federation purpose and objectives
- **Capability Documentation**: Document what each capability provides
- **Integration Guide**: Provide integration guide for new members

## Troubleshooting

### Common Issues

#### Validation Failures
- **Schema Errors**: Check against JSON schema using online validators
- **Business Rule Violations**: Review business rules in validation output
- **Domain References**: Ensure all domain codes are valid and exist

#### Signature Issues
- **Invalid Signatures**: Verify private key and canonical hash computation
- **Signer Not Authorized**: Check if signer is in validator registry
- **Replay Attacks**: Increment nonce for each new version

#### Network Issues
- **Endpoint Failures**: Verify endpoint URLs and authentication
- **Timeout Issues**: Adjust timeout values for network conditions
- **Connectivity**: Check network connectivity and firewall rules

### Debugging Tools

#### AQUA Validation
```bash
# Test manifest validation
curl -X POST $AQUA_WEBHOOK_URL/api/v1/manifests/validate \
  -H "Content-Type: application/json" \
  -d '{"manifest": {...}, "domain": "AAA", "llc_path": "TFA/ELEMENTS/FE"}'
```

#### Signature Verification
```python
# Verify signature manually
from services.aqua_webhook.eip712_verify import verify_federation_signature
is_valid = verify_federation_signature(manifest, signature, canonical_hash)
```

#### Schema Validation
```python
# Validate against schema
import jsonschema
from services.aqua_webhook.schemas.manifest_schema import get_llc_schema
schema = get_llc_schema("TFA/ELEMENTS/FE")
jsonschema.validate(manifest, schema)
```

## Support

For additional support:
- **Documentation**: See main TFA V2 architecture documentation
- **Issues**: Create GitHub issues for bugs or feature requests
- **Community**: Join TFA V2 Slack channel for discussions
- **Architecture Council**: Contact TFA Architecture Council for design questions

---

**Last Updated**: 2025-01-27  
**Version**: 2.0.0  
**Maintainer**: TFA Architecture Council