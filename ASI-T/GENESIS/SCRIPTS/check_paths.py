#!/usr/bin/env python3
"""
Genesis Path Grammar & UTCS-MI Header Validator

This script validates that all files in the repository follow the TFA path grammar
and contain the required UTCS-MI headers with proper structure.

Based on ASI-T Genesis specification.
"""

import os
import sys
import re
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional

# TFA path grammar regex patterns
TFA_LAYER_PATTERN = r'^portfolio/2-DOMAINS-LEVELS/[A-Z]{3}-[A-Z0-9-]+/TFA/(SYSTEMS|STATIONS|COMPONENTS|BITS|QUBITS|ELEMENTS|WAVES|STATES)/'
LLC_PATTERN = r'(SI|DI|SE|CV|CE|CC|CI|CP|CB|QB|UE|FE|FWD|QS)/'
UTCS_ID_PATTERN = r'[A-Z]{2}-[A-Z]{2}-[A-Z0-9]+-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{3}-(OV|IV|PV|ER|EV|HV|IN|ML|TE|DR|DB|SW|FW)(-[A-Z])?'

# Required UTCS-MI header fields
REQUIRED_UTCS_FIELDS = [
    'id', 'rev', 'llc', 'title', 'provenance', 'licenses', 'bridge', 'ethics_guard'
]

REQUIRED_PROVENANCE_FIELDS = [
    'policy_hash', 'model_sha', 'data_manifest_hash', 'operator_id', 'canonical_hash'
]

def check_path_grammar(file_path: str) -> List[str]:
    """Check if a file path follows TFA grammar rules."""
    errors = []
    
    # Skip certain directories that are allowed to be non-TFA
    skip_patterns = [
        r'^\.github/',
        r'^\.git/',
        r'^__pycache__/',
        r'\.pyc$',
        r'^node_modules/',
        r'^\.vscode/',
        r'^\.idea/',
        r'^8-RESOURCES/',
        r'^scripts/',
        r'^tools/',
        r'^tests/',
        r'^ASI-T/GENESIS/',
        r'^ASIT-GENESIS-',
        r'^\..*',
        r'Makefile$',
        r'README\.md$',
        r'.*\.json$',
        r'.*\.yaml$',
        r'.*\.yml$',
        r'.*\.toml$',
        r'.*\.txt$',
        r'.*\.py$'
    ]
    
    # Check if path should be skipped
    for pattern in skip_patterns:
        if re.match(pattern, file_path):
            return errors
    
    # Check if it's in portfolio domain structure but not following TFA grammar
    if file_path.startswith('portfolio/2-DOMAINS-LEVELS/'):
        # Must follow TFA grammar inside domain folders
        if '/TFA/' in file_path:
            tfa_match = re.match(TFA_LAYER_PATTERN, file_path)
            if not tfa_match:
                errors.append(f"[E1001] PathGrammarError: TFA path doesn't match layer pattern in: {file_path}")
                return errors
            
            # Check for LLC pattern after layer
            remaining_path = file_path[len(re.match(TFA_LAYER_PATTERN, file_path).group()):]
            if not re.match(LLC_PATTERN, remaining_path):
                errors.append(f"[E1002] PathGrammarError: Missing or invalid LLC code in: {file_path}")
    
    return errors

def extract_yaml_frontmatter(content: str) -> Optional[Dict[str, Any]]:
    """Extract YAML frontmatter from file content."""
    if not content.startswith('---'):
        return None
    
    try:
        # Find the end of frontmatter
        end_match = re.search(r'\n---\s*\n', content)
        if not end_match:
            return None
        
        frontmatter_content = content[3:end_match.start()]
        return yaml.safe_load(frontmatter_content)
    except yaml.YAMLError:
        return None

def check_utcs_headers(file_path: str, content: str) -> List[str]:
    """Check if file has required UTCS-MI headers."""
    errors = []
    
    # Only check markdown files that should have UTCS headers
    if not (file_path.endswith('.md') and '/TFA/' in file_path):
        return errors
    
    frontmatter = extract_yaml_frontmatter(content)
    if not frontmatter:
        errors.append(f"[E2001] UTCS-MI Header Missing: No YAML frontmatter found in: {file_path}")
        return errors
    
    # Check required fields
    for field in REQUIRED_UTCS_FIELDS:
        if field not in frontmatter:
            errors.append(f"[E2002] UTCS-MI Field Missing: '{field}' not found in: {file_path}")
    
    # Check provenance subfields if provenance exists
    if 'provenance' in frontmatter:
        provenance = frontmatter['provenance']
        if isinstance(provenance, dict):
            for field in REQUIRED_PROVENANCE_FIELDS:
                if field not in provenance:
                    errors.append(f"[E2003] UTCS-MI Provenance Field Missing: 'provenance.{field}' not found in: {file_path}")
        else:
            errors.append(f"[E2004] UTCS-MI Provenance Invalid: 'provenance' must be a dictionary in: {file_path}")
    
    # Validate UTCS-MI ID format if present
    if 'id' in frontmatter:
        utcs_id = frontmatter['id']
        if not re.match(f'^{UTCS_ID_PATTERN}$', utcs_id):
            errors.append(f"[E2005] UTCS-MI ID Invalid: '{utcs_id}' doesn't match pattern in: {file_path}")
    
    # Check LLC field matches path
    if 'llc' in frontmatter and '/TFA/' in file_path:
        llc_from_header = frontmatter['llc']
        # Extract LLC from path
        llc_match = re.search(rf'/({"|".join(["SI", "DI", "SE", "CV", "CE", "CC", "CI", "CP", "CB", "QB", "UE", "FE", "FWD", "QS"])})/', file_path)
        if llc_match:
            llc_from_path = llc_match.group(1)
            if llc_from_header != llc_from_path:
                errors.append(f"[E2006] UTCS-MI LLC Mismatch: header has '{llc_from_header}' but path has '{llc_from_path}' in: {file_path}")
    
    return errors

def main():
    """Main validation function."""
    repo_root = Path.cwd()
    errors = []
    
    print("🔍 Genesis Path Grammar & UTCS-MI Header Validation")
    print("=" * 60)
    
    # Get all tracked files
    try:
        import subprocess
        result = subprocess.run(['git', 'ls-files'], capture_output=True, text=True, check=True)
        tracked_files = result.stdout.strip().split('\n')
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback to walking directory
        tracked_files = []
        for root, dirs, files in os.walk(repo_root):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                if not file.startswith('.'):
                    rel_path = os.path.relpath(os.path.join(root, file), repo_root)
                    tracked_files.append(rel_path)
    
    files_checked = 0
    for file_path in tracked_files:
        if not file_path or file_path == '.':
            continue
            
        files_checked += 1
        
        # Check path grammar
        path_errors = check_path_grammar(file_path)
        errors.extend(path_errors)
        
        # Check UTCS headers for relevant files
        full_path = repo_root / file_path
        if full_path.exists() and full_path.is_file():
            try:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                header_errors = check_utcs_headers(file_path, content)
                errors.extend(header_errors)
            except Exception as e:
                errors.append(f"[E3001] File Read Error: Could not read {file_path}: {e}")
    
    print(f"📊 Checked {files_checked} files")
    
    if errors:
        print(f"\n❌ Found {len(errors)} validation errors:")
        for error in errors:
            print(f"  {error}")
        print("\n💡 Action required: Fix path grammar violations or add proper UTCS-MI headers")
        sys.exit(1)
    else:
        print("✅ All files pass TFA path grammar and UTCS-MI header validation")
        sys.exit(0)

if __name__ == '__main__':
    main()