#!/usr/bin/env python3
"""
TFA CB Template Validation Script

Validates that CB templates are properly structured and all domains have consistent implementations.
"""
import yaml
from pathlib import Path
from string import Template


class CBTemplateValidator:
    """Validator for CB template consistency and completeness."""
    
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.template_generator_path = self.base_path / "TEMPLATE-GENERATOR"
        self.template_path = self.base_path / "BITS-TEMPLATES" / "CB" / "CB_TEMPLATE.md"
        self.domains_path = Path("/home/runner/work/PORTFOLIO/PORTFOLIO/2-DOMAINS-LEVELS")
        
    def validate_template_structure(self):
        """Validate that the template file exists and is properly structured."""
        if not self.template_path.exists():
            return False, f"Template not found: {self.template_path}"
        
        # Load template and check for required placeholders
        template_text = self.template_path.read_text(encoding='utf-8')
        template = Template(template_text)
        
        required_placeholders = [
            'DOMAIN_CODE', 'DOMAIN_NAME', 'DOMAIN_FULL_NAME',
            'CB_PURPOSE_1', 'CB_PURPOSE_2', 'CB_PURPOSE_3', 'CB_PURPOSE_4',
            'COMPONENT_1_NAME', 'COMPONENT_2_NAME', 'COMPONENT_3_NAME'
        ]
        
        identifiers = set(template.get_identifiers())
        missing = set(required_placeholders) - identifiers
        
        if missing:
            return False, f"Missing required placeholders: {missing}"
        
        return True, f"Template structure valid with {len(identifiers)} placeholders"
    
    def validate_config_files(self):
        """Validate that all required domain config files exist and are complete."""
        config_dir = self.template_generator_path / "domain_configs"
        required_domains = ["aaa", "cqh", "iis"]
        
        results = []
        for domain in required_domains:
            config_file = config_dir / f"{domain}_config.yaml"
            
            if not config_file.exists():
                results.append((False, f"Config not found: {config_file}"))
                continue
            
            # Load and validate config
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                
                # Check required keys
                required_keys = [
                    'DOMAIN_CODE', 'DOMAIN_NAME', 'DOMAIN_FULL_NAME',
                    'CB_PURPOSE_1', 'COMPONENT_1_NAME'
                ]
                
                missing_keys = set(required_keys) - set(config.keys())
                if missing_keys:
                    results.append((False, f"{domain}: Missing keys: {missing_keys}"))
                else:
                    results.append((True, f"{domain}: Config valid with {len(config)} keys"))
                    
            except Exception as e:
                results.append((False, f"{domain}: Config load error: {e}"))
        
        return results
    
    def validate_generated_files(self):
        """Validate that generated CB README files exist in domain directories."""
        test_domains = [
            ("AAA", "AAA-AERODYNAMICS-AND-AIRFRAMES-ARCHITECTURES"),
            ("CQH", "CQH-CRYOGENICS-QUANTUM-AND-H2"),
            ("IIS", "IIS-INTEGRATED-INTELLIGENCE-SOFTWARE")
        ]
        
        results = []
        for domain_code, domain_dir in test_domains:
            cb_readme = self.domains_path / domain_dir / "TFA" / "BITS" / "CB" / "README.md"
            
            if not cb_readme.exists():
                results.append((False, f"{domain_code}: CB README not found: {cb_readme}"))
                continue
                
            # Check that the file was generated properly (contains domain-specific content)
            content = cb_readme.read_text(encoding='utf-8')
            if domain_code in content and "CLASSICAL BIT" in content:
                results.append((True, f"{domain_code}: CB README exists and contains expected content"))
            else:
                results.append((False, f"{domain_code}: CB README exists but seems incomplete"))
        
        return results
    
    def validate_all(self):
        """Run all validations and return comprehensive report."""
        print("🔍 Running TFA CB Template Validation...")
        print("=" * 50)
        
        # Template structure
        success, message = self.validate_template_structure()
        print(f"Template Structure: {'✅' if success else '❌'} {message}")
        
        # Config files  
        print("\nConfig Files:")
        config_results = self.validate_config_files()
        all_configs_ok = True
        for success, message in config_results:
            print(f"  {'✅' if success else '❌'} {message}")
            if not success:
                all_configs_ok = False
        
        # Generated files
        print("\nGenerated Files:")
        file_results = self.validate_generated_files()
        all_files_ok = True
        for success, message in file_results:
            print(f"  {'✅' if success else '❌'} {message}")
            if not success:
                all_files_ok = False
        
        # Overall result
        print("\n" + "=" * 50)
        overall_success = success and all_configs_ok and all_files_ok
        print(f"Overall: {'✅ All validations passed!' if overall_success else '❌ Some validations failed'}")
        
        return overall_success


def main():
    """Main validation runner."""
    validator = CBTemplateValidator("/home/runner/work/PORTFOLIO/PORTFOLIO/8-RESOURCES/TEMPLATES/TFA-LAYER-TEMPLATES")
    success = validator.validate_all()
    exit(0 if success else 1)


if __name__ == "__main__":
    main()