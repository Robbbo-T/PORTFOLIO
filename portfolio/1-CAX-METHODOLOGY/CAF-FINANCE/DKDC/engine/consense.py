#!/usr/bin/env python3
"""
DKDC Consense Engine
Handles consent + consensus negotiation for context sharing
"""

import yaml
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class ConsenseOffer:
    """Context sharing offer"""
    ddi: Dict  # Declaration of Development Intent
    catalog: List[Dict]  # Context catalog
    llc: str  # Lifecycle Level Context
    controller: str
    timestamp: float

@dataclass
class ConsensePolicy:
    """Generated consense policy"""
    cpl_version: str = "0.1"
    controller: str = ""
    processors: List[str] = None
    purpose: str = ""
    scopes: List[str] = None
    llc: str = "session"
    retention: Dict = None
    redactions: List[Dict] = None
    export_controls: Dict = None
    privacy: Dict = None
    revocation_uri: str = ""
    auditable: bool = True
    utcs_mi_compliance: bool = True
    
    def __post_init__(self):
        if self.processors is None:
            self.processors = []
        if self.scopes is None:
            self.scopes = []
        if self.redactions is None:
            self.redactions = []
        if self.retention is None:
            self.retention = {"ttl": "PT4H", "revoke_on": ["policy_violation"]}
        if self.export_controls is None:
            self.export_controls = {
                "allow_internet": False,
                "allow_model_to_model": True,
                "allow_third_party": False
            }
        if self.privacy is None:
            self.privacy = {
                "differential_privacy": {"epsilon": 2.0, "mechanism": "laplace"},
                "canaries": ["DKDC-CANARY-%RND%"],
                "watermarks": True
            }

class ConsenseEngine:
    """Engine for processing consense negotiations"""
    
    def __init__(self):
        self.pending_offers = {}
        self.approved_policies = {}
        
    def process_offer(self, offer) -> Dict:
        """Process a context sharing offer and generate draft policy"""
        
        # Extract purpose from DDI
        purpose = offer.ddi.get('statement', 'General development collaboration')
        
        # Generate scopes from catalog
        scopes = []
        for artifact in offer.catalog:
            if 'path' in artifact:
                scopes.append(f"read:repo:{artifact['path']}")
        
        # Add write permissions based on DDI outputs
        if 'outputs' in offer.ddi:
            for output in offer.ddi['outputs']:
                if 'prs' in output or 'pull' in output.lower():
                    scopes.append("write:suggestions:pull-requests")
                if 'ci' in output.lower():
                    scopes.append("write:ci:rules")
        
        # Create draft policy
        draft_policy = ConsensePolicy(
            controller=offer.controller,
            processors=["did:example:llm.gateway"],  # Default processor
            purpose=purpose,
            scopes=scopes,
            llc=offer.llc
        )
        
        # Apply default redactions for security
        draft_policy.redactions = [
            {"path": "**/personal/**"},
            {"path": "**/secrets/**"},
            {"selector": "emails, tokens, credentials, passwords"}
        ]
        
        # Set retention based on LLC
        if offer.llc == "ephemeral":
            draft_policy.retention["ttl"] = "PT1H"  # 1 hour
        elif offer.llc == "session":
            draft_policy.retention["ttl"] = "PT4H"  # 4 hours  
        elif offer.llc == "project":
            draft_policy.retention["ttl"] = "P7D"   # 7 days
        elif offer.llc == "portfolio":
            draft_policy.retention["ttl"] = "P30D"  # 30 days
        
        # Store pending offer
        offer_hash = hashlib.sha256(
            f"{offer.controller}:{offer.timestamp}".encode()
        ).hexdigest()[:16]
        
        offer_id = f"dkdc:offer:{offer_hash}"
        self.pending_offers[offer_id] = {
            'offer': offer,
            'draft_policy': draft_policy,
            'created_at': time.time()
        }
        
        return asdict(draft_policy)
    
    def finalize_consense(self, offer_id: str, approvals: List[Dict], policy: Dict) -> Dict:
        """Finalize consense through multi-party approval"""
        
        if offer_id not in self.pending_offers:
            return {"status": "error", "message": "Offer not found"}
        
        offer_data = self.pending_offers[offer_id]
        
        # Validate approvals
        required_roles = policy.get('approvals', {}).get('required', ['controller'])
        threshold = policy.get('approvals', {}).get('threshold', 1)
        
        approved_roles = []
        for approval in approvals:
            if self._verify_approval_signature(approval):
                approved_roles.append(approval['role'])
        
        # Check if threshold met
        if len(approved_roles) < threshold:
            return {
                "status": "insufficient_approvals",
                "required": threshold,
                "received": len(approved_roles)
            }
        
        # Check required roles
        missing_roles = []
        for role in required_roles:
            if role not in approved_roles:
                missing_roles.append(role)
        
        if missing_roles:
            return {
                "status": "missing_required_roles", 
                "missing": missing_roles
            }
        
        # Approve policy
        policy_hash = hashlib.sha256(
            yaml.dump(policy, sort_keys=True).encode()
        ).hexdigest()
        
        policy_id = f"policy:consense:{policy_hash[:16]}"
        
        self.approved_policies[policy_id] = {
            'policy': policy,
            'approvals': approvals,
            'approved_at': time.time(),
            'hash': policy_hash
        }
        
        # Clean up pending offer
        del self.pending_offers[offer_id]
        
        return {
            "status": "approved",
            "policy_id": policy_id,
            "policy_hash": policy_hash
        }
    
    def _verify_approval_signature(self, approval: Dict) -> bool:
        """Verify approval signature (simplified for MVP)"""
        # In production, verify cryptographic signatures
        required_fields = ['role', 'signer', 'timestamp']
        return all(field in approval for field in required_fields)
    
    def get_policy(self, policy_id: str) -> Optional[Dict]:
        """Retrieve approved policy by ID"""
        return self.approved_policies.get(policy_id)
    
    def cleanup_expired_offers(self):
        """Clean up expired pending offers"""
        current_time = time.time()
        expired = []
        
        for offer_id, data in self.pending_offers.items():
            # Offers expire after 1 hour
            if current_time - data['created_at'] > 3600:
                expired.append(offer_id)
        
        for offer_id in expired:
            del self.pending_offers[offer_id]