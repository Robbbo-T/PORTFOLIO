#!/usr/bin/env python3
"""
UE Contract Validator for BasIC Component
Validates Unit Element contracts and ensures TFA compliance.
"""

import json
import os
import sys
import yaml
from pathlib import Path
from typing import Dict, Any, List


def validate_ue_contract(leaf_dir: Path) -> bool:
    """Validate UE leaf directory structure and content."""
    errors = []
    
    # Check required files exist
    required_files = ["meta.yaml", "ue-contract.json", "validate_ue_contract.py", "id-profile.yaml"]
    for file_name in required_files:
        file_path = leaf_dir / file_name
        if not file_path.exists():
            errors.append(f"Missing required file: {file_name}")
    
    # Validate ue-contract.json
    contract_path = leaf_dir / "ue-contract.json"
    if contract_path.exists():
        try:
            with open(contract_path) as f:
                contract = json.load(f)
            
            # Check required contract fields
            required_fields = ["contract_id", "element_type", "capabilities", "interfaces"]
            for field in required_fields:
                if field not in contract:
                    errors.append(f"Missing required field in ue-contract.json: {field}")
            
            # Validate contract ID format
            if "contract_id" in contract:
                contract_id = contract["contract_id"]
                if not contract_id.startswith("UE-BasIC-"):
                    errors.append(f"UE contract ID format invalid: {contract_id}")
            
            # Validate element type
            if contract.get("element_type") != "UE":
                errors.append(f"Invalid element_type, expected 'UE': {contract.get('element_type')}")
                
            # Check QS integration requirements
            if "qs_integration" not in contract:
                errors.append("Missing qs_integration configuration")
            elif not contract["qs_integration"].get("evidence_required"):
                errors.append("QS evidence is required for BasIC component")
                    
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON in ue-contract.json: {e}")
    
    # Validate meta.yaml
    meta_path = leaf_dir / "meta.yaml"
    if meta_path.exists():
        try:
            with open(meta_path) as f:
                meta = yaml.safe_load(f)
            
            # Check required meta fields
            required_meta = ["id", "version", "layer", "group"]
            for field in required_meta:
                if field not in meta:
                    errors.append(f"Missing required field in meta.yaml: {field}")
            
            # Validate layer and group
            if meta.get("layer") != "UE":
                errors.append(f"Invalid layer in meta.yaml, expected 'UE': {meta.get('layer')}")
            if meta.get("group") != "ELEMENTS":
                errors.append(f"Invalid group in meta.yaml, expected 'ELEMENTS': {meta.get('group')}")
                
        except yaml.YAMLError as e:
            errors.append(f"Invalid YAML in meta.yaml: {e}")
    
    # Validate id-profile.yaml (BasIC specific)
    profile_path = leaf_dir / "id-profile.yaml"
    if profile_path.exists():
        try:
            with open(profile_path) as f:
                profile = yaml.safe_load(f)
            
            # Check BasIC-specific profile fields
            required_profile = ["identity_provider", "key_management", "attestation_policy"]
            for field in required_profile:
                if field not in profile:
                    errors.append(f"Missing required field in id-profile.yaml: {field}")
                    
        except yaml.YAMLError as e:
            errors.append(f"Invalid YAML in id-profile.yaml: {e}")
    
    if errors:
        for error in errors:
            print(f"::error file={leaf_dir}::{error} (violates 13.4 Required Leaf Files)")
        return False
    else:
        print(f"✓ UE BasIC leaf validation passed: {leaf_dir}")
        return True


if __name__ == "__main__":
    leaf_dir = Path(__file__).parent
    success = validate_ue_contract(leaf_dir)
    sys.exit(0 if success else 1)