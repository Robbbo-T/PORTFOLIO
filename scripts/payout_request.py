#!/usr/bin/env python3
"""
TeknIA Token Payout Request Script

Automates the creation and submission of payout requests for TeknIA token distributions
based on innovation assessments and governance approvals.

Features:
- Multi-signature wallet integration (Gnosis Safe)
- Innovation value calculations
- Governance proposal generation
- Audit trail and transparency
- Integration with UTCS anchoring

Usage:
    python scripts/payout_request.py --innovation-id UTCS-1234 --amount 10000 --recipient 0x123...
    python scripts/payout_request.py --governance-proposal proposal-456 --execute
    python scripts/payout_request.py --batch-file payouts.json
"""

import argparse
import json
import yaml
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv
import os

load_dotenv()

@dataclass
class PayoutRequest:
    """Structure for a TeknIA token payout request"""
    innovation_id: str
    recipient_address: str
    amount: int  # Amount in TEK (will be converted to wei)
    justification: str
    assessment_hash: str
    governance_proposal_id: Optional[str] = None
    multisig_address: Optional[str] = None
    status: str = "pending"
    created_at: str = ""
    approved_at: Optional[str] = None
    executed_at: Optional[str] = None
    transaction_hash: Optional[str] = None
    utcs_anchor_hash: Optional[str] = None

@dataclass(frozen=True)
class GovernanceProposal:
    """Structure for governance proposals"""
    proposal_id: str
    title: str
    description: str
    payout_requests: List[str]  # List of payout request IDs
    total_amount: int
    proposer: str
    voting_start: str
    voting_end: str
    status: str = "draft"
    votes_for: int = 0
    votes_against: int = 0
    votes_abstain: int = 0

