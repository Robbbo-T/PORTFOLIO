#!/usr/bin/env python3
"""
Unit tests for AQUA Dual-Literacy Standard (PR+QM) Validator
"""

import unittest
import json
import tempfile
import os
from pathlib import Path
import sys

# Add the templates directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '8-RESOURCES', 'TEMPLATES'))

from aqua_dual_literacy_validator import (
    PromptReadinessValidator,
    QuantumMappabilityValidator,
    AquaDualLiteracyValidator,
    ValidationResult
)

class TestPromptReadinessValidator(unittest.TestCase):
    """Test cases for Prompt-Readiness validation"""
    
    def setUp(self):
        self.validator = PromptReadinessValidator()
    
    def test_valid_spec_sheet(self):
        """Test validation of a valid spec sheet"""
        spec_sheet = {
            "goal": "Optimize flight path for fuel efficiency while maintaining safety standards.",
            "constraints": [
                {
                    "type": "safety",
                    "description": "Maintain minimum separation from other aircraft",
                    "enforcement": "hard_limit"
                }
            ],
            "tool_access": {
                "available_tools": ["weather_api", "route_planner"],
                "permissions": ["read_weather", "plan_route"],
                "rate_limits": {"weather_api": "100/hour"}
            },
            "safety_rails": {
                "primary_failsafe": "Revert to standard routing",
                "secondary_failsafe": "Human pilot oversight",
                "escalation_path": "Flight dispatcher approval"
            }
        }
        
        errors, warnings = self.validator.validate_spec_sheet(spec_sheet)
        self.assertEqual(len(errors), 0, f"Unexpected errors: {errors}")
    
    def test_invalid_spec_sheet(self):
        """Test validation of an invalid spec sheet"""
        spec_sheet = {
            "goal": "bad",  # Too short
            "constraints": [],  # Empty
            "tool_access": {},  # Missing required fields
            "safety_rails": {}  # Missing required fields
        }
        
        errors, warnings = self.validator.validate_spec_sheet(spec_sheet)
        self.assertGreater(len(errors), 0, "Expected validation errors")
        
        # Check for specific errors
        error_msgs = ' '.join(errors)
        self.assertIn("Goal specification too short", error_msgs)
        self.assertIn("No constraints specified", error_msgs)
    
    def test_golden_set_validation(self):
        """Test golden set validation"""
        # Valid golden set
        valid_golden_set = {
            "inputs": ["input1", "input2"],
            "expected_outputs": ["output1", "output2"],
            "test_cases": [
                {"input": "test", "expected_output": "result", "test_id": "test1"},
                {"input": "test2", "expected_output": "result2", "test_id": "test2"},
                {"input": "test3", "expected_output": "result3", "test_id": "test3"},
                {"input": "test4", "expected_output": "result4", "test_id": "test4"},
                {"input": "test5", "expected_output": "result5", "test_id": "test5"}
            ],
            "eval_metrics": {
                "fidelity": {
                    "accuracy_threshold": 0.9,
                    "consistency_threshold": 0.95
                },
                "harmlessness": {
                    "safety_score_min": 0.98,
                    "ethics_compliance": True
                },
                "determinism": {
                    "variance_threshold": 0.05,
                    "reproducibility_tests": 3
                }
            }
        }
        
        errors, warnings = self.validator.validate_golden_set(valid_golden_set)
        self.assertEqual(len(errors), 0, f"Unexpected errors: {errors}")
        
        # Invalid golden set - insufficient test cases
        invalid_golden_set = {
            "inputs": [],
            "expected_outputs": [],
            "test_cases": [{"input": "test", "expected_output": "result", "test_id": "test1"}],  # Only 1 test case
            "eval_metrics": {}  # Missing required metrics
        }
        
        errors, warnings = self.validator.validate_golden_set(invalid_golden_set)
        self.assertGreater(len(errors), 0, "Expected validation errors")
        
        error_msgs = ' '.join(errors)
        self.assertIn("Minimum 5 test cases required", error_msgs)

