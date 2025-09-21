#!/usr/bin/env python3
"""
Tests for CQEA Decision Kernel

Validates the core CQEA kernel functionality including:
- Solver registration and execution
- Adversarial wrapping (non-destructive)
- Evidence generation with UTCS provenance
- Performance requirements (MAL-CB SLO compliance)
"""

import pytest
import time
import json
from pathlib import Path
import tempfile
import sys
import os

# Add the module path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '5-ARTIFACTS-IMPLEMENTATION', 'CODE', 'python', 'classical-bits'))

from cqea_kernel import DecisionKernel, RunConfig, create_kernel, milp_solver, heuristic_solver, qaoa_stub


class TestDecisionKernel:
    """Test the core DecisionKernel functionality"""
    
    def test_kernel_initialization(self):
        """Test kernel creates successfully"""
        kernel = DecisionKernel()
        assert kernel.solvers == {}
    
    def test_solver_registration(self):
        """Test solver registration works"""
        kernel = DecisionKernel()
        
        def dummy_solver(model, seed=0):
            return {"status": "OK"}
        
        kernel.register("dummy", dummy_solver)
        assert "dummy" in kernel.solvers
        assert kernel.solvers["dummy"] == dummy_solver
    
    def test_unknown_solver_assertion(self):
        """Test that unknown solver raises assertion error"""
        kernel = DecisionKernel()
        config = RunConfig("test", "model.yaml", "unknown_solver")
        
        with pytest.raises(AssertionError, match="Unknown solver"):
            kernel.run(config, {})
    
    def test_basic_run(self):
        """Test basic kernel run functionality"""
        kernel = DecisionKernel()
        
        def test_solver(model, seed=0):
            return {
                "status": "OPTIMAL",
                "metrics": {"objective": 42.0, "solve_time_ms": 10.0}
            }
        
        kernel.register("test", test_solver)
        config = RunConfig("TEST-001", "test.yaml", "test")
        
        result, evidence = kernel.run(config, {"variables": []})
        
        assert result["status"] == "OPTIMAL"
        assert result["metrics"]["objective"] == 42.0
        assert "canonical_hash" in evidence
        assert evidence["det"]["utcs_fields"]["id"] == "TEST-001"
        assert evidence["det"]["utcs_fields"]["determinism"] is True
    
    def test_adversarial_wrapping(self):
        """Test adversarial wrapping adds robustness scenarios"""
        kernel = DecisionKernel()
        
        def capture_model_solver(model, seed=0):
            # Return the model so we can inspect what was passed
            return {"captured_model": model, "status": "OK"}
        
        kernel.register("capture", capture_model_solver)
        config = RunConfig("TEST-002", "test.yaml", "capture", adversarial_mode=True)
        
        original_model = {"variables": ["x1", "x2"], "constraints": []}
        result, evidence = kernel.run(config, original_model)
        
        captured = result["captured_model"]
        
        # Check adversarial scenarios were added
        assert "scenarios" in captured
        scenarios = captured["scenarios"]
        assert "noise:bounded" in scenarios
        assert "sensor_drift:2sigma" in scenarios
        assert "timing_jitter:50ms" in scenarios
        
        # Check robustness constraints were added
        assert "constraints" in captured
        constraints = captured["constraints"]
        robustness_constraint = next((c for c in constraints if c.get("type") == "robustness"), None)
        assert robustness_constraint is not None
        assert robustness_constraint["tolerance"] == 0.02
        
        # Ensure original model wasn't mutated
        assert original_model == {"variables": ["x1", "x2"], "constraints": []}
    
    def test_adversarial_mode_disabled(self):
        """Test adversarial mode can be disabled"""
        kernel = DecisionKernel()
        
        def capture_model_solver(model, seed=0):
            return {"captured_model": model, "status": "OK"}
        
        kernel.register("capture", capture_model_solver)
        config = RunConfig("TEST-003", "test.yaml", "capture", adversarial_mode=False)
        
        original_model = {"variables": ["x1", "x2"]}
        result, evidence = kernel.run(config, original_model)
        
        captured = result["captured_model"]
        
        # Model should be unchanged when adversarial mode is off
        assert captured == original_model
    
    def test_evidence_generation(self):
        """Test UTCS evidence generation"""
        kernel = DecisionKernel()
        
        def metrics_solver(model, seed=0):
            return {
                "status": "OPTIMAL",
                "metrics": {
                    "objective": 123.45,
                    "solve_time_ms": 45.6,
                    "iterations": 10
                }
            }
        
        kernel.register("metrics", metrics_solver)
        config = RunConfig("UTCS-TEST-001", "utcs_test.yaml", "metrics", seed=12345)
        
        start_time = time.time()
        result, evidence = kernel.run(config, {"test": "model"})
        end_time = time.time()
        
        # Check evidence structure
        assert "canonical_hash" in evidence
        assert "det" in evidence
        
        det = evidence["det"]
        
        # Check UTCS fields
        assert det["utcs_fields"]["id"] == "UTCS-TEST-001"
        assert det["utcs_fields"]["bridge"] == "CB→QB→UE→FE→FWD→QS"
        assert det["utcs_fields"]["determinism"] is True
        
        # Check timing
        assert start_time <= det["utcs_fields"]["ts_start"] <= det["utcs_fields"]["ts_end"] <= end_time
        
        # Check performance metrics
        assert det["performance"]["duration_ms"] > 0
        assert isinstance(det["performance"]["within_slo"], bool)
        
        # Check config preservation
        assert det["config"]["problem_id"] == "UTCS-TEST-001"
        assert det["config"]["solver"] == "metrics"
        assert det["config"]["seed"] == 12345
        
        # Check metrics preservation
        assert det["metrics"]["objective"] == 123.45
        assert det["metrics"]["solve_time_ms"] == 45.6
        
        # Check canonical hash is deterministic
        result2, evidence2 = kernel.run(config, {"test": "model"})
        # Hashes should be different due to different timestamps
        assert evidence["canonical_hash"] != evidence2["canonical_hash"]
    
    def test_performance_slo_compliance(self):
        """Test MAL-CB SLO compliance detection"""
        kernel = DecisionKernel()
        
        def fast_solver(model, seed=0):
            time.sleep(0.05)  # 50ms - well within SLO
            return {"status": "OPTIMAL", "metrics": {}}
        
        def slow_solver(model, seed=0):
            time.sleep(0.35)  # 350ms - exceeds P99 SLO  
            return {"status": "OPTIMAL", "metrics": {}}
        
        kernel.register("fast", fast_solver)
        kernel.register("slow", slow_solver)
        
        # Test fast solver - should be within SLO
        config_fast = RunConfig("PERF-001", "test.yaml", "fast")
        result, evidence = kernel.run(config_fast, {})
        
        assert evidence["det"]["performance"]["within_slo"] is True
        assert evidence["det"]["performance"]["duration_ms"] < 300.0
        
        # Test slow solver - should exceed SLO
        config_slow = RunConfig("PERF-002", "test.yaml", "slow")
        result, evidence = kernel.run(config_slow, {})
        
        assert evidence["det"]["performance"]["within_slo"] is False
        assert evidence["det"]["performance"]["duration_ms"] > 300.0


