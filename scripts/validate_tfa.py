#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TFA Portfolio Structure Validator (V2)
- Verifies 15 domains exist under 2-DOMAINS-LEVELS/
- Verifies required TFA layers & LLC leafs per domain
- Guards quantum-classical bridge (CB/QB/UE/FE/FWD/QS)
- Fails on forbidden terms ('Fine Element', 'Station Envelop')
"""
from pathlib import Path
import sys
import re
import yaml

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

LLC_MAP = yaml.safe_load("""
SI: SYSTEM INTEGRATION
DI: DOMAIN INTERFACE
SE: STATION ENVELOPE
CV: COMPONENT VENDOR
CE: COMPONENT EQUIPMENT
CC: CONFIGURATION CELL
CI: CONFIGURATION ITEM
CP: COMPONENT PART
CB: CLASSICAL BIT
QB: QUBIT
UE: UNIT ELEMENT
FE: FEDERATION ELEMENT
FWD: Future/Foresight/Fluctuant/Functional Waves Dynamics
QS: QUANTUM STATE
""")

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
    r"\bFine\s+Element\b",
    r"\bStation\s+Envelop\b",
]

def find_issues():
    issues = []

    if not DOMAINS_DIR.exists():
        issues.append(f"Missing directory: {DOMAINS_DIR.relative_to(REPO)}")
        return issues

    existing = sorted(p.name for p in DOMAINS_DIR.iterdir() if p.is_dir())
    for d in EXPECTED_DOMAINS:
        if d not in existing:
            issues.append(f"Missing domain: 2-DOMAINS-LEVELS/{d}/")

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
                path = layer_path / leaf
                if leaf.endswith(".md"):
                    if not path.is_file():
                        issues.append(f"[{d}] Missing file: TFA/{layer}/{leaf}")
                else:
                    if not path.exists():
                        issues.append(f"[{d}] Missing node: TFA/{layer}/{leaf}/")

    text_exts = {".md", ".yaml", ".yml", ".json", ".py", ".qasm", ".xml", ".xsd", ".proto", ".r", ".jl"}
    for path in REPO.rglob("*"):
        if path.is_file() and path.suffix in text_exts:
            # Skip the validation script itself to avoid self-detection
            if path.name == "validate_tfa.py":
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for pat in FORBIDDEN_PHRASES:
                if re.search(pat, text):
                    issues.append(f"Forbidden term in {path.relative_to(REPO)} → pattern '{pat}'")

    bridge = REPO / "5-ARTIFACTS-IMPLEMENTATION" / "CODE" / "python"
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
    print("✅ TFA validation passed. Structure and terminology are consistent.")

if __name__ == "__main__":
    main()