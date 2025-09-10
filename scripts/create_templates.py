#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Template Structure Generator for TFA V2
Creates the comprehensive template system as specified
"""

from pathlib import Path
import yaml

REPO = Path(__file__).resolve().parents[1]
TEMPLATES_DIR = REPO / "8-RESOURCES" / "TEMPLATES"
LLC_MAP_FILE = REPO / "8-RESOURCES" / "llc-map.yaml"

def load_llc_config():
    """Load LLC configuration."""
    with open(LLC_MAP_FILE, 'r') as f:
        return yaml.safe_load(f)

def create_tfa_layer_templates():
    """Create TFA layer templates."""
    config = load_llc_config()
    tfa_layers = config['tfa_layers']
    llc_codes = config['llc_codes']
    
    templates_root = TEMPLATES_DIR / "TFA-LAYER-TEMPLATES"
    templates_root.mkdir(exist_ok=True)
    
    for layer_name, layer_config in tfa_layers.items():
        layer_dir = templates_root / f"{layer_name}-TEMPLATES"
        layer_dir.mkdir(exist_ok=True)
        
        if 'llc_codes' in layer_config:
            for llc_code in layer_config['llc_codes']:
                llc_name = llc_codes[llc_code]
                llc_dir = layer_dir / f"{llc_code}-{llc_name.replace(' ', '-').replace('/', '-')}"
                llc_dir.mkdir(exist_ok=True)
                
                # Create README template
                readme_content = f"""# {llc_code} · {llc_name} Template

**Template Type:** TFA Layer Template  
**LLC Code:** {llc_code}  
**Canonical Meaning:** {llc_name}  
**TFA Layer:** {layer_name}

## Purpose

This template provides the standard structure and content for {llc_name} ({llc_code}) 
implementations across all domains in the TFA V2 architecture.

## Template Files

- `README.template.md` - Standard documentation template
- `specification.template.yaml` - Configuration template  
- `implementation.template.py` - Python implementation template

## Usage

1. Copy template files to target domain location
2. Replace placeholder values `[PLACEHOLDER]` with actual values
3. Customize for domain-specific requirements
4. Validate against TFA V2 structure requirements

## Placeholders

Standard placeholders used across templates:

- `[DOMAIN-CODE]` - Three-letter domain code (e.g., AAA, CQH)
- `[SYSTEM-ID]` - Unique system identifier
- `[COMPONENT-ID]` - Component identifier
- `[VERSION]` - Version number
- `[DATE]` - ISO 8601 date
- `[AUTHOR]` - Implementation author
"""
                
                (llc_dir / "README.template.md").write_text(readme_content)
                
                # Create basic YAML specification template
                yaml_content = f"""# {llc_code} Specification Template
metadata:
  template_version: "1.0"
  llc_code: "{llc_code}"
  llc_name: "{llc_name}"
  tfa_layer: "{layer_name}"
  domain: "[DOMAIN-CODE]"
  created: "[DATE]"
  author: "[AUTHOR]"

specification:
  id: "[{llc_code}-ID]"
  description: "[DESCRIPTION]"
  version: "[VERSION]"
  
  # {llc_name} specific configuration
  configuration:
    # Add {llc_code}-specific parameters here
    placeholder_param: "[VALUE]"
    
  # Standard TFA V2 metadata
  tfa_metadata:
    layer: "{layer_name}"
    llc: "{llc_code}"
    quantum_enabled: {'true' if llc_code in ['QB', 'QS', 'FWD'] else 'false'}
    classical_bridge: {'true' if llc_code == 'CB' else 'false'}
    federation_capable: {'true' if llc_code == 'FE' else 'false'}

# Validation rules
validation:
  required_fields: ["id", "description", "version"]
  format_rules:
    id: "^[A-Z]{{3}}-{llc_code}-[0-9]{{3}}$"
    version: "^[0-9]+\\.[0-9]+\\.[0-9]+$"