class TestSolverImplementations:
    """Test the built-in solver implementations"""
    
    def test_milp_solver(self):
        """Test MILP solver implementation"""
        model = {
            "variables": [{"name": "x1"}, {"name": "x2"}, {"name": "x3"}],
            "constraints": [{"type": "linear"}]
        }
        
        result = milp_solver(model, seed=42)
        
        assert result["status"] == "OPTIMAL"
        assert "x" in result
        assert "metrics" in result
        assert result["metrics"]["objective"] > 0
        assert result["metrics"]["solve_time_ms"] > 0
        assert result["metrics"]["gap"] == 0.001
        
        # Test determinism
        result2 = milp_solver(model, seed=42)
        assert result["metrics"]["objective"] == result2["metrics"]["objective"]
        assert result["x"] == result2["x"]
    
    def test_heuristic_solver(self):
        """Test heuristic solver implementation"""
        model = {
            "variables": [{"name": "x1"}, {"name": "x2"}],
            "constraints": []
        }
        
        result = heuristic_solver(model, seed=123)
        
        assert result["status"] == "FEASIBLE"
        assert "x" in result
        assert "metrics" in result
        assert result["metrics"]["generations"] == 50
        assert result["metrics"]["convergence"] == 0.95
        
        # Should be faster than MILP
        assert result["metrics"]["solve_time_ms"] < milp_solver(model)["metrics"]["solve_time_ms"]
    
    def test_qaoa_stub(self):
        """Test QAOA quantum stub implementation"""
        model = {
            "variables": [{"name": "x1"}, {"name": "x2"}, {"name": "x3"}, {"name": "x4"}]
        }
        
        result = qaoa_stub(model, seed=99)
        
        assert result["status"] == "FEASIBLE"
        assert "quantum_params" in result
        assert "beta" in result["quantum_params"]
        assert "gamma" in result["quantum_params"]
        assert result["metrics"]["beta_gamma"] == "prepared"
        assert result["metrics"]["shots"] == 1024
        assert result["metrics"]["quantum_advantage"] == 0.5
        
        # Check QAOA parameters
        p_layers = result["metrics"]["p_layers"]
        assert p_layers == 2  # min(4//2, 3) = 2
        assert len(result["quantum_params"]["beta"]) == p_layers
        assert len(result["quantum_params"]["gamma"]) == p_layers
    
    def test_create_kernel(self):
        """Test the factory function creates properly configured kernel"""
        kernel = create_kernel()
        
        assert "milp" in kernel.solvers
        assert "heuristic" in kernel.solvers  
        assert "qaoa_stub" in kernel.solvers
        
        # Test each solver works
        config = RunConfig("FACTORY-TEST", "test.yaml", "milp")
        result, evidence = kernel.run(config, {"variables": []})
        assert result["status"] == "OPTIMAL"
        
        config.solver = "heuristic"
        result, evidence = kernel.run(config, {"variables": []})
        assert result["status"] == "FEASIBLE"
        
        config.solver = "qaoa_stub"
        result, evidence = kernel.run(config, {"variables": []})
        assert result["status"] == "FEASIBLE"
        assert "quantum_params" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])