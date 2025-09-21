#!/usr/bin/env python3
"""
CB Leaf Validator for Industrial Infrastructure Facilities Domain
Validates Classical Bit configurations and ensures TFA compliance.
"""

import json
import os
import sys
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
                if not cb_id.startswith("ampel360bwbq-0001-IIF-CB-"):
                    errors.append(f"CB ID format invalid: {cb_id}")
                    
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON in cb-config.json: {e}")
    
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