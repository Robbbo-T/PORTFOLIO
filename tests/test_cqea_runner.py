#!/usr/bin/env python3
"""
Tests for CQEA Runner

Validates the YAML manifest-driven execution system including:
- Manifest loading and parsing
- Model generation for different aerospace use cases
- Output generation (JSON evidence, Markdown reports)
- Integration with DecisionKernel
"""

import pytest
import yaml
import json
import tempfile
from pathlib import Path
import sys
import os

# Add the module path

from cqea_runner import CQEARunner, ManifestConfig
from cqea_kernel import create_kernel


class TestCQEARunner:
    """Test the CQEA Runner functionality"""
    
    def test_runner_initialization(self):
        """Test runner creates successfully"""
        runner = CQEARunner()
        assert runner.runs_executed == 0
        assert runner.kernel is not None
    
    def test_runner_with_custom_kernel(self):
        """Test runner with custom kernel"""
        kernel = create_kernel()
        runner = CQEARunner(kernel)
        assert runner.kernel == kernel
    
    def test_load_manifest_success(self):
        """Test successful manifest loading"""
        manifest_data = {
            "id": "TEST-MANIFEST-001",
            "bridge": "CB→QB→UE→FE→FWD→QS",
            "model": {
                "kind": "MILP",
                "source": "test.yaml"
            },
            "solver": {
                "name": "milp",
                "seed": 42
            },
            "resilience": {
                "adversarial_mode": True
            },
            "assurance": {
                "outputs": ["test_output.json"]
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(manifest_data, f)
            manifest_path = Path(f.name)
        
        try:
            runner = CQEARunner()
            manifest = runner.load_manifest(manifest_path)
            
            assert manifest.id == "TEST-MANIFEST-001"
            assert manifest.bridge == "CB→QB→UE→FE→FWD→QS"
            assert manifest.model["kind"] == "MILP"
            assert manifest.solver["name"] == "milp"
            assert manifest.resilience["adversarial_mode"] is True
            assert manifest.assurance["outputs"] == ["test_output.json"]
        finally:
            manifest_path.unlink()
    
    def test_load_manifest_with_defaults(self):
        """Test manifest loading with default values"""
        minimal_manifest = {
            "id": "MINIMAL-001", 
            "bridge": "CB→QB",
            "model": {"kind": "MILP"},
            "solver": {"name": "milp"}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(minimal_manifest, f)
            manifest_path = Path(f.name)
        
        try:
            runner = CQEARunner()
            manifest = runner.load_manifest(manifest_path)
            
            # Should have defaults
            assert manifest.resilience == {"adversarial_mode": True}
            assert manifest.assurance == {"outputs": []}
        finally:
            manifest_path.unlink()
    
    def test_load_manifest_invalid_file(self):
        """Test manifest loading with invalid file"""
        runner = CQEARunner()
        
        # Non-existent file
        with pytest.raises(Exception):
            runner.load_manifest(Path("non_existent.yaml"))
    
    def test_create_milp_model(self):
        """Test H₂ energy optimization MILP model creation"""
        runner = CQEARunner()
        config = {
            "kind": "MILP",
            "assumptions": ["payload=100 pax", "H2 cryo boil-off modeled"]  
        }
        
        model = runner.load_model(config)
        
        assert model["kind"] == "H2_ENERGY_OPTIMIZATION"
        assert "variables" in model
        assert "constraints" in model
        assert "objective" in model
        
        # Check variables
        variables = model["variables"]
        var_names = [v["name"] for v in variables]
        assert "fuel_flow" in var_names
        assert "altitude" in var_names
        assert "speed" in var_names
        assert "tank_pressure" in var_names
        
        # Check constraints
        constraints = model["constraints"]
        constraint_types = [c["type"] for c in constraints]
        assert "energy_balance" in constraint_types
        assert "thermal_limit" in constraint_types
        assert "payload_constraint" in constraint_types
        
        # Check objective
        assert model["objective"]["type"] == "minimize"
        assert model["objective"]["target"] == "total_energy_consumption"
        assert model["assumptions"] == config["assumptions"]
    
    def test_create_scheduling_model(self):
        """Test avionics partition scheduling model creation"""
        runner = CQEARunner()
        config = {"kind": "SCHEDULING"}
        
        model = runner.load_model(config)
        
        assert model["kind"] == "AVIONICS_SCHEDULING"
        assert "variables" in model
        assert "constraints" in model
        
        # Check partition variables
        variables = model["variables"]
        var_names = [v["name"] for v in variables]
        assert "partition_1" in var_names
        assert "partition_2" in var_names
        assert "partition_3" in var_names
        assert "hypervisor_overhead" in var_names
        
        # Check DO-178C constraints
        constraints = model["constraints"]
        constraint_types = [c["type"] for c in constraints]
        assert "temporal_isolation" in constraint_types
        assert "resource_limit" in constraint_types
        assert "criticality_separation" in constraint_types
        
        # Check timing objective
        assert model["objective"]["target"] == "worst_case_latency"
        assert model["objective"]["deadline_ms"] == 10.0
    
    def test_create_composite_model(self):
        """Test composite layup optimization model creation"""
        runner = CQEARunner()
        config = {"kind": "COMPOSITE"}
        
        model = runner.load_model(config)
        
        assert model["kind"] == "COMPOSITE_LAYUP"
        assert "variables" in model
        assert "constraints" in model
        
        # Check ply variables
        variables = model["variables"]
        var_names = [v["name"] for v in variables]
        assert "ply_1_angle" in var_names
        assert "ply_2_angle" in var_names 
        assert "ply_3_angle" in var_names
        assert "thickness" in var_names
        
        # Check structural constraints
        constraints = model["constraints"]
        constraint_types = [c["type"] for c in constraints]
        assert "buckling_limit" in constraint_types
        assert "fatigue_life" in constraint_types
        assert "manufacturing" in constraint_types
        
        # Check weight objective
        assert model["objective"]["target"] == "structural_weight"
    
    def test_unknown_model_kind(self):
        """Test error handling for unknown model kind"""
        runner = CQEARunner()
        config = {"kind": "UNKNOWN_MODEL"}
        
        with pytest.raises(ValueError, match="Unknown model kind"):
            runner.load_model(config)


class TestCQEARunnerExecution:
    """Test end-to-end CQEA runner execution"""
    
    def test_complete_execution(self):
        """Test complete manifest execution"""
        manifest_data = {
            "id": "INTEGRATION-TEST-001",
            "bridge": "CB→QB→UE→FE→FWD→QS",
            "model": {
                "kind": "MILP",
                "assumptions": ["test_mode=true"]
            },
            "solver": {
                "name": "milp",
                "seed": 42
            },
            "resilience": {
                "adversarial_mode": True,
                "tests": ["noise_test", "timing_test"]
            },
            "assurance": {
                "outputs": []  # No file outputs for this test
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(manifest_data, f)
            manifest_path = Path(f.name)
        
        try:
            runner = CQEARunner()
            result = runner.execute_run(manifest_path)
            
            # Check result structure
            assert result["manifest_id"] == "INTEGRATION-TEST-001"
            assert "result" in result
            assert "evidence" in result
            assert "execution_time_ms" in result
            
            # Check solver result
            solver_result = result["result"]
            assert solver_result["status"] == "OPTIMAL"
            assert "metrics" in solver_result
            
            # Check evidence
            evidence = result["evidence"]
            assert "canonical_hash" in evidence
            assert evidence["det"]["utcs_fields"]["id"] == "INTEGRATION-TEST-001"
            
            # Check runner state
            assert runner.runs_executed == 1
            
        finally:
            manifest_path.unlink()
    
    def test_output_generation(self):
        """Test JSON and Markdown output generation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            manifest_data = {
                "id": "OUTPUT-TEST-001",
                "bridge": "CB→QB→UE→FE→FWD→QS",
                "model": {"kind": "MILP"},
                "solver": {"name": "heuristic", "seed": 123},
                "resilience": {"adversarial_mode": False},
                "assurance": {
                    "outputs": [
                        str(temp_path / "evidence.json"),
                        str(temp_path / "report.md")
                    ]
                }
            }
            
            manifest_file = temp_path / "manifest.yaml"
            with open(manifest_file, 'w') as f:
                yaml.dump(manifest_data, f)
            
            runner = CQEARunner()
            result = runner.execute_run(manifest_file)
            
            # Check JSON output
            json_file = temp_path / "evidence.json"
            assert json_file.exists()
            
            with open(json_file, 'r') as f:
                json_data = json.load(f)
            
            assert "utcs_anchor" in json_data
            assert "result" in json_data
            assert json_data["manifest_id"] == "OUTPUT-TEST-001"
            
            # Check Markdown output
            md_file = temp_path / "report.md"
            assert md_file.exists()
            
            with open(md_file, 'r') as f:
                md_content = f.read()
            
            assert "# CQEA Decision Run Report" in md_content
            assert "OUTPUT-TEST-001" in md_content
            assert "OPTIMAL" in md_content or "FEASIBLE" in md_content
            assert "Generated by CQEA Runner" in md_content
    
    def test_quantum_report_formatting(self):
        """Test quantum-specific report formatting"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            manifest_data = {
                "id": "QUANTUM-TEST-001",
                "bridge": "CB→QB→UE→FE→FWD→QS",
                "model": {"kind": "COMPOSITE"},
                "solver": {"name": "qaoa_stub", "seed": 99},
                "resilience": {"adversarial_mode": True},
                "assurance": {
                    "outputs": [str(temp_path / "quantum_report.md")]
                }
            }
            
            manifest_file = temp_path / "manifest.yaml"
            with open(manifest_file, 'w') as f:
                yaml.dump(manifest_data, f)
            
            runner = CQEARunner()
            result = runner.execute_run(manifest_file)
            
            # Check quantum parameters in report
            md_file = temp_path / "quantum_report.md"
            with open(md_file, 'r') as f:
                md_content = f.read()
            
            assert "Quantum Parameters Prepared" in md_content
            assert "Circuit Depth" in md_content
            assert "Beta/Gamma Parameters" in md_content
            assert "Quantum Advantage" in md_content


class TestManifestExamples:
    """Test the example manifest files work correctly"""
    
    @pytest.fixture
    def manifests_dir(self):
        """Get the manifests directory path (configurable via CQEA_MANIFESTS_DIR env var)"""
        env_path = os.environ.get("CQEA_MANIFESTS_DIR")
        if env_path:
            return Path(env_path)
        return Path(__file__).parent.parent / "5-ARTIFACTS-IMPLEMENTATION" / "CODE" / "python" / "classical-bits" / "manifests"
    def test_h2_energy_manifest(self, manifests_dir):
        """Test H₂ energy optimization manifest execution"""
        manifest_path = manifests_dir / "h2_energy_opt.yaml"
        
        if not manifest_path.exists():
            pytest.skip("H₂ energy manifest not found")
        
        runner = CQEARunner()
        
        # Just test loading and basic validation
        manifest = runner.load_manifest(manifest_path)
        assert manifest.id.startswith("AAA:AMP-BWB-Q100")
        assert manifest.solver["name"] == "milp"
        
        # Test model creation
        model = runner.load_model(manifest.model)
        assert model["kind"] == "H2_ENERGY_OPTIMIZATION"
    
    def test_avionics_manifest(self, manifests_dir):
        """Test avionics scheduling manifest execution"""
        manifest_path = manifests_dir / "avionics_scheduling.yaml"
        
        if not manifest_path.exists():
            pytest.skip("Avionics manifest not found")
        
        runner = CQEARunner()
        
        manifest = runner.load_manifest(manifest_path)
        assert manifest.id.startswith("LCC:AVIONICS")
        assert manifest.solver["name"] == "heuristic"
        
        model = runner.load_model(manifest.model)
        assert model["kind"] == "AVIONICS_SCHEDULING"
    
    def test_composite_manifest(self, manifests_dir):
        """Test composite layup manifest execution"""
        manifest_path = manifests_dir / "composite_layup.yaml"
        
        if not manifest_path.exists():
            pytest.skip("Composite manifest not found")
        
        runner = CQEARunner()
        
        manifest = runner.load_manifest(manifest_path)
        assert manifest.id.startswith("MMM:COMPOSITE")
        assert manifest.solver["name"] == "qaoa_stub"
        
        model = runner.load_model(manifest.model)
        assert model["kind"] == "COMPOSITE_LAYUP"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])