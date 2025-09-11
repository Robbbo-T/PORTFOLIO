#!/usr/bin/env python3
"""
JSON Schema Validation for TFA Manifests

Provides comprehensive schema validation for TFA V2 manifests across all LLC levels.
Supports Federation Entanglement (FE), Quantum States (QS), and other TFA artifacts.

Schema validation includes:
- Structure validation (required fields, types)
- Cross-reference validation (domain references, LLC consistency)
- Business rule validation (quorum thresholds, member weights)
- Content validation (naming conventions, value ranges)
"""

import json
import yaml
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import jsonschema
from jsonschema import validate, ValidationError
from datetime import datetime


# Base schema directory (relative to this file)
SCHEMA_DIR = Path(__file__).parent / "schemas"


def load_schema(schema_name: str) -> Dict[str, Any]:
    """
    Load JSON schema from schemas directory.
    
    Args:
        schema_name: Name of schema file (with or without .json extension)
        
    Returns:
        Loaded schema as dictionary
    """
    if not schema_name.endswith('.json'):
        schema_name += '.json'
    
    schema_path = SCHEMA_DIR / schema_name
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema not found: {schema_path}")
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_llc_schema(llc_path: str) -> Dict[str, Any]:
    """
    Get appropriate schema based on LLC path.
    
    Args:
        llc_path: TFA LLC path like "TFA/ELEMENTS/FE" or "TFA/STATES/QS"
        
    Returns:
        Schema dictionary for the LLC type
    """
    path_parts = llc_path.strip('/').split('/')
    
    if len(path_parts) < 3:
        raise ValueError(f"Invalid LLC path format: {llc_path}")
    
    if path_parts[0] != 'TFA':
        raise ValueError(f"LLC path must start with TFA: {llc_path}")
    
    llc_group = path_parts[1]  # ELEMENTS, STATES, etc.
    llc_type = path_parts[2]   # FE, QS, etc.
    
    # Map LLC types to schema files
    schema_mapping = {
        'FE': 'federation_entanglement',
        'UE': 'unit_element', 
        'QS': 'quantum_state',
        'CB': 'classical_bit',
        'QB': 'qubit',
        'FWD': 'wave_dynamics',
        'SE': 'station_envelope',
        'SI': 'system_integration',
        'DI': 'domain_interface',
        'CV': 'component_vendor',
        'CE': 'component_equipment',
        'CC': 'configuration_cell',
        'CI': 'configuration_item',
        'CP': 'component_part'
    }
    
    if llc_type not in schema_mapping:
        raise ValueError(f"Unknown LLC type: {llc_type}")
    
    schema_name = schema_mapping[llc_type]
    return load_schema(schema_name)


