# UTCS Integration: CI-Prepares/Multisig-Approves Workflow

This document describes the secure UTCS anchoring workflow that follows the principle: **"CI-prepares / multisig-approves"** - meaning continuous integration prepares the groundwork for anchoring, but multi-signature approval is required for mainnet transactions.

## Workflow Overview

### 1. CI Preparation (No Direct Mainnet Action)

When a manifest passes validation and is ready for anchoring:

```bash
# CI calls UTCS anchoring service in staging mode
curl -X POST "https://utcs-api.example.com/utcs/anchor" \
  -H "Content-Type: application/json" \
  -d '{
    "manifest_hash": "0x1234567890abcdef...",
    "domain": "AAA-AERODYNAMICS-AND-AIRFRAMES-ARCHITECTURES",
    "llc_path": "TFA/ELEMENTS/FE",
    "staging": true
  }'
```

**Response:**
```json
{
  "submission_id": "UTCS-PREP-2025-001",
  "prepared_tx": {
    "to": "0x...",
    "data": "0x...",
    "gas_estimate": 150000
  },
  "requires_approval": true
}
```

### 2. Output for Approval

CI surfaces the prepared transaction information:
- Logs submission ID and transaction details 
- Creates PR comment with anchor proposal
- Updates `manifest-anchor.json` with pending anchors

**Example PR Comment:**
```markdown
## 🔗 UTCS Anchor Prepared

**Submission ID:** UTCS-PREP-2025-001
**Canonical Hash:** 0x1234567890abcdef...
**Estimated Gas:** 150,000
**Domain:** AAA-AERODYNAMICS-AND-AIRFRAMES-ARCHITECTURES

✅ **Ready for Multisig Approval**
```

### 3. Multisig Review and Approval

Project maintainers review the prepared anchor:
- Verify canonical hash matches manifest content
- Confirm domain and LLC path are correct  
- Check gas estimates and transaction details
- Multiple approvers sign via multisig wallet

**Approval Methods:**
- Ethereum multisig wallet (e.g., Gnosis Safe)
- Internal approval workflow with N-of-M signatures
- Protected GitHub Actions workflow requiring multiple approvals

### 4. Execution on Mainnet

After approval, anchoring is executed:

```bash
# Final anchoring call with approval tokens
curl -X POST "https://utcs-api.example.com/utcs/anchor/execute" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $APPROVED_TOKEN" \
  -d '{
    "submission_id": "UTCS-PREP-2025-001",
    "multisig_signatures": ["0x...", "0x...", "0x..."]
  }'
```

**Response:**
```json
{
  "transaction_hash": "0xabc123...",
  "block_number": 12345678,
  "utcs_id": "UTCS-2025-09-20-AAA-00001",
  "status": "anchored"
}
```

## Security Benefits

This workflow ensures:
- **No Automatic Mainnet Actions**: CI cannot execute blockchain transactions directly
- **Human Oversight**: Multiple reviewers must approve each anchor
- **Two-Man Rule**: Critical operations require multi-party consensus  
- **Audit Trail**: All preparations and approvals are logged
- **Reversibility**: Prepared transactions can be cancelled before approval

## Implementation Notes

- **Testnet First**: All preparations happen on testnet for validation
- **Gas Management**: Estimate costs before approval
- **Error Handling**: Failed preparations don't affect CI/CD pipeline
- **Monitoring**: Alert on unusual anchor requests or failures