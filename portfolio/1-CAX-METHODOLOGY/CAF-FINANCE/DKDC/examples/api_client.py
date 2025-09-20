#!/usr/bin/env python3
"""
DKDC API Client Example
Demonstrates how to interact with DKDC API endpoints
"""

import json
import requests
from typing import Dict, List

class DKDCClient:
    """Client for DKDC API"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
    
    def submit_offer(self, ddi: Dict, catalog: List[Dict], llc: str, 
                    controller: str = "did:example:controller") -> Dict:
        """Submit context offer"""
        
        payload = {
            "ddi": ddi,
            "catalog": catalog,
            "llc": llc,
            "controller": controller
        }
        
        response = self.session.post(
            f"{self.base_url}/dkdc/offer",
            json=payload
        )
        
        response.raise_for_status()
        return response.json()
    
    def finalize_consense(self, offer_id: str, approvals: List[Dict], 
                         policy: Dict) -> Dict:
        """Finalize consense with approvals"""
        
        payload = {
            "offer_id": offer_id,
            "approvals": approvals,
            "policy": policy
        }
        
        response = self.session.post(
            f"{self.base_url}/dkdc/consense",
            json=payload
        )
        
        response.raise_for_status()
        return response.json()
    
    def issue_token(self, policy_id: str, controller: str, processors: List[str],
                   purpose: str = "", scopes: List[str] = None, llc: str = "session") -> Dict:
        """Issue CCT token"""
        
        payload = {
            "policy_id": policy_id,
            "controller": controller,
            "processors": processors,
            "purpose": purpose,
            "scopes": scopes or [],
            "llc": llc
        }
        
        response = self.session.post(
            f"{self.base_url}/dkdc/token",
            json=payload
        )
        
        response.raise_for_status()
        return response.json()
    
    def create_parcel(self, cct_token: str, recipient: str, 
                     context_paths: List[str]) -> Dict:
        """Create context parcel"""
        
        payload = {
            "cct_token": cct_token,
            "recipient": recipient,
            "context_paths": context_paths
        }
        
        response = self.session.post(
            f"{self.base_url}/dkdc/context-parcel",
            json=payload
        )
        
        response.raise_for_status()
        return response.json()
    
    def get_audit_trail(self, det_id: str) -> Dict:
        """Get audit trail"""
        
        response = self.session.get(
            f"{self.base_url}/dkdc/audit/{det_id}"
        )
        
        response.raise_for_status()
        return response.json()
    
    def revoke_token(self, token_id: str, reason: str) -> Dict:
        """Revoke token"""
        
        payload = {
            "token_id": token_id,
            "reason": reason
        }
        
        response = self.session.post(
            f"{self.base_url}/dkdc/revoke",
            json=payload
        )
        
        response.raise_for_status()
        return response.json()
    
    def get_revocation_list(self) -> Dict:
        """Get revocation list"""
        
        response = self.session.get(
            f"{self.base_url}/dkdc/crl"
        )
        
        response.raise_for_status()
        return response.json()
    
    def health_check(self) -> Dict:
        """Check API health"""
        
        response = self.session.get(
            f"{self.base_url}/health"
        )
        
        response.raise_for_status()
        return response.json()

def example_api_flow():
    """Complete API flow example"""
    print("=== DKDC API Client Example ===\n")
    
    # Initialize client
    client = DKDCClient()
    
    try:
        # Health check
        print("1. Checking API health...")
        health = client.health_check()
        print(f"   API Status: {health['status']}")
        
        # Submit offer
        print("\n2. Submitting context offer...")
        
        offer_response = client.submit_offer(
            ddi={
                "project": "utcs:proj:AMEDEO/BWB-Q100", 
                "statement": "Co-author BWB-Q100 READMEs and CI rules",
                "outputs": ["prs:readme-normalizer"]
            },
            catalog=[
                {"path": "0-STRATEGY/GOVERNANCE.md", "hash": "sha256-abc123"},
                {"path": "2-DOMAINS-LEVELS/**/README.md"}
            ],
            llc="project",
            controller="did:example:amedeo"
        )
        
        print(f"   Offer ID: {offer_response['offer_id']}")
        print(f"   Status: {offer_response['status']}")
        
        # Finalize consense (mock approvals)
        print("\n3. Finalizing consense...")
        
        approvals = [
            {
                "role": "controller",
                "signer": "did:example:amedeo",
                "timestamp": "2024-01-15T10:00:00Z",
                "signature": "mock_controller_sig"
            }
        ]
        
        consense_response = client.finalize_consense(
            offer_id=offer_response['offer_id'],
            approvals=approvals,
            policy=offer_response['draft_policy']
        )
        
        print(f"   Policy ID: {consense_response.get('policy_id', 'mock:policy')}")
        
        # Issue token
        print("\n4. Issuing CCT token...")
        
        token_response = client.issue_token(
            policy_id=consense_response.get('policy_id', 'mock:policy'),
            controller="did:example:amedeo",
            processors=["did:example:llm.gateway"],
            purpose="coauthor:bwb-q100",
            scopes=["read:repo:0-STRATEGY/GOVERNANCE.md"],
            llc="project"
        )
        
        print(f"   Token ID: {token_response['token_id']}")
        print(f"   Expires: {token_response['expires_at']}")
        
        # Create parcel
        print("\n5. Creating context parcel...")
        
        parcel_response = client.create_parcel(
            cct_token=token_response['cct_token'],
            recipient="did:example:llm.gateway",
            context_paths=["0-STRATEGY/GOVERNANCE.md"]
        )
        
        print(f"   Parcels created: {len(parcel_response['parcels'])}")
        print(f"   DET ID: {parcel_response['det_id']}")
        
        # Get audit trail
        print("\n6. Retrieving audit trail...")
        
        audit_response = client.get_audit_trail(parcel_response['det_id'])
        print(f"   Record found: {audit_response['det_id']}")
        print(f"   Integrity: {audit_response['verification']['integrity_valid']}")
        
        # Revoke token
        print("\n7. Revoking token...")
        
        revoke_response = client.revoke_token(
            token_id=token_response['token_id'],
            reason="example_complete"
        )
        
        print(f"   Revoked: {revoke_response['revoked']}")
        
        # Check CRL
        print("\n8. Checking revocation list...")
        
        crl_response = client.get_revocation_list()
        print(f"   Revoked tokens: {len(crl_response['revoked_tokens'])}")
        
        print("\n=== API Flow Complete ===")
        
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to DKDC API server")
        print("Start the server with: python api/server.py")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    example_api_flow()