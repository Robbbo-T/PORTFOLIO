#!/usr/bin/env python3
"""
CQEA Runner - YAML Manifest-Driven Decision Execution

Executes CQEA decision runs from YAML manifests with full traceability.
Supports the three key aerospace use cases:
1. Route-level H₂ energy optimization
2. Avionics partition scheduling  
3. Composite layup/ply-drop optimization
"""

import yaml
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import time

try:
    from .cqea_kernel import DecisionKernel, RunConfig, create_kernel
except ImportError:
    from cqea_kernel import DecisionKernel, RunConfig, create_kernel

logger = logging.getLogger(__name__)

@dataclass
class ManifestConfig:
    """Parsed YAML manifest configuration"""
    id: str
    bridge: str
    model: Dict[str, Any]
    solver: Dict[str, Any]
    resilience: Dict[str, Any]
    assurance: Dict[str, Any]

class CQEARunner:
    """
    CQEA Manifest Runner
    
    Executes decision runs from YAML manifests with complete audit trails.
    Handles model loading, solver selection, and evidence generation.
    """
    
    def __init__(self, kernel: Optional[DecisionKernel] = None):
        self.kernel = kernel or create_kernel()
        self.runs_executed = 0
        logger.info("CQEA Runner initialized")
    
    def load_manifest(self, manifest_path: Path) -> ManifestConfig:
        """Load and validate YAML manifest"""
        try:
            with open(manifest_path, 'r') as f:
                data = yaml.safe_load(f)
            
            manifest = ManifestConfig(
                id=data["id"],
                bridge=data["bridge"],
                model=data["model"],
                solver=data["solver"],
                resilience=data.get("resilience", {"adversarial_mode": True}),
                assurance=data.get("assurance", {"outputs": []})
            )
            
            logger.info(f"Loaded manifest: {manifest.id}")
            return manifest
            
        except Exception as e:
            logger.error(f"Failed to load manifest {manifest_path}: {e}")
            raise
    
    def load_model(self, model_config: Dict[str, Any]) -> Dict[str, Any]:
        """Load problem model from configuration"""
        model_kind = model_config.get("kind", "MILP")
        model_source = model_config.get("source")
        
        # In production, this would load from actual model files
        # For now, create representative models based on kind
        if model_kind == "MILP":
            return self._create_milp_model(model_config)
        elif model_kind == "SCHEDULING":
            return self._create_scheduling_model(model_config)
        elif model_kind == "COMPOSITE":
            return self._create_composite_model(model_config)
        else:
            raise ValueError(f"Unknown model kind: {model_kind}")
    
    def _create_milp_model(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create H₂ energy optimization MILP model"""
        assumptions = config.get("assumptions", [])
        
        return {
            "kind": "H2_ENERGY_OPTIMIZATION",
            "description": "BWB-Q100 route energy optimization with H₂ boil-off",
            "variables": [
                {"name": "fuel_flow", "type": "continuous", "bounds": [0, 1000]},
                {"name": "altitude", "type": "continuous", "bounds": [30000, 45000]},
                {"name": "speed", "type": "continuous", "bounds": [0.7, 0.9]},
                {"name": "tank_pressure", "type": "continuous", "bounds": [1, 350]}
            ],
            "constraints": [
                {
                    "type": "energy_balance",
                    "description": "Total energy = propulsion + boil-off losses",
                    "coefficients": [1, -0.1, 0.5, 0.02]
                },
                {
                    "type": "thermal_limit",
                    "description": "H₂ tank thermal management",
                    "bounds": {"min": -253, "max": -240}
                },
                {
                    "type": "payload_constraint", 
                    "description": "100 passenger payload requirement",
                    "value": 100
                }
            ],
            "objective": {
                "type": "minimize",
                "target": "total_energy_consumption",
                "weights": {"fuel": 0.6, "time": 0.3, "emissions": 0.1}
            },
            "assumptions": assumptions
        }
    
    def _create_scheduling_model(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create avionics partition scheduling model"""
        return {
            "kind": "AVIONICS_SCHEDULING",
            "description": "DAL-A DO-178C partition scheduling with timing bounds",
            "variables": [
                {"name": "partition_1", "type": "integer", "bounds": [0, 100]},
                {"name": "partition_2", "type": "integer", "bounds": [0, 100]},
                {"name": "partition_3", "type": "integer", "bounds": [0, 100]},
                {"name": "hypervisor_overhead", "type": "continuous", "bounds": [1, 10]}
            ],
            "constraints": [
                {
                    "type": "temporal_isolation",
                    "description": "DO-178C temporal isolation requirements",
                    "max_jitter_ms": 2.0
                },
                {
                    "type": "resource_limit",
                    "description": "CPU utilization limit",
                    "bound": 0.85
                },
                {
                    "type": "criticality_separation",
                    "description": "DAL-A separation from lower criticality",
                    "isolation_factor": 100
                }
            ],
            "objective": {
                "type": "minimize",
                "target": "worst_case_latency",
                "deadline_ms": 10.0
            }
        }
    
    def _create_composite_model(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create composite layup optimization model"""
        return {
            "kind": "COMPOSITE_LAYUP",
            "description": "Ply-drop optimization under buckling/fatigue constraints",
            "variables": [
                {"name": "ply_1_angle", "type": "continuous", "bounds": [-90, 90]},
                {"name": "ply_2_angle", "type": "continuous", "bounds": [-90, 90]},
                {"name": "ply_3_angle", "type": "continuous", "bounds": [-90, 90]},
                {"name": "thickness", "type": "continuous", "bounds": [0.1, 10.0]}
            ],
            "constraints": [
                {
                    "type": "buckling_limit",
                    "description": "Critical buckling load safety factor",
                    "safety_factor": 1.5
                },
                {
                    "type": "fatigue_life",
                    "description": "Minimum fatigue life requirement",
                    "cycles": 1000000
                },
                {
                    "type": "manufacturing",
                    "description": "Ply-drop angle constraints",
                    "max_angle_change": 45
                }
            ],
            "objective": {
                "type": "minimize",
                "target": "structural_weight",
                "strength_penalty": 0.1
            }
        }
    
    def execute_run(self, manifest_path: Path) -> Dict[str, Any]:
        """Execute complete CQEA run from manifest"""
        start_time = time.time()
        
        # Load manifest and model
        manifest = self.load_manifest(manifest_path)
        model = self.load_model(manifest.model)
        
        # Create run configuration
        run_config = RunConfig(
            problem_id=manifest.id,
            model_path=str(manifest_path),
            solver=manifest.solver["name"],
            seed=manifest.solver.get("seed", 42),
            adversarial_mode=manifest.resilience.get("adversarial_mode", True)
        )
        
        # Execute decision kernel
        result, evidence = self.kernel.run(run_config, model)
        
        # Generate outputs
        self._generate_outputs(manifest, result, evidence)
        
        self.runs_executed += 1
        execution_time = time.time() - start_time
        
        logger.info(f"CQEA run {manifest.id} completed in {execution_time:.3f}s")
        
        return {
            "manifest_id": manifest.id,
            "result": result,
            "evidence": evidence,
            "execution_time_ms": execution_time * 1000
        }
    
    def _generate_outputs(self, manifest: ManifestConfig, result: Dict[str, Any], evidence: Dict[str, Any]) -> None:
        """Generate assurance outputs as specified in manifest"""
        outputs = manifest.assurance.get("outputs", [])
        
        for output_path in outputs:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            if output_path.endswith(".json"):
                # JSON evidence output
                with open(output_file, 'w') as f:
                    json.dump({
                        "utcs_anchor": evidence,
                        "result": result,
                        "manifest_id": manifest.id
                    }, f, indent=2)
                    
            elif output_path.endswith(".md"):
                # Markdown report output
                self._generate_markdown_report(output_file, manifest, result, evidence)
                
            logger.info(f"Generated output: {output_path}")
    
    def _generate_markdown_report(self, output_file: Path, manifest: ManifestConfig, 
                                 result: Dict[str, Any], evidence: Dict[str, Any]) -> None:
        """Generate markdown assurance report"""
        
        metrics = result.get("metrics", {})
        utcs_fields = evidence["det"]["utcs_fields"]
        
        report = f"""# CQEA Decision Run Report

## Problem Identification
**UTCS ID**: {manifest.id}  
**Bridge Flow**: {manifest.bridge}  
**Execution Time**: {utcs_fields['ts_end'] - utcs_fields['ts_start']:.3f}s  
**Deterministic**: {'✅' if utcs_fields['determinism'] else '❌'}

## Model Configuration
- **Kind**: {manifest.model.get('kind', 'Unknown')}
- **Solver**: {manifest.solver['name']}
- **Adversarial Mode**: {'✅' if manifest.resilience.get('adversarial_mode') else '❌'}

## Results
- **Status**: {result.get('status', 'Unknown')}
- **Objective Value**: {metrics.get('objective', 'N/A')}
- **Solve Time**: {metrics.get('solve_time_ms', 'N/A')}ms
- **Within SLO**: {'✅' if evidence['det']['performance']['within_slo'] else '❌'}

## Evidence
- **Canonical Hash**: `{evidence['canonical_hash']}`
- **UTCS Provenance**: Available in JSON output

## Quantum Readiness
{self._format_quantum_status(result)}

---
*Generated by CQEA Runner at {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}*
"""
        
        with open(output_file, 'w') as f:
            f.write(report)
    
    def _format_quantum_status(self, result: Dict[str, Any]) -> str:
        """Format quantum readiness information"""
        if "quantum_params" in result:
            params = result["quantum_params"]
            return f"""- **Quantum Parameters Prepared**: ✅
- **Circuit Depth**: {params.get('circuit_depth', 'N/A')}
- **Beta/Gamma Parameters**: {len(params.get('beta', []))} layers
- **Quantum Advantage**: {result['metrics'].get('quantum_advantage', 'N/A')}"""
        else:
            return "- **Quantum Parameters**: Not applicable for this solver"


# CLI Interface
def main():
    """CLI entry point for CQEA runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="CQEA Decision Runner")
    parser.add_argument("manifest", type=Path, help="Path to YAML manifest file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    runner = CQEARunner()
    result = runner.execute_run(args.manifest)
    
    print(f"✅ CQEA run completed: {result['manifest_id']}")
    print(f"   Execution time: {result['execution_time_ms']:.1f}ms")
    print(f"   Status: {result['result']['status']}")
    print(f"   Objective: {result['result']['metrics'].get('objective', 'N/A')}")


if __name__ == "__main__":
    main()