"""
                
                (llc_dir / "specification.template.yaml").write_text(yaml_content)

def create_cax_lifecycle_templates():
    """Create CAx lifecycle templates."""
    cax_phases = [
        ("CAB-BRAINSTORMING", "Concept capture and idea evaluation"),
        ("CAC-COMPLIANCE-SAFETY", "Safety cases and compliance validation"),
        ("CAD-DESIGN", "Design specifications and MBSE models"),
        ("CAE-ENGINEERING", "Engineering analysis and simulations"),
        ("CAF-FINANCE", "Financial models and blockchain economics"),
        ("CAI-AI-INTEGRATION", "AI model integration and orchestration"),
        ("CAM-MANUFACTURING", "Manufacturing plans and processes"),
        ("CAO-ORGANIZATION", "Organizational structures and governance"),
        ("CAP-PRODUCTION", "Production scheduling and optimization"),
        ("CAS-SUSTAINMENT", "Maintenance plans and S1000D compliance"),
        ("CAT-TESTING", "Test plans and validation procedures"),
        ("CAV-VERIFICATION", "Verification and V&V processes")
    ]
    
    cax_root = TEMPLATES_DIR / "CAX-LIFECYCLE-TEMPLATES"
    cax_root.mkdir(exist_ok=True)
    
    for phase_code, description in cax_phases:
        phase_dir = cax_root / phase_code
        phase_dir.mkdir(exist_ok=True)
        
        # Create phase README
        readme_content = f"""# {phase_code} Templates

**Phase:** {phase_code}  
**Description:** {description}

## Template Files

This directory contains templates for the {phase_code} phase of the CAx methodology.

### Standard Templates

- `process-template.yaml` - Process definition template
- `deliverable-template.md` - Deliverable documentation template  
- `checklist-template.md` - Phase completion checklist

### Usage

Templates in this directory support the {phase_code} phase activities across all domains
and integrate with the TFA V2 architecture through domain-specific implementations.
"""
        
        (phase_dir / "README.template.md").write_text(readme_content)

def create_domain_specific_templates():
    """Create domain-specific templates."""
    config = load_llc_config()
    domains = config['domains']
    
    domain_root = TEMPLATES_DIR / "DOMAIN-SPECIFIC-TEMPLATES"
    domain_root.mkdir(exist_ok=True)
    
    # Create templates for key domains
    key_domains = [
        ("AAA-AERODYNAMICS-AND-AIRFRAMES-ARCHITECTURES", "Aerodynamic analysis and airframe structures"),
        ("CQH-CRYOGENICS-QUANTUM-AND-H2", "Cryogenic systems, quantum computing, and hydrogen"),
        ("IIS-INTEGRATED-INTELLIGENCE-SOFTWARE", "AI model architectures and software intelligence")
    ]
    
    for domain_code, description in key_domains:
        domain_dir = domain_root / f"{domain_code}-TEMPLATES"
        domain_dir.mkdir(exist_ok=True)
        
        readme_content = f"""# {domain_code} Domain Templates

**Domain:** {domain_code}  
**Description:** {description}

## Domain-Specific Templates

Templates customized for the unique requirements of the {domain_code} domain.

### Available Templates

- `domain-model.template.yaml` - Domain-specific modeling template
- `integration-spec.template.json` - Domain integration specifications  
- `validation-suite.template.py` - Domain validation test suites

### Integration with TFA V2

These templates implement the complete TFA V2 quantum-classical architecture
specifically tailored for {domain_code} domain requirements.
"""
        
        (domain_dir / "README.template.md").write_text(readme_content)

def create_usage_guide():
    """Create template usage guide."""
    guide_content = """# TFA V2 Template System Usage Guide

This guide explains how to use the comprehensive TFA V2 template system for creating
consistent implementations across all domains and lifecycle phases.

## Template Structure

The template system is organized into three main categories:

### 1. TFA Layer Templates (`TFA-LAYER-TEMPLATES/`)

Templates organized by TFA hierarchy layers:

