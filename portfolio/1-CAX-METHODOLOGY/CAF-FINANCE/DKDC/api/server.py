#!/usr/bin/env python3
"""
DKDC API Server
Consensed Sharing Protocol v0.1

Provides REST endpoints for:
- Context offer submission
- Consense negotiation 
- CCT token issuance
- Context parcel delivery
- Audit and revocation
"""

import json
import yaml
import hashlib
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

from flask import Flask, request, jsonify
from jsonschema import validate, ValidationError

# Import DKDC modules
import sys
sys.path.append(str(Path(__file__).parent.parent))

from engine.consense import ConsenseEngine
from engine.cct import CCTTokenManager
from parcels.parcelizer import ContextParcelizer
from audit.det import DETAnchor

app = Flask(__name__)

# Initialize DKDC components
consense_engine = ConsenseEngine()
cct_manager = CCTTokenManager()
parcelizer = ContextParcelizer()
det_anchor = DETAnchor()

@dataclass
class DKDCOffer:
    """Context sharing offer"""
    ddi: Dict  # Declaration of Development Intent
    catalog: List[Dict]  # Context catalog
    llc: str  # Lifecycle Level Context
    controller: str = ""
    timestamp: float = 0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()

@app.route('/dkdc/offer', methods=['POST'])
def submit_offer():
    """Submit context catalog + DDI for consense"""
    try:
        data = request.json
        
        # Validate required fields
        required = ['ddi', 'catalog', 'llc']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create offer
        offer = DKDCOffer(
            ddi=data['ddi'],
            catalog=data['catalog'],
            llc=data['llc'],
            controller=data.get('controller', 'did:example:controller')
        )
        
        # Process offer through consense engine
        draft_policy = consense_engine.process_offer(offer)
        
        # Generate offer ID
        offer_hash = hashlib.sha256(
            json.dumps(asdict(offer), sort_keys=True).encode()
        ).hexdigest()[:16]
        
        offer_id = f"dkdc:offer:{offer_hash}"
        
        return jsonify({
            'offer_id': offer_id,
            'status': 'pending_consense',
            'draft_policy': draft_policy,
            'expires_at': (datetime.now() + timedelta(hours=1)).isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/dkdc/consense', methods=['POST'])
def finalize_consense():
    """Finalize CPL through multi-party consense"""
    try:
        data = request.json
        
        # Validate required fields  
        required = ['offer_id', 'approvals', 'policy']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Process consense
        result = consense_engine.finalize_consense(
            offer_id=data['offer_id'],
            approvals=data['approvals'],
            policy=data['policy']
        )
        
        if result['status'] == 'approved':
            # Generate policy hash
            policy_hash = hashlib.sha256(
                yaml.dump(data['policy'], sort_keys=True).encode()
            ).hexdigest()
            
            policy_id = f"policy:consense:{policy_hash[:16]}"
            
            # Anchor in DET
            det_id = det_anchor.record_consense(
                policy_id=policy_id,
                policy_hash=policy_hash,
                approvals=data['approvals']
            )
            
            return jsonify({
                'policy_id': policy_id,
                'policy_hash': f"sha256-{policy_hash}",
                'det_id': det_id,
                'status': 'consense_approved',
                'ready_for_token': True
            })
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/dkdc/token', methods=['POST'])
def issue_cct():
    """Issue Context Capability Token (SD-JWT)"""
    try:
        data = request.json
        
        # Validate required fields
        required = ['policy_id', 'controller', 'processors']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Generate CCT
        cct_token = cct_manager.issue_token(
            policy_id=data['policy_id'],
            controller=data['controller'],
            processors=data['processors'],
            purpose=data.get('purpose', ''),
            scopes=data.get('scopes', []),
            llc=data.get('llc', 'session')
        )
        
        return jsonify({
            'cct_token': cct_token['jwt'],
            'token_id': cct_token['jti'],
            'expires_at': cct_token['exp_iso'],
            'revocation_uri': cct_token['revocation_uri']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/dkdc/context-parcel', methods=['POST']) 
def create_parcel():
    """Build and deliver context parcels per scope/recipient"""
    try:
        data = request.json
        
        # Validate required fields
        required = ['cct_token', 'recipient', 'context_paths']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Verify CCT token
        token_claims = cct_manager.verify_token(data['cct_token'])
        
        # Create parcels
        parcels = parcelizer.create_parcels(
            context_paths=data['context_paths'],
            recipient=data['recipient'],
            scopes=token_claims['dkdc']['scopes'],
            redaction_vectors=token_claims['dkdc'].get('redaction_vectors', [])
        )
        
        # Record parcel delivery in DET
        det_id = det_anchor.record_parcel_delivery(
            token_id=token_claims['jti'],
            recipient=data['recipient'],
            parcel_hashes=[p['hash'] for p in parcels]
        )
        
        return jsonify({
            'parcels': parcels,
            'det_id': det_id,
            'delivered_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/dkdc/audit/<det_id>', methods=['GET'])
def get_audit_trail(det_id: str):
    """Retrieve DET entry and proofs"""
    try:
        audit_data = det_anchor.get_audit_trail(det_id)
        return jsonify(audit_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/dkdc/revoke', methods=['POST'])
def revoke_token():
    """Revoke/rotate CCT"""
    try:
        data = request.json
        
        required = ['token_id', 'reason']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Process revocation
        result = cct_manager.revoke_token(
            token_id=data['token_id'],
            reason=data['reason']
        )
        
        # Record in DET
        det_id = det_anchor.record_revocation(
            token_id=data['token_id'],
            reason=data['reason']
        )
        
        return jsonify({
            'revoked': True,
            'det_id': det_id,
            'revoked_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/dkdc/crl', methods=['GET'])
def get_revocation_list():
    """Get certificate revocation list"""
    try:
        crl = cct_manager.get_revocation_list()
        return jsonify(crl)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '0.1.0',
        'protocol': 'DKDC',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)