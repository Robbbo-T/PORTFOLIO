#!/usr/bin/env python3
"""
ASI-T Copilot Styleguide Validator
Validates the new styleguide format and ensures consistency
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Tuple

# Repository root
REPO_ROOT = Path(__file__).parent.parent

# CAx canonical phases in chronological order
CAX_PHASES_CANONICAL = [
    "STRATEGY", "CAX-METHODOLOGY", "CAB", "CAIR", "CAD",
    "CAE", "CAI", "CAV", "CAT", "CAM", 
    "CA-PRO", "CAO", "CAF", "CAS0", "CAEPOST"
]

# TFA path grammar regex
TFA_PATH_REGEX = re.compile(
    r"^(?:ASI-T|TFA)/(SYSTEMS|STATIONS|COMPONENTS|BITS|QUBITS|ELEMENTS|WAVES|STATES)/[A-Z]{2}/(?:_revisions/REV_[A-Z]/HOV_[^/]+/)?[A-Z0-9-]{10,}\.md$"
)

def validate_styleguide_exists() -> Tuple[bool, str]:
    """Check if the styleguide file exists"""
    styleguide_path = REPO_ROOT / ".github" / "ASI-T-COPILOT-AGENT-STYLEGUIDE.md"
    if not styleguide_path.exists():
        return False, f"Styleguide not found at {styleguide_path}"
    return True, f"Styleguide found at {styleguide_path}"

def validate_cax_phases_in_styleguide() -> Tuple[bool, str]:
    """Validate that all CAx phases are documented in the styleguide"""
    styleguide_path = REPO_ROOT / ".github" / "ASI-T-COPILOT-AGENT-STYLEGUIDE.md"
    
    if not styleguide_path.exists():
        return False, "Styleguide file not found"
    
    content = styleguide_path.read_text()
    
    # Check if all phases are mentioned
    missing_phases = []
    for phase in CAX_PHASES_CANONICAL:
        if phase not in content:
            missing_phases.append(phase)
    
    if missing_phases:
        return False, f"Missing CAx phases in styleguide: {missing_phases}"
    
    return True, f"All {len(CAX_PHASES_CANONICAL)} CAx phases documented"

def validate_path_regex_in_styleguide() -> Tuple[bool, str]:
    """Validate that the path regex is properly documented"""
    styleguide_path = REPO_ROOT / ".github" / "ASI-T-COPILOT-AGENT-STYLEGUIDE.md"
    
    if not styleguide_path.exists():
        return False, "Styleguide file not found"
    
    content = styleguide_path.read_text()
    
    # Check if regex pattern is documented
    if "^(?:ASI-T|TFA)/" not in content:
        return False, "TFA path regex not found in styleguide"
    
    if "POSIX ERE" not in content:
        return False, "POSIX ERE specification not found"
    
    return True, "TFA path regex properly documented"

def validate_error_codes() -> Tuple[bool, str]:
    """Validate that error codes are properly documented"""
    styleguide_path = REPO_ROOT / ".github" / "ASI-T-COPILOT-AGENT-STYLEGUIDE.md"
    
    if not styleguide_path.exists():
        return False, "Styleguide file not found"
    
    content = styleguide_path.read_text()
    
    # Check for error code patterns
    error_codes = ["E1001", "E2001", "E2107", "E2108", "E2110", "E2111", "E6001"]
    missing_codes = []
    
    for code in error_codes:
        if code not in content:
            missing_codes.append(code)
    
    if missing_codes:
        return False, f"Missing error codes: {missing_codes}"
    
    return True, f"All {len(error_codes)} error codes documented"

def validate_front_matter_template() -> Tuple[bool, str]:
    """Validate the UTCS-MI front-matter template format"""
    styleguide_path = REPO_ROOT / ".github" / "ASI-T-COPILOT-AGENT-STYLEGUIDE.md"
    
    if not styleguide_path.exists():
        return False, "Styleguide file not found"
    
    content = styleguide_path.read_text()
    
    # Check for required front-matter fields
    required_fields = ["id:", "rev:", "llc:", "configuration: baseline", "provenance:", "hov:"]
    missing_fields = []
    
    for field in required_fields:
        if field not in content:
            missing_fields.append(field)
    
    if missing_fields:
        return False, f"Missing front-matter fields: {missing_fields}"
    
    return True, "UTCS-MI front-matter template properly documented"

def main():
    """Run all validations"""
    print("🔍 Validating ASI-T Copilot Styleguide...")
    print()
    
    validations = [
        ("Styleguide file exists", validate_styleguide_exists),
        ("CAx phases documented", validate_cax_phases_in_styleguide),
        ("Path regex documented", validate_path_regex_in_styleguide),
        ("Error codes documented", validate_error_codes),
        ("Front-matter template", validate_front_matter_template),
    ]
    
    all_passed = True
    
    for name, validation_func in validations:
        passed, message = validation_func()
        status = "✅" if passed else "❌"
        print(f"{status} {name}: {message}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("🎯 All styleguide validations passed!")
        return 0
    else:
        print("⚠️  Some validations failed!")
        return 1

if __name__ == "__main__":
    exit(main())