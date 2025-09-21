#!/usr/bin/env python3
"""
AQUA OS PRO Validation Framework

This module provides comprehensive validation for AQUA OS PRO implementations
across all domains and TFA layers.
"""

import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
import jsonschema
import importlib.util
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Result of a validation check"""
    component: str
    status: str  # "pass", "fail", "warning"
    message: str
    details: Optional[Dict[str, Any]] = None

class AquaProValidator:
    """Comprehensive validator for AQUA OS PRO implementations"""
    
    def __init__(self, portfolio_root: Path):
        self.portfolio_root = Path(portfolio_root)
        self.validation_results: List[ValidationResult] = []
        self.domains = ["AAA", "AAP", "CCC", "CQH", "DDD", "EDI", "EEE", "EER", 
                       "IIF", "IIS", "LCC", "LIB", "MMM", "OOO", "PPP"]
        self.layers = ["SI", "DI", "SE", "CB", "QB", "FWD", "QS", "FE"]
        self.tfa_mapping = {
            "SI": ("SYSTEMS", "SI"),
            "DI": ("SYSTEMS", "DI"),
            "SE": ("STATIONS", "SE"),
            "CB": ("BITS", "CB"),
            "QB": ("QUBITS", "QB"),
            "FWD": ("WAVES", "FWD"),
            "QS": ("STATES", "QS"),
            "FE": ("ELEMENTS", "FE")
        }
        
    async def validate_all(self) -> Dict[str, Any]:
        """Run comprehensive validation of AQUA OS PRO implementation"""
        logger.info("Starting comprehensive AQUA OS PRO validation...")
        
        # Validate TFA structure
        await self._validate_tfa_structure()
        
        # Validate specifications
        await self._validate_specifications()
        
        # Validate implementations
        await self._validate_implementations()
        
        # Validate schemas
        await self._validate_schemas()
        
        # Validate API contracts
        await self._validate_api_contracts()
        
        # Validate performance requirements
        await self._validate_performance_requirements()
        
        # Validate quantum-classical bridge
        await self._validate_quantum_classical_bridge()
        
        # Validate federation layer
        await self._validate_federation_layer()
        
        # Generate validation report
        return self._generate_validation_report()
    
    async def _validate_tfa_structure(self) -> None:
        """Validate TFA structure compliance"""
        logger.info("Validating TFA structure...")
        
        domains_path = self.portfolio_root / "2-DOMAINS-LEVELS"
        
        for domain_code in self.domains:
            domain_name = self._get_domain_name(domain_code)
            domain_path = domains_path / f"{domain_code}-{domain_name}"
            
            if not domain_path.exists():
                self.validation_results.append(ValidationResult(
                    component=f"TFA.{domain_code}",
                    status="fail",
                    message=f"Domain directory not found: {domain_path}"
                ))
                continue
            
            tfa_path = domain_path / "TFA"
            if not tfa_path.exists():
                self.validation_results.append(ValidationResult(
                    component=f"TFA.{domain_code}",
                    status="fail",
                    message=f"TFA directory not found: {tfa_path}"
                ))
                continue
            
            # Validate each layer
            for layer_code in self.layers:
                tfa_group, tfa_layer = self.tfa_mapping[layer_code]
                layer_path = tfa_path / tfa_group / tfa_layer
                
                if not layer_path.exists():
                    self.validation_results.append(ValidationResult(
                        component=f"TFA.{domain_code}.{layer_code}",
                        status="fail",
                        message=f"Layer directory not found: {layer_path}"
                    ))
                    continue
                
                # Check for AQUA OS PRO specification
                spec_file = layer_path / "AQUA-OS-PRO-SPEC.md"
                if not spec_file.exists():
                    self.validation_results.append(ValidationResult(
                        component=f"TFA.{domain_code}.{layer_code}.spec",
                        status="fail",
                        message=f"AQUA OS PRO specification not found: {spec_file}"
                    ))
                else:
                    self.validation_results.append(ValidationResult(
                        component=f"TFA.{domain_code}.{layer_code}.spec",
                        status="pass",
                        message="AQUA OS PRO specification found"
                    ))
                
                # Check for implementation
                impl_file = layer_path / "aqua_pro_implementation.py"
                if not impl_file.exists():
                    self.validation_results.append(ValidationResult(
                        component=f"TFA.{domain_code}.{layer_code}.impl",
                        status="fail", 
                        message=f"Implementation not found: {impl_file}"
                    ))
                else:
                    self.validation_results.append(ValidationResult(
                        component=f"TFA.{domain_code}.{layer_code}.impl",
                        status="pass",
                        message="Implementation file found"
                    ))
    
    async def _validate_specifications(self) -> None:
        """Validate AQUA OS PRO specifications"""
        logger.info("Validating specifications...")
        
        domains_path = self.portfolio_root / "2-DOMAINS-LEVELS"
        
        for domain_code in self.domains:
            domain_name = self._get_domain_name(domain_code)
            domain_path = domains_path / f"{domain_code}-{domain_name}" / "TFA"
            
            for layer_code in self.layers:
                tfa_group, tfa_layer = self.tfa_mapping[layer_code]
                spec_file = domain_path / tfa_group / tfa_layer / "AQUA-OS-PRO-SPEC.md"
                
                if spec_file.exists():
                    try:
                        content = spec_file.read_text(encoding='utf-8')
                        
                        # Validate required sections
                        required_sections = [
                            "# AQUA OS PRO",
                            "## Requirement Specification",
                            "## Technical Context",
                            "## Implementation Details",
                            "## Performance Metrics",
                            "## Testing Requirements"
                        ]
                        
                        missing_sections = []
                        for section in required_sections:
                            if section not in content:
                                missing_sections.append(section)
                        
                        if missing_sections:
                            self.validation_results.append(ValidationResult(
                                component=f"SPEC.{domain_code}.{layer_code}",
                                status="warning",
                                message="Missing required sections",
                                details={"missing": missing_sections}
                            ))
                        else:
                            self.validation_results.append(ValidationResult(
                                component=f"SPEC.{domain_code}.{layer_code}",
                                status="pass",
                                message="All required sections present"
                            ))
                        
                        # Validate UTCS ID format
                        if f"**UTCS ID**: {domain_code}/{layer_code}/REQ-" in content:
                            self.validation_results.append(ValidationResult(
                                component=f"SPEC.{domain_code}.{layer_code}.utcs",
                                status="pass",
                                message="UTCS ID format valid"
                            ))
                        else:
                            self.validation_results.append(ValidationResult(
                                component=f"SPEC.{domain_code}.{layer_code}.utcs",
                                status="fail",
                                message="Invalid or missing UTCS ID format"
                            ))
                            
                    except Exception as e:
                        self.validation_results.append(ValidationResult(
                            component=f"SPEC.{domain_code}.{layer_code}",
                            status="fail",
                            message=f"Error reading specification: {e}"
                        ))
    
    async def _validate_implementations(self) -> None:
        """Validate Python implementations"""
        logger.info("Validating implementations...")
        
        domains_path = self.portfolio_root / "2-DOMAINS-LEVELS"
        
        for domain_code in self.domains:
            domain_name = self._get_domain_name(domain_code)
            domain_path = domains_path / f"{domain_code}-{domain_name}" / "TFA"
            
            for layer_code in self.layers:
                tfa_group, tfa_layer = self.tfa_mapping[layer_code]
                impl_file = domain_path / tfa_group / tfa_layer / "aqua_pro_implementation.py"
                
                if impl_file.exists():
                    try:
                        # Basic syntax validation
                        content = impl_file.read_text(encoding='utf-8')
                        compile(content, str(impl_file), 'exec')
                        
                        # Check for required classes and functions
                        required_elements = [
                            f"class AquaPro{layer_code}Interface",
                            f"class AquaPro{layer_code}Implementation",
                            "def initialize(",
                            "def process(",
                            "def get_status("
                        ]
                        
                        missing_elements = []
                        for element in required_elements:
                            if element not in content:
                                missing_elements.append(element)
                        
                        if missing_elements:
                            self.validation_results.append(ValidationResult(
                                component=f"IMPL.{domain_code}.{layer_code}",
                                status="warning",
                                message="Missing required elements",
                                details={"missing": missing_elements}
                            ))
                        else:
                            self.validation_results.append(ValidationResult(
                                component=f"IMPL.{domain_code}.{layer_code}",
                                status="pass",
                                message="Implementation structure valid"
                            ))
                            
                        # Try to import the module
                        try:
                            spec = importlib.util.spec_from_file_location(
                                f"{domain_code}_{layer_code}", impl_file)
                            module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(module)
                            
                            self.validation_results.append(ValidationResult(
                                component=f"IMPL.{domain_code}.{layer_code}.import",
                                status="pass",
                                message="Module imports successfully"
                            ))
                        except Exception as e:
                            self.validation_results.append(ValidationResult(
                                component=f"IMPL.{domain_code}.{layer_code}.import",
                                status="fail",
                                message=f"Import error: {e}"
                            ))
                            
                    except SyntaxError as e:
                        self.validation_results.append(ValidationResult(
                            component=f"IMPL.{domain_code}.{layer_code}",
                            status="fail",
                            message=f"Syntax error: {e}"
                        ))
                    except Exception as e:
                        self.validation_results.append(ValidationResult(
                            component=f"IMPL.{domain_code}.{layer_code}",
                            status="fail",
                            message=f"Error validating implementation: {e}"
                        ))
    
    async def _validate_schemas(self) -> None:
        """Validate JSON schemas"""
        logger.info("Validating schemas...")
        
        schemas_path = self.portfolio_root / "services" / "aqua-os-pro" / "schemas"
        
        if not schemas_path.exists():
            self.validation_results.append(ValidationResult(
                component="SCHEMA.directory",
                status="fail",
                message=f"Schemas directory not found: {schemas_path}"
            ))
            return
        
        # Validate route optimization schema
        route_schema_file = schemas_path / "route_optimization.json"
        if route_schema_file.exists():
            try:
                with route_schema_file.open() as f:
                    schema = json.load(f)
                
                # Validate schema syntax
                jsonschema.Draft7Validator.check_schema(schema)
                
                self.validation_results.append(ValidationResult(
                    component="SCHEMA.route_optimization",
                    status="pass",
                    message="Route optimization schema valid"
                ))
                
                # Validate sample data against schema
                sample_data = {
                    "route_request": {
                        "utcs_id": "AAA/SI/REQ-0101",
                        "domain": "AAA",
                        "layer": "SI",
                        "timestamp": "2024-01-01T00:00:00Z",
                        "route_params": {
                            "origin": {"latitude": 40.7128, "longitude": -74.0060},
                            "destination": {"latitude": 34.0522, "longitude": -118.2437},
                            "cruise_altitude": 35000,
                            "optimization_weights": {
                                "fuel": 0.4,
                                "time": 0.4,
                                "emissions": 0.2
                            }
                        }
                    }
                }
                
                jsonschema.validate(sample_data, schema)
                
                self.validation_results.append(ValidationResult(
                    component="SCHEMA.route_optimization.validation",
                    status="pass",
                    message="Schema validation with sample data successful"
                ))
                
            except jsonschema.SchemaError as e:
                self.validation_results.append(ValidationResult(
                    component="SCHEMA.route_optimization",
                    status="fail",
                    message=f"Schema syntax error: {e}"
                ))
            except jsonschema.ValidationError as e:
                self.validation_results.append(ValidationResult(
                    component="SCHEMA.route_optimization.validation",
                    status="fail", 
                    message=f"Sample data validation error: {e}"
                ))
            except Exception as e:
                self.validation_results.append(ValidationResult(
                    component="SCHEMA.route_optimization",
                    status="fail",
                    message=f"Error validating schema: {e}"
                ))
        else:
            self.validation_results.append(ValidationResult(
                component="SCHEMA.route_optimization",
                status="fail",
                message="Route optimization schema file not found"
            ))
    
    async def _validate_api_contracts(self) -> None:
        """Validate API contracts"""
        logger.info("Validating API contracts...")
        
        # Check for API contract specifications in each layer spec
        domains_path = self.portfolio_root / "2-DOMAINS-LEVELS"
        
        contract_count = 0
        for domain_code in self.domains:
            domain_name = self._get_domain_name(domain_code)
            domain_path = domains_path / f"{domain_code}-{domain_name}" / "TFA"
            
            for layer_code in self.layers:
                tfa_group, tfa_layer = self.tfa_mapping[layer_code]
                spec_file = domain_path / tfa_group / tfa_layer / "AQUA-OS-PRO-SPEC.md"
                
                if spec_file.exists():
                    content = spec_file.read_text(encoding='utf-8')
                    if "### API Contracts" in content:
                        contract_count += 1
        
        if contract_count == len(self.domains) * len(self.layers):
            self.validation_results.append(ValidationResult(
                component="API.contracts",
                status="pass",
                message=f"All {contract_count} API contracts specified"
            ))
        else:
            self.validation_results.append(ValidationResult(
                component="API.contracts",
                status="warning",
                message=f"Only {contract_count}/{len(self.domains) * len(self.layers)} API contracts found"
            ))
    
    async def _validate_performance_requirements(self) -> None:
        """Validate performance requirements"""
        logger.info("Validating performance requirements...")
        
        # Check orchestrator exists and has proper configuration
        orchestrator_file = self.portfolio_root / "services" / "aqua-os-pro" / "core" / "aqua_pro_orchestrator.py"
        
        if orchestrator_file.exists():
            content = orchestrator_file.read_text(encoding='utf-8')
            
            # Check for key performance elements
            performance_elements = [
                "sla_threshold_ms",
                "cadence_seconds", 
                "loop_duration_minutes",
                "processing_time_ms",
                "sla_compliant"
            ]
            
            missing_elements = []
            for element in performance_elements:
                if element not in content:
                    missing_elements.append(element)
            
            if missing_elements:
                self.validation_results.append(ValidationResult(
                    component="PERF.orchestrator",
                    status="warning",
                    message="Missing performance elements",
                    details={"missing": missing_elements}
                ))
            else:
                self.validation_results.append(ValidationResult(
                    component="PERF.orchestrator",
                    status="pass",
                    message="Performance monitoring elements present"
                ))
        else:
            self.validation_results.append(ValidationResult(
                component="PERF.orchestrator",
                status="fail",
                message="Orchestrator not found"
            ))
    
    async def _validate_quantum_classical_bridge(self) -> None:
        """Validate quantum-classical bridge implementation"""
        logger.info("Validating quantum-classical bridge...")
        
        # Check for quantum implementations in QB layers
        qb_implementations = 0
        cb_implementations = 0
        
        domains_path = self.portfolio_root / "2-DOMAINS-LEVELS"
        
        for domain_code in self.domains:
            domain_name = self._get_domain_name(domain_code)
            domain_path = domains_path / f"{domain_code}-{domain_name}" / "TFA"
            
            # Check QB layer
            qb_impl = domain_path / "QUBITS" / "QB" / "aqua_pro_implementation.py"
            if qb_impl.exists():
                content = qb_impl.read_text(encoding='utf-8')
                if "quantum" in content.lower() or "qaoa" in content.lower() or "vqe" in content.lower():
                    qb_implementations += 1
            
            # Check CB layer
            cb_impl = domain_path / "BITS" / "CB" / "aqua_pro_implementation.py"
            if cb_impl.exists():
                content = cb_impl.read_text(encoding='utf-8')
                if "classical" in content.lower() or "fallback" in content.lower():
                    cb_implementations += 1
        
        if qb_implementations == len(self.domains) and cb_implementations == len(self.domains):
            self.validation_results.append(ValidationResult(
                component="QUANTUM.bridge",
                status="pass",
                message="Quantum-classical bridge implemented in all domains"
            ))
        else:
            self.validation_results.append(ValidationResult(
                component="QUANTUM.bridge",
                status="warning",
                message=f"Partial quantum-classical implementation: QB={qb_implementations}, CB={cb_implementations}"
            ))
    
    async def _validate_federation_layer(self) -> None:
        """Validate federation entanglement layer"""
        logger.info("Validating federation layer...")
        
        # Check for FE implementations
        fe_implementations = 0
        
        domains_path = self.portfolio_root / "2-DOMAINS-LEVELS"
        
        for domain_code in self.domains:
            domain_name = self._get_domain_name(domain_code)
            fe_impl = domains_path / f"{domain_code}-{domain_name}" / "TFA" / "ELEMENTS" / "FE" / "aqua_pro_implementation.py"
            
            if fe_impl.exists():
                content = fe_impl.read_text(encoding='utf-8')
                if "federation" in content.lower() or "entanglement" in content.lower():
                    fe_implementations += 1
        
        if fe_implementations == len(self.domains):
            self.validation_results.append(ValidationResult(
                component="FEDERATION.layer",
                status="pass",
                message="Federation layer implemented in all domains"
            ))
        else:
            self.validation_results.append(ValidationResult(
                component="FEDERATION.layer",
                status="warning",
                message=f"Federation layer implementation: {fe_implementations}/{len(self.domains)} domains"
            ))
    
    def _generate_validation_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        logger.info("Generating validation report...")
        
        # Count results by status
        pass_count = sum(1 for r in self.validation_results if r.status == "pass")
        fail_count = sum(1 for r in self.validation_results if r.status == "fail")
        warning_count = sum(1 for r in self.validation_results if r.status == "warning")
        
        # Group results by component type
        results_by_type = {}
        for result in self.validation_results:
            component_type = result.component.split('.')[0]
            if component_type not in results_by_type:
                results_by_type[component_type] = []
            results_by_type[component_type].append(result)
        
        # Calculate coverage metrics
        total_expected = len(self.domains) * len(self.layers) * 2  # spec + impl per layer
        total_found = sum(1 for r in self.validation_results 
                         if r.component.startswith(('TFA.', 'SPEC.', 'IMPL.')) and r.status == "pass")
        coverage_percentage = (total_found / total_expected) * 100 if total_expected > 0 else 0
        
        report = {
            "validation_summary": {
                "total_checks": len(self.validation_results),
                "passed": pass_count,
                "failed": fail_count,
                "warnings": warning_count,
                "success_rate": (pass_count / len(self.validation_results)) * 100 if self.validation_results else 0
            },
            "coverage_metrics": {
                "total_expected_components": total_expected,
                "implemented_components": total_found,
                "coverage_percentage": coverage_percentage,
                "domains_validated": len(self.domains),
                "layers_per_domain": len(self.layers)
            },
            "results_by_type": {
                component_type: {
                    "total": len(results),
                    "passed": sum(1 for r in results if r.status == "pass"),
                    "failed": sum(1 for r in results if r.status == "fail"),
                    "warnings": sum(1 for r in results if r.status == "warning")
                }
                for component_type, results in results_by_type.items()
            },
            "detailed_results": [
                {
                    "component": r.component,
                    "status": r.status,
                    "message": r.message,
                    "details": r.details
                }
                for r in self.validation_results
            ],
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        # Check for high failure rate
        fail_count = sum(1 for r in self.validation_results if r.status == "fail")
        total_count = len(self.validation_results)
        
        if fail_count / total_count > 0.1:  # More than 10% failures
            recommendations.append("High failure rate detected. Consider reviewing implementation standards and templates.")
        
        # Check for missing implementations
        impl_failures = [r for r in self.validation_results 
                        if r.component.startswith("IMPL.") and r.status == "fail"]
        if impl_failures:
            recommendations.append(f"Missing implementations detected in {len(impl_failures)} components. Consider using code generation tools.")
        
        # Check for schema issues
        schema_failures = [r for r in self.validation_results 
                          if r.component.startswith("SCHEMA.") and r.status == "fail"]
        if schema_failures:
            recommendations.append("Schema validation failures detected. Review API contract specifications.")
        
        return recommendations
    
    def _get_domain_name(self, domain_code: str) -> str:
        """Get full domain name from code"""
        domain_mapping = {
            'AAA': 'AERODYNAMICS-AND-AIRFRAMES-ARCHITECTURES',
            'AAP': 'AIRPORTS-PLATFORMS-AND-HYDROGEN-ENABLERS',
            'CCC': 'COCKPIT-CABIN-AND-CARGO',
            'CQH': 'CRYOGENICS-QUANTUM-AND-H2',
            'DDD': 'DIGITAL-AND-DATA-DEFENSE',
            'EDI': 'ELECTRONICS-DIGITAL-INSTRUMENTS',
            'EEE': 'ECOLOGICAL-EFFICIENT-ELECTRIFICATION',
            'EER': 'ENVIRONMENTAL-EMISSIONS-AND-REMEDIATION',
            'IIF': 'INDUSTRIAL-INFRASTRUCTURE-FACILITIES',
            'IIS': 'INTEGRATED-INTELLIGENCE-SOFTWARE',
            'LCC': 'LINKAGES-CONTROL-AND-COMMUNICATIONS',
            'LIB': 'LOGISTICS-INVENTORY-AND-BLOCKCHAIN',
            'MMM': 'MECHANICS-MATERIALS-AND-MANUFACTURING',
            'OOO': 'OS-ONTOLOGIES-AND-OFFICE-INTERFACES',
            'PPP': 'PROPULSION-AND-FUEL-SYSTEMS'
        }
        return domain_mapping.get(domain_code, domain_code)

# Main entry point
async def main():
    """Main function for running validation"""
    portfolio_root = Path("/home/runner/work/PORTFOLIO/PORTFOLIO")
    validator = AquaProValidator(portfolio_root)
    
    report = await validator.validate_all()
    
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    asyncio.run(main())