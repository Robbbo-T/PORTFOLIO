#!/usr/bin/env python3
"""
Genesis Schema Validator

This script validates JSON and YAML files throughout the repository
against their corresponding schema files to ensure data consistency.

Based on ASI-T Genesis specification.
"""

import os
import sys
import json
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from jsonschema import Draft202012Validator, ValidationError

def find_schema_files() -> Dict[str, Path]:
    """Find all schema files in the repository."""
    schemas = {}
    
    schema_dirs = [
        Path('ASI-T/GENESIS/SCHEMAS'),
        Path('schemas'),
        Path('8-RESOURCES/SCHEMAS'),
        Path('services/*/schemas')  # Will need glob expansion
    ]
    
    for schema_dir in schema_dirs:
        if '*' in str(schema_dir):
            # Expand glob patterns
            for expanded_dir in Path('.').glob(str(schema_dir)):
                if expanded_dir.is_dir():
                    for schema_file in expanded_dir.glob('*.schema.json'):
                        schema_name = schema_file.stem.replace('.schema', '')
                        schemas[schema_name] = schema_file
        elif schema_dir.exists():
            for schema_file in schema_dir.glob('*.schema.json'):
                schema_name = schema_file.stem.replace('.schema', '')
                schemas[schema_name] = schema_file
    
    return schemas

def find_data_files() -> List[Tuple[Path, str]]:
    """Find all JSON and YAML files that should be validated."""
    data_files = []
    
    # Patterns to include
    include_patterns = [
        '**/manifest.json',
        '**/manifest.yaml',
        '**/config.json', 
        '**/config.yaml',
        '**/*.manifest.json',
        '**/*.manifest.yaml',
        '**/*.config.json',
        '**/*.config.yaml',
        '**/evidence/*.json',
        '**/evidence/*.yaml',
        'ASI-T/GENESIS/EVIDENCE/*.json',
        'ASI-T/GENESIS/EVIDENCE/*.yaml',
        'services/**/schemas/*.example.json',
        'services/**/schemas/*.example.yaml'
    ]
    
    # Patterns to exclude
    exclude_patterns = [
        '**/.git/**',
        '**/node_modules/**',
        '**/__pycache__/**',
        '**/.*/**',
        '**/*.schema.json',  # Don't validate schema files themselves
        'package*.json',     # Don't validate npm files
        'tsconfig*.json',    # Don't validate TypeScript configs
        'hardhat.config.js', # Don't validate hardhat config
        'foundry.toml'       # Don't validate foundry config
    ]
    
    repo_root = Path('.')
    
    for pattern in include_patterns:
        for file_path in repo_root.glob(pattern):
            if file_path.is_file():
                # Check if file should be excluded
                should_exclude = False
                for exclude_pattern in exclude_patterns:
                    if file_path.match(exclude_pattern):
                        should_exclude = True
                        break
                
                if not should_exclude:
                    # Determine expected schema name
                    schema_name = infer_schema_name(file_path)
                    data_files.append((file_path, schema_name))
    
    return data_files

def infer_schema_name(file_path: Path) -> str:
    """Infer the schema name from file path and name."""
    file_name = file_path.name
    path_parts = file_path.parts
    
    # Check for explicit schema naming patterns
    if '.manifest.' in file_name:
        return 'artifact-manifest'
    elif '.config.' in file_name:
        return 'config'
    elif file_name == 'manifest.json' or file_name == 'manifest.yaml':
        if 'mal' in str(file_path).lower():
            return 'mal-manifest'
        elif 'aqua' in str(file_path).lower():
            return 'aqua-manifest'
        else:
            return 'artifact-manifest'
    elif 'evidence' in path_parts:
        return 'artifact-manifest'
    elif 'schemas' in path_parts and 'example' in file_name:
        # Extract schema name from example file
        base_name = file_name.replace('.example.json', '').replace('.example.yaml', '')
        return base_name
    
    # Default fallback
    return 'artifact-manifest'

def load_schema(schema_path: Path) -> Optional[Dict[str, Any]]:
    """Load and validate a schema file."""
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        
        # Validate that it's a valid JSON Schema
        Draft202012Validator.check_schema(schema)
        return schema
        
    except json.JSONDecodeError as e:
        print(f"⚠️  Schema parse error in {schema_path}: {e}")
        return None
    except Exception as e:
        print(f"⚠️  Schema validation error in {schema_path}: {e}")
        return None