class TestQuantumMappabilityValidator(unittest.TestCase):
    """Test cases for Quantum-Mappability validation"""
    
    def setUp(self):
        self.validator = QuantumMappabilityValidator()
    
    def test_valid_canonical_form(self):
        """Test validation of a valid canonical form"""
        canonical_form = {
            "problem_type": "QUBO",
            "derivation_notes": "This is a sufficiently long derivation explaining the mathematical transformation from classical to quantum formulation with proper detail.",
            "variable_mapping": {
                "classical_vars": ["x1", "x2", "x3"],
                "quantum_vars": ["q1", "q2", "q3"],
                "mapping_function": "linear mapping from classical to quantum variables"
            }
        }
        
        errors, warnings = self.validator.validate_canonical_form(canonical_form)
        self.assertEqual(len(errors), 0, f"Unexpected errors: {errors}")
    
    def test_invalid_canonical_form(self):
        """Test validation of an invalid canonical form"""
        canonical_form = {
            "problem_type": "INVALID_TYPE",
            "derivation_notes": "too short",
            "variable_mapping": {}  # Missing required fields
        }
        
        errors, warnings = self.validator.validate_canonical_form(canonical_form)
        self.assertGreater(len(errors), 0, "Expected validation errors")
        
        error_msgs = ' '.join(errors)
        self.assertIn("Invalid problem_type", error_msgs)
        self.assertIn("Derivation notes must be at least 50 characters", error_msgs)
    
    def test_performance_budget_validation(self):
        """Test performance budget validation"""
        # Valid budget
        valid_budget = {
            "noise_tolerance": 0.05,
            "latency_budget": 1000,
            "baseline_gap": 0.1,
            "fallback_criteria": "Revert to classical if quantum fails"
        }
        
        errors, warnings = self.validator.validate_performance_budget(valid_budget)
        self.assertEqual(len(errors), 0, f"Unexpected errors: {errors}")
        
        # Invalid budget
        invalid_budget = {
            "noise_tolerance": 0.5,  # Too high
            "latency_budget": 0.5,   # Too low
            "baseline_gap": 5.0,     # Out of range
            "fallback_criteria": ""  # Empty
        }
        
        errors, warnings = self.validator.validate_performance_budget(invalid_budget)
        self.assertGreater(len(errors), 0, "Expected validation errors")
        
        error_msgs = ' '.join(errors)
        self.assertIn("Noise tolerance must be between 0 and 0.1", error_msgs)
        self.assertIn("Latency budget must be at least 1ms", error_msgs)

class TestAquaDualLiteracyValidator(unittest.TestCase):
    """Test cases for the complete dual-literacy validator"""
    
    def setUp(self):
        self.validator = AquaDualLiteracyValidator()
    
    def test_gate_policy_pass(self):
        """Test gate policy with passing PR and QM"""
        pr_result = ValidationResult("PASS", 1.0, [], [], "hash1")
        qm_result = ValidationResult("DECLARED", 1.0, [], [], "hash2")
        
        gate_status = self.validator.validate_gate_policy(pr_result, qm_result)
        self.assertEqual(gate_status, "GATE_PASS")
    
    def test_gate_policy_fail_pr(self):
        """Test gate policy with failing PR"""
        pr_result = ValidationResult("FAIL", 0.5, ["PR error"], [], "hash1")
        qm_result = ValidationResult("DECLARED", 1.0, [], [], "hash2")
        
        gate_status = self.validator.validate_gate_policy(pr_result, qm_result)
        self.assertEqual(gate_status, "GATE_FAIL")
    
    def test_gate_policy_fail_qm(self):
        """Test gate policy with failing QM"""
        pr_result = ValidationResult("PASS", 1.0, [], [], "hash1")
        qm_result = ValidationResult("FAIL", 0.5, ["QM error"], [], "hash2")
        
        gate_status = self.validator.validate_gate_policy(pr_result, qm_result)
        self.assertEqual(gate_status, "GATE_FAIL")
    
    def test_complete_validation_with_example(self):
        """Test complete validation with the H2 route planning example"""
        # Load the H2 route planning example
        example_path = Path(__file__).parent.parent / "8-RESOURCES" / "TEMPLATES" / "examples" / "h2-route-planning-bwb-q100.json"
        
        if example_path.exists():
            with open(example_path, 'r') as f:
                artifact_data = json.load(f)
            
            result = self.validator.validate(artifact_data)
            
            # Should pass all validations
            self.assertEqual(result.pr_result.status, "PASS", f"PR validation failed: {result.pr_result.errors}")
            self.assertEqual(result.qm_result.status, "DECLARED", f"QM validation failed: {result.qm_result.errors}")
            self.assertEqual(result.gate_status, "GATE_PASS", "Gate should pass for valid artifact")
            self.assertIsNotNone(result.evidence_bundle_hash, "Evidence bundle hash should be generated")
            self.assertIsNotNone(result.utcs_anchor_id, "UTCS anchor ID should be generated")

class TestValidationIntegration(unittest.TestCase):
    """Integration tests for the validation system"""
    
    def test_schema_compliance(self):
        """Test that our examples comply with the JSON schema"""
        # This test would require jsonschema library
        # For now, just check that examples can be loaded
        examples_dir = Path(__file__).parent.parent / "8-RESOURCES" / "TEMPLATES" / "examples"
        
        if examples_dir.exists():
            for example_file in examples_dir.glob("*.json"):
                if example_file.name == "test-failure-case.json":
                    continue  # Skip the intentional failure case
                
                with open(example_file, 'r') as f:
                    try:
                        data = json.load(f)
                        self.assertIn("artifact_id", data, f"Missing artifact_id in {example_file}")
                        self.assertIn("prompt_readiness", data, f"Missing prompt_readiness in {example_file}")
                        self.assertIn("quantum_mappability", data, f"Missing quantum_mappability in {example_file}")
                    except json.JSONDecodeError as e:
                        self.fail(f"Invalid JSON in {example_file}: {e}")

if __name__ == '__main__':
    # Set up test environment
    unittest.main(verbosity=2)