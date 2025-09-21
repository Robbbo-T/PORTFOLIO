#!/usr/bin/env python3
"""
ASI-T Template Generator
Provides templates for change_notice.yaml and pack.yaml as specified in the ASI-T prompt.
"""

import argparse
import time
import yaml
import sys
from pathlib import Path


def generate_change_notice_template(component="MOD-BASE", reason="spec update"):
    """Generate change_notice.yaml template as specified in ASI-T prompt."""
    timestamp = time.strftime('%Y%m%d', time.gmtime())
    cn_id = f"CN-{timestamp}-0001"
    
    template = {
        "cn_id": cn_id,
        "component": component,
        "reason": reason,
        "scope": {
            "cb": True,
            "qb": False,
            "fwd": False,
            "qs": True
        },
        "artifacts": {
            "metrics_path": "services/mod-base/eval/metrics.json",
            "evidence_path": "services/mod-base/qs/evidence.json"
        },
        "hashes": {
            "spec_sha256": "",
            "data_sha256": "",
            "metrics_sha256": "",
            "evidence_sha256": ""
        }
    }
    
    return template


def generate_pack_template(pack_id="20-aero-cruise-opt@0.1.0"):
    """Generate pack.yaml template for mod-pack."""
    template = {
        "id": pack_id,
        "kind": ["model_overlay"],
        "patches": {
            "model": "patch.model.yaml"
        }
    }
    
    return template


def generate_stack_template(stack_id=None):
    """Generate stack.yaml template as specified in ASI-T prompt."""
    if stack_id is None:
        stack_id = f"STACK-AERO-LITE@{time.strftime('%Y-%m-%d', time.gmtime())}"
    
    template = {
        "stack_id": stack_id,
        "baseline": {
            "model_spec": "services/mod-base/model_spec.yaml",
            "data": "services/mod-base/data/sample_flight_plan.csv"
        },
        "order": [
            "10-structure-lightening",
            "20-aero-cruise-opt"
        ],
        "outputs": {
            "metrics": "services/mod-base/eval/metrics.stack.json",
            "evidence": "services/mod-base/stack/evidence/stack_evidence.json"
        }
    }
    
    return template


def main():
    parser = argparse.ArgumentParser(description='Generate ASI-T templates')
    parser.add_argument('--type', choices=['change_notice', 'pack', 'stack'], 
                       default='change_notice', help='Template type to generate')
    parser.add_argument('--output', type=Path, help='Output file path')
    parser.add_argument('--component', default='MOD-BASE', help='Component for change notice')
    parser.add_argument('--reason', default='spec update', help='Reason for change notice')
    parser.add_argument('--pack-id', default='20-aero-cruise-opt@0.1.0', help='Pack ID for pack template')
    parser.add_argument('--stack-id', help='Stack ID for stack template')
    
    args = parser.parse_args()
    
    if args.type == 'change_notice':
        template = generate_change_notice_template(args.component, args.reason)
    elif args.type == 'pack':
        template = generate_pack_template(args.pack_id)
    elif args.type == 'stack':
        template = generate_stack_template(args.stack_id)
    
    if args.output:
        with open(args.output, 'w') as f:
            yaml.dump(template, f, default_flow_style=False)
        print(f"✅ Template generated: {args.output}")
    else:
        print(yaml.dump(template, default_flow_style=False))
    
    return 0


if __name__ == '__main__':
    sys.exit(main())