- **SYSTEMS-TEMPLATES/**: SI (System Integration), DI (Domain Interface)
- **STATIONS-TEMPLATES/**: SE (Station Envelope)  
- **COMPONENTS-TEMPLATES/**: CV, CE, CC, CI, CP
- **BITS-TEMPLATES/**: CB (Classical Bit)
- **QUBITS-TEMPLATES/**: QB (Qubit)
- **ELEMENTS-TEMPLATES/**: UE (Unit Element), FE (Federation Element)
- **WAVES-TEMPLATES/**: FWD (Waves Dynamics)
- **STATES-TEMPLATES/**: QS (Quantum State)

### 2. CAx Lifecycle Templates (`CAX-LIFECYCLE-TEMPLATES/`)

Templates for each phase of the Computer-Aided X methodology:

- **CAB-BRAINSTORMING/**: Innovation and concept development
- **CAC-COMPLIANCE-SAFETY/**: Safety and regulatory compliance
- **CAD-DESIGN/**: Design and MBSE modeling
- **CAE-ENGINEERING/**: Engineering analysis and simulation
- **CAF-FINANCE/**: Financial modeling and blockchain economics
- **CAI-AI-INTEGRATION/**: AI model integration and orchestration
- **CAM-MANUFACTURING/**: Manufacturing processes
- **CAO-ORGANIZATION/**: Organizational governance
- **CAP-PRODUCTION/**: Production planning and optimization
- **CAS-SUSTAINMENT/**: Maintenance and sustainment (S1000D)
- **CAT-TESTING/**: Testing and validation
- **CAV-VERIFICATION/**: Verification and V&V

### 3. Domain-Specific Templates (`DOMAIN-SPECIFIC-TEMPLATES/`)

Specialized templates for specific aerospace domains with unique requirements.

## How to Use Templates

### Step 1: Choose Appropriate Template

1. Identify your target TFA layer (SYSTEMS, COMPONENTS, etc.)
2. Select the specific LLC code (SI, FE, QB, etc.)
3. Navigate to the corresponding template directory

### Step 2: Copy Template Files

```bash
# Example: Using FE (Federation Element) template for CQH domain
cp -r 8-RESOURCES/TEMPLATES/TFA-LAYER-TEMPLATES/ELEMENTS-TEMPLATES/FE-FEDERATION-ELEMENT/* \\
      2-DOMAINS-LEVELS/CQH-CRYOGENICS-QUANTUM-AND-H2/TFA/ELEMENTS/FE/
```

### Step 3: Replace Placeholders

Standard placeholders used across all templates:

- `[DOMAIN-CODE]` - Replace with domain code (e.g., CQH, AAA)
- `[SYSTEM-ID]` - Unique system identifier  
- `[COMPONENT-ID]` - Component identifier
- `[VERSION]` - Semantic version (e.g., 1.0.0)
- `[DATE]` - ISO 8601 date (e.g., 2025-01-15)
- `[AUTHOR]` - Implementation author name

### Step 4: Customize for Domain

Adapt the template content for your specific domain requirements while
maintaining compliance with TFA V2 architecture principles.

### Step 5: Validate

Run the TFA validator to ensure your implementation meets all requirements:

```bash
python scripts/validate_tfa.py
```

## Template Development Guidelines

When creating new templates:

1. **Follow TFA V2 Principles**: Maintain strict TFA-only structure
2. **Use Standard Placeholders**: Ensure consistency across templates
3. **Include Documentation**: Every template should have clear usage instructions
4. **Quantum-Classical Awareness**: Consider quantum/classical bridge requirements
5. **Validation Ready**: Templates should validate successfully when placeholders are replaced

## Integration with CI/CD

Templates integrate with the CI/CD pipeline through:

- Automated structure validation
- Quantum layer compliance checking
- Terminology consistency enforcement
- Cross-domain federation validation

## Support

For template system support:

1. Check validation output: `python scripts/validate_tfa.py`
2. Review LLC mapping: `8-RESOURCES/llc-map.yaml`
3. Consult domain documentation in respective README files
"""
    
    (TEMPLATES_DIR / "USAGE-GUIDE.md").write_text(guide_content)

def main():
    """Main template creation function."""
    print("🏗️ Creating TFA V2 template system...")
    
    create_tfa_layer_templates()
    print("✅ TFA layer templates created")
    
    create_cax_lifecycle_templates()
    print("✅ CAx lifecycle templates created")
    
    create_domain_specific_templates()
    print("✅ Domain-specific templates created")
    
    create_usage_guide()
    print("✅ Usage guide created")
    
    print("🎯 TFA V2 template system creation complete!")

if __name__ == "__main__":
    main()
