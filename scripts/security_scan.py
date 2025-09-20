#!/usr/bin/env python3
"""
Security scanning script for TFA manifests and documentation.

This script scans for potentially sensitive information like secret keys 
or private keys in TFA manifests and documentation files, ensuring 
compliance with DEFENSE context partitioning and SBOM requirements.
"""

import re
import glob
import sys
from pathlib import Path

# Define regex patterns for sensitive data
patterns = [
    re.compile(r"-----BEGIN[ A-Z]*PRIVATE KEY-----"),  # any kind of private key block
    re.compile(r"AKIA[0-9A-Z]{16}"),                   # AWS Access Key pattern
    re.compile(r"secret[_-]?key", re.IGNORECASE),      # any "secret key" mention
    re.compile(r"0x[0-9a-fA-F]{64}"),                  # 64-digit hex (potential crypto key)
]

def file_contains_secret(filepath):
    """Check if a file contains any patterns matching secrets."""
    try:
        with open(filepath, 'r', errors='ignore') as f:
            text = f.read()
        for pat in patterns:
            if pat.search(text):
                return True
        return False
    except Exception:
        return False

def main():
    """Main security scanning function."""
    # Gather manifest and documentation files to scan
    files_to_scan = []
    files_to_scan += glob.glob("2-DOMAINS-LEVELS/*/TFA/**/*.yaml", recursive=True)
    files_to_scan += glob.glob("2-DOMAINS-LEVELS/*/TFA/**/*.json", recursive=True)
    files_to_scan += glob.glob("2-DOMAINS-LEVELS/*/TFA/**/*.md", recursive=True)
    files_to_scan += glob.glob("docs/**/*.md", recursive=True)
    
    # Scan each file and collect any that contain secrets
    suspect_files = []
    for filepath in files_to_scan:
        if file_contains_secret(filepath):
            suspect_files.append(filepath)
    
    # Output results and exit with error if any secret found
    if suspect_files:
        print("❌ Security violation: Potential secrets found in the following files:")
        for f in suspect_files:
            print(f"  - {f}")
        print("Please remove secrets and use the approved secure storage for any sensitive data.")
        sys.exit(1)
    else:
        print("✅ No secrets or private keys found in manifests or documentation.")

if __name__ == "__main__":
    main()