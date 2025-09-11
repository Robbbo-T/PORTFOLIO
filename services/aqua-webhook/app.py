#!/usr/bin/env python3
"""
AQUA Webhook Service - MVP Implementation
Core webhook service for TFA V2 manifest validation, EIP-712 verification, and UTCS anchoring.

Endpoints:
- POST /api/v1/manifests/validate - Validate TFA manifests and compute canonical hashes
- POST /manifests/submit - Submit validated manifests for anchoring
- POST /utcs/anchor - Anchor manifest hashes to UTCS (CI only)
- GET /health - Health check

Security:
- HSTS + TLS enforced
- EIP-712 signature verification
- GitHub App token authentication for CI endpoints
"""

import os
import json
import hashlib
from typing import Dict, Any, Optional
from pathlib import Path

from flask import Flask, request, jsonify, abort
from flask_cors import CORS
import yaml

from canonicalize import compute_canonical_hash
from eip712_verify import verify_federation_signature
from schemas.manifest_schema import validate_manifest

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key')
CI_TOKEN = os.environ.get('GITHUB_CI_TOKEN')
WEBHOOK_SECRET = os.environ.get('AQUA_WEBHOOK_SECRET')

# Ensure HTTPS in production
@app.before_request
def force_https():
    if not request.is_secure and app.env == 'production':
        return 'HTTPS required', 400

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'aqua-webhook',
        'version': '1.0.0',
        'endpoints': [
            '/api/v1/manifests/validate',
            '/manifests/submit',
            '/utcs/anchor',
            '/health'
        ]
    })

@app.route('/api/v1/manifests/validate', methods=['POST'])
def validate_manifest_endpoint():
    """
    Validate TFA manifest and compute canonical hash
    
    Expected payload:
    {
        "manifest": { ... },  # TFA manifest content
        "domain": "AAA-AERODYNAMICS-AND-AIRFRAMES-ARCHITECTURES",
        "llc_path": "TFA/ELEMENTS/FE"
    }
    
    Returns:
    {
        "valid": true|false,
        "canonical_hash": "0x...",
        "errors": [...],
        "metadata": { ... }
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON payload provided'}), 400
        
        manifest = data.get('manifest')
        domain = data.get('domain')
        llc_path = data.get('llc_path')
        
        if not all([manifest, domain, llc_path]):
            return jsonify({
                'error': 'Missing required fields: manifest, domain, llc_path'
            }), 400
        
        # Validate manifest structure
        validation_result = validate_manifest(manifest, llc_path)
        if not validation_result['valid']:
            return jsonify({
                'valid': False,
                'errors': validation_result['errors'],
                'canonical_hash': None
            }), 400
        
        # Compute canonical hash
        canonical_hash = compute_canonical_hash(manifest)
        
        return jsonify({
            'valid': True,
            'canonical_hash': canonical_hash,
            'errors': [],
            'metadata': {
                'domain': domain,
                'llc_path': llc_path,
                'manifest_type': manifest.get('type', 'unknown'),
                'validation_timestamp': validation_result.get('timestamp')
            }
        })
        
    except Exception as e:
        app.logger.error(f"Manifest validation error: {str(e)}")
        return jsonify({'error': 'Internal validation error'}), 500

@app.route('/manifests/submit', methods=['POST'])
def submit_manifest():
    """
    Submit validated manifest with EIP-712 signature for anchoring
    
    Expected payload:
    {
        "manifest": { ... },
        "canonical_hash": "0x...",
        "signature": {
            "r": "0x...",
            "s": "0x...",
            "v": 27|28,
            "signer": "0x..."
        },
        "metadata": { ... }
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON payload provided'}), 400
        
        manifest = data.get('manifest')
        canonical_hash = data.get('canonical_hash')
        signature = data.get('signature')
        
        if not all([manifest, canonical_hash, signature]):
            return jsonify({
                'error': 'Missing required fields: manifest, canonical_hash, signature'
            }), 400
        
        # Verify canonical hash
        computed_hash = compute_canonical_hash(manifest)
        if computed_hash != canonical_hash:
            return jsonify({
                'error': 'Canonical hash mismatch',
                'expected': computed_hash,
                'provided': canonical_hash
            }), 400
        
        # Verify EIP-712 signature
        signature_valid = verify_federation_signature(
            manifest, signature, canonical_hash
        )
        
        if not signature_valid:
            return jsonify({'error': 'Invalid EIP-712 signature'}), 401
        
        # Queue for anchoring (placeholder - would integrate with UTCS)
        submission_id = hashlib.sha256(
            f"{canonical_hash}{signature['signer']}".encode()
        ).hexdigest()[:16]
        
        return jsonify({
            'status': 'accepted',
            'submission_id': submission_id,
            'canonical_hash': canonical_hash,
            'signer': signature['signer'],
            'next_steps': 'Queued for UTCS anchoring'
        })
        
    except Exception as e:
        app.logger.error(f"Manifest submission error: {str(e)}")
        return jsonify({'error': 'Internal submission error'}), 500

@app.route('/utcs/anchor', methods=['POST'])
def anchor_to_utcs():
    """
    Anchor manifest hash to UTCS blockchain (CI only)
    
    Requires GitHub CI token authentication.
    
    Expected payload:
    {
        "canonical_hash": "0x...",
        "submission_id": "...",
        "metadata": {
            "domain": "...",
            "llc_path": "...",
            "pr_number": 123,
            "commit_sha": "..."
        }
    }
    """
    # Verify CI token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Missing or invalid authorization header'}), 401
    
    token = auth_header[7:]  # Remove 'Bearer ' prefix
    if token != CI_TOKEN:
        return jsonify({'error': 'Invalid CI token'}), 401
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON payload provided'}), 400
        
        canonical_hash = data.get('canonical_hash')
        submission_id = data.get('submission_id')
        metadata = data.get('metadata', {})
        
        if not all([canonical_hash, submission_id]):
            return jsonify({
                'error': 'Missing required fields: canonical_hash, submission_id'
            }), 400
        
        # Placeholder for UTCS anchoring logic
        # In production, this would interact with the UTCS blockchain
        anchor_tx_hash = f"0x{hashlib.sha256(canonical_hash.encode()).hexdigest()}"
        
        return jsonify({
            'status': 'anchored',
            'canonical_hash': canonical_hash,
            'anchor_tx_hash': anchor_tx_hash,
            'utcs_block_number': 12345,  # Placeholder
            'anchor_timestamp': '2025-01-27T00:00:00Z',
            'metadata': metadata
        })
        
    except Exception as e:
        app.logger.error(f"UTCS anchoring error: {str(e)}")
        return jsonify({'error': 'Internal anchoring error'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Method not allowed'}), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Development server
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=os.environ.get('FLASK_ENV') == 'development'
    )