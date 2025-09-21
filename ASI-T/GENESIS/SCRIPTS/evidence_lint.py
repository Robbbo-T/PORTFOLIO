#!/usr/bin/env python3
"""
Genesis Evidence Linter

This script validates QS (Quantum State) blob schema and evidence manifest files
to ensure they conform to the required structure for UTCS anchoring.

Based on ASI-T Genesis specification.
"""

import os
import sys
import json
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from jsonschema import Draft202012Validator, ValidationError

# Default artifact manifest schema
ARTIFACT_MANIFEST_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "artifact-manifest.schema.json",
    "title": "ASI-T Genesis Artifact Manifest",
    "description": "Schema for QS evidence blobs and UTCS anchoring",
    "type": "object",
    "required": [
        "artifact_id",
        "timestamp", 
        "validation_version",
        "status",
        "evidence_hash",
        "provenance"
    ],
    "properties": {
        "artifact_id": {
            "type": "string",
            "pattern": "^[A-Z]{2}-[A-Z]{2}-[A-Z0-9]+-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{3}-(OV|IV|PV|ER|EV|HV|IN|ML|TE|DR|DB|SW|FW)(-[A-Z])?$",
            "description": "UTCS-MI identifier"
        },
        "timestamp": {
            "type": "string",
            "format": "date-time",
            "description": "ISO 8601 timestamp"
        },
        "validation_version": {
            "type": "string",
            "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$",
            "description": "Semantic version of validation schema"
        },
        "status": {
            "type": "string",
            "enum": ["PASS", "FAIL", "DECLARED", "NOT_APPLICABLE"],
            "description": "Validation status"
        },
        "evidence_hash": {
            "type": "string",
            "pattern": "^sha256:[a-fA-F0-9]{64}$",
            "description": "SHA-256 hash of evidence data"
        },
        "provenance": {
            "type": "object",
            "required": [
                "policy_hash",
                "model_sha", 
                "data_manifest_hash",
                "operator_id",
                "canonical_hash"
            ],
            "properties": {
                "policy_hash": {
                    "type": "string",
                    "pattern": "^sha256:[a-fA-F0-9]{64}$"
                },
                "model_sha": {
                    "type": "string", 
                    "pattern": "^sha256:[a-fA-F0-9]{64}$"
                },
                "data_manifest_hash": {
                    "type": "string",
                    "pattern": "^sha256:[a-fA-F0-9]{64}$"
                },
                "operator_id": {
                    "type": "string",
                    "pattern": "^UTCS:OP:[a-zA-Z0-9-]+$"
                },
                "canonical_hash": {
                    "type": "string", 
                    "pattern": "^sha256:[a-fA-F0-9]{64}$"
                }
            },
            "additionalProperties": False
        },
        "errors": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of validation errors"
        },
        "warnings": {
            "type": "array", 
            "items": {"type": "string"},
            "description": "List of validation warnings"
        },
        "metadata": {
            "type": "object",
            "description": "Additional metadata for the artifact"
        }
    },
    "additionalProperties": False
}

