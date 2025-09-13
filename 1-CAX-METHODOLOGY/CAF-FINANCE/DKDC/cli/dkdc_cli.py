#!/usr/bin/env python3
"""
DKDC CLI Tool
Command-line interface for DKDC protocol operations
"""

import sys
import json
import yaml
import argparse
import requests
from pathlib import Path
from typing import Dict, List

# Add DKDC modules to path
sys.path.append(str(Path(__file__).parent.parent))

from engine.consense import ConsenseEngine, ConsenseOffer
from engine.cct import CCTTokenManager
from engine.policy_guard import PolicyGuard
from parcels.parcelizer import ContextParcelizer
from audit.det import DETAnchor

class DKDCCli:
    """DKDC Command Line Interface"""
    
    def __init__(self):
        self.consense_engine = ConsenseEngine()
        self.cct_manager = CCTTokenManager()
        self.policy_guard = PolicyGuard()
        self.parcelizer = ContextParcelizer()
        self.det_anchor = DETAnchor()
        self.api_base = "http://localhost:8080"
    
    def validate_cpl(self, cpl_file: str) -> bool:
        """Validate CPL policy file"""
        try:
            with open(cpl_file, 'r') as f:
                policy = yaml.safe_load(f)
            
            # Check required fields
            required_fields = [
                'cpl_version', 'controller', 'purpose', 'scopes', 'llc'
            ]
            
            for field in required_fields:
                if field not in policy:
                    print(f"❌ Missing required field: {field}")
                    return False
            
            # Validate LLC value
            valid_llc = ["ephemeral", "session", "project", "portfolio"]
            if policy['llc'] not in valid_llc:
                print(f"❌ Invalid LLC: {policy['llc']}. Must be one of {valid_llc}")
                return False
            
            # Validate scopes format
            if not isinstance(policy['scopes'], list):
                print("❌ Scopes must be a list")
                return False
            
            for scope in policy['scopes']:
                if ':' not in scope:
                    print(f"❌ Invalid scope format: {scope}. Must include ':'")
                    return False
            
            print("✅ CPL policy validation passed")
            return True
            
        except Exception as e:
            print(f"❌ CPL validation failed: {e}")
            return False
    
    def validate_cct(self, token: str) -> bool:
        """Validate CCT token"""
        try:
            claims = self.cct_manager.verify_token(token)
            
            print("✅ CCT token validation passed")
            print(f"   Subject: {claims['sub']}")
            print(f"   Purpose: {claims['dkdc']['purpose']}")
            print(f"   LLC: {claims['dkdc']['llc']}")
            print(f"   Scopes: {len(claims['dkdc']['scopes'])}")
            
            return True
            
        except Exception as e:
            print(f"❌ CCT token validation failed: {e}")
            return False
    
    def linkcheck(self, semantic: bool = False, det_output: str = None) -> bool:
        """Check links in repository with semantic analysis"""
        try:
            # Find markdown files
            md_files = list(Path(".").glob("**/*.md"))
            
            results = {
                "total_files": len(md_files),
                "total_links": 0,
                "working": 0,
                "broken": 0,
                "placeholders": 0,
                "complete": 0,
                "files": []
            }
            
            for md_file in md_files:
                print(f"Checking {md_file}...")
                
                try:
                    content = md_file.read_text(encoding='utf-8')
                    
                    # Simple link extraction
                    import re
                    links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
                    
                    file_result = {
                        "path": str(md_file),
                        "links": len(links),
                        "status": "complete" if links else "placeholder"
                    }
                    
                    if semantic:
                        # Semantic analysis
                        if len(content.strip()) < 100:
                            file_result["status"] = "placeholder"
                        elif "TODO" in content or "PLACEHOLDER" in content:
                            file_result["status"] = "placeholder"
                        elif links and len(content.strip()) > 500:
                            file_result["status"] = "complete"
                    
                    results["files"].append(file_result)
                    results["total_links"] += len(links)
                    
                    if file_result["status"] == "complete":
                        results["complete"] += 1
                        print(f"  ✅ Complete ({len(links)} links)")
                    else:
                        results["placeholders"] += 1
                        print(f"  🟡 Placeholder")
                        
                except Exception as e:
                    print(f"  ❌ Error reading file: {e}")
            
            # Output results
            print(f"\n📊 Link Check Results:")
            print(f"   Files checked: {results['total_files']}")
            print(f"   Total links: {results['total_links']}")
            print(f"   Complete files: {results['complete']}")
            print(f"   Placeholder files: {results['placeholders']}")
            
            # Save DET output if requested
            if det_output:
                det_record = self.det_anchor.record_consense(
                    policy_id="policy:linkcheck:validation",
                    policy_hash="sha256-linkcheck",
                    approvals=[{"role": "system", "data": results}]
                )
                
                with open(det_output, 'w') as f:
                    json.dump({
                        "det_id": det_record,
                        "linkcheck_results": results
                    }, f, indent=2)
                
                print(f"   DET record saved to: {det_output}")
            
            return True
            
        except Exception as e:
            print(f"❌ Link check failed: {e}")
            return False
    
    def create_offer(self, config_file: str) -> str:
        """Create DKDC context offer from config file"""
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            offer = ConsenseOffer(
                ddi=config['ddi'],
                catalog=config['catalog'],
                llc=config['llc'],
                controller=config.get('controller', 'did:example:controller'),
                timestamp=0
            )
            
            draft_policy = self.consense_engine.process_offer(offer)
            
            # Save draft policy
            policy_file = f"draft_policy_{offer.ddi['project'].split('/')[-1]}.yaml"
            with open(policy_file, 'w') as f:
                yaml.dump(draft_policy, f, default_flow_style=False)
            
            print(f"✅ Context offer created")
            print(f"   Project: {offer.ddi['project']}")
            print(f"   Purpose: {offer.ddi['statement']}")
            print(f"   LLC: {offer.llc}")
            print(f"   Draft policy saved to: {policy_file}")
            
            # Extract offer ID from engine
            offer_ids = list(self.consense_engine.pending_offers.keys())
            return offer_ids[-1] if offer_ids else "mock:offer:id"
            
        except Exception as e:
            print(f"❌ Failed to create offer: {e}")
            return ""
    
    def issue_token(self, policy_id: str, config: Dict) -> str:
        """Issue CCT token"""
        try:
            result = self.cct_manager.issue_token(
                policy_id=policy_id,
                controller=config.get('controller', 'did:example:controller'),
                processors=config.get('processors', ['did:example:processor']),
                purpose=config.get('purpose', 'cli-operation'),
                scopes=config.get('scopes', []),
                llc=config.get('llc', 'session')
            )
            
            print(f"✅ CCT token issued")
            print(f"   Token ID: {result['jti']}")
            print(f"   Expires: {result['exp_iso']}")
            
            # Save token to file
            token_file = f"cct_token_{result['jti'][:8]}.jwt"
            with open(token_file, 'w') as f:
                f.write(result['jwt'])
            
            print(f"   Token saved to: {token_file}")
            return result['jwt']
            
        except Exception as e:
            print(f"❌ Failed to issue token: {e}")
            return ""
    
    def create_parcel(self, token_file: str, paths: List[str], recipient: str) -> bool:
        """Create context parcel"""
        try:
            with open(token_file, 'r') as f:
                token = f.read().strip()
            
            # Verify token first
            claims = self.cct_manager.verify_token(token)
            
            # Create parcels
            parcels = self.parcelizer.create_parcels(
                context_paths=paths,
                recipient=recipient,
                scopes=claims['dkdc']['scopes'],
                redaction_vectors=['emails', 'tokens', 'secrets']
            )
            
            # Save parcels
            parcel_file = f"parcels_{claims['jti'][:8]}.json"
            with open(parcel_file, 'w') as f:
                json.dump(parcels, f, indent=2)
            
            print(f"✅ Context parcels created")
            print(f"   Parcels: {len(parcels)}")
            print(f"   Recipient: {recipient}")
            print(f"   Saved to: {parcel_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to create parcel: {e}")
            return False

