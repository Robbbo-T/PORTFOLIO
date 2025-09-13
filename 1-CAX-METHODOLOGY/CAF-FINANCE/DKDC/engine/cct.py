#!/usr/bin/env python3
"""
DKDC Context Capability Token (CCT) Manager
Handles SD-JWT token issuance, verification, and revocation
"""

import json
import jwt
import uuid
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class CCTClaims:
    """CCT token claims structure"""
    iss: str  # Issuer
    sub: str  # Subject (controller)
    aud: str  # Audience (processor)
    iat: int  # Issued at
    exp: int  # Expires at
    jti: str  # JWT ID
    dkdc: Dict  # DKDC-specific claims

class CCTTokenManager:
    """Manager for Context Capability Tokens"""
    
    def __init__(self):
        # In production, use proper key management (HSM, KMS)
        self.signing_key = "dkdc-signing-key-dev-only"
        self.issuer_did = "did:example:consense-engine"
        self.revocation_list = set()
        self.issued_tokens = {}
        
    def issue_token(self, policy_id: str, controller: str, processors: List[str], 
                   purpose: str, scopes: List[str], llc: str = "session") -> Dict:
        """Issue a new CCT token"""
        
        # Generate token ID
        jti = str(uuid.uuid4())
        
        # Calculate expiration based on LLC
        ttl_map = {
            "ephemeral": timedelta(hours=1),
            "session": timedelta(hours=4), 
            "project": timedelta(days=7),
            "portfolio": timedelta(days=30)
        }
        
        ttl = ttl_map.get(llc, timedelta(hours=4))
        
        now = datetime.now()
        exp = now + ttl
        
        # Create DET anchor ID (simplified)
        det_id = f"det:tx:{hashlib.sha256(f'{jti}:{now.isoformat()}'.encode()).hexdigest()[:16]}"
        
        # Build DKDC claims
        dkdc_claims = {
            "cpl_hash": f"sha256-{policy_id.split(':')[-1]}",  # Simplified
            "llc": llc,
            "scopes": scopes,
            "purpose": purpose,
            "redaction_vectors": ["/secrets", "/personal", "/credentials"],
            "dp": {
                "epsilon": 2.0,
                "mechanism": "laplace"
            },
            "export": {
                "internet": False,
                "model_to_model": True,
                "third_party": False
            },
            "det_id": det_id,
            "rev": f"https://dkdc.aqua/revoke/{jti}",
            "utcs_mi": f"EstándarUniversal:DKDC-v0.1-CCT-{jti[:8]}"
        }
        
        # Build JWT payload
        payload = {
            "iss": self.issuer_did,
            "sub": controller,
            "aud": processors[0] if processors else "did:example:processor",
            "iat": int(now.timestamp()),
            "exp": int(exp.timestamp()),
            "jti": jti,
            "dkdc": dkdc_claims
        }
        
        # Sign token (using HS256 for MVP, use RS256/ES256 in production)
        token = jwt.encode(payload, self.signing_key, algorithm="HS256")
        
        # Store token metadata
        self.issued_tokens[jti] = {
            "payload": payload,
            "issued_at": now.isoformat(),
            "expires_at": exp.isoformat(),
            "status": "active"
        }
        
        return {
            "jwt": token,
            "jti": jti,
            "exp_iso": exp.isoformat(),
            "revocation_uri": f"https://dkdc.aqua/revoke/{jti}"
        }
    
    def verify_token(self, token: str) -> Dict:
        """Verify and decode CCT token"""
        try:
            # Decode token without audience validation for MVP
            payload = jwt.decode(token, self.signing_key, algorithms=["HS256"], options={"verify_aud": False})
            
            # Check revocation
            if payload["jti"] in self.revocation_list:
                raise jwt.InvalidTokenError("Token has been revoked")
            
            # Validate DKDC claims
            if "dkdc" not in payload:
                raise jwt.InvalidTokenError("Missing DKDC claims")
            
            dkdc = payload["dkdc"]
            required_dkdc_fields = ["cpl_hash", "llc", "scopes", "purpose", "det_id", "rev"]
            
            for field in required_dkdc_fields:
                if field not in dkdc:
                    raise jwt.InvalidTokenError(f"Missing DKDC field: {field}")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise jwt.InvalidTokenError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise e
    
    def revoke_token(self, token_id: str, reason: str = "user_requested") -> Dict:
        """Revoke a CCT token"""
        
        # Add to revocation list
        self.revocation_list.add(token_id)
        
        # Update token status
        if token_id in self.issued_tokens:
            self.issued_tokens[token_id]["status"] = "revoked"
            self.issued_tokens[token_id]["revoked_at"] = datetime.now().isoformat()
            self.issued_tokens[token_id]["revocation_reason"] = reason
        
        return {
            "revoked": True,
            "token_id": token_id,
            "reason": reason,
            "revoked_at": datetime.now().isoformat()
        }
    
    def get_revocation_list(self) -> Dict:
        """Get Certificate Revocation List (CRL)"""
        revoked_tokens = []
        
        for token_id in self.revocation_list:
            if token_id in self.issued_tokens:
                token_data = self.issued_tokens[token_id]
                revoked_tokens.append({
                    "token_id": token_id,
                    "revoked_at": token_data.get("revoked_at", ""),
                    "reason": token_data.get("revocation_reason", "unknown")
                })
        
        return {
            "version": "1",
            "issuer": self.issuer_did,
            "generated_at": datetime.now().isoformat(),
            "revoked_tokens": revoked_tokens
        }
    
    def cleanup_expired_tokens(self):
        """Clean up expired tokens from memory"""
        current_time = time.time()
        expired = []
        
        for token_id, data in self.issued_tokens.items():
            try:
                exp_time = datetime.fromisoformat(data["expires_at"]).timestamp()
                if current_time > exp_time:
                    expired.append(token_id)
            except:
                # Invalid timestamp, remove
                expired.append(token_id)
        
        for token_id in expired:
            if data["status"] != "revoked":  # Keep revoked tokens for CRL
                del self.issued_tokens[token_id]
                
    def validate_scopes(self, token_claims: Dict, requested_scopes: List[str]) -> bool:
        """Validate if requested scopes are authorized by token"""
        authorized_scopes = token_claims.get("dkdc", {}).get("scopes", [])
        
        for scope in requested_scopes:
            if not self._scope_matches(scope, authorized_scopes):
                return False
        
        return True
    
    def _scope_matches(self, requested: str, authorized: List[str]) -> bool:
        """Check if requested scope matches any authorized scope"""
        for auth_scope in authorized:
            # Exact match
            if requested == auth_scope:
                return True
            
            # Wildcard match (e.g., "read:repo:**/README.md")
            if "*" in auth_scope:
                import fnmatch
                if fnmatch.fnmatch(requested, auth_scope):
                    return True
        
        return False