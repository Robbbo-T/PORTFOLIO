#!/usr/bin/env python3
"""
Tests for DKDC CCT Token Manager
"""

import unittest
import time
import jwt
import sys
from pathlib import Path

# Add DKDC modules to path
sys.path.append(str(Path(__file__).parent.parent))

from engine.cct import CCTTokenManager

class TestCCTTokenManager(unittest.TestCase):
    """Test CCT token manager functionality"""
    
    def setUp(self):
        self.manager = CCTTokenManager()
    
    def test_issue_token_basic(self):
        """Test basic token issuance"""
        result = self.manager.issue_token(
            policy_id="policy:consense:test123",
            controller="did:example:controller",
            processors=["did:example:processor"],
            purpose="test:purpose",
            scopes=["read:repo:test.md"],
            llc="session"
        )
        
        # Verify response structure
        self.assertIn("jwt", result)
        self.assertIn("jti", result)
        self.assertIn("exp_iso", result)
        self.assertIn("revocation_uri", result)
        
        # Verify token is stored
        jti = result["jti"]
        self.assertIn(jti, self.manager.issued_tokens)
        
        token_data = self.manager.issued_tokens[jti]
        self.assertEqual(token_data["status"], "active")
    
    def test_issue_token_llc_expiry(self):
        """Test LLC-based expiry times"""
        test_cases = [
            ("ephemeral", 3600),    # 1 hour
            ("session", 14400),     # 4 hours  
            ("project", 604800),    # 7 days
            ("portfolio", 2592000)  # 30 days
        ]
        
        for llc, expected_seconds in test_cases:
            result = self.manager.issue_token(
                policy_id="policy:consense:test",
                controller="did:example:test",
                processors=["did:example:processor"],
                purpose="test",
                scopes=[],
                llc=llc
            )
            
            # Decode token to check expiry
            claims = jwt.decode(result["jwt"], self.manager.signing_key, algorithms=["HS256"])
            
            # Allow some tolerance for processing time
            actual_duration = claims["exp"] - claims["iat"]
            self.assertAlmostEqual(actual_duration, expected_seconds, delta=10)
    
    def test_verify_token_valid(self):
        """Test verification of valid token"""
        # Issue token
        result = self.manager.issue_token(
            policy_id="policy:consense:test",
            controller="did:example:controller",
            processors=["did:example:processor"],
            purpose="test",
            scopes=["read:repo:test.md"],
            llc="session"
        )
        
        # Verify token
        claims = self.manager.verify_token(result["jwt"])
        
        # Check standard JWT claims
        self.assertEqual(claims["iss"], self.manager.issuer_did)
        self.assertEqual(claims["sub"], "did:example:controller")
        self.assertEqual(claims["aud"], "did:example:processor")
        
        # Check DKDC claims
        dkdc = claims["dkdc"]
        self.assertEqual(dkdc["llc"], "session")
        self.assertEqual(dkdc["scopes"], ["read:repo:test.md"])
        self.assertEqual(dkdc["purpose"], "test")
        self.assertIn("det_id", dkdc)
        self.assertIn("rev", dkdc)
    
    def test_verify_token_expired(self):
        """Test verification of expired token"""
        # Create expired token manually
        import datetime
        
        past_time = datetime.datetime.now() - datetime.timedelta(hours=2)
        
        payload = {
            "iss": self.manager.issuer_did,
            "sub": "did:example:test",
            "aud": "did:example:processor",
            "iat": int(past_time.timestamp()),
            "exp": int((past_time + datetime.timedelta(hours=1)).timestamp()),  # Expired 1 hour ago
            "jti": "expired-token",
            "dkdc": {
                "cpl_hash": "sha256-test",
                "llc": "session",
                "scopes": [],
                "purpose": "test",
                "det_id": "det:tx:test",
                "rev": "https://example.com/revoke"
            }
        }
        
        expired_token = jwt.encode(payload, self.manager.signing_key, algorithm="HS256")
        
        # Should raise InvalidTokenError
        with self.assertRaises(jwt.InvalidTokenError):
            self.manager.verify_token(expired_token)
    
    def test_verify_token_revoked(self):
        """Test verification of revoked token"""
        # Issue and then revoke token
        result = self.manager.issue_token(
            policy_id="policy:consense:test",
            controller="did:example:test",
            processors=["did:example:processor"],
            purpose="test",
            scopes=[],
            llc="session"
        )
        
        jti = result["jti"]
        
        # Verify it works initially
        self.manager.verify_token(result["jwt"])
        
        # Revoke token
        self.manager.revoke_token(jti, "test_revocation")
        
        # Should now fail verification
        with self.assertRaises(jwt.InvalidTokenError):
            self.manager.verify_token(result["jwt"])
    
    def test_verify_token_missing_dkdc_claims(self):
        """Test verification fails with missing DKDC claims"""
        # Create token without DKDC claims
        payload = {
            "iss": self.manager.issuer_did,
            "sub": "did:example:test",
            "aud": "did:example:processor",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600,
            "jti": "no-dkdc-token"
        }
        
        token = jwt.encode(payload, self.manager.signing_key, algorithm="HS256")
        
        with self.assertRaises(jwt.InvalidTokenError):
            self.manager.verify_token(token)
    
    def test_revoke_token(self):
        """Test token revocation"""
        # Issue token
        result = self.manager.issue_token(
            policy_id="policy:consense:test",
            controller="did:example:test",
            processors=["did:example:processor"],
            purpose="test",
            scopes=[],
            llc="session"
        )
        
        jti = result["jti"]
        
        # Revoke token
        revocation = self.manager.revoke_token(jti, "user_requested")
        
        self.assertTrue(revocation["revoked"])
        self.assertEqual(revocation["token_id"], jti)
        self.assertEqual(revocation["reason"], "user_requested")
        
        # Verify token is in revocation list
        self.assertIn(jti, self.manager.revocation_list)
        
        # Verify token status updated
        token_data = self.manager.issued_tokens[jti]
        self.assertEqual(token_data["status"], "revoked")
        self.assertEqual(token_data["revocation_reason"], "user_requested")
    
    def test_get_revocation_list(self):
        """Test CRL generation"""
        # Issue and revoke some tokens
        tokens = []
        for i in range(3):
            result = self.manager.issue_token(
                policy_id=f"policy:consense:test{i}",
                controller="did:example:test",
                processors=["did:example:processor"],
                purpose="test",
                scopes=[],
                llc="session"
            )
            tokens.append(result)
        
        # Revoke first two tokens
        self.manager.revoke_token(tokens[0]["jti"], "reason1")
        self.manager.revoke_token(tokens[1]["jti"], "reason2")
        
        # Get CRL
        crl = self.manager.get_revocation_list()
        
        self.assertEqual(crl["version"], "1")
        self.assertEqual(crl["issuer"], self.manager.issuer_did)
        self.assertEqual(len(crl["revoked_tokens"]), 2)
        
        # Verify revoked tokens are listed
        revoked_ids = [t["token_id"] for t in crl["revoked_tokens"]]
        self.assertIn(tokens[0]["jti"], revoked_ids)
        self.assertIn(tokens[1]["jti"], revoked_ids)
        self.assertNotIn(tokens[2]["jti"], revoked_ids)
    
    def test_validate_scopes(self):
        """Test scope validation"""
        # Create token claims
        token_claims = {
            "dkdc": {
                "scopes": [
                    "read:repo:test.md",
                    "read:repo:docs/*.md",
                    "write:suggestions:pull-requests"
                ]
            }
        }
        
        # Test exact scope match
        self.assertTrue(
            self.manager.validate_scopes(token_claims, ["read:repo:test.md"])
        )
        
        # Test wildcard scope match
        self.assertTrue(
            self.manager.validate_scopes(token_claims, ["read:repo:docs/README.md"])
        )
        
        # Test multiple scopes
        self.assertTrue(
            self.manager.validate_scopes(token_claims, [
                "read:repo:test.md",
                "write:suggestions:pull-requests"
            ])
        )
        
        # Test unauthorized scope
        self.assertFalse(
            self.manager.validate_scopes(token_claims, ["delete:repo:test.md"])
        )
        
        # Test mixed authorized/unauthorized
        self.assertFalse(
            self.manager.validate_scopes(token_claims, [
                "read:repo:test.md",
                "admin:repo:all"  # Unauthorized
            ])
        )
    
    def test_cleanup_expired_tokens(self):
        """Test cleanup of expired tokens"""
        # Create expired token manually
        import datetime
        
        expired_jti = "expired-token-123"
        past_time = datetime.datetime.now() - datetime.timedelta(hours=2)
        
        self.manager.issued_tokens[expired_jti] = {
            "payload": {},
            "issued_at": past_time.isoformat(),
            "expires_at": (past_time + datetime.timedelta(hours=1)).isoformat(),
            "status": "active"
        }
        
        # Create current token
        current_result = self.manager.issue_token(
            policy_id="policy:consense:current",
            controller="did:example:test",
            processors=["did:example:processor"],
            purpose="test",
            scopes=[],
            llc="session"
        )
        
        current_jti = current_result["jti"]
        
        # Run cleanup
        self.manager.cleanup_expired_tokens()
        
        # Verify expired token removed, current preserved
        self.assertNotIn(expired_jti, self.manager.issued_tokens)
        self.assertIn(current_jti, self.manager.issued_tokens)

if __name__ == "__main__":
    unittest.main()