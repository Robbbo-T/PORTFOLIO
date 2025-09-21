#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TFA V2 Scaffolding Script
Creates missing domain directories and complete TFA structure
"""

from pathlib import Path
import sys
import yaml

REPO = Path(__file__).resolve().parents[1]
DOMAINS_DIR = REPO / "portfolio" / "2-DOMAINS-LEVELS"

# Load LLC mapping from canonical source
LLC_MAP_FILE = REPO / "8-RESOURCES" / "llc-map.yaml"

def load_llc_config():
    """Load LLC configuration from YAML file."""
    if not LLC_MAP_FILE.exists():
        print(f"❌ LLC mapping file not found: {LLC_MAP_FILE}")
        sys.exit(1)
    
    with open(LLC_MAP_FILE, 'r') as f:
        return yaml.safe_load(f)

def create_tfa_structure(domain_path, config):
    """Create complete TFA structure for a domain."""
    tfa_root = domain_path / "TFA"
    tfa_root.mkdir(exist_ok=True)
    
    tfa_layers = config['tfa_layers']
    llc_codes = config['llc_codes']
    
    for layer_name, layer_config in tfa_layers.items():
        layer_path = tfa_root / layer_name
        layer_path.mkdir(exist_ok=True)
        
        if 'llc_codes' in layer_config:
            # Create LLC directories
            for llc_code in layer_config['llc_codes']:
                llc_path = layer_path / llc_code
                llc_path.mkdir(exist_ok=True)
                
                # Create README.md with canonical LLC meaning
                readme_path = llc_path / "README.md"
                if not readme_path.exists():
                    llc_meaning = llc_codes.get(llc_code, "UNKNOWN")
                    content = f"# {llc_code} · {llc_meaning} ({domain_path.name})\n\n"
                    content += f"**Layer:** {layer_name}\n"
                    content += f"**LLC Code:** {llc_code}\n"
                    content += f"**Canonical Meaning:** {llc_meaning}\n\n"
                    content += "This directory contains artifacts and implementations for the "
                    content += f"{llc_meaning} within the {domain_path.name} domain.\n"
                    
                    readme_path.write_text(content)
        
        elif 'files' in layer_config:
            # Create required files (e.g., META layer)
            for filename in layer_config['files']:
                file_path = layer_path / filename
                if not file_path.exists():
                    content = f"# {domain_path.name} · TFA {layer_name}\n\n"
                    content += f"**TFA Layer:** {layer_name}\n"
                    content += f"**Description:** {layer_config['description']}\n\n"
                    content += "STRICT TFA-only structure. Updated from TFA V2 scaffolding.\n"
                    
                    file_path.write_text(content)

def scaffold_domains():
    """Create missing domains and TFA structures."""
    config = load_llc_config()
    expected_domains = config['domains']
    
    created_domains = 0
    updated_domains = 0
    
    for domain_name in expected_domains:
        domain_path = DOMAINS_DIR / domain_name
        
        if not domain_path.exists():
            print(f"🏗️ Creating domain: {domain_name}")
            domain_path.mkdir(parents=True)
            
            # Create domain README
            readme_path = domain_path / "README.md"
            content = f"# {domain_name}\n\n"
            content += "**TFA Scope:** Full quantum-classical architecture\n"
            content += "**STRICT TFA-ONLY:** No flat LLC folders under this domain.\n\n"
            content += "This domain implements the complete TFA V2 structure with quantum-classical integration:\n\n"
            content += "- **SYSTEMS/**: SI (System Integration), DI (Domain Interface)\n"
            content += "- **STATIONS/**: SE (Station Envelope)\n" 
            content += "- **COMPONENTS/**: CV, CE, CC, CI, CP\n"
            content += "- **BITS/**: CB (Classical Bit)\n"
            content += "- **QUBITS/**: QB (Qubit)\n"
            content += "- **ELEMENTS/**: UE (Unit Element), FE (Federation Entanglement)\n"
            content += "- **WAVES/**: FWD (Waves Dynamics)\n"
            content += "- **STATES/**: QS (Quantum State)\n"
            
            readme_path.write_text(content)
            created_domains += 1
            
        # Create/update TFA structure
        create_tfa_structure(domain_path, config)
        if domain_path.exists():
            updated_domains += 1
    
    print("✅ Scaffolding complete:")
    print(f"   Created domains: {created_domains}")
    print(f"   Updated domains: {updated_domains}")
    print(f"   Total domains: {len(expected_domains)}")

def main():
    """Main scaffolding function."""
    print("🏗️ Starting TFA V2 scaffolding...")
    
    # Ensure domains directory exists
    DOMAINS_DIR.mkdir(exist_ok=True)
    
    scaffold_domains()
    
    print("🎯 TFA V2 scaffolding completed successfully!")

if __name__ == "__main__":
    main()