class PayoutManager:
    """Manages TeknIA token payout requests and governance"""
    
    def __init__(self, config_file: str = "payout_config.yaml"):
        self.config = self._load_config(config_file)
        self.w3 = self._setup_web3()
        self.requests_dir = Path("governance/payout-requests")
        self.proposals_dir = Path("governance/proposals")
        self.audit_dir = Path("governance/audit-trail")
        
        # Create directories if they don't exist
        for directory in [self.requests_dir, self.proposals_dir, self.audit_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        config_path = Path(config_file)
        if config_path.exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        
        # Default configuration
        return {
            'networks': {
                'testnet': {
                    'rpc_url': 'https://sepolia.infura.io/v3/YOUR-PROJECT-ID',
                    'teknia_token_address': '0x1234567890abcdef1234567890abcdef12345678',
                    'multisig_address': '0xabcdef1234567890abcdef1234567890abcdef12',
                    'chain_id': 11155111
                },
                'mainnet': {
                    'rpc_url': 'https://mainnet.infura.io/v3/YOUR-PROJECT-ID',
                    'teknia_token_address': '0xfedcba0987654321fedcba0987654321fedcba09',
                    'multisig_address': '0x9876543210fedcba9876543210fedcba98765432',
                    'chain_id': 1
                }
            },
            'governance': {
                'voting_period_days': 7,
                'quorum_threshold': 0.25,
                'approval_threshold': 0.6,
                'min_payout_amount': 100,
                'max_payout_amount': 1000000,
                'daily_payout_limit': 50000
            },
            'security': {
                'require_multisig': True,
                'require_governance_approval': True,
                'min_confirmations': 3,
                'audit_trail_required': True
            }
        }
    
    def _setup_web3(self) -> Web3:
        """Setup Web3 connection"""
        network = os.environ.get('TEKNIA_NETWORK', 'testnet')
        rpc_url = self.config['networks'][network]['rpc_url']
        
        # Replace placeholder with actual RPC URL from environment
        if 'YOUR-PROJECT-ID' in rpc_url:
            rpc_url = os.environ.get('WEB3_RPC_URL', 'http://localhost:8545')
        
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        return w3
    
    def create_payout_request(self, innovation_id: str, recipient: str, 
                            amount: int, justification: str, 
                            assessment_hash: str) -> PayoutRequest:
        """Create a new payout request"""
        
        # Validate inputs
        if not Web3.is_address(recipient):
            raise ValueError(f"Invalid recipient address: {recipient}")
        
        if amount < self.config['governance']['min_payout_amount']:
            raise ValueError(f"Amount {amount} below minimum {self.config['governance']['min_payout_amount']}")
        
        if amount > self.config['governance']['max_payout_amount']:
            raise ValueError(f"Amount {amount} exceeds maximum {self.config['governance']['max_payout_amount']}")
        
        # Create request
        request = PayoutRequest(
            innovation_id=innovation_id,
            recipient_address=Web3.to_checksum_address(recipient),
            amount=amount,
            justification=justification,
            assessment_hash=assessment_hash,
            multisig_address=self.config['networks'][os.environ.get('TEKNIA_NETWORK', 'testnet')]['multisig_address'],
            created_at=datetime.now(timezone.utc).isoformat()
        )
        
        # Generate request ID
        request_id = self._generate_request_id(request)
        
        # Save request
        self._save_request(request_id, request)
        
        print(f"✅ Created payout request: {request_id}")
        print(f"   Innovation: {innovation_id}")
        print(f"   Recipient: {recipient}")
        print(f"   Amount: {amount:,} TEK")
        print(f"   Saved to: {self.requests_dir / f'{request_id}.json'}")
        
        return request
    
    def create_governance_proposal(self, request_ids: List[str], 
                                 title: str, description: str) -> GovernanceProposal:
        """Create a governance proposal for multiple payout requests"""
        
        # Load and validate requests
        requests = []
        total_amount = 0
        
        for request_id in request_ids:
            request = self._load_request(request_id)
            if not request:
                raise ValueError(f"Request not found: {request_id}")
            
            if request.status != "pending":
                raise ValueError(f"Request {request_id} is not pending (status: {request.status})")
            
            requests.append(request)
            total_amount += request.amount
        
        # Check daily limit
        if total_amount > self.config['governance']['daily_payout_limit']:
            raise ValueError(f"Total amount {total_amount} exceeds daily limit {self.config['governance']['daily_payout_limit']}")
        
        # Create proposal
        voting_start = datetime.now(timezone.utc)
        voting_end = voting_start.replace(days=voting_start.day + self.config['governance']['voting_period_days'])
        
        proposal = GovernanceProposal(
            proposal_id=self._generate_proposal_id(title, request_ids),
            title=title,
            description=description,
            payout_requests=request_ids,
            total_amount=total_amount,
            proposer=os.environ.get('GOVERNANCE_PROPOSER', 'system'),
            voting_start=voting_start.isoformat(),
            voting_end=voting_end.isoformat()
        )
        
        # Save proposal
        self._save_proposal(proposal)
        
        # Update request statuses
        for request_id in request_ids:
            self._update_request_status(request_id, "under_governance_review", 
                                      governance_proposal_id=proposal.proposal_id)
        
        print(f"✅ Created governance proposal: {proposal.proposal_id}")
        print(f"   Title: {title}")
        print(f"   Requests: {len(request_ids)}")
        print(f"   Total Amount: {total_amount:,} TEK")
        print(f"   Voting Period: {voting_start.date()} to {voting_end.date()}")
        
        return proposal
    
    def execute_approved_proposal(self, proposal_id: str, dry_run: bool = False) -> Dict[str, Any]:
        """Execute an approved governance proposal"""
        
        proposal = self._load_proposal(proposal_id)
        if not proposal:
            raise ValueError(f"Proposal not found: {proposal_id}")
        
        if proposal.status != "approved":
            raise ValueError(f"Proposal {proposal_id} is not approved (status: {proposal.status})")
        
        # Load all requests
        requests = []
        for request_id in proposal.payout_requests:
            request = self._load_request(request_id)
            if request:
                requests.append((request_id, request))
        
        execution_plan = {
            'proposal_id': proposal_id,
            'total_requests': len(requests),
            'total_amount': proposal.total_amount,
            'multisig_address': requests[0][1].multisig_address if requests else None,
            'transactions': [],
            'dry_run': dry_run
        }
        
        if dry_run:
            print(f"🧪 DRY RUN: Executing proposal {proposal_id}")
        else:
            print(f"⚡ Executing approved proposal: {proposal_id}")
        
        # Generate multisig transactions
        for request_id, request in requests:
            tx_data = self._generate_multisig_transaction(request)
            execution_plan['transactions'].append({
                'request_id': request_id,
                'recipient': request.recipient_address,
                'amount': request.amount,
                'transaction_data': tx_data,
                'status': 'planned' if dry_run else 'pending_signatures'
            })
            
            print(f"   📋 {request_id}: {request.amount:,} TEK → {request.recipient_address}")
        
        if not dry_run:
            # Update proposal status
            proposal.status = "executing"
            self._save_proposal(proposal)
            
            # Update request statuses
            for request_id, _ in requests:
                self._update_request_status(request_id, "approved_executing")
        
        # Create audit trail entry
        self._create_audit_entry('proposal_execution', execution_plan)
        
        return execution_plan
    
    def batch_process(self, batch_file: str) -> Dict[str, Any]:
        """Process multiple payout requests from a JSON file"""
        
        with open(batch_file, 'r') as f:
            batch_data = json.load(f)
        
        results = {
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'requests': [],
            'errors': []
        }
        
        for item in batch_data.get('requests', []):
            try:
                request = self.create_payout_request(
                    innovation_id=item['innovation_id'],
                    recipient=item['recipient'],
                    amount=item['amount'],
                    justification=item['justification'],
                    assessment_hash=item['assessment_hash']
                )
                results['requests'].append(request)
                results['successful'] += 1
                
            except Exception as e:
                results['errors'].append({
                    'innovation_id': item.get('innovation_id'),
                    'error': str(e)
                })
                results['failed'] += 1
            
            results['processed'] += 1
        
        # Auto-create governance proposal if requested
        if batch_data.get('auto_governance_proposal') and results['successful'] > 0:
            request_ids = [self._generate_request_id(req) for req in results['requests']]
            proposal = self.create_governance_proposal(
                request_ids=request_ids,
                title=batch_data.get('proposal_title', f"Batch Payout Proposal {datetime.now().strftime('%Y-%m-%d')}"),
                description=batch_data.get('proposal_description', "Automated batch payout proposal")
            )
            results['governance_proposal'] = proposal.proposal_id
        
        return results
    
    def _generate_request_id(self, request: PayoutRequest) -> str:
        """Generate a unique request ID"""
        content = f"{request.innovation_id}{request.recipient_address}{request.amount}{request.created_at}"
        return f"PAYOUT-{hashlib.sha256(content.encode()).hexdigest()[:12].upper()}"
    
    def _generate_proposal_id(self, title: str, request_ids: List[str]) -> str:
        """Generate a unique proposal ID"""
        content = f"{title}{''.join(request_ids)}{datetime.now().isoformat()}"
        return f"PROP-{hashlib.sha256(content.encode()).hexdigest()[:12].upper()}"
    
    def _save_request(self, request_id: str, request: PayoutRequest):
        """Save payout request to file"""
        request_file = self.requests_dir / f"{request_id}.json"
        with open(request_file, 'w') as f:
            json.dump(asdict(request), f, indent=2)
    
    def _load_request(self, request_id: str) -> Optional[PayoutRequest]:
        """Load payout request from file"""
        request_file = self.requests_dir / f"{request_id}.json"
        if not request_file.exists():
            return None
        
        with open(request_file, 'r') as f:
            data = json.load(f)
            return PayoutRequest(**data)
    
    def _save_proposal(self, proposal: GovernanceProposal):
        """Save governance proposal to file"""
        proposal_file = self.proposals_dir / f"{proposal.proposal_id}.json"
        with open(proposal_file, 'w') as f:
            json.dump(asdict(proposal), f, indent=2)
    
    def _load_proposal(self, proposal_id: str) -> Optional[GovernanceProposal]:
        """Load governance proposal from file"""
        proposal_file = self.proposals_dir / f"{proposal_id}.json"
        if not proposal_file.exists():
            return None
        
        with open(proposal_file, 'r') as f:
            data = json.load(f)
            return GovernanceProposal(**data)
    
    def _update_request_status(self, request_id: str, status: str, **kwargs):
        """Update request status and additional fields"""
        request = self._load_request(request_id)
        if request:
            request.status = status
            for key, value in kwargs.items():
                if hasattr(request, key):
                    setattr(request, key, value)
            self._save_request(request_id, request)
    
    def _generate_multisig_transaction(self, request: PayoutRequest) -> Dict[str, Any]:
        """Generate multisig transaction data for Gnosis Safe"""
        
        # This would integrate with actual Gnosis Safe SDK
        # For now, return a structured transaction template
        
        network = os.environ.get('TEKNIA_NETWORK', 'testnet')
        token_address = self.config['networks'][network]['teknia_token_address']
        
        return {
            'to': token_address,
            'value': 0,
            'data': f"0xa9059cbb{request.recipient_address[2:].zfill(64)}{hex(request.amount * 10**18)[2:].zfill(64)}",  # transfer(address,uint256)
            'operation': 0,  # CALL
            'gasPrice': 0,
            'gasLimit': 100000,
            'nonce': None,  # Will be filled by multisig
            'signatures': []
        }
    
    def _create_audit_entry(self, event_type: str, data: Dict[str, Any]):
        """Create audit trail entry"""
        audit_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'event_type': event_type,
            'data': data,
            'hash': hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
        }
        
        audit_file = self.audit_dir / f"{event_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(audit_file, 'w') as f:
            json.dump(audit_entry, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description='TeknIA Token Payout Request Manager')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create payout request
    create_parser = subparsers.add_parser('create', help='Create a new payout request')
    create_parser.add_argument('--innovation-id', required=True, help='Innovation UTCS ID')
    create_parser.add_argument('--recipient', required=True, help='Recipient address')
    create_parser.add_argument('--amount', type=int, required=True, help='Amount in TEK')
    create_parser.add_argument('--justification', required=True, help='Justification for payout')
    create_parser.add_argument('--assessment-hash', required=True, help='Assessment hash')
    
    # Create governance proposal
    proposal_parser = subparsers.add_parser('proposal', help='Create governance proposal')
    proposal_parser.add_argument('--request-ids', nargs='+', required=True, help='Request IDs to include')
    proposal_parser.add_argument('--title', required=True, help='Proposal title')
    proposal_parser.add_argument('--description', required=True, help='Proposal description')
    
    # Execute proposal
    execute_parser = subparsers.add_parser('execute', help='Execute approved proposal')
    execute_parser.add_argument('--proposal-id', required=True, help='Proposal ID to execute')
    execute_parser.add_argument('--dry-run', action='store_true', help='Dry run only')
    
    # Batch process
    batch_parser = subparsers.add_parser('batch', help='Batch process from file')
    batch_parser.add_argument('--file', required=True, help='JSON file with batch requests')
    
    # List commands
    list_parser = subparsers.add_parser('list', help='List requests or proposals')
    list_parser.add_argument('--type', choices=['requests', 'proposals'], default='requests')
    list_parser.add_argument('--status', help='Filter by status')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize manager
    manager = PayoutManager()
    
    try:
        if args.command == 'create':
            manager.create_payout_request(
                innovation_id=args.innovation_id,
                recipient=args.recipient,
                amount=args.amount,
                justification=args.justification,
                assessment_hash=args.assessment_hash
            )
        
        elif args.command == 'proposal':
            manager.create_governance_proposal(
                request_ids=args.request_ids,
                title=args.title,
                description=args.description
            )
        
        elif args.command == 'execute':
            result = manager.execute_approved_proposal(
                proposal_id=args.proposal_id,
                dry_run=args.dry_run
            )
            print(f"📊 Execution Plan:")
            print(json.dumps(result, indent=2))
        
        elif args.command == 'batch':
            result = manager.batch_process(args.file)
            print(f"📊 Batch Processing Results:")
            print(f"   Processed: {result['processed']}")
            print(f"   Successful: {result['successful']}")
            print(f"   Failed: {result['failed']}")
            if result['errors']:
                print("   Errors:")
                for error in result['errors']:
                    print(f"     {error['innovation_id']}: {error['error']}")
        
        elif args.command == 'list':
            # Implementation would list requests/proposals with filtering
            print(f"📋 Listing {args.type}...")
            if args.status:
                print(f"   Filtered by status: {args.status}")
            # TODO: Implement listing functionality
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())