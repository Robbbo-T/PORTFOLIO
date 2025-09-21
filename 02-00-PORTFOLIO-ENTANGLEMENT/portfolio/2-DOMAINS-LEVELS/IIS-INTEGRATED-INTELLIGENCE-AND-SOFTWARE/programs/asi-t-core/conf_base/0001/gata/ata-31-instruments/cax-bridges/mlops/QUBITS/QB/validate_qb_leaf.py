#!/usr/bin/env python3
"""
QB Leaf Validator for IIS MLOps Domain
Validates Quantum Bit configurations and ensures TFA compliance.
"""

import json
import os
import sys
import yaml
from pathlib import Path


def validate_qb_leaf(leaf_dir: Path) -> bool:
    """Validate QB leaf directory structure and content."""
    errors = []
    
    # Check required files exist
    required_files = ["meta.yaml", "qb-config.json", "validate_qb_leaf.py"]
    for file_name in required_files:
        file_path = leaf_dir / file_name
        if not file_path.exists():
            errors.append(f"Missing required file: {file_name}")
    
    # Validate qb-config.json
    config_path = leaf_dir / "qb-config.json"
    if config_path.exists():
        try:
            with open(config_path) as f:
                config = json.load(f)
            
            # Check required config fields
            required_fields = ["qb_id", "description", "version", "quantum_backend"]
            for field in required_fields:
                if field not in config:
                    errors.append(f"Missing required field in qb-config.json: {field}")
                    
            # Validate QB ID format
            if "qb_id" in config:
                qb_id = config["qb_id"]
                if not qb_id.startswith("asi-t-core-0001-IIS-QB-"):
                    errors.append(f"QB ID format invalid: {qb_id}")
                    
            # Validate quantum backend configuration
            if "quantum_backend" in config:
                backend = config["quantum_backend"]
                required_backend_fields = ["primary", "fallback", "providers"]
                for field in required_backend_fields:
                    if field not in backend:
                        errors.append(f"Missing {field} in quantum_backend")
                        
            # Validate fallback policy
            if "fallback_policy" in config:
                fallback = config["fallback_policy"]
                if not fallback.get("cb_fallback"):
                    errors.append("CB fallback must be enabled for compliance")
                if "deterministic_seed" not in fallback:
                    errors.append("Deterministic seed required for fallback")
                    
            # Validate security requirements
            if "security" in config:
                security = config["security"]
                if not security.get("no_vendor_secrets"):
                    errors.append("Vendor secrets not allowed in repository")
                if not security.get("adapter_only"):
                    errors.append("Only adapter patterns allowed for vendor integration")
                    
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON in qb-config.json: {e}")
    
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
            if meta.get("layer") != "QB":
                errors.append(f"Invalid layer in meta.yaml, expected 'QB': {meta.get('layer')}")
            if meta.get("group") != "QUBITS":
                errors.append(f"Invalid group in meta.yaml, expected 'QUBITS': {meta.get('group')}")
                
        except yaml.YAMLError as e:
            errors.append(f"Invalid YAML in meta.yaml: {e}")
    
    if errors:
        for error in errors:
            print(f"::error file={leaf_dir}::{error} (violates 13.4 Required Leaf Files)")
        return False
    else:
        print(f"✓ QB leaf validation passed: {leaf_dir}")
        return True


if __name__ == "__main__":
    leaf_dir = Path(__file__).parent
    success = validate_qb_leaf(leaf_dir)
    sys.exit(0 if success else 1)