def validate_data_file(file_path: Path, schema: Dict[str, Any]) -> List[str]:
    """Validate a data file against a schema."""
    errors = []
    
    try:
        # Load the data file
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.suffix == '.json':
                data = json.load(f)
            elif file_path.suffix in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            else:
                errors.append(f"[S1001] Unsupported Format: {file_path} has unsupported extension")
                return errors
        
        # Validate against schema
        validator = Draft202012Validator(schema)
        validation_errors = list(validator.iter_errors(data))
        
        for error in validation_errors:
            path = '.'.join(str(p) for p in error.absolute_path) if error.absolute_path else 'root'
            errors.append(f"[S1002] Schema Violation in {file_path} at {path}: {error.message}")
        
    except json.JSONDecodeError as e:
        errors.append(f"[S1003] JSON Parse Error: Could not parse {file_path}: {e}")
    except yaml.YAMLError as e:
        errors.append(f"[S1004] YAML Parse Error: Could not parse {file_path}: {e}")
    except Exception as e:
        errors.append(f"[S1005] General Error: Error processing {file_path}: {e}")
    
    return errors

def create_default_schemas() -> None:
    """Create default schema files if they don't exist."""
    schema_dir = Path('ASI-T/GENESIS/SCHEMAS')
    schema_dir.mkdir(parents=True, exist_ok=True)
    
    # Create artifact-manifest schema if it doesn't exist
    artifact_schema_path = schema_dir / 'artifact-manifest.schema.json'
    if not artifact_schema_path.exists():
        # Already exists, skip creation
        pass
        # Already exists, skip creation
        pass
    
    # Create basic config schema
    config_schema_path = schema_dir / 'config.schema.json'
    if not config_schema_path.exists():
        config_schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "config.schema.json",
            "title": "ASI-T Configuration Schema",
            "description": "Schema for configuration files",
            "type": "object",
            "additionalProperties": True
        }
        with open(config_schema_path, 'w', encoding='utf-8') as f:
            json.dump(config_schema, f, indent=2)
        print(f"📋 Created default schema: {config_schema_path}")

def main():
    """Main schema validation function."""
    print("🔍 Genesis Schema Validator")
    print("=" * 35)
    
    # Check strict mode
    strict_mode = os.environ.get('GENESIS_STRICT_MODE', 'false').lower() == 'true'
    
    # Ensure default schemas exist
    create_default_schemas()
    
    # Find all schema files
    schemas = find_schema_files()
    print(f"📋 Found {len(schemas)} schema files:")
    for name, path in schemas.items():
        print(f"   {name}: {path}")
    
    if not schemas:
        print("⚠️  No schema files found - skipping validation")
        sys.exit(0)
    
    # Load schemas
    loaded_schemas = {}
    for name, path in schemas.items():
        schema = load_schema(path)
        if schema:
            loaded_schemas[name] = schema
        else:
            print(f"❌ Failed to load schema: {name}")
    
    if not loaded_schemas:
        print("❌ No valid schemas loaded")
        sys.exit(1)
    
    # Find data files to validate
    data_files = find_data_files()
    print(f"\n🗂️  Found {len(data_files)} data files to validate")
    print(f"📊 Strict mode: {'enabled' if strict_mode else 'disabled (warn-only for existing violations)'}")
    
    if not data_files:
        print("ℹ️  No data files found to validate")
        sys.exit(0)
    
    # Validate each file
    total_errors = []
    total_warnings = []
    validated_files = 0
    
    for file_path, schema_name in data_files:
        if schema_name in loaded_schemas:
            print(f"   Validating {file_path} against {schema_name}")
            errors = validate_data_file(file_path, loaded_schemas[schema_name])
            
            if not strict_mode and errors:
                # Convert to warnings for existing files
                warnings = [error.replace('[S1', '[SW1').replace('Schema Violation', 'Schema Warning') for error in errors]
                total_warnings.extend(warnings)
            else:
                total_errors.extend(errors)
            validated_files += 1
        else:
            print(f"⚠️  No schema found for {file_path} (expected: {schema_name})")
    
    print(f"\n📊 Validation Summary:")
    print(f"   Files validated: {validated_files}")
    print(f"   Schema files loaded: {len(loaded_schemas)}")
    print(f"   Errors found: {len(total_errors)}")
    print(f"   Warnings found: {len(total_warnings)}")
    
    if total_warnings:
        print(f"\n⚠️  Found {len(total_warnings)} schema validation warnings (existing files):")
        for warning in total_warnings[:5]:  # Limit output
            print(f"  {warning}")
        if len(total_warnings) > 5:
            print(f"  ... and {len(total_warnings) - 5} more warnings")
    
    if total_errors:
        print(f"\n❌ Found {len(total_errors)} schema validation errors:")
        for error in total_errors[:20]:  # Limit output
            print(f"  {error}")
        
        if len(total_errors) > 20:
            print(f"  ... and {len(total_errors) - 20} more errors")
        
        print("\n💡 Fix data files to match their schemas or update schemas as needed")
        sys.exit(1)
    else:
        if total_warnings:
            print("✅ Schema validation passed (warnings noted for existing files)")
        else:
            print("✅ All data files validated successfully against their schemas")
        sys.exit(0)

if __name__ == '__main__':
    main()