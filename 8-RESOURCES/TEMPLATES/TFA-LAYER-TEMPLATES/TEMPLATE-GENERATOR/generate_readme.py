#!/usr/bin/env python3
"""
TFA CB Template Generator

Generates instantiated CB README files from templates and domain configurations.
"""
import yaml
import sys
from pathlib import Path
from string import Template


class TFATemplateGenerator:
    """Generator for TFA CB templates with domain-specific configurations."""
    
    def __init__(self, template_path, config_path):
        """Initialize generator with template and config paths."""
        self.template_path = Path(template_path)
        self.config_path = Path(config_path)
        
        # Load template
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template not found: {self.template_path}")
        self.template = Template(self.template_path.read_text(encoding='utf-8'))
        
        # Load config
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config not found: {self.config_path}")
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
    
    def validate(self):
        """Check that all template tokens are defined in config."""
        template_tokens = set(self.template.get_identifiers())
        config_tokens = set(self.config.keys())
        missing = template_tokens - config_tokens
        
        if missing:
            raise ValueError(f"Missing configuration tokens: {missing}")
        
        print(f"✅ Validation passed - {len(config_tokens)} tokens defined")
        return True
    
    def generate(self, output_path):
        """Generate instantiated README from template and config."""
        output_path = Path(output_path)
        
        # Create output directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate content
        try:
            content = self.template.safe_substitute(self.config)
        except KeyError as e:
            raise ValueError(f"Template substitution failed for: {e}")
        
        # Write output
        output_path.write_text(content, encoding='utf-8')
        print(f"Generated: {output_path}")
        return output_path
    
    def preview(self):
        """Preview generated content without writing to file."""
        content = self.template.safe_substitute(self.config)
        return content


def main():
    """Main CLI interface."""
    if len(sys.argv) < 2:
        print("Usage: python generate_readme.py <config_file> <output_path>")
        print("       python generate_readme.py --validate <config_file>")
        print("       python generate_readme.py --generate-all")
        sys.exit(1)
    
    script_dir = Path(__file__).parent
    template_path = script_dir.parent / "BITS-TEMPLATES" / "CB" / "CB_TEMPLATE.md"
    
    if sys.argv[1] == "--generate-all":
        # Generate all domain examples
        domains = ["aaa", "cqh", "iis"]
        base_output_dir = script_dir / ".." / "INSTANTIATED-EXAMPLES"
        
        for domain in domains:
            config_path = script_dir / "domain_configs" / f"{domain}_config.yaml"
            output_path = base_output_dir / domain.upper() / "CB-README.md"
            
            try:
                generator = TFATemplateGenerator(template_path, config_path)
                generator.validate()
                generator.generate(output_path)
                print(f"✅ Generated {domain.upper()} CB README")
            except Exception as e:
                print(f"❌ Failed to generate {domain.upper()}: {e}")
                
        return
    
    if sys.argv[1] == "--validate":
        config_path = Path(sys.argv[2])
        try:
            generator = TFATemplateGenerator(template_path, config_path)
            generator.validate()
            print("✅ Configuration validation passed")
        except Exception as e:
            print(f"❌ Validation failed: {e}")
            sys.exit(1)
        return
    
    # Standard generation
    config_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    
    try:
        generator = TFATemplateGenerator(template_path, config_path)
        generator.validate()
        generator.generate(output_path)
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()