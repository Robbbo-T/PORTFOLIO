# Copilot Smoke Prompts (paste into Copilot Chat)

Test these prompts in Copilot Chat to verify the instructions are working correctly:

## 1. TFA Domain Scaffolding
```
Scaffold AAA domain under TFA with SYSTEMS/STATIONS/COMPONENTS/BITS/QUBITS/ELEMENTS/WAVES/STATES and add META/README.md placeholders that cite docs/quantum-classical-bridge.md. Provide paths and file contents.
```

**Expected**: Complete TFA hierarchy for AAA-AERODYNAMICS-AND-AIRFRAMES-ARCHITECTURES with all 8 layer groups and correct LLC codes.

## 2. FE Manifest Creation
```
Create an FE manifest example (YAML) for a cross-domain workflow coordinating AAA and PPP. Ensure it passes the artifact-manifest.schema.json and includes a placeholder EIP-712 FE signature block.
```

**Expected**: Valid YAML with Federation Entanglement structure, cross-domain coordination, and EIP-712 signature placeholder.

## 3. QS Artifact Manifest
```
Draft a QS artifact manifest for a Bell-state experiment (QB→QS). Include provenance, canonical_hash placeholder, and UTCS candidate ID.
```

**Expected**: Quantum State manifest with quantum experiment details, proper provenance chain, and UTCS integration.

## 4. GitHub Action for Validation
```
Write a GitHub Action job that runs tfa_structure_validator and quantum-layers-check. Fail the PR if deprecated terms appear.
```

**Expected**: Complete workflow that integrates with existing validation system and terminology enforcement.

## 5. AQUA API Integration
```
Given services/aqua-webhook/README.md, produce a curl example calling POST /api/v1/manifests/validate with a minimal manifest, and show the expected JSON response.
```

**Expected**: Working curl command with proper manifest structure and realistic API response format.

## 6. Terminology Test
```
Show me the difference between 'Federation Entanglement' and 'Fine Element', and explain why one is forbidden.
```

**Expected**: Clear explanation of approved vs deprecated terminology, with reference to quantum semantics and CI enforcement.

## 7. Idempotent Scaffold
```
Create a make target that idempotently scaffolds the CQH-CRYOGENICS-QUANTUM-AND-H2 domain with all TFA layers, ensuring it won't break existing structure.
```

**Expected**: Makefile target using idempotent patterns that check existing structure before creating.

## 8. Cross-Domain Workflow
```
Design a workflow that spans AAA (aerodynamics) and PPP (propulsion) domains, showing how FE coordinates between them using the quantum-classical bridge.
```

**Expected**: Multi-domain architecture showing CB→QB→UE/FE→FWD→QS flow with proper domain separation.

## 9. Security Validation
```
Write a script that validates no secrets or private keys appear in TFA manifests or documentation, following DEFENSE context partitioning rules.
```

**Expected**: Security scanning script that respects DEFENSE/CROSS contexts and SBOM requirements.

## 10. UTCS Integration
```
Show how to prepare a manifest for UTCS anchoring without proposing mainnet actions, following the CI-prepares/multisig-approves pattern.
```

**Expected**: Staging workflow that prepares payloads for human approval, no direct mainnet operations.

## Validation Steps
After running prompts, verify:
1. ✅ No deprecated terminology used
2. ✅ Proper TFA hierarchy followed  
3. ✅ LLC codes from canonical llc-map.yaml
4. ✅ Idempotent patterns preferred
5. ✅ CI validation compatibility
6. ✅ Security best practices followed
7. ✅ AQUA/UTCS integration patterns used

## Expected Failures (good signs)
- Copilot refuses to use "Fine Element" or "Station Envelop"
- Copilot suggests `make check` before committing
- Copilot references grounding documents
- Copilot creates TFA-compliant paths only