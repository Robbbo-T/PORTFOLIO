#!/usr/bin/env python3
"""
FCR (Follow-up Chain Rules) Enforcement Script
Implements FCR-1 and FCR-2 automation for post-base changes.
"""

import argparse
import json
import hashlib
import os
import sys
import time
import yaml
from pathlib import Path
from typing import Dict, Any, List, Set


def compute_sha256(file_path: Path) -> str:
    """Compute SHA256 hash of a file."""
    if not file_path.exists():
        return "file_not_found"
    
    with open(file_path, 'rb') as f:
        content = f.read()
    return hashlib.sha256(content).hexdigest()


def get_changed_files() -> List[str]:
    """Get list of changed files from git."""
    import subprocess
    try:
        result = subprocess.run(['git', 'diff', '--name-only', 'HEAD~1'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return [line.strip() for line in result.stdout.split('\n') if line.strip()]
        else:
            # Fallback for initial commit or other cases
            result = subprocess.run(['git', 'ls-files'], 
                                  capture_output=True, text=True)
            return [line.strip() for line in result.stdout.split('\n') if line.strip()]
    except:
        return []


def check_fcr1_triggers(changed_files: List[str]) -> bool:
    """Check if any files trigger FCR-1 (Post-Base changes)."""
    fcr1_triggers = {
        "services/mod-base/model_spec.yaml",
        "services/mod-base/run_mod_base.py",
    }
    
    # Check for data changes
    data_pattern = "services/mod-base/data/"
    qb_pattern = "**/QUBITS/QB/**"
    fwd_pattern = "**/WAVES/FWD/**"
    
    for file_path in changed_files:
        if file_path in fcr1_triggers:
            return True
        if file_path.startswith(data_pattern):
            return True
        if "/QUBITS/QB/" in file_path:
            return True
        if "/WAVES/FWD/" in file_path:
            return True
    
    return False


def check_fcr2_triggers(changed_files: List[str]) -> bool:
    """Check if any files trigger FCR-2 (Stacks)."""
    stack_patterns = [
        "services/mod-base/stack/",
        "services/mod-base/stack/mods/"
    ]
    
    for file_path in changed_files:
        for pattern in stack_patterns:
            if file_path.startswith(pattern):
                return True
    
    return False


def execute_fcr1_actions() -> bool:
    """Execute FCR-1 required actions."""
    print("🔄 Executing FCR-1 actions...")
    
    try:
        # 1. Re-run MOD-BASE
        print("  1. Re-running MOD-BASE...")
        import subprocess
        result = subprocess.run(['make', 'mod-base'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  ✗ MOD-BASE execution failed: {result.stderr}")
            return False
        print("  ✓ MOD-BASE execution completed")
        
        # 2. Update QS proof with metrics hash
        print("  2. Updating QS proof...")
        update_qs_proof()
        print("  ✓ QS proof updated")
        
        # 3. Update change notice
        print("  3. Updating change notice...")
        update_change_notice("FCR-1 automatic update")
        print("  ✓ Change notice updated")
        
        return True
        
    except Exception as e:
        print(f"  ✗ FCR-1 execution failed: {e}")
        return False


def execute_fcr2_actions() -> bool:
    """Execute FCR-2 required actions."""
    print("🔄 Executing FCR-2 actions...")
    
    try:
        # 1. Run apply_stack.py
        print("  1. Running stack composition...")
        import subprocess
        result = subprocess.run(['make', 'mod-stack'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  ✗ Stack composition failed: {result.stderr}")
            return False
        print("  ✓ Stack composition completed")
        
        # 2. Sync QS proof to metrics hash
        print("  2. Syncing QS proof...")
        update_qs_proof()
        print("  ✓ QS proof synced")
        
        return True
        
    except Exception as e:
        print(f"  ✗ FCR-2 execution failed: {e}")
        return False


def update_qs_proof():
    """Update QS proof with current metrics hash."""
    qs_proof_path = Path("02-00-PORTFOLIO-ENTANGLEMENT/portfolio/2-DOMAINS-LEVELS/IIS-INTEGRATED-INTELLIGENCE-AND-SOFTWARE/programs/asi-t-core/conf_base/0001/gata/ata-31-instruments/cax-bridges/mlops/STATES/QS/qs-proof.json")
    metrics_path = Path("services/mod-base/eval/metrics.json")
    
    if not metrics_path.exists():
        return
    
    # Get current metrics hash
    metrics_hash = compute_sha256(metrics_path)
    
    # Update QS proof
    if qs_proof_path.exists():
        with open(qs_proof_path) as f:
            proof = json.load(f)
        
        proof["evidence_chain"]["mod_base_metrics"] = metrics_hash
        proof["utcs_fields"]["decision_record"] = metrics_hash
        proof["timestamp"] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        
        with open(qs_proof_path, 'w') as f:
            json.dump(proof, f, indent=2)


def update_change_notice(reason: str):
    """Update change notice with current hashes."""
    change_notice_path = Path("change_notice.yaml")
    
    # Compute current hashes
    spec_hash = compute_sha256(Path("services/mod-base/model_spec.yaml"))
    data_hash = compute_sha256(Path("services/mod-base/data/sample_flight_plan.csv"))
    metrics_hash = compute_sha256(Path("services/mod-base/eval/metrics.json"))
    evidence_hash = compute_sha256(Path("services/mod-base/qs/evidence.json"))
    
    # Generate new CN ID
    timestamp = time.strftime('%Y%m%d', time.gmtime())
    cn_id = f"CN-{timestamp}-{int(time.time()) % 10000:04d}"
    
    change_notice = {
        "cn_id": cn_id,
        "component": "MOD-BASE",
        "reason": reason,
        "scope": {
            "cb": True,
            "qb": True,
            "ue": False,
            "fe": False,
            "fwd": True,
            "qs": True
        },
        "artifacts": {
            "metrics_path": "services/mod-base/eval/metrics.json",
            "evidence_path": "services/mod-base/qs/evidence.json",
            "spec_path": "services/mod-base/model_spec.yaml",
            "data_path": "services/mod-base/data/sample_flight_plan.csv"
        },
        "hashes": {
            "spec_sha256": spec_hash,
            "data_sha256": data_hash,
            "metrics_sha256": metrics_hash,
            "evidence_sha256": evidence_hash
        },
        "signoff": {
            "operator_id": "fcr-automation",
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        }
    }
    
    with open(change_notice_path, 'w') as f:
        yaml.dump(change_notice, f, default_flow_style=False)


def main():
    parser = argparse.ArgumentParser(description='FCR (Follow-up Chain Rules) Enforcement')
    parser.add_argument('--check-only', action='store_true', help='Only check triggers, do not execute')
    parser.add_argument('--force-fcr1', action='store_true', help='Force FCR-1 execution')
    parser.add_argument('--force-fcr2', action='store_true', help='Force FCR-2 execution')
    
    args = parser.parse_args()
    
    changed_files = get_changed_files()
    print(f"📝 Detected {len(changed_files)} changed files")
    
    fcr1_triggered = check_fcr1_triggers(changed_files) or args.force_fcr1
    fcr2_triggered = check_fcr2_triggers(changed_files) or args.force_fcr2
    
    if args.check_only:
        print(f"🔍 FCR-1 (Post-Base) triggered: {fcr1_triggered}")
        print(f"🔍 FCR-2 (Stacks) triggered: {fcr2_triggered}")
        return 0
    
    success = True
    
    if fcr1_triggered:
        print("⚡ FCR-1 triggered - executing post-base actions...")
        success &= execute_fcr1_actions()
    
    if fcr2_triggered:
        print("⚡ FCR-2 triggered - executing stack actions...")
        success &= execute_fcr2_actions()
    
    if not fcr1_triggered and not fcr2_triggered:
        print("✅ No FCR triggers detected - no actions required")
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())