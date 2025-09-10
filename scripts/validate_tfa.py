#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TFA Portfolio Structure Validator (V2)
- Verifies 15 domains exist under 2-DOMAINS-LEVELS/
- Verifies required TFA layers & LLC leafs exist per domain
- Guards quantum-classical bridge (CB/QB/UE/FE/FWD/QS)
- Fails on forbidden terms (e.g., 'Fine Element' instead of 'Federation Element')
"""

from pathlib import Path
import sys
import re

REPO = Path(__file__).resolve().parents[1]

DOMAINS_DIR = REPO / "2-DOMAINS-LEVELS"

EXPECTED_DOMAINS = [
    "AAA-AERODYNAMICS-AND-AIRFRAMES-ARCHITECTURES",
    "AAP-AIRPORT-ADAPTABLE-PLATFORMS",
    "CCC-COCKPIT-CABIN-AND-CARGO",
    "CQH-CRYOGENICS-QUANTUM-AND-H2",
    "DDD-DIGITAL-AND-DATA-DEFENSE",
    "EDI-ELECTRONICS-DIGITAL-INSTRUMENTS",
    "EEE-ECOLOGICAL-EFFICIENT-ELECTRIFICATION",
    "EER-ENVIRONMENTAL-EMISSIONS-AND-REMEDIATION",
    "IIF-INDUSTRIAL-INFRASTRUCTURE-FACILITIES",
    "IIS-INTEGRATED-INTELLIGENCE-SOFTWARE",
    "LCC-LINKAGES-CONTROL-AND-COMMUNICATIONS",
    "LIB-LOGISTICS-INVENTORY-AND-BLOCKCHAIN",
    "MMM-MECHANICAL-AND-MATERIAL-MODULES",
    "OOO-OS-ONTOLOGIES-AND-OFFICE-INTERFACES",
    "PPP-PROPULSION-AND-FUEL-SYSTEMS",
]

# Single source of truth for LLC codes
LLC_MAP = {
    "SI": "SYSTEM INTEGRATION",
    "DI": "DOMAIN INTERFACE",
    "SE": "STATION ENVELOPE",
    "CV": "COMPONENT VENDOR",
    "CE": "COMPONENT EQUIPMENT",
    "CC": "CONFIGURATION CELL",
    "CI": "CONFIGURATION ITEM",
    "CP": "COMPONENT PART",
    "CB": "CLASSICAL BIT",
    "QB": "QUBIT",
    "UE": "UNIT ELEMENT",
    "FE": "FEDERATION ELEMENT",
    "FWD": "Future/Foresight/Fluctuant/Functional Waves Dynamics",
    "QS": "QUANTUM STATE",
}

REQUIRED_TREE = {
    "SYSTEMS": ["SI", "DI"],
    "STATIONS": ["SE"],
    "COMPONENTS": ["CV", "CE", "CC", "CI", "CP"],
    "BITS": ["CB"],
    "QUBITS": ["QB"],
    "ELEMENTS": ["UE", "FE"],
    "WAVES": ["FWD"],
    "STATES": ["QS"],
    "META": ["README.md"],  # file
}

FORBIDDEN_PHRASES = [
    r"\bFine\s+Element\b",           # must be Federation Element
    r"\bStation\s+Envelop\b",        # must be Envelope (not Envelop)
]

def find_issues():
    issues = []

    # 1) Domains present
    if not DOMAINS_DIR.exists():
        issues.append(f"Missing directory: {DOMAINS_DIR.relative_to(REPO)}")
        return issues

    # Identify existing domains
    existing = sorted([p.name for p in DOMAINS_DIR.iterdir() if p.is_dir() and not p.name.startswith('_')])
    for d in EXPECTED_DOMAINS:
        if d not in existing:
            issues.append(f"Missing domain: 2-DOMAINS-LEVELS/{d}/")

    # 2) Per-domain TFA tree
    for d in EXPECTED_DOMAINS:
        root = DOMAINS_DIR / d / "TFA"
        if not root.exists():
            issues.append(f"Missing TFA directory: 2-DOMAINS-LEVELS/{d}/TFA/")
            continue

        for layer, leaves in REQUIRED_TREE.items():
            layer_path = root / layer
            if not layer_path.exists():
                issues.append(f"[{d}] Missing layer: TFA/{layer}/")
                continue

            for leaf in leaves:
                leaf_path = layer_path / leaf
                if leaf.endswith(".md"):  # file requirement in META
                    if not leaf_path.is_file():
                        issues.append(f"[{d}] Missing file: TFA/{layer}/{leaf}")
                else:
                    if not leaf_path.exists():
                        issues.append(f"[{d}] Missing node: TFA/{layer}/{leaf}/")

    # 3) Forbidden terminology scan (repo-wide, light pass)
    text_exts = {".md", ".yaml", ".yml", ".json", ".py", ".qasm", ".xml", ".xsd", ".proto", ".r", ".jl"}
    excluded_files = {
        "scripts/validate_tfa.py",  # This validator itself
        "scripts/scaffold_tfa.py",  # Scaffolding script
        "8-RESOURCES/llc-map.yaml", # LLC mapping defines forbidden terms
        ".github/workflows/quantum-layers-check.yml", # Workflow file
    }
    
    for path in REPO.rglob("*"):
        if path.is_file() and path.suffix in text_exts:
            # Skip validation scripts and configuration files that define forbidden terms
            relative_path = str(path.relative_to(REPO))
            if relative_path in excluded_files:
                continue
                
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for pat in FORBIDDEN_PHRASES:
                if re.search(pat, text):
                    issues.append(f"Forbidden term in {path.relative_to(REPO)} → pattern '{pat}'")

    # 4) Quantum-classical bridge sanity in 5-ARTIFACTS-IMPLEMENTATION/CODE/python
    bridge = REPO / "5-ARTIFACTS-IMPLEMENTATION" / "CODE" / "python"
    if bridge.exists():
        for leaf in ["classical-bits", "quantum-qubits", "unit-elements", "federation-elements", "wave-dynamics"]:
            if not (bridge / leaf).exists():
                issues.append(f"Missing code bucket: 5-ARTIFACTS-IMPLEMENTATION/CODE/python/{leaf}/")

    return issues

def main():
    issues = find_issues()
    if issues:
        print("❌ TFA validation failed:\n")
        for i, msg in enumerate(issues, 1):
            print(f"{i:02d}. {msg}")
        print("\nTip: run `make scaffold` to create any missing folders.")
        sys.exit(1)
    else:
        print("✅ TFA V2 structure validation passed!")
        print(f"✓ All {len(EXPECTED_DOMAINS)} domains present with complete TFA hierarchy")
        print("✓ Quantum-classical bridge verified (CB/QB/UE/FE/FWD/QS)")
        print(f"✓ No forbidden terminology found")

if __name__ == "__main__":
    main()
