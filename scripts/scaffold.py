#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TFA Portfolio Structure Scaffolder (V2)
Creates missing TFA layers and quantum-classical bridge structure
"""
from pathlib import Path

root = Path(__file__).resolve().parents[1]

domains = [
    "AAA-AERODYNAMICS-AND-AIRFRAMES-ARCHITECTURES",
    "AAP-AIRPORTS-PLATFORMS-AND-HYDROGEN-ENABLERS",
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
    "MMM-MECHANICS-MATERIALS-AND-MANUFACTURING",
    "OOO-OS-ONTOLOGIES-AND-OFFICE-INTERFACES",
    "PPP-PROPULSION-AND-FUEL-SYSTEMS",
]

tree = {
    "SYSTEMS": ["SI", "DI"],
    "STATIONS": ["SE"],
    "COMPONENTS": ["CV", "CE", "CC", "CI", "CP"],
    "BITS": ["CB"],
    "QUBITS": ["QB"],
    "ELEMENTS": ["UE", "FE"],
    "WAVES": ["FWD"],
    "STATES": ["QS"],
    "META": ["README.md"],
}

def main():
    # Create TFA structure for all domains
    for d in domains:
        base = root / "2-DOMAINS-LEVELS" / d / "TFA"
        for layer, leaves in tree.items():
            (base / layer).mkdir(parents=True, exist_ok=True)
            for leaf in leaves:
                p = base / layer / leaf
                if leaf.endswith(".md"):
                    if not p.exists():
                        p.write_text("# META\n", encoding="utf-8")
                else:
                    p.mkdir(exist_ok=True)
    
    # Create quantum-classical bridge code buckets
    pb = root / "5-ARTIFACTS-IMPLEMENTATION" / "CODE" / "python"
    for leaf in ["classical-bits", "quantum-qubits", "unit-elements", "federation-elements", "wave-dynamics"]:
        (pb / leaf).mkdir(parents=True, exist_ok=True)
    
    print("Scaffold ensured.")

if __name__ == "__main__":
    main()