#!/usr/bin/env python3
"""
QS Proof Validator for IIS MLOps Domain
Validates Quantum State proofs and ensures TFA compliance.
"""

import json
import os
import sys
import yaml
from pathlib import Path


def validate_qs_proof(leaf_dir: Path) -> bool:
    """Validate QS proof directory structure and content."""
    errors = []
    
    # Check required files exist
    required_files = ["meta.yaml", "qs-proof.json", "validate_qs_proof.py"]
    for file_name in required_files:
        file_path = leaf_dir / file_name
        if not file_path.exists():
            errors.append(f"Missing required file: {file_name}")
    
    # Validate qs-proof.json
    proof_path = leaf_dir / "qs-proof.json"
    if proof_path.exists():
        try:
            with open(proof_path) as f:
                proof = json.load(f)
            
            # Check required proof fields
            required_fields = ["qs_id", "version", "proof_type", "utcs_fields", "provenance"]
            for field in required_fields:
                if field not in proof:
                    errors.append(f"Missing required field in qs-proof.json: {field}")
                    
            # Validate QS ID format
            if "qs_id" in proof:
                qs_id = proof["qs_id"]
                if not qs_id.startswith("asi-t-core-0001-IIS-QS-"):
                    errors.append(f"QS ID format invalid: {qs_id}")
                    
            # Validate UTCS fields
            if "utcs_fields" in proof:
                utcs = proof["utcs_fields"]
                required_utcs_fields = ["policy_hash", "model_sha", "data_manifest", 
                                      "decision_record", "operator_id"]
                for field in required_utcs_fields:
                    if field not in utcs:
                        errors.append(f"Missing {field} in utcs_fields")
                        
            # Validate provenance chain
            if "provenance" in proof:
                prov = proof["provenance"]
                required_prov_fields = ["cb_hash", "qb_hash", "ue_hash", "fwd_hash", "bridge_path"]
                for field in required_prov_fields:
                    if field not in prov:
                        errors.append(f"Missing {field} in provenance")
                        
                # Validate bridge path
                expected_bridge = "CB→QB→UE→FE→FWD→QS"
                if prov.get("bridge_path") != expected_bridge:
                    errors.append(f"Invalid bridge_path, expected '{expected_bridge}'")
                    
            # Validate evidence chain
            if "evidence_chain" in proof:
                evidence = proof["evidence_chain"]
                required_evidence = ["mod_base_metrics", "validation_results"]
                for field in required_evidence:
                    if field not in evidence:
                        errors.append(f"Missing {field} in evidence_chain")
                        
            # Validate compliance fields
            if "compliance" in proof:
                compliance = proof["compliance"]
                if not compliance.get("schema_valid"):
                    errors.append("Schema validation must pass for QS proof")
                    
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON in qs-proof.json: {e}")
    
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
            if meta.get("layer") != "QS":
                errors.append(f"Invalid layer in meta.yaml, expected 'QS': {meta.get('layer')}")
            if meta.get("group") != "STATES":
                errors.append(f"Invalid group in meta.yaml, expected 'STATES': {meta.get('group')}")
                
        except yaml.YAMLError as e:
            errors.append(f"Invalid YAML in meta.yaml: {e}")
    
    if errors:
        for error in errors:
            print(f"::error file={leaf_dir}::{error} (violates 13.4 Required Leaf Files)")
        return False
    else:
        print(f"✓ QS proof validation passed: {leaf_dir}")
        return True


if __name__ == "__main__":
    leaf_dir = Path(__file__).parent
    success = validate_qs_proof(leaf_dir)
    sys.exit(0 if success else 1)