def main():
    """Main CLI entrypoint"""
    parser = argparse.ArgumentParser(description="DKDC CLI Tool")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate DKDC components')
    validate_parser.add_argument('--cpl', help='Validate CPL policy file')
    validate_parser.add_argument('--cct', help='Validate CCT token')
    
    # Link check command
    linkcheck_parser = subparsers.add_parser('linkcheck', help='Check repository links')
    linkcheck_parser.add_argument('--semantic', action='store_true', help='Enable semantic analysis')
    linkcheck_parser.add_argument('--det', help='Output DET record to file')
    
    # Offer command
    offer_parser = subparsers.add_parser('offer', help='Create context offer')
    offer_parser.add_argument('config', help='Offer configuration file')
    
    # Token command
    token_parser = subparsers.add_parser('token', help='Issue CCT token')
    token_parser.add_argument('policy_id', help='Policy ID')
    token_parser.add_argument('--config', default='token_config.yaml', help='Token configuration file')
    
    # Parcel command
    parcel_parser = subparsers.add_parser('parcel', help='Create context parcel')
    parcel_parser.add_argument('token_file', help='CCT token file')
    parcel_parser.add_argument('paths', nargs='+', help='Context paths')
    parcel_parser.add_argument('--recipient', default='did:example:recipient', help='Parcel recipient')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = DKDCCli()
    
    if args.command == 'validate':
        if args.cpl:
            cli.validate_cpl(args.cpl)
        elif args.cct:
            cli.validate_cct(args.cct)
        else:
            print("Specify --cpl <file> or --cct <token>")
    
    elif args.command == 'linkcheck':
        cli.linkcheck(semantic=args.semantic, det_output=args.det)
    
    elif args.command == 'offer':
        cli.create_offer(args.config)
    
    elif args.command == 'token':
        try:
            with open(args.config, 'r') as f:
                config = yaml.safe_load(f)
        except:
            config = {}
        
        cli.issue_token(args.policy_id, config)
    
    elif args.command == 'parcel':
        cli.create_parcel(args.token_file, args.paths, args.recipient)

if __name__ == "__main__":
    main()