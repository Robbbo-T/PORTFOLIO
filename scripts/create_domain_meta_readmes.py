#!/usr/bin/env python3
"""Create META/README.md stubs for all TFA domains.

This script is idempotent: it creates missing README.md files under
2-DOMAINS-LEVELS/<DOMAIN>/TFA/META/ with a standardized template.
Existing files are left untouched.
"""
from pathlib import Path

DOMAINS = {
    "AAA-AERODYNAMICS-AND-AIRFRAMES-ARCHITECTURES": "AAA — AERODYNAMICS-AND-AIRFRAMES-ARCHITECTURES",
    "AAP-AIRPORTS-PLATFORMS-AND-HYDROGEN-ENABLERS": "AAP — AIRPORTS-PLATFORMS-AND-HYDROGEN-ENABLERS",
    "CCC-COCKPIT-CABIN-AND-CARGO": "CCC — COCKPIT-CABIN-AND-CARGO",
    "CQH-CRYOGENICS-QUANTUM-AND-H2": "CQH — CRYOGENICS-QUANTUM-AND-H2",
    "DDD-DIGITAL-AND-DATA-DEFENSE": "DDD — DIGITAL-AND-DATA-DEFENSE",
    "EDI-ELECTRONICS-DIGITAL-INSTRUMENTS": "EDI — ELECTRONICS-DIGITAL-INSTRUMENTS",
    "EEE-ECOLOGICAL-EFFICIENT-ELECTRIFICATION": "EEE — ECOLOGICAL-EFFICIENT-ELECTRIFICATION",
    "EER-ENVIRONMENTAL-EMISSIONS-AND-REMEDIATION": "EER — ENVIRONMENTAL-EMISSIONS-AND-REMEDIATION",
    "IIF-INDUSTRIAL-INFRASTRUCTURE-FACILITIES": "IIF — INDUSTRIAL-INFRASTRUCTURE-FACILITIES",
    "IIS-INTEGRATED-INTELLIGENCE-SOFTWARE": "IIS — INTEGRATED-INTELLIGENCE-SOFTWARE",
    "LCC-LINKAGES-CONTROL-AND-COMMUNICATIONS": "LCC — LINKAGES-CONTROL-AND-COMMUNICATIONS",
    "LIB-LOGISTICS-INVENTORY-AND-BLOCKCHAIN": "LIB — LOGISTICS-INVENTORY-AND-BLOCKCHAIN",
    "MMM-MECHANICS-MATERIALS-AND-MANUFACTURING": "MMM — MECHANICS-MATERIALS-AND-MANUFACTURING",
    "OOO-OS-ONTOLOGIES-AND-OFFICE-INTERFACES": "OOO — OS-ONTOLOGIES-AND-OFFICE-INTERFACES",
    "PPP-PROPULSION-AND-FUEL-SYSTEMS": "PPP — PROPULSION-AND-FUEL-SYSTEMS",
}

TEMPLATE = """# {title}

## Purpose & Scope
This META page captures domain-level decisions, authorship, and references for {code}. Scope: {domain_short}.

## Domain Steward
- Primary steward: [Team / Person Name]
- Contact: [email]

## Interfaces
- Upstream: 0-STRATEGY, 1-CAX-METHODOLOGY (as applicable)
- Downstream: relevant domains and OPTIMO-DT
- Typical interface artifacts: SysML models, ICDs, integration matrices

## Compliance & Standards
- Applicable standards and certification notes (list here)

## Variants & Notable Items
- Variant families and notable subsystems

## Quantum Layers Map (local decisions)
- BITS/CB: [classical responsibilities]
- QUBITS/QB: [quantum experiments/reservations]
- ELEMENTS/UE: [unit element responsibilities]
- ELEMENTS/FE: [federation responsibilities]
- WAVES/FWD: [predictive/foresight uses]
- STATES/QS: [quantum state artifacts or none]

## Local Decisions / Deviations
- Record deviation IDs, date, approver and rationale.

## Links / Templates
- Templates: 8-RESOURCES/TEMPLATES/DOMAIN-SPECIFIC-TEMPLATES/{domain_code}-TEMPLATES/ (adjust as needed)

## Change log
- Created: [YYYY-MM-DD] by [author]
- Last updated: [YYYY-MM-DD]
"""

def main():
    root = Path(__file__).resolve().parents[1]
    base_root = root / "2-DOMAINS-LEVELS"
    for code, title in DOMAINS.items():
        domain_short = title.split('—')[-1].strip()
        content = TEMPLATE.format(title=title, code=code, domain_short=domain_short, domain_code=code.split('-')[0])
        meta_dir = base_root / code / "TFA" / "META"
        meta_dir.mkdir(parents=True, exist_ok=True)
        readme = meta_dir / "README.md"
        if readme.exists():
            print(f"Skipping existing: {readme}")
        else:
            try:
                readme.write_text(content, encoding="utf-8")
                print(f"Created: {readme}")
            except OSError as e:
                print(f"Error creating {readme}: {e}")

if __name__ == "__main__":
    main()
