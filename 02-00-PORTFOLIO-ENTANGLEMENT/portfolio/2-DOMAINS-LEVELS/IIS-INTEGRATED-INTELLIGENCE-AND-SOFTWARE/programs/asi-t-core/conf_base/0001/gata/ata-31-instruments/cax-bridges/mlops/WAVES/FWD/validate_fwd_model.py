#!/usr/bin/env python3
"""
FWD Model Validator for IIS MLOps Domain
Validates Forward Wave Dynamics models and ensures TFA compliance.
"""

import os
import sys
import yaml
from pathlib import Path


def validate_fwd_model(leaf_dir: Path) -> bool:
    """Validate FWD model directory structure and content."""
    errors = []
    
    # Check required files exist
    required_files = ["meta.yaml", "fwd-model.yaml", "validate_fwd_model.py"]
    for file_name in required_files:
        file_path = leaf_dir / file_name
        if not file_path.exists():
            errors.append(f"Missing required file: {file_name}")
    
    # Validate fwd-model.yaml
    model_path = leaf_dir / "fwd-model.yaml"
    if model_path.exists():
        try:
            with open(model_path) as f:
                model = yaml.safe_load(f)
            
            # Check required model fields
            required_fields = ["fwd_id", "version", "description", "wave_configuration"]
            for field in required_fields:
                if field not in model:
                    errors.append(f"Missing required field in fwd-model.yaml: {field}")
                    
            # Validate FWD ID format
            if "fwd_id" in model:
                fwd_id = model["fwd_id"]
                if not fwd_id.startswith("asi-t-core-0001-IIS-FWD-"):
                    errors.append(f"FWD ID format invalid: {fwd_id}")
                    
            # Validate wave configuration
            if "wave_configuration" in model:
                wave_config = model["wave_configuration"]
                required_wave_fields = ["propagation_method", "boundary_conditions", "grid_resolution"]
                for field in required_wave_fields:
                    if field not in wave_config:
                        errors.append(f"Missing {field} in wave_configuration")
                        
            # Validate performance requirements
            if "performance_requirements" in model:
                perf = model["performance_requirements"]
                required_perf_fields = ["max_propagation_time_ms", "stability_threshold"]
                for field in required_perf_fields:
                    if field not in perf:
                        errors.append(f"Missing {field} in performance_requirements")
                        
            # Validate integration requirements
            if "integration" in model:
                integration = model["integration"]
                if not integration.get("qs_evidence"):
                    errors.append("QS evidence generation must be enabled")
                if not integration.get("deterministic"):
                    errors.append("Deterministic operation required for compliance")
                    
        except yaml.YAMLError as e:
            errors.append(f"Invalid YAML in fwd-model.yaml: {e}")
    
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
            if meta.get("layer") != "FWD":
                errors.append(f"Invalid layer in meta.yaml, expected 'FWD': {meta.get('layer')}")
            if meta.get("group") != "WAVES":
                errors.append(f"Invalid group in meta.yaml, expected 'WAVES': {meta.get('group')}")
                
        except yaml.YAMLError as e:
            errors.append(f"Invalid YAML in meta.yaml: {e}")
    
    if errors:
        for error in errors:
            print(f"::error file={leaf_dir}::{error} (violates 13.4 Required Leaf Files)")
        return False
    else:
        print(f"✓ FWD model validation passed: {leaf_dir}")
        return True


if __name__ == "__main__":
    leaf_dir = Path(__file__).parent
    success = validate_fwd_model(leaf_dir)
    sys.exit(0 if success else 1)