def validate_manifest(manifest: Dict[str, Any], llc_path: str) -> Dict[str, Any]:
    """
    Validate TFA manifest against appropriate schema.
    
    Args:
        manifest: Manifest to validate
        llc_path: LLC path to determine schema
        
    Returns:
        Validation result dictionary with:
        - valid: Boolean indicating if validation passed
        - errors: List of validation errors
        - warnings: List of warnings (non-fatal issues)
        - metadata: Additional validation metadata
        - timestamp: Validation timestamp
    """
    validation_result = {
        'valid': False,
        'errors': [],
        'warnings': [],
        'metadata': {},
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    
    try:
        # Load appropriate schema
        schema = get_llc_schema(llc_path)
        
        # Perform JSON schema validation
        validate(manifest, schema)
        
        # Perform additional business rule validation
        business_validation = validate_business_rules(manifest, llc_path)
        
        # Combine results
        validation_result['valid'] = business_validation['valid']
        validation_result['errors'].extend(business_validation['errors'])
        validation_result['warnings'].extend(business_validation['warnings'])
        validation_result['metadata'] = {
            'llc_path': llc_path,
            'schema_version': schema.get('version', 'unknown'),
            'manifest_type': manifest.get('type', 'unknown')
        }
        
    except ValidationError as e:
        validation_result['errors'].append({
            'type': 'schema_validation',
            'message': str(e.message),
            'path': list(e.absolute_path),
            'invalid_value': e.instance
        })
    except Exception as e:
        validation_result['errors'].append({
            'type': 'validation_error',
            'message': str(e)
        })
    
    return validation_result


def validate_business_rules(manifest: Dict[str, Any], llc_path: str) -> Dict[str, Any]:
    """
    Validate business rules specific to TFA manifests.
    
    Args:
        manifest: Manifest to validate
        llc_path: LLC path context
        
    Returns:
        Business validation result
    """
    result = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    manifest_type = manifest.get('type', '')
    
    # Federation Entanglement specific rules
    if manifest_type == 'FE':
        result = validate_fe_business_rules(manifest, result)
    
    # Quantum State specific rules
    elif manifest_type == 'QS':
        result = validate_qs_business_rules(manifest, result)
    
    # General TFA rules
    result = validate_general_tfa_rules(manifest, llc_path, result)
    
    # Set overall validity
    result['valid'] = len(result['errors']) == 0
    
    return result


def validate_fe_business_rules(manifest: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
    """Validate Federation Entanglement specific business rules."""
    
    members = manifest.get('members', [])
    rules = manifest.get('orchestration_rules', {})
    
    # Validate member requirements
    if len(members) < 2:
        result['errors'].append({
            'type': 'business_rule',
            'rule': 'fe_minimum_members',
            'message': 'Federation Entanglement must have at least 2 members'
        })
    
    # Validate quorum threshold
    quorum = rules.get('quorum_threshold')
    if quorum is not None:
        if not (0.5 <= quorum <= 1.0):
            result['errors'].append({
                'type': 'business_rule',
                'rule': 'fe_quorum_range',
                'message': f'Quorum threshold must be between 0.5 and 1.0, got {quorum}'
            })
    
    # Validate member roles
    coordinator_count = sum(1 for m in members if m.get('role') == 'coordinator')
    if coordinator_count == 0:
        result['warnings'].append({
            'type': 'business_rule',
            'rule': 'fe_coordinator_recommended',
            'message': 'Federation should have at least one coordinator'
        })
    elif coordinator_count > 1:
        result['warnings'].append({
            'type': 'business_rule', 
            'rule': 'fe_multiple_coordinators',
            'message': 'Multiple coordinators detected, ensure clear authority delegation'
        })
    
    # Validate timeout values
    timeout = rules.get('timeout_seconds')
    if timeout is not None:
        if timeout < 30:
            result['warnings'].append({
                'type': 'business_rule',
                'rule': 'fe_timeout_minimum',
                'message': f'Timeout of {timeout}s may be too short for distributed operations'
            })
        elif timeout > 3600:
            result['warnings'].append({
                'type': 'business_rule',
                'rule': 'fe_timeout_maximum', 
                'message': f'Timeout of {timeout}s may be too long for responsive operations'
            })
    
    return result


def validate_qs_business_rules(manifest: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
    """Validate Quantum State specific business rules."""
    
    state_data = manifest.get('state_data', {})
    representation = state_data.get('representation_type')
    
    # Validate quantum state representation
    valid_representations = ['state_vector', 'density_matrix', 'bloch_sphere', 'process_matrix']
    if representation not in valid_representations:
        result['errors'].append({
            'type': 'business_rule',
            'rule': 'qs_valid_representation',
            'message': f'Invalid representation type: {representation}. Must be one of {valid_representations}'
        })
    
    # Validate state vector dimensions
    if representation == 'state_vector':
        state_vector = state_data.get('state_vector', [])
        if len(state_vector) == 0:
            result['errors'].append({
                'type': 'business_rule',
                'rule': 'qs_state_vector_required',
                'message': 'State vector is required for state_vector representation'
            })
        elif len(state_vector) & (len(state_vector) - 1) != 0:
            result['warnings'].append({
                'type': 'business_rule',
                'rule': 'qs_state_vector_dimension',
                'message': f'State vector dimension {len(state_vector)} is not a power of 2'
            })
    
    # Validate coherence metrics
    coherence = manifest.get('coherence_metrics', {})
    if coherence:
        t1_time = coherence.get('t1_relaxation_time')
        t2_time = coherence.get('t2_coherence_time')
        
        if t1_time is not None and t2_time is not None:
            if t2_time > 2 * t1_time:
                result['warnings'].append({
                    'type': 'business_rule',
                    'rule': 'qs_coherence_times',
                    'message': f'T2 time ({t2_time}) > 2*T1 time ({t1_time}) may indicate measurement error'
                })
    
    return result


def validate_general_tfa_rules(manifest: Dict[str, Any], llc_path: str, result: Dict[str, Any]) -> Dict[str, Any]:
    """Validate general TFA rules applicable to all manifests."""
    
    # Validate version format
    version = manifest.get('version')
    if version and not is_valid_semantic_version(version):
        result['warnings'].append({
            'type': 'business_rule',
            'rule': 'tfa_version_format',
            'message': f'Version "{version}" should follow semantic versioning (e.g., 1.2.3)'
        })
    
    # Validate name conventions
    name = manifest.get('name', '')
    if len(name) < 3:
        result['warnings'].append({
            'type': 'business_rule',
            'rule': 'tfa_name_length',
            'message': 'Manifest name should be at least 3 characters'
        })
    
    # Validate required metadata
    required_metadata = ['type', 'name', 'version']
    for field in required_metadata:
        if field not in manifest:
            result['errors'].append({
                'type': 'business_rule',
                'rule': 'tfa_required_metadata',
                'message': f'Required field missing: {field}'
            })
    
    return result


def is_valid_semantic_version(version: str) -> bool:
    """Check if version follows semantic versioning."""
    import re
    pattern = r'^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$'
    return bool(re.match(pattern, version))


def validate_manifest_file(file_path: str, llc_path: str) -> Dict[str, Any]:
    """
    Validate manifest file from disk.
    
    Args:
        file_path: Path to manifest file (JSON or YAML)
        llc_path: LLC path context
        
    Returns:
        Validation result
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        return {
            'valid': False,
            'errors': [{'type': 'file_error', 'message': f'File not found: {file_path}'}],
            'warnings': [],
            'metadata': {},
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.suffix.lower() in ['.yaml', '.yml']:
                manifest = yaml.safe_load(f)
            else:
                manifest = json.load(f)
        
        return validate_manifest(manifest, llc_path)
        
    except Exception as e:
        return {
            'valid': False,
            'errors': [{'type': 'file_error', 'message': f'Error reading file: {str(e)}'}],
            'warnings': [],
            'metadata': {},
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }


if __name__ == "__main__":
    # Example usage
    sample_fe_manifest = {
        "type": "FE",
        "name": "Test Federation Entanglement", 
        "version": "1.0.0",
        "description": "Test federation for validation",
        "members": [
            {"domain": "AAA", "role": "coordinator", "weight": 2},
            {"domain": "CQH", "role": "participant", "weight": 1}
        ],
        "orchestration_rules": {
            "consensus_protocol": "proof-of-authority",
            "quorum_threshold": 0.67,
            "timeout_seconds": 300
        }
    }
    
    # Validate the sample manifest
    result = validate_manifest(sample_fe_manifest, "TFA/ELEMENTS/FE")
    
    print("Validation Result:")
    print(json.dumps(result, indent=2))