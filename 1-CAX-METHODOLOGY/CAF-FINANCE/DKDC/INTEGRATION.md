# DKDC Integration Guide

This guide shows how to integrate DKDC (Deep Knowledge & Development Context) protocol with existing TFA portfolio workflows.

## Integration Overview

DKDC integrates with the TFA (Three-Faceted Architecture) portfolio through:

1. **GitHub Actions**: Automated CPL validation and link checking
2. **CLI Tools**: Command-line interface for manual operations
3. **API Endpoints**: REST API for programmatic integration
4. **DET Anchoring**: Integration with Digital Evidence Twin system
5. **UTCS-MI Compatibility**: Using universal identifiers for traceability

## GitHub Actions Integration

### Workflow: DKDC Validation

The `.github/workflows/dkdc-validation.yml` workflow runs on:
- Push to DKDC files
- Pull request changes
- Weekly scheduled validation

### Usage in CI/CD

```yaml
# In your existing workflow
- name: Validate DKDC Context
  run: |
    cd 1-CAX-METHODOLOGY/CAF-FINANCE/DKDC
    python cli/dkdc_cli.py validate --cpl .dkdc/policy.yaml
    python cli/dkdc_cli.py linkcheck --semantic --det audit_trail.json
```

## CLI Integration

### Basic Commands

```bash
# Validate CPL policy
dkdc-cli validate --cpl policy.yaml

# Check repository links with semantic analysis
dkdc-cli linkcheck --semantic --det results.json

# Create context offer
dkdc-cli offer offer_config.yaml

# Issue CCT token
dkdc-cli token policy:consense:abc123 --config token_config.yaml

# Create context parcel
dkdc-cli parcel token.jwt path1.md path2.md --recipient did:example:llm
```

### Configuration Files

#### Offer Configuration (`offer_config.yaml`)
```yaml
ddi:
  project: "utcs:proj:YOUR-PROJECT"
  statement: "Development collaboration purpose"
  outputs: ["prs:enhancements"]
  
catalog:
  - path: "README.md"
    hash: "sha256-..."
    
llc: "project"
controller: "did:example:your-did"
processors: ["did:example:llm.gateway"]
```

#### Token Configuration (`token_config.yaml`)
```yaml
controller: "did:example:your-did"
processors: ["did:example:processor"]
purpose: "specific-development-task"
scopes:
  - "read:repo:docs/**"
  - "write:suggestions:pull-requests"
llc: "session"
```

## API Integration

### Starting the API Server

```bash
cd 1-CAX-METHODOLOGY/CAF-FINANCE/DKDC
python api/server.py
```

### Example API Usage

```python
from examples.api_client import DKDCClient

client = DKDCClient("http://localhost:8080")

# Submit context offer
offer = client.submit_offer(
    ddi={"project": "utcs:proj:DEMO", "statement": "Test"},
    catalog=[{"path": "README.md"}],
    llc="session"
)

# Issue token
token = client.issue_token(
    policy_id=offer["policy_id"],
    controller="did:example:user",
    processors=["did:example:llm"]
)
```

## TFA Integration Patterns

### 1. Domain-Level Integration

```
2-DOMAINS-LEVELS/
├── <DOMAIN>/
│   ├── TFA/
│   └── .dkdc/
│       ├── policy.yaml      # Domain-specific CPL
│       └── context.json     # Context catalog
```

### 2. Project-Level Integration

```
3-PROJECTS-USE-CASES/
├── <PROJECT>/
│   ├── .dkdc/
│   │   ├── project_policy.yaml
│   │   └── context_catalog.json
│   └── README.md           # Links to DKDC context
```

### 3. System-Level Integration

Add to system specifications:

```yaml
# In TFA system templates
dkdc_integration:
  policy_template: "templates/si_system_policy.yaml"
  context_scopes:
    - "read:system:specifications"
    - "read:system:interfaces"
  retention: "P30D"  # 30 days for system context
```

## DET Integration

### Audit Trail Generation

Every DKDC operation creates DET records:

```python
# Automatic DET anchoring
det_id = det_anchor.record_consense(
    policy_id="policy:consense:abc123",
    policy_hash="sha256-...",
    approvals=[...]
)

# Retrieve audit trail
audit_trail = det_anchor.get_audit_trail(det_id)
```

### UTCS-MI Identifiers

DKDC uses UTCS-MI compatible identifiers:

```
EstándarUniversal:DKDC-v0.1-CCT-<token_id>
EstándarUniversal:DET-CONSENSE-<policy_id>
EstándarUniversal:DKDC-Parcel-<parcel_hash>
```

## Security Integration

### Policy Enforcement

```python
from engine.policy_guard import PolicyGuard

guard = PolicyGuard()

# Before any context operation
violations = guard.evaluate({
    "request": {"scopes": ["read:repo:sensitive.md"]},
    "cct": cct_claims,
    "now": current_time
})

if violations:
    raise SecurityError("Policy violations detected")
```

### Export Controls

DKDC enforces export controls at runtime:

- **Internet Export**: Disabled by default
- **Third-party Sharing**: Requires explicit permission
- **Model-to-model**: Allowed within trusted boundaries

## Compliance Integration

### S1000D Compatibility

```yaml
# CPL with S1000D data module reference
s1000d_format: true
data_module: "DMC-DKDC-A-00-00-00-00A-040A-A"
technical_name: "DKDC Context Sharing Policy"
```

### DO-178C Patterns

- **Deterministic Behavior**: All operations are reproducible
- **Traceable Requirements**: Each scope maps to specific requirements
- **Evidence Generation**: Comprehensive audit trails

## Migration Guide

### From Manual Context Sharing

1. **Inventory Context**: List all shared documents/data
2. **Define Policies**: Create CPL files for each sharing scenario
3. **Implement Guards**: Add policy enforcement to existing workflows
4. **Enable Auditing**: Configure DET anchoring

### From Basic OAuth2

1. **Map Scopes**: Convert OAuth2 scopes to DKDC format
2. **Add Context Metadata**: Enhance tokens with DKDC claims
3. **Implement Redaction**: Add content filtering capabilities
4. **Enable Revocation**: Implement CCT revocation lists

## Best Practices

### Policy Design

- **Principle of Least Privilege**: Grant minimum necessary scopes
- **Time-bounded Access**: Use appropriate LLC levels
- **Purpose Binding**: Explicitly state development intentions
- **Regular Review**: Audit and update policies regularly

### Implementation

- **Gradual Rollout**: Start with non-sensitive context
- **Monitor Usage**: Track policy violations and access patterns
- **Test Thoroughly**: Validate all integration points
- **Document Everything**: Maintain clear audit trails

### Security

- **Rotate Keys**: Regular cryptographic key rotation
- **Monitor Exports**: Track all context sharing activities
- **Validate Inputs**: Sanitize all user-provided data
- **Implement Canaries**: Use detection tokens in sensitive content

## Troubleshooting

### Common Issues

1. **Token Validation Fails**
   ```bash
   dkdc-cli validate --cct your_token.jwt
   ```

2. **Policy Violations**
   ```python
   violations = policy_guard.evaluate(request_data)
   for v in violations:
       print(f"{v.rule}: {v.message}")
   ```

3. **Context Access Denied**
   - Check scope authorization
   - Verify token expiration
   - Confirm redaction compliance

### Debugging

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Support

- Check DET audit trails for operation history
- Review policy enforcement logs
- Validate UTCS-MI identifier formats
- Ensure TFA structure compliance