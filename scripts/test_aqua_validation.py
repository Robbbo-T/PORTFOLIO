#!/usr/bin/env python3
"""
Test script for AQUA API validation.

This script demonstrates how to validate manifests via the AQUA webhook service
as specified in the problem statement.
"""

import json
import sys
import os
from pathlib import Path

# Add AQUA service to path
sys.path.append(str(Path(__file__).parent.parent / "services" / "aqua-webhook"))

try:
    from canonicalize import compute_canonical_hash
    from schemas.manifest_schema import validate_manifest
except ImportError as e:
    print(f"❌ Failed to import AQUA modules: {e}")
    print("This script requires the AQUA webhook service modules to be available.")
    sys.exit(1)

def test_fe_manifest_validation():
    """Test FE manifest validation as shown in problem statement."""
    print("🧪 Testing FE manifest validation...")
    
    # Sample FE manifest from problem statement
    sample_manifest = {
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
    }
    
    # Test validation
    try:
        result = validate_manifest(sample_manifest, "TFA/ELEMENTS/FE")
        
        expected_response = {
            "valid": True,
            "canonical_hash": compute_canonical_hash(sample_manifest),
            "errors": [],
            "metadata": {
                "domain": "AAA-AERODYNAMICS-AND-AIRFRAMES-ARCHITECTURES",
                "llc_path": "TFA/ELEMENTS/FE", 
                "manifest_type": "FE",
                "validation_timestamp": "2025-09-20T05:17:43Z"  # Will be different
            }
        }
        
        print(f"✅ FE manifest validation result:")
        print(f"   Valid: {result.get('valid', False)}")
        print(f"   Canonical Hash: {result.get('canonical_hash', 'N/A')}")
        print(f"   Errors: {len(result.get('errors', []))}")
        
        if result.get('valid'):
            print("✅ FE manifest validation passed")
            return True
        else:
            print("❌ FE manifest validation failed")
            for error in result.get('errors', []):
                print(f"   Error: {error}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during FE validation: {e}")
        return False

def simulate_curl_request():
    """Simulate the curl request from the problem statement."""
    print("\n📡 Simulating AQUA API curl request...")
    
    request_payload = {
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
    
    print("📤 Request payload:")
    print(json.dumps(request_payload, indent=2))
    
    # Simulate validation
    try:
        manifest = request_payload["manifest"]
        llc_path = request_payload["llc_path"]
        
        result = validate_manifest(manifest, llc_path)
        canonical_hash = compute_canonical_hash(manifest)
        
        response = {
            "valid": result.get('valid', False),
            "canonical_hash": canonical_hash,
            "errors": result.get('errors', []),
            "metadata": {
                "domain": request_payload["domain"],
                "llc_path": llc_path,
                "manifest_type": manifest["type"],
                "validation_timestamp": "2025-09-20T05:17:43Z"
            }
        }
        
        print("\n📥 Expected response:")
        print(json.dumps(response, indent=2))
        
        return response.get("valid", False)
        
    except Exception as e:
        print(f"❌ Error simulating curl request: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 AQUA API Integration Test")
    print("=" * 50)
    
    success = True
    
    # Test FE manifest validation
    if not test_fe_manifest_validation():
        success = False
    
    # Simulate curl request
    if not simulate_curl_request():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All AQUA validation tests passed!")
        return 0
    else:
        print("❌ Some AQUA validation tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())