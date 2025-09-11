#!/usr/bin/env python3
"""
EIP-712 Signature Verification for Federation Entanglement Manifests

Implements EIP-712 typed structured data hashing and signature verification
for TFA manifests, particularly Federation Entanglement (FE) artifacts.

EIP-712 provides a standard way to hash and sign typed structured data,
enabling secure off-chain signing of TFA manifests with on-chain verification.

Domain Separator includes:
- name: "TFA-FEDERATION-ENTANGLEMENT"  
- version: "2"
- chainId: Network-specific chain ID
- verifyingContract: Address of the verification contract

Primary Type: "FederationManifest"
"""

import json
import hashlib
from typing import Dict, Any, Optional, List
from eth_account.messages import encode_structured_data
from eth_account import Account
from eth_utils import to_checksum_address, is_address


# EIP-712 Domain for TFA Federation Entanglement
TFA_EIP712_DOMAIN = {
    "name": "TFA-FEDERATION-ENTANGLEMENT",
    "version": "2",
    "chainId": 1,  # Mainnet default, should be configurable
    "verifyingContract": "0x0000000000000000000000000000000000000000"  # Placeholder
}

# EIP-712 Type definitions for Federation Entanglement manifests
FE_MANIFEST_TYPES = {
    "EIP712Domain": [
        {"name": "name", "type": "string"},
        {"name": "version", "type": "string"},
        {"name": "chainId", "type": "uint256"},
        {"name": "verifyingContract", "type": "address"}
    ],
    "FederationMember": [
        {"name": "domain", "type": "string"},
        {"name": "role", "type": "string"},
        {"name": "weight", "type": "uint256"}
    ],
    "OrchestrationRules": [
        {"name": "consensusProtocol", "type": "string"},
        {"name": "quorumThreshold", "type": "uint256"},
        {"name": "timeoutSeconds", "type": "uint256"}
    ],
    "FederationManifest": [
        {"name": "manifestType", "type": "string"},
        {"name": "name", "type": "string"},
        {"name": "version", "type": "string"},
        {"name": "canonicalHash", "type": "bytes32"},
        {"name": "members", "type": "FederationMember[]"},
        {"name": "orchestrationRules", "type": "OrchestrationRules"},
        {"name": "nonce", "type": "uint256"}
    ]
}


def normalize_manifest_for_eip712(manifest: Dict[str, Any], canonical_hash: str) -> Dict[str, Any]:
    """
    Normalize TFA manifest for EIP-712 signing.
    
    Converts manifest into EIP-712 compatible structure matching
    the FederationManifest type definition.
    
    Args:
        manifest: Raw TFA manifest
        canonical_hash: Canonical hash of the manifest (0x prefixed)
        
    Returns:
        EIP-712 compatible message structure
    """
    # Extract and normalize members
    members = []
    for member in manifest.get('members', []):
        members.append({
            "domain": str(member.get('domain', '')),
            "role": str(member.get('role', 'participant')),
            "weight": int(member.get('weight', 1))
        })
    
    # Extract orchestration rules
    rules = manifest.get('orchestration_rules', {})
    orchestration_rules = {
        "consensusProtocol": str(rules.get('consensus_protocol', 'proof-of-authority')),
        "quorumThreshold": int(float(rules.get('quorum_threshold', 0.67)) * 1000),  # Convert to basis points
        "timeoutSeconds": int(rules.get('timeout_seconds', 300))
    }
    
    # Ensure canonical hash is bytes32 format
    if canonical_hash.startswith('0x'):
        canonical_hash_bytes32 = canonical_hash
    else:
        canonical_hash_bytes32 = f"0x{canonical_hash}"
    
    # Build EIP-712 message
    eip712_message = {
        "manifestType": str(manifest.get('type', 'FE')),
        "name": str(manifest.get('name', '')),
        "version": str(manifest.get('version', '1.0.0')),
        "canonicalHash": canonical_hash_bytes32,
        "members": members,
        "orchestrationRules": orchestration_rules,
        "nonce": int(manifest.get('nonce', 0))
    }
    
    return eip712_message


def create_eip712_message(manifest: Dict[str, Any], canonical_hash: str, 
                         domain: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Create complete EIP-712 structured data message.
    
    Args:
        manifest: TFA manifest
        canonical_hash: Canonical hash of manifest
        domain: Custom domain (uses default if not provided)
        
    Returns:
        Complete EIP-712 message ready for signing
    """
    if domain is None:
        domain = TFA_EIP712_DOMAIN.copy()
    
    message = normalize_manifest_for_eip712(manifest, canonical_hash)
    
    return {
        "types": FE_MANIFEST_TYPES,
        "primaryType": "FederationManifest",
        "domain": domain,
        "message": message
    }


def sign_federation_manifest(manifest: Dict[str, Any], canonical_hash: str, 
                           private_key: str, domain: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Sign a Federation Entanglement manifest using EIP-712.
    
    Args:
        manifest: TFA manifest to sign
        canonical_hash: Canonical hash of the manifest
        private_key: Private key for signing (hex string with or without 0x)
        domain: Custom EIP-712 domain (uses default if not provided)
        
    Returns:
        Signature dictionary with r, s, v, and signer address
    """
    # Create EIP-712 message
    eip712_message = create_eip712_message(manifest, canonical_hash, domain)
    
    # Encode the structured data
    encoded_message = encode_structured_data(eip712_message)
    
    # Sign with private key
    if not private_key.startswith('0x'):
        private_key = f"0x{private_key}"
    
    account = Account.from_key(private_key)
    signed_message = account.sign_message(encoded_message)
    
    return {
        "r": signed_message.r.to_bytes(32, 'big').hex(),
        "s": signed_message.s.to_bytes(32, 'big').hex(),
        "v": signed_message.v,
        "signer": account.address,
        "signature": signed_message.signature.hex()
    }


def verify_federation_signature(manifest: Dict[str, Any], signature_data: Dict[str, Any], 
                               canonical_hash: str, domain: Optional[Dict[str, Any]] = None) -> bool:
    """
    Verify an EIP-712 signature for a Federation Entanglement manifest.
    
    Args:
        manifest: Original TFA manifest
        signature_data: Signature data with r, s, v, and signer
        canonical_hash: Canonical hash of the manifest
        domain: Custom EIP-712 domain (uses default if not provided)
        
    Returns:
        True if signature is valid, False otherwise
    """
    try:
        # Create the same EIP-712 message that was signed
        eip712_message = create_eip712_message(manifest, canonical_hash, domain)
        
        # Encode the structured data
        encoded_message = encode_structured_data(eip712_message)
        
        # Reconstruct signature from components
        r = int(signature_data['r'], 16) if isinstance(signature_data['r'], str) else signature_data['r']
        s = int(signature_data['s'], 16) if isinstance(signature_data['s'], str) else signature_data['s']
        v = signature_data['v']
        
        # Recover signer address
        recovered_address = Account.recover_message(
            encoded_message, 
            vrs=(v, r, s)
        )
        
        # Verify signer matches
        expected_signer = signature_data['signer']
        if not is_address(expected_signer):
            return False
            
        return to_checksum_address(recovered_address) == to_checksum_address(expected_signer)
        
    except Exception as e:
        print(f"Signature verification error: {e}")
        return False


def get_validator_registry() -> List[str]:
    """
    Get list of authorized validator addresses.
    
    In production, this would query the on-chain validator registry.
    For now, returns a placeholder list.
    
    Returns:
        List of authorized validator addresses
    """
    # Placeholder validator addresses
    return [
        "0x742d35Cc6635C0532925a3b8D0D8c5b4c8d46AAB",  # Example validator 1
        "0x123d45Cc6635C0532925a3b8D0D8c5b4c8d46DDD",  # Example validator 2
    ]


def is_authorized_validator(signer_address: str) -> bool:
    """
    Check if signer is an authorized validator.
    
    Args:
        signer_address: Address to check
        
    Returns:
        True if signer is authorized, False otherwise
    """
    authorized_validators = get_validator_registry()
    return to_checksum_address(signer_address) in [
        to_checksum_address(addr) for addr in authorized_validators
    ]


def verify_with_registry(manifest: Dict[str, Any], signature_data: Dict[str, Any], 
                        canonical_hash: str, domain: Optional[Dict[str, Any]] = None) -> Dict[str, bool]:
    """
    Verify signature and check against validator registry.
    
    Args:
        manifest: TFA manifest
        signature_data: Signature data
        canonical_hash: Canonical hash
        domain: Custom EIP-712 domain
        
    Returns:
        Dictionary with verification results:
        - signature_valid: Whether signature is cryptographically valid
        - signer_authorized: Whether signer is in validator registry
        - overall_valid: Whether both checks pass
    """
    signature_valid = verify_federation_signature(manifest, signature_data, canonical_hash, domain)
    signer_authorized = is_authorized_validator(signature_data['signer']) if signature_valid else False
    
    return {
        'signature_valid': signature_valid,
        'signer_authorized': signer_authorized,
        'overall_valid': signature_valid and signer_authorized,
        'signer': signature_data['signer']
    }


if __name__ == "__main__":
    # Example usage and testing
    from eth_account import Account
    
    # Create a test account
    test_account = Account.create()
    print(f"Test signer address: {test_account.address}")
    print(f"Test private key: {test_account.key.hex()}")
    print()
    
    # Sample manifest
    sample_manifest = {
        "type": "FE",
        "name": "Test Federation",
        "version": "1.0.0",
        "members": [
            {"domain": "AAA", "role": "coordinator", "weight": 2},
            {"domain": "CQH", "role": "participant", "weight": 1}
        ],
        "orchestration_rules": {
            "consensus_protocol": "proof-of-authority",
            "quorum_threshold": 0.67,
            "timeout_seconds": 300
        },
        "nonce": 42
    }
    
    canonical_hash = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    
    print("Sample Manifest:")
    print(json.dumps(sample_manifest, indent=2))
    print()
    
    # Sign the manifest
    signature = sign_federation_manifest(sample_manifest, canonical_hash, test_account.key.hex())
    print("Signature:")
    print(json.dumps(signature, indent=2))
    print()
    
    # Verify the signature
    is_valid = verify_federation_signature(sample_manifest, signature, canonical_hash)
    print(f"Signature Verification: {'✓ PASS' if is_valid else '✗ FAIL'}")
    
    # Check against registry
    registry_result = verify_with_registry(sample_manifest, signature, canonical_hash)
    print(f"Registry Check: {json.dumps(registry_result, indent=2)}")