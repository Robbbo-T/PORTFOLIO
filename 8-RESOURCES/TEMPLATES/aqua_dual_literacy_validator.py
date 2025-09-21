#!/usr/bin/env python3
"""
AQUA Dual-Literacy Standard (PR+QM) Validator

Validates Prompt-Readiness and Quantum-Mappability of decision artifacts
according to the AQUA Dual-Literacy Standard.

Policy: "No decision artifact enters production unless it is Prompt-Ready and 
Quantum-Mappable—even if executed purely classically—with evidence anchored 
to UTCS and safety rails verified."
"""

import json
import hashlib
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Result of PR or QM validation"""
    status: str  # PASS, FAIL, PENDING
    score: float  # 0.0 to 1.0
    errors: List[str]
    warnings: List[str]
    evidence_hash: str

@dataclass
class DualLiteracyResult:
    """Combined PR+QM validation result"""
    artifact_id: str
    pr_result: ValidationResult
    qm_result: ValidationResult
    gate_status: str  # GATE_PASS, GATE_FAIL, GATE_PENDING
    evidence_bundle_hash: str
    utcs_anchor_id: Optional[str] = None

class PromptReadinessValidator:
    """Validates Prompt-Readiness (PR) criteria"""
    
    def __init__(self, schema_path: Optional[Path] = None):
        self.schema_path = schema_path
        self.required_pr_keys = ["spec_sheet", "golden_set", "adversarial_suite", "utcs_anchor"]
    
    def validate_spec_sheet(self, spec_sheet: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Validate PR-1: Spec Sheet"""
        errors = []
        warnings = []
        
        # Check goal format
        goal = spec_sheet.get("goal", "")
        if not goal:
            errors.append("PR-1: Missing goal specification")
        elif len(goal) < 10:
            errors.append("PR-1: Goal specification too short (minimum 10 characters)")
        elif not re.match(r"^[A-Z].*\.$", goal):
            warnings.append("PR-1: Goal should start with capital letter and end with period")
        
        # Check constraints
        constraints = spec_sheet.get("constraints", [])
        if not constraints:
            errors.append("PR-1: No constraints specified")
        else:
            valid_constraint_types = {"safety", "operational", "compliance", "resource"}
            valid_enforcement = {"hard_limit", "soft_limit", "advisory"}
            
            for i, constraint in enumerate(constraints):
                if not isinstance(constraint, dict):
                    errors.append(f"PR-1: Constraint {i} must be an object")
                    continue
                
                constraint_type = constraint.get("type")
                if constraint_type not in valid_constraint_types:
                    errors.append(f"PR-1: Invalid constraint type '{constraint_type}' at index {i}")
                
                enforcement = constraint.get("enforcement")
                if enforcement not in valid_enforcement:
                    errors.append(f"PR-1: Invalid enforcement '{enforcement}' at index {i}")
        
        # Check tool access
        tool_access = spec_sheet.get("tool_access", {})
        required_tool_keys = {"available_tools", "permissions", "rate_limits"}
        for key in required_tool_keys:
            if key not in tool_access:
                errors.append(f"PR-1: Missing tool_access.{key}")
        
        # Check safety rails
        safety_rails = spec_sheet.get("safety_rails", {})
        required_safety_keys = {"primary_failsafe", "secondary_failsafe", "escalation_path"}
        for key in required_safety_keys:
            if key not in safety_rails:
                errors.append(f"PR-1: Missing safety_rails.{key}")
        
        return errors, warnings
    
    def validate_golden_set(self, golden_set: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Validate PR-2: Golden Set & Eval Metrics"""
        errors = []
        warnings = []
        
        # Check test cases
        test_cases = golden_set.get("test_cases", [])
        if len(test_cases) < 5:
            errors.append("PR-2: Minimum 5 test cases required")
        
        # Check eval metrics
        eval_metrics = golden_set.get("eval_metrics", {})
        if "fidelity" not in eval_metrics:
            errors.append("PR-2: Missing fidelity metrics")
        else:
            fidelity = eval_metrics["fidelity"]
            accuracy_threshold = fidelity.get("accuracy_threshold", 0)
            if accuracy_threshold < 0.8:
                errors.append("PR-2: Accuracy threshold must be >= 0.8")
            
            consistency_threshold = fidelity.get("consistency_threshold", 0)
            if consistency_threshold < 0.9:
                errors.append("PR-2: Consistency threshold must be >= 0.9")
        
        if "harmlessness" not in eval_metrics:
            errors.append("PR-2: Missing harmlessness metrics")
        
        if "determinism" not in eval_metrics:
            errors.append("PR-2: Missing determinism metrics")
        
        return errors, warnings
    
    def validate_adversarial_suite(self, adversarial_suite: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Validate PR-3: Adversarial Suite"""
        errors = []
        warnings = []
        
        required_categories = {"instruction_inversion", "role_hijack", "tool_abuse", "prompt_injection"}
        for category in required_categories:
            tests = adversarial_suite.get(category, [])
            if len(tests) < 3:
                errors.append(f"PR-3: Minimum 3 {category} tests required")
        
        # Check pass criteria
        pass_criteria = adversarial_suite.get("pass_criteria", {})
        max_failure_rate = pass_criteria.get("max_failure_rate", 1.0)
        if max_failure_rate > 0.05:
            errors.append("PR-3: Maximum failure rate must be <= 5%")
        
        return errors, warnings
    
    def validate_utcs_anchor(self, utcs_anchor: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Validate PR-4: UTCS/DET Anchor"""
        errors = []
        warnings = []
        
        required_hashes = {"prompt_hash", "data_snapshot_hash", "eval_results_hash"}
        hash_pattern = re.compile(r"^sha256:[a-f0-9]{64}$")
        
        for hash_key in required_hashes:
            hash_value = utcs_anchor.get(hash_key)
            if not hash_value:
                errors.append(f"PR-4: Missing {hash_key}")
            elif not hash_pattern.match(hash_value):
                errors.append(f"PR-4: Invalid {hash_key} format (must be sha256:...)")
        
        return errors, warnings
    
    def validate(self, pr_data: Dict[str, Any]) -> ValidationResult:
        """Validate complete Prompt-Readiness criteria"""
        all_errors = []
        all_warnings = []
        
        # Check required top-level keys
        for key in self.required_pr_keys:
            if key not in pr_data:
                all_errors.append(f"PR: Missing required section '{key}'")
                continue
        
        # Validate each section
        if "spec_sheet" in pr_data:
            errors, warnings = self.validate_spec_sheet(pr_data["spec_sheet"])
            all_errors.extend(errors)
            all_warnings.extend(warnings)
        
        if "golden_set" in pr_data:
            errors, warnings = self.validate_golden_set(pr_data["golden_set"])
            all_errors.extend(errors)
            all_warnings.extend(warnings)
        
        if "adversarial_suite" in pr_data:
            errors, warnings = self.validate_adversarial_suite(pr_data["adversarial_suite"])
            all_errors.extend(errors)
            all_warnings.extend(warnings)
        
        if "utcs_anchor" in pr_data:
            errors, warnings = self.validate_utcs_anchor(pr_data["utcs_anchor"])
            all_errors.extend(errors)
            all_warnings.extend(warnings)
        
        # Calculate score
        total_checks = 20  # Estimated total validation checks
        error_weight = 1.0
        warning_weight = 0.1
        
        penalty = len(all_errors) * error_weight + len(all_warnings) * warning_weight
        score = max(0.0, 1.0 - (penalty / total_checks))
        
        # Determine status
        if all_errors:
            status = "FAIL"
        elif score >= 0.8:
            status = "PASS"
        else:
            status = "PENDING"
        
        # Generate evidence hash
        evidence_data = {
            "pr_data": pr_data,
            "errors": all_errors,
            "warnings": all_warnings,
            "score": score,
            "timestamp": datetime.utcnow().isoformat()
        }
        evidence_hash = self._generate_hash(evidence_data)
        
        return ValidationResult(
            status=status,
            score=score,
            errors=all_errors,
            warnings=all_warnings,
            evidence_hash=evidence_hash
        )
    
    def _generate_hash(self, data: Any) -> str:
        """Generate SHA-256 hash of data"""
        json_str = json.dumps(data, sort_keys=True, default=str)
        return f"sha256:{hashlib.sha256(json_str.encode()).hexdigest()}"

class QuantumMappabilityValidator:
    """Validates Quantum-Mappability (QM) criteria"""
    
    def __init__(self, schema_path: Optional[Path] = None):
        self.schema_path = schema_path
        self.required_qm_keys = ["canonical_form", "encoding", "performance_budget", "utcs_anchor"]
    
    def validate_canonical_form(self, canonical_form: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Validate QM-1: Canonical Form Declaration"""
        errors = []
        warnings = []
        
        # Check problem type
        valid_problem_types = {"LP", "MILP", "QUBO", "ISING", "MAXCUT", "TSP", "CUSTOM"}
        problem_type = canonical_form.get("problem_type")
        if problem_type not in valid_problem_types:
            errors.append(f"QM-1: Invalid problem_type '{problem_type}'")
        
        # Check derivation notes
        derivation_notes = canonical_form.get("derivation_notes", "")
        if len(derivation_notes) < 50:
            errors.append("QM-1: Derivation notes must be at least 50 characters")
        
        # Check variable mapping
        variable_mapping = canonical_form.get("variable_mapping", {})
        required_mapping_keys = {"classical_vars", "quantum_vars", "mapping_function"}
        for key in required_mapping_keys:
            if key not in variable_mapping:
                errors.append(f"QM-1: Missing variable_mapping.{key}")
        
        return errors, warnings
    
    def validate_encoding(self, encoding: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Validate QM-2: Encoding Choice & Penalty Scaling"""
        errors = []
        warnings = []
        
        # Check rationale
        rationale = encoding.get("rationale", "")
        if len(rationale) < 20:
            errors.append("QM-2: Encoding rationale must be at least 20 characters")
        
        # Check penalty weights
        penalty_weights = encoding.get("penalty_weights", {})
        if not penalty_weights:
            errors.append("QM-2: Penalty weights must be specified")
        else:
            for weight_name, weight_value in penalty_weights.items():
                if not isinstance(weight_value, (int, float)) or weight_value < 0:
                    errors.append(f"QM-2: Invalid penalty weight '{weight_name}': {weight_value}")
        
        # Check unit conversion
        unit_conversion = encoding.get("unit_conversion", {})
        if "method" not in unit_conversion:
            errors.append("QM-2: Unit conversion method must be specified")
        if "validation_tests" not in unit_conversion:
            errors.append("QM-2: Unit conversion validation tests must be specified")
        
        # Check scaling justification
        scaling_justification = encoding.get("scaling_justification", "")
        if len(scaling_justification) < 20:
            errors.append("QM-2: Scaling justification must be at least 20 characters")
        
        return errors, warnings
    
    def validate_performance_budget(self, performance_budget: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Validate QM-3: Noise/Latency Budget"""
        errors = []
        warnings = []
        
        # Check noise tolerance
        noise_tolerance = performance_budget.get("noise_tolerance")
        if noise_tolerance is None:
            errors.append("QM-3: Noise tolerance must be specified")
        elif not (0 <= noise_tolerance <= 0.1):
            errors.append("QM-3: Noise tolerance must be between 0 and 0.1 (10%)")
        
        # Check latency budget
        latency_budget = performance_budget.get("latency_budget")
        if latency_budget is None:
            errors.append("QM-3: Latency budget must be specified")
        elif latency_budget < 1:
            errors.append("QM-3: Latency budget must be at least 1ms")
        
        # Check baseline gap
        baseline_gap = performance_budget.get("baseline_gap")
        if baseline_gap is None:
            errors.append("QM-3: Baseline gap must be specified")
        elif not (-0.5 <= baseline_gap <= 2.0):
            errors.append("QM-3: Baseline gap must be between -0.5 and 2.0")
        
        # Check fallback criteria
        fallback_criteria = performance_budget.get("fallback_criteria")
        if not fallback_criteria:
            errors.append("QM-3: Fallback criteria must be specified")
        
        return errors, warnings
    
    def validate_utcs_anchor(self, utcs_anchor: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Validate QM-4: UTCS/DET Anchor"""
        errors = []
        warnings = []
        
        required_hashes = {"encoding_hash", "results_hash"}
        hash_pattern = re.compile(r"^sha256:[a-f0-9]{64}$")
        
        for hash_key in required_hashes:
            hash_value = utcs_anchor.get(hash_key)
            if not hash_value:
                errors.append(f"QM-4: Missing {hash_key}")
            elif not hash_pattern.match(hash_value):
                errors.append(f"QM-4: Invalid {hash_key} format (must be sha256:...)")
        
        # Check documentation requirements
        if "seed_documentation" not in utcs_anchor:
            errors.append("QM-4: Missing seed documentation")
        if "schedule_documentation" not in utcs_anchor:
            errors.append("QM-4: Missing schedule documentation")
        
        return errors, warnings
    
    def validate(self, qm_data: Dict[str, Any]) -> ValidationResult:
        """Validate complete Quantum-Mappability criteria"""
        all_errors = []
        all_warnings = []
        
        # Check required top-level keys
        for key in self.required_qm_keys:
            if key not in qm_data:
                all_errors.append(f"QM: Missing required section '{key}'")
                continue
        
        # Validate each section
        if "canonical_form" in qm_data:
            errors, warnings = self.validate_canonical_form(qm_data["canonical_form"])
            all_errors.extend(errors)
            all_warnings.extend(warnings)
        
        if "encoding" in qm_data:
            errors, warnings = self.validate_encoding(qm_data["encoding"])
            all_errors.extend(errors)
            all_warnings.extend(warnings)
        
        if "performance_budget" in qm_data:
            errors, warnings = self.validate_performance_budget(qm_data["performance_budget"])
            all_errors.extend(errors)
            all_warnings.extend(warnings)
        
        if "utcs_anchor" in qm_data:
            errors, warnings = self.validate_utcs_anchor(qm_data["utcs_anchor"])
            all_errors.extend(errors)
            all_warnings.extend(warnings)
        
        # Calculate score
        total_checks = 15  # Estimated total validation checks
        error_weight = 1.0
        warning_weight = 0.1
        
        penalty = len(all_errors) * error_weight + len(all_warnings) * warning_weight
        score = max(0.0, 1.0 - (penalty / total_checks))
        
        # Determine status
        if all_errors:
            status = "FAIL"
        elif score >= 0.8:
            status = "DECLARED"  # QM uses DECLARED instead of PASS
        else:
            status = "NOT_APPLICABLE"
        
        # Generate evidence hash
        evidence_data = {
            "qm_data": qm_data,
            "errors": all_errors,
            "warnings": all_warnings,
            "score": score,
            "timestamp": datetime.utcnow().isoformat()
        }
        evidence_hash = self._generate_hash(evidence_data)
        
        return ValidationResult(
            status=status,
            score=score,
            errors=all_errors,
            warnings=all_warnings,
            evidence_hash=evidence_hash
        )
    
    def _generate_hash(self, data: Any) -> str:
        """Generate SHA-256 hash of data"""
        json_str = json.dumps(data, sort_keys=True, default=str)
        return f"sha256:{hashlib.sha256(json_str.encode()).hexdigest()}"

class AquaDualLiteracyValidator:
    """Main AQUA Dual-Literacy Standard validator"""
    
    def __init__(self, schema_path: Optional[Path] = None):
        self.schema_path = schema_path
        self.pr_validator = PromptReadinessValidator(schema_path)
        self.qm_validator = QuantumMappabilityValidator(schema_path)
    
    def validate_gate_policy(self, pr_result: ValidationResult, qm_result: ValidationResult) -> str:
        """Apply CI gate policy: Block merge unless PR:PASS and QM:DECLARED"""
        if pr_result.status != "PASS":
            return "GATE_FAIL"
        
        if qm_result.status not in ["DECLARED", "IMPLEMENTED"]:
            return "GATE_FAIL"
        
        return "GATE_PASS"
    
    def create_evidence_bundle(self, artifact_data: Dict[str, Any], 
                             pr_result: ValidationResult, 
                             qm_result: ValidationResult) -> Dict[str, Any]:
        """Create evidence bundle for UTCS anchoring"""
        evidence_bundle = {
            "artifact_id": artifact_data.get("artifact_id"),
            "timestamp": datetime.utcnow().isoformat(),
            "validation_version": "1.0.0",
            "pr_status": pr_result.status,
            "qm_status": qm_result.status,
            "pr_evidence_hash": pr_result.evidence_hash,
            "qm_evidence_hash": qm_result.evidence_hash,
            "cb_qb_metadata": artifact_data.get("metadata", {}).get("cb_qb_metadata", {}),
            "pr_errors": pr_result.errors,
            "qm_errors": qm_result.errors,
            "pr_warnings": pr_result.warnings,
            "qm_warnings": qm_result.warnings
        }
        return evidence_bundle
    
    def validate(self, artifact_data: Dict[str, Any]) -> DualLiteracyResult:
        """Validate complete AQUA Dual-Literacy Standard"""
        artifact_id = artifact_data.get("artifact_id", "UNKNOWN")
        
        # Validate PR
        pr_data = artifact_data.get("prompt_readiness", {})
        pr_result = self.pr_validator.validate(pr_data)
        
        # Validate QM
        qm_data = artifact_data.get("quantum_mappability", {})
        qm_result = self.qm_validator.validate(qm_data)
        
        # Apply gate policy
        gate_status = self.validate_gate_policy(pr_result, qm_result)
        
        # Create evidence bundle
        evidence_bundle = self.create_evidence_bundle(artifact_data, pr_result, qm_result)
        evidence_bundle_hash = self._generate_hash(evidence_bundle)
        
        # Generate UTCS anchor ID (simulated)
        utcs_anchor_id = f"utcs://anchor/{evidence_bundle_hash.split(':')[1][:16]}"
        
        return DualLiteracyResult(
            artifact_id=artifact_id,
            pr_result=pr_result,
            qm_result=qm_result,
            gate_status=gate_status,
            evidence_bundle_hash=evidence_bundle_hash,
            utcs_anchor_id=utcs_anchor_id
        )
    
    def _generate_hash(self, data: Any) -> str:
        """Generate SHA-256 hash of data"""
        json_str = json.dumps(data, sort_keys=True, default=str)
        return f"sha256:{hashlib.sha256(json_str.encode()).hexdigest()}"

def main():
    """CLI entry point for AQUA Dual-Literacy validation"""
    parser = argparse.ArgumentParser(description="AQUA Dual-Literacy Standard (PR+QM) Validator")
    parser.add_argument("input_file", help="JSON file containing artifact data")
    parser.add_argument("--schema", help="Path to validation schema")
    parser.add_argument("--output", help="Output file for validation results")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--fail-on-warnings", action="store_true", help="Fail on warnings")
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    try:
        # Load input data
        with open(args.input_file, 'r') as f:
            artifact_data = json.load(f)
        
        # Create validator
        schema_path = Path(args.schema) if args.schema else None
        validator = AquaDualLiteracyValidator(schema_path)
        
        # Validate
        result = validator.validate(artifact_data)
        
        # Output results
        output_data = {
            "artifact_id": result.artifact_id,
            "validation_timestamp": datetime.utcnow().isoformat(),
            "pr_status": result.pr_result.status,
            "qm_status": result.qm_result.status,
            "gate_status": result.gate_status,
            "pr_score": result.pr_result.score,
            "qm_score": result.qm_result.score,
            "pr_errors": result.pr_result.errors,
            "qm_errors": result.qm_result.errors,
            "pr_warnings": result.pr_result.warnings,
            "qm_warnings": result.qm_result.warnings,
            "evidence_bundle_hash": result.evidence_bundle_hash,
            "utcs_anchor_id": result.utcs_anchor_id
        }
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(output_data, f, indent=2)
            logger.info(f"Results written to {args.output}")
        else:
            print(json.dumps(output_data, indent=2))
        
        # Log summary
        logger.info(f"Artifact: {result.artifact_id}")
        logger.info(f"PR Status: {result.pr_result.status} (Score: {result.pr_result.score:.2f})")
        logger.info(f"QM Status: {result.qm_result.status} (Score: {result.qm_result.score:.2f})")
        logger.info(f"Gate Status: {result.gate_status}")
        
        # Exit with appropriate code
        if result.gate_status == "GATE_FAIL":
            logger.error("GATE FAILURE: Artifact blocked from production")
            sys.exit(1)
        elif (result.pr_result.warnings or result.qm_result.warnings) and args.fail_on_warnings:
            logger.warning("Warnings detected and --fail-on-warnings specified")
            sys.exit(1)
        else:
            logger.info("Validation completed successfully")
            sys.exit(0)
    
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()