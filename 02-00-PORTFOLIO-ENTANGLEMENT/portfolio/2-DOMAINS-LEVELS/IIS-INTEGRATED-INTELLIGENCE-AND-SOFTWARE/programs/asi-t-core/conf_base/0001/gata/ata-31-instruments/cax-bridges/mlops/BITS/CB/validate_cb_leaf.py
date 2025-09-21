#!/usr/bin/env python3
"""
CB Leaf Validator for IIS MLOps Domain
Validates Classical Bit configurations and ensures TFA compliance.
"""

import json
import os
import sys
import yaml
from pathlib import Path


def validate_cb_leaf(leaf_dir: Path) -> bool:
    """Validate CB leaf directory structure and content."""
    errors = []
    
    # Check required files exist
    required_files = ["meta.yaml", "cb-config.json", "validate_cb_leaf.py"]
    for file_name in required_files:
        file_path = leaf_dir / file_name
        if not file_path.exists():
            errors.append(f"Missing required file: {file_name}")
    
    # Validate cb-config.json
    config_path = leaf_dir / "cb-config.json"
    if config_path.exists():
        try:
            with open(config_path) as f:
                config = json.load(f)
            
            # Check required config fields
            required_fields = ["cb_id", "description", "version", "algorithms"]
            for field in required_fields:
                if field not in config:
                    errors.append(f"Missing required field in cb-config.json: {field}")
                    
            # Validate CB ID format
            if "cb_id" in config:
                cb_id = config["cb_id"]
                # Should match: {program}-{baseline}-{domain}-{layer}-{code}-{mapChapter}
                if not cb_id.startswith("asi-t-core-0001-IIS-CB-"):
                    errors.append(f"CB ID format invalid: {cb_id}")
                    
            # Validate MAL requirements
            if "mal_requirements" in config:
                mal_req = config["mal_requirements"]
                if "wcet_budget_ms" not in mal_req:
                    errors.append("Missing wcet_budget_ms in mal_requirements")
                if "safety_fence" not in mal_req:
                    errors.append("Missing safety_fence in mal_requirements")
                    
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON in cb-config.json: {e}")
    
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
            if meta.get("layer") != "CB":
                errors.append(f"Invalid layer in meta.yaml, expected 'CB': {meta.get('layer')}")
            if meta.get("group") != "BITS":
                errors.append(f"Invalid group in meta.yaml, expected 'BITS': {meta.get('group')}")
                
        except yaml.YAMLError as e:
            errors.append(f"Invalid YAML in meta.yaml: {e}")
    
    if errors:
        for error in errors:
            print(f"::error file={leaf_dir}::{error} (violates 13.4 Required Leaf Files)")
        return False
    else:
        print(f"✓ CB leaf validation passed: {leaf_dir}")
        return True


if __name__ == "__main__":
    leaf_dir = Path(__file__).parent
    success = validate_cb_leaf(leaf_dir)
    sys.exit(0 if success else 1)