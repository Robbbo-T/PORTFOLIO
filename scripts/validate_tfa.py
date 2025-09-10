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

# Optional YAML support (for llc-map.yaml). Falls back to hardcoded map if PyYAML missing.
try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None  # handled below

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

# Load LLC map from 8-RESOURCES/llc-map.yaml if present (supports both flat and versioned formats)
def load_llc_map():
    llc_path = REPO / "8-RESOURCES" / "llc-map.yaml"
    if llc_path.exists() and yaml is not None:
        try:
            data = yaml.safe_load(llc_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                if "llc_codes" in data and isinstance(data["llc_codes"], dict):
                    return data["llc_codes"]
                # Flat style fallback
                return data
        except Exception:
            pass
    # Hard fallback
    return {
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

LLC_MAP = load_llc_map()

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
    r"\bFine\s+Element\b",    # must be Federation Element
    r"\bStation\s+Envelop\b", # must be Envelope (not Envelop)
]

def find_issues():
    issues = []

    # 1) Domains present
    if not DOMAINS_DIR.exists():
        issues.append(f"Missing directory: {DOMAINS_DIR.relative_to(REPO)}")
        return issues

    # Identify existing domains (ignore hidden/underscore)
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
                path = layer_path / leaf
                if leaf.endswith(".md"):
                    if not path.is_file():
                        issues.append(f"[{d}] Missing file: TFA/{layer}/{leaf}")
                else:
                    if not path.exists():
                        issues.append(f"[{d}] Missing node: TFA/{layer}/{leaf}/")

    # 3) Forbidden terminology scan (repo-wide, light pass)
    text_exts = {".md", ".yaml", ".yml", ".json", ".py", ".qasm", ".xml", ".xsd", ".proto", ".r", ".jl"}
    excluded_files = {
        "scripts/validate_tfa.py",                 # This validator itself
        "scripts/scaffold_tfa.py",                 # Scaffolding script (if present)
        "8-RESOURCES/llc-map.yaml",                # Canonical map defines phrases by design
        ".github/workflows/quantum-layers-check.yml",
    }
    for path in REPO.rglob("*"):
        if path.is_file() and path.suffix in text_exts:
            rel = str(path.relative_to(REPO)).replace("\\", "/")
            if rel in excluded_files:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for pat in FORBIDDEN_PHRASES:
                if re.search(pat, text):
                    issues.append(f"Forbidden term in {rel} → pattern '{pat}'")

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
    print("✅ TFA V2 structure validation passed!")
    print(f"✓ All {len(EXPECTED_DOMAINS)} domains checked with complete TFA hierarchy")
    print("✓ Quantum-classical bridge verified (CB/QB/UE/FE/FWD/QS)")
    print("✓ No forbidden terminology found")

if __name__ == "__main__":
    main()