def load_schema(schema_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load the artifact manifest schema."""
    if schema_path and schema_path.exists():
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Could not load schema from {schema_path}: {e}")
            print("📋 Using default schema")
    
    return ARTIFACT_MANIFEST_SCHEMA

def validate_qs_blob(blob_path: Path, schema: Dict[str, Any]) -> List[str]:
    """Validate a single QS blob against the schema."""
    errors = []
    
    try:
        # Load the blob
        with open(blob_path, 'r', encoding='utf-8') as f:
            if blob_path.suffix == '.json':
                data = json.load(f)
            elif blob_path.suffix in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            else:
                errors.append(f"[E5001] Unsupported Format: {blob_path} must be .json, .yaml, or .yml")
                return errors
        
        # Validate against schema
        validator = Draft202012Validator(schema)
        validation_errors = list(validator.iter_errors(data))
        
        for error in validation_errors:
            path = '.'.join(str(p) for p in error.absolute_path) if error.absolute_path else 'root'
            errors.append(f"[E5002] Schema Violation in {blob_path} at {path}: {error.message}")
        
        # Additional business logic validations
        if isinstance(data, dict):
            # Check timestamp format
            if 'timestamp' in data:
                timestamp = data['timestamp']
                if not re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', timestamp):
                    errors.append(f"[E5003] Timestamp Format: Invalid timestamp format in {blob_path}")
            
            # Validate hash formats
            hash_fields = ['evidence_hash']
            if 'provenance' in data and isinstance(data['provenance'], dict):
                hash_fields.extend(['policy_hash', 'model_sha', 'data_manifest_hash', 'canonical_hash'])
                
                for field in hash_fields:
                    if field in data['provenance'] or field in data:
                        hash_value = data.get(field) or data['provenance'].get(field, '')
                        if not re.match(r'^sha256:[a-fA-F0-9]{64}$', hash_value):
                            errors.append(f"[E5004] Hash Format: Invalid {field} format in {blob_path}")
        
    except json.JSONDecodeError as e:
        errors.append(f"[E5005] JSON Parse Error: Could not parse {blob_path}: {e}")
    except yaml.YAMLError as e:
        errors.append(f"[E5006] YAML Parse Error: Could not parse {blob_path}: {e}")
    except Exception as e:
        errors.append(f"[E5007] General Error: Error processing {blob_path}: {e}")
    
    return errors

def find_evidence_files(evidence_dir: Path) -> List[Path]:
    """Find all evidence files in the evidence directory."""
    if not evidence_dir.exists():
        return []
    
    patterns = ['*.qs.json', '*.qs.yaml', '*.qs.yml', '*.evidence.json', '*.evidence.yaml', '*.evidence.yml']
    files = []
    
    for pattern in patterns:
        files.extend(evidence_dir.glob(pattern))
    
    return sorted(files)

def check_utcs_anchor_files(evidence_dir: Path) -> List[str]:
    """Check for UTCS anchor files and their validity."""
    errors = []
    
    anchor_files = list(evidence_dir.glob('*.anchor.*')) + list(evidence_dir.glob('*utcs*'))
    
    if not anchor_files:
        errors.append("[E6001] UTCS Anchor Missing: No UTCS anchor files found in evidence directory")
    
    for anchor_file in anchor_files:
        try:
            with open(anchor_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
            # Basic validation - should contain UTCS reference
            if not re.search(r'UTCS:', content, re.IGNORECASE):
                errors.append(f"[E6002] UTCS Anchor Invalid: No UTCS reference found in {anchor_file}")
                
        except Exception as e:
            errors.append(f"[E6003] UTCS Anchor Error: Could not read {anchor_file}: {e}")
    
    return errors

def main():
    """Main evidence linting function."""
    print("🔍 Genesis Evidence Linter")
    print("=" * 35)
    
    errors = []
    repo_root = Path.cwd()
    
    # Load schema
    schema_path = repo_root / 'ASI-T' / 'GENESIS' / 'SCHEMAS' / 'artifact-manifest.schema.json'
    schema = load_schema(schema_path if schema_path.exists() else None)
    print(f"📋 Using schema: {'custom' if schema_path.exists() else 'default'}")
    
    # Find evidence directory
    evidence_dir = repo_root / 'ASI-T' / 'GENESIS' / 'EVIDENCE'
    
    if not evidence_dir.exists():
        errors.append("[E4001] Evidence Directory Missing: ASI-T/GENESIS/EVIDENCE directory not found")
        print(f"\n❌ Found {len(errors)} evidence validation errors:")
        for error in errors:
            print(f"  {error}")
        sys.exit(1)
    
    # Find evidence files
    evidence_files = find_evidence_files(evidence_dir)
    print(f"🗂️  Found {len(evidence_files)} evidence files")
    
    if not evidence_files:
        errors.append("[E4002] Evidence Files Missing: No QS evidence files found")
    else:
        # Validate each evidence file
        for blob_path in evidence_files:
            print(f"   Validating {blob_path.name}")
            blob_errors = validate_qs_blob(blob_path, schema)
            errors.extend(blob_errors)
    
    # Check UTCS anchor files
    anchor_errors = check_utcs_anchor_files(evidence_dir)
    errors.extend(anchor_errors)
    
    print(f"📊 Validation Summary:")
    print(f"   Evidence files: {len(evidence_files)}")
    print(f"   Errors found: {len(errors)}")
    
    if errors:
        print(f"\n❌ Found {len(errors)} evidence validation errors:")
        for error in errors:
            print(f"  {error}")
        
        print("\n💡 Required evidence structure:")
        print("   ASI-T/GENESIS/EVIDENCE/")
        print("   ├── sample.qs.json    # QS blob with validation results")
        print("   ├── utcs.anchor       # UTCS anchor reference") 
        print("   └── manifest.evidence.yaml  # Additional evidence")
        
        sys.exit(1)
    else:
        print("✅ All evidence files validated successfully")
        sys.exit(0)

if __name__ == '__main__':
    import re
    main()