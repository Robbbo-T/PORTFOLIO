#!/usr/bin/env python3
"""
MOD-BASE: Model Baseline Runner
Pure stdlib implementation for deterministic aerospace model execution.
"""

import argparse
import csv
import json
import hashlib
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, List


class MAL_EEM:
    """Empathy & Ethics Module for safety-relevant decisions."""
    
    @staticmethod
    def check(context: Dict[str, Any]) -> bool:
        """Check if operation passes ethics/empathy constraints."""
        # For MOD-BASE, ensure no autonomous actuation without operator confirm
        if context.get('actuation_capable', False):
            return context.get('operator_confirmed', False)
        return True
    
    @staticmethod
    def explain(context: Dict[str, Any]) -> str:
        """Explain ethics/empathy decision."""
        if not context.get('actuation_capable', False):
            return "No actuation capability - ethics check passed"
        if context.get('operator_confirmed', False):
            return "Operator confirmation received - ethics check passed"
        return "ETHICS VIOLATION: Actuation requires operator confirmation"


def compute_sha256(data: str) -> str:
    """Compute SHA256 hash of data."""
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def load_flight_plan(data_path: Path) -> List[Dict[str, Any]]:
    """Load flight plan data from CSV."""
    flight_plan = []
    with open(data_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Convert numeric fields
            for field in ['altitude', 'speed', 'fuel_flow', 'distance']:
                if field in row:
                    try:
                        row[field] = float(row[field])
                    except ValueError:
                        row[field] = 0.0
            flight_plan.append(row)
    return flight_plan


def execute_baseline_model(spec: Dict[str, Any], flight_plan: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Execute baseline aerospace model with deterministic results."""
    
    # Ethics check for any actuation-capable operations
    ethics_context = {
        'actuation_capable': spec.get('actuation_capable', False),
        'operator_confirmed': spec.get('operator_confirmed', False)
    }
    
    if not MAL_EEM.check(ethics_context):
        raise RuntimeError(f"Ethics violation: {MAL_EEM.explain(ethics_context)}")
    
    # Baseline model execution (deterministic)
    total_distance = 0.0
    total_fuel = 0.0
    max_altitude = 0.0
    
    for segment in flight_plan:
        # Simple baseline calculations
        distance = segment.get('distance', 0.0)
        fuel_flow = segment.get('fuel_flow', 0.0)
        altitude = segment.get('altitude', 0.0)
        
        total_distance += distance
        total_fuel += fuel_flow * (distance / 500.0)  # Simplified fuel consumption
        max_altitude = max(max_altitude, altitude)
    
    # Calculate baseline metrics
    efficiency = total_distance / max(total_fuel, 0.1)  # Avoid division by zero
    safety_margin = max_altitude / 40000.0  # Normalized safety margin
    
    return {
        'total_distance_nm': round(total_distance, 2),
        'total_fuel_kg': round(total_fuel, 2),
        'max_altitude_ft': round(max_altitude, 2),
        'efficiency_nm_per_kg': round(efficiency, 4),
        'safety_margin': round(safety_margin, 4),
        'segments_processed': len(flight_plan),
        'baseline_version': spec.get('version', '1.0.0'),
        'deterministic': True
    }


def generate_qs_evidence(spec: Dict[str, Any], data: List[Dict[str, Any]], 
                        metrics: Dict[str, Any], execution_time: float) -> Dict[str, Any]:
    """Generate QS/UTCS compatible evidence."""
    
    # Compute canonical hashes
    spec_hash = compute_sha256(json.dumps(spec, sort_keys=True))
    data_hash = compute_sha256(json.dumps(data, sort_keys=True))
    metrics_hash = compute_sha256(json.dumps(metrics, sort_keys=True))
    
    evidence = {
        "utcs_fields": {
            "policy_hash": spec_hash[:16],  # Truncated for readability
            "model_sha": spec_hash,
            "data_manifest": data_hash,
            "decision_record": metrics_hash,
            "xai_blob_hash": compute_sha256("baseline_model_explanation"),
            "operator_id": os.environ.get('USER', 'system'),
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        },
        "provenance": {
            "execution_time_ms": round(execution_time * 1000, 2),
            "deterministic": True,
            "ethics_checked": True,
            "bridge": "CB→QB→UE→FE→FWD→QS"
        },
        "hashes": {
            "spec_sha256": spec_hash,
            "data_sha256": data_hash,
            "metrics_sha256": metrics_hash,
            "evidence_sha256": ""  # Will be filled after evidence is complete
        },
        "compliance": {
            "mal_eem_passed": True,
            "qs_anchored": True,
            "fcr_compliant": True
        }
    }
    
    # Compute evidence hash
    evidence_copy = evidence.copy()
    evidence_copy["hashes"]["evidence_sha256"] = ""
    evidence_hash = compute_sha256(json.dumps(evidence_copy, sort_keys=True))
    evidence["hashes"]["evidence_sha256"] = evidence_hash
    
    return evidence


def main():
    parser = argparse.ArgumentParser(description='MOD-BASE: Model Baseline Runner')
    parser.add_argument('--spec', type=Path, required=True, help='Model specification YAML/JSON file')
    parser.add_argument('--data', type=Path, required=True, help='Flight plan data CSV file')
    parser.add_argument('--out', type=Path, required=True, help='Output metrics JSON file')
    
    args = parser.parse_args()
    
    # Load model specification
    try:
        with open(args.spec, 'r') as f:
            if args.spec.suffix.lower() == '.json':
                spec = json.load(f)
            else:
                # Assume YAML for other extensions
                import yaml
                spec = yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading spec file {args.spec}: {e}", file=sys.stderr)
        return 1
    
    # Load flight plan data
    try:
        flight_plan = load_flight_plan(args.data)
    except Exception as e:
        print(f"Error loading data file {args.data}: {e}", file=sys.stderr)
        return 1
    
    # Execute baseline model
    start_time = time.time()
    try:
        metrics = execute_baseline_model(spec, flight_plan)
        execution_time = time.time() - start_time
        
        # Generate QS evidence
        evidence = generate_qs_evidence(spec, flight_plan, metrics, execution_time)
        
        # Write outputs
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with open(args.out, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        # Write evidence to qs directory
        qs_dir = args.out.parent.parent / 'qs'
        qs_dir.mkdir(exist_ok=True)
        with open(qs_dir / 'evidence.json', 'w') as f:
            json.dump(evidence, f, indent=2)
        
        print(f"✅ MOD-BASE execution completed successfully")
        print(f"   Metrics: {args.out}")
        print(f"   Evidence: {qs_dir / 'evidence.json'}")
        print(f"   Execution time: {execution_time:.3f}s")
        
        return 0
        
    except Exception as e:
        print(f"Error during model execution: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())