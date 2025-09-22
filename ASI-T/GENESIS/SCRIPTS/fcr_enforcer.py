#!/usr/bin/env python3
"""
Genesis FCR (Formal Change Request) Enforcer

This script validates that PR descriptions contain required FCR-1 and FCR-2 links
and that evidence blocks follow the proper structure.

Based on ASI-T Genesis specification.
"""

import os
import sys
import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

def get_pr_description() -> Optional[str]:
    """Get PR description from environment variables or git."""
    # Try GitHub Actions environment first
    pr_body = os.environ.get('GITHUB_PR_BODY', '').strip()
    if pr_body:
        return pr_body
    
    # Try to get from git if available (for local testing)
    try:
        import subprocess
        # Get the latest commit message which might contain FCR info
        result = subprocess.run(['git', 'log', '-1', '--pretty=format:%B'], 
                              capture_output=True, text=True, check=False)
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    return None

def check_fcr_links(pr_description: str) -> List[str]:
    """Check if PR description contains required FCR-1 and FCR-2 links."""
    errors = []
    
    if not pr_description:
        errors.append("[F1001] FCR Missing: No PR description found")
        return errors
    
    # Check for FCR-1 link pattern
    fcr1_pattern = r'FCR-1\s*[:→⟶]\s*<?([^\s<>]+)>?'
    fcr1_match = re.search(fcr1_pattern, pr_description, re.IGNORECASE)
    
    if not fcr1_match:
        errors.append("[F1002] FCR-1 Missing: No FCR-1 link found in PR description")
    else:
        fcr1_url = fcr1_match.group(1)
        if not (fcr1_url.startswith('http') or fcr1_url.startswith('https')):
            errors.append(f"[F1003] FCR-1 Invalid: FCR-1 link must be a valid URL: {fcr1_url}")
    
    # Check for FCR-2 link pattern  
    fcr2_pattern = r'FCR-2\s*[:→⟶]\s*<?([^\s<>]+)>?'
    fcr2_match = re.search(fcr2_pattern, pr_description, re.IGNORECASE)
    
    if not fcr2_match:
        errors.append("[F1004] FCR-2 Missing: No FCR-2 link found in PR description")
    else:
        fcr2_url = fcr2_match.group(1)
        if not (fcr2_url.startswith('http') or fcr2_url.startswith('https')):
            errors.append(f"[F1005] FCR-2 Invalid: FCR-2 link must be a valid URL: {fcr2_url}")
    
    return errors

def check_evidence_provenance(pr_description: str) -> List[str]:
    """Check if PR description contains required evidence and provenance fields."""
    errors = []
    
    if not pr_description:
        return errors
    
    # Required evidence fields
    required_hashes = [
        'policy_hash',
        'model_sha', 
        'data_manifest_hash',
        'canonical_hash'
    ]
    
    for hash_field in required_hashes:
        hash_pattern = rf'{hash_field}\s*:\s*sha256:([a-fA-F0-9]+)'
        if not re.search(hash_pattern, pr_description):
            errors.append(f"[F2001] Evidence Missing: {hash_field} with sha256 hash not found in PR description")
    
    # Check for operator ID
    operator_pattern = r'Operator\s*:\s*UTCS:OP:[a-zA-Z0-9-]+'
    if not re.search(operator_pattern, pr_description):
        errors.append("[F2002] Evidence Missing: Operator ID (UTCS:OP:*) not found in PR description")
    
    return errors

def check_commit_message_format() -> List[str]:
    """Check if recent commits follow FCR format."""
    errors = []
    
    try:
        import subprocess
        # Get the latest commit message
        result = subprocess.run(['git', 'log', '-1', '--pretty=format:%B'], 
                              capture_output=True, text=True, check=False)
        if result.returncode != 0:
            return errors  # Skip if git not available
        
        commit_msg = result.stdout.strip()
        if not commit_msg:
            return errors
        
        # Check for FCR references in commit message
        if 'FCR-1:' in commit_msg and 'FCR-2:' in commit_msg:
            # Good, commit has FCR references
            pass
        elif len(commit_msg.split('\n')) > 1:
            # Multi-line commit, check if it follows template
            lines = commit_msg.split('\n')
            body = '\n'.join(lines[2:]) if len(lines) > 2 else ''
            
            if not re.search(r'FCR-1:\s*<[^>]+>', body):
                errors.append("[F3001] Commit Format: FCR-1 link missing from commit message body")
            
            if not re.search(r'FCR-2:\s*<[^>]+>', body):
                errors.append("[F3002] Commit Format: FCR-2 link missing from commit message body")
    
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass  # Skip commit checks if git not available
    
    return errors

def validate_evidence_files() -> List[str]:
    """Check if evidence files exist and are properly formatted."""
    errors = []
    
    evidence_dir = Path('ASI-T/GENESIS/EVIDENCE')
    if not evidence_dir.exists():
        errors.append("[F4001] Evidence Directory Missing: ASI-T/GENESIS/EVIDENCE directory not found")
        return errors
    
    # Look for evidence blob files
    blob_files = list(evidence_dir.glob('*.qs.json')) + list(evidence_dir.glob('*.qs.yaml'))
    
    if not blob_files:
        errors.append("[F4002] Evidence Blob Missing: No QS evidence files found in ASI-T/GENESIS/EVIDENCE/")
    
    # Validate evidence file format
    for blob_file in blob_files:
        try:
            with open(blob_file, 'r', encoding='utf-8') as f:
                if blob_file.suffix == '.json':
                    data = json.load(f)
                else:  # .yaml
                    import yaml
                    data = yaml.safe_load(f)
            
            # Check required fields in evidence blob
            required_evidence_fields = ['artifact_id', 'timestamp', 'validation_version']
            for field in required_evidence_fields:
                if field not in data:
                    errors.append(f"[F4003] Evidence Format: Missing '{field}' in {blob_file}")
                    
        except Exception as e:
            errors.append(f"[F4004] Evidence Parse Error: Could not parse {blob_file}: {e}")
    
    return errors

def main():
    """Main FCR validation function."""
    print("🔍 Genesis FCR Enforcer Validation")
    print("=" * 40)
    
    errors = []
    
    # Get PR description
    pr_description = get_pr_description()
    
    if pr_description:
        print(f"📋 Checking PR/commit description ({len(pr_description)} chars)")
        
        # Check FCR links
        fcr_errors = check_fcr_links(pr_description)
        errors.extend(fcr_errors)
        
        # Check evidence and provenance
        evidence_errors = check_evidence_provenance(pr_description)
        errors.extend(evidence_errors)
    else:
        print("⚠️  No PR description found (may be running locally)")
    
    # Check commit message format
    commit_errors = check_commit_message_format()
    errors.extend(commit_errors)
    
    # Validate evidence files
    file_errors = validate_evidence_files()
    errors.extend(file_errors)
    
    if errors:
        print(f"\n❌ Found {len(errors)} FCR validation errors:")
        for error in errors:
            print(f"  {error}")
        
        print("\n💡 Required format for PR description:")
        print("  FCR-1 ⟶ <intent-url>")
        print("  FCR-2 ⟶ <diff-evidence-url>") 
        print("  policy_hash: sha256:POLICY")
        print("  model_sha: sha256:MODEL")
        print("  data_manifest_hash: sha256:DATA")
        print("  canonical_hash: sha256:CANONICAL-BLOB")
        print("  Operator: UTCS:OP:operator-id")
        
        sys.exit(1)
    else:
        print("✅ All FCR requirements validated successfully")
        sys.exit(0)

if __name__ == '__main__':
    main()