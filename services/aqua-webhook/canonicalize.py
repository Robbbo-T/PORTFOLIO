#!/usr/bin/env python3
"""
Canonical Hash Computation for TFA Manifests

Provides deterministic canonical hashing for Federation Entanglement (FE) manifests
and other TFA artifacts to ensure consistency across distributed systems.

The canonical hash algorithm:
1. Normalize manifest structure (sort keys, standardize formatting)
2. Extract essential fields only (exclude metadata like timestamps)
3. Compute SHA-256 hash of normalized JSON representation
4. Return hex-encoded hash with 0x prefix
"""

import json
import hashlib
from typing import Dict, Any, List
from collections import OrderedDict


def normalize_manifest(manifest: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize manifest structure for canonical hashing.
    
    Rules:
    - Sort all dictionary keys recursively
    - Remove timestamp and volatile metadata fields
    - Standardize field names and values
    - Ensure consistent ordering of arrays where order doesn't matter
    
    Args:
        manifest: Raw manifest dictionary
        
    Returns:
        Normalized manifest ready for hashing
    """
    def _normalize_recursive(obj):
        if isinstance(obj, dict):
            # Remove volatile fields
            filtered = {k: v for k, v in obj.items() 
                       if k not in ['timestamp', 'created_at', 'updated_at', 
                                   'last_modified', 'version_timestamp']}
            # Sort keys and normalize values
            return OrderedDict(
                (k, _normalize_recursive(v)) 
                for k, v in sorted(filtered.items())
            )
        elif isinstance(obj, list):
            # For arrays that should be order-independent (like member lists),
            # sort them. For ordered arrays (like process steps), preserve order.
            normalized_items = [_normalize_recursive(item) for item in obj]
            
            # Heuristic: if all items are strings or simple types, sort them
            # This handles cases like member lists, dependency lists, etc.
            if all(isinstance(item, (str, int, float, bool)) for item in normalized_items):
                return sorted(normalized_items)
            else:
                return normalized_items
        else:
            return obj
    
    return _normalize_recursive(manifest)


def compute_canonical_hash(manifest: Dict[str, Any]) -> str:
    """
    Compute canonical hash for a TFA manifest.
    
    Args:
        manifest: TFA manifest dictionary
        
    Returns:
        Hex-encoded SHA-256 hash with 0x prefix
        
    Example:
        >>> manifest = {"type": "FE", "members": ["A", "B"], "timestamp": "2025-01-27"}
        >>> compute_canonical_hash(manifest)
        '0x1234567890abcdef...'
    """
    # Normalize the manifest
    normalized = normalize_manifest(manifest)
    
    # Convert to canonical JSON (sorted keys, no whitespace)
    canonical_json = json.dumps(
        normalized,
        sort_keys=True,
        separators=(',', ':'),  # No whitespace
        ensure_ascii=True
    )
    
    # Compute SHA-256 hash
    hash_digest = hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()
    
    # Return with 0x prefix for consistency with blockchain conventions
    return f"0x{hash_digest}"


def verify_canonical_hash(manifest: Dict[str, Any], expected_hash: str) -> bool:
    """
    Verify that a manifest produces the expected canonical hash.
    
    Args:
        manifest: TFA manifest dictionary
        expected_hash: Expected canonical hash (with or without 0x prefix)
        
    Returns:
        True if hashes match, False otherwise
    """
    computed_hash = compute_canonical_hash(manifest)
    
    # Normalize expected hash (ensure 0x prefix)
    if not expected_hash.startswith('0x'):
        expected_hash = f"0x{expected_hash}"
    
    return computed_hash.lower() == expected_hash.lower()


def batch_compute_hashes(manifests: List[Dict[str, Any]]) -> List[str]:
    """
    Compute canonical hashes for multiple manifests.
    
    Args:
        manifests: List of TFA manifest dictionaries
        
    Returns:
        List of canonical hashes in the same order
    """
    return [compute_canonical_hash(manifest) for manifest in manifests]


def get_hash_metadata(manifest: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get metadata about the canonical hash computation.
    
    Args:
        manifest: TFA manifest dictionary
        
    Returns:
        Dictionary with hash metadata including:
        - canonical_hash: The computed hash
        - normalized_size: Size of normalized JSON in bytes
        - excluded_fields: Fields that were excluded from hashing
        - normalization_stats: Statistics about the normalization process
    """
    normalized = normalize_manifest(manifest)
    canonical_json = json.dumps(normalized, sort_keys=True, separators=(',', ':'))
    canonical_hash = compute_canonical_hash(manifest)
    
    # Find excluded fields by comparing original and normalized
    def find_excluded_fields(original, normalized, path=""):
        excluded = []
        if isinstance(original, dict):
            for key, value in original.items():
                current_path = f"{path}.{key}" if path else key
                if key not in normalized:
                    excluded.append(current_path)
                elif key in normalized:
                    excluded.extend(find_excluded_fields(value, normalized[key], current_path))
        return excluded
    
    excluded_fields = find_excluded_fields(manifest, normalized)
    
    return {
        'canonical_hash': canonical_hash,
        'normalized_size': len(canonical_json.encode('utf-8')),
        'original_size': len(json.dumps(manifest).encode('utf-8')),
        'excluded_fields': excluded_fields,
        'normalization_stats': {
            'keys_sorted': True,
            'volatile_fields_removed': len(excluded_fields),
            'canonical_format': 'JSON_compact'
        }
    }


if __name__ == "__main__":
    # Example usage and testing
    sample_manifest = {
        "type": "FE",
        "name": "Cross-Domain Aerodynamics Federation",
        "version": "1.0.0",
        "timestamp": "2025-01-27T12:00:00Z",  # This will be excluded
        "members": [
            {"domain": "AAA", "role": "coordinator"},
            {"domain": "CQH", "role": "participant"}
        ],
        "orchestration_rules": {
            "consensus_protocol": "proof-of-authority",
            "quorum_threshold": 0.67,
            "timeout_seconds": 300
        },
        "last_modified": "2025-01-27T12:30:00Z"  # This will be excluded
    }
    
    print("Sample Manifest:")
    print(json.dumps(sample_manifest, indent=2))
    print()
    
    canonical_hash = compute_canonical_hash(sample_manifest)
    print(f"Canonical Hash: {canonical_hash}")
    print()
    
    metadata = get_hash_metadata(sample_manifest)
    print("Hash Metadata:")
    print(json.dumps(metadata, indent=2))
    print()
    
    # Verify the hash
    is_valid = verify_canonical_hash(sample_manifest, canonical_hash)
    print(f"Hash Verification: {'✓ PASS' if is_valid else '✗ FAIL'}")