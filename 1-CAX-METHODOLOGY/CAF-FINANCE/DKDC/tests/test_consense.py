#!/usr/bin/env python3
"""
Tests for DKDC Consense Engine
"""

import unittest
import sys
from pathlib import Path

# Add DKDC modules to path
sys.path.append(str(Path(__file__).parent.parent))

from engine.consense import ConsenseEngine, ConsenseOffer

class TestConsenseEngine(unittest.TestCase):
    """Test consense engine functionality"""
    
    def setUp(self):
        self.engine = ConsenseEngine()
    
    def test_process_offer_basic(self):
        """Test basic offer processing"""
        offer = ConsenseOffer(
            ddi={
                "project": "utcs:proj:TEST/DEMO",
                "statement": "Test collaboration",
                "outputs": ["prs:test"]
            },
            catalog=[
                {"path": "test.md", "hash": "sha256-abc123"}
            ],
            llc="session",
            controller="did:example:test",
            timestamp=1234567890
        )
        
        draft_policy = self.engine.process_offer(offer)
        
        # Verify draft policy structure
        self.assertEqual(draft_policy["controller"], "did:example:test")
        self.assertEqual(draft_policy["llc"], "session")
        self.assertIn("read:repo:test.md", draft_policy["scopes"])
        self.assertIn("write:suggestions:pull-requests", draft_policy["scopes"])
        
        # Verify security defaults
        redaction_paths = [r.get("path", "") for r in draft_policy["redactions"] or []]
        redaction_selectors = [r.get("selector", "") for r in draft_policy["redactions"] or []]
        
        # Check that we have path-based and selector-based redactions
        path_redactions = [p for p in redaction_paths if p]
        selector_redactions = [s for s in redaction_selectors if s]
        
        self.assertTrue(len(path_redactions) > 0 or len(selector_redactions) > 0, "Should have redactions")
        
        # Check for common security patterns
        all_redaction_text = " ".join(redaction_paths + redaction_selectors)
        self.assertTrue("secret" in all_redaction_text or "personal" in all_redaction_text, 
                       "Should include security redactions")
    
    def test_llc_retention_mapping(self):
        """Test LLC to retention time mapping"""
        test_cases = [
            ("ephemeral", "PT1H"),
            ("session", "PT4H"),
            ("project", "P7D"),
            ("portfolio", "P30D")
        ]
        
        for llc, expected_ttl in test_cases:
            offer = ConsenseOffer(
                ddi={"statement": "test"},
                catalog=[{"path": "test.md"}],
                llc=llc,
                controller="did:example:test",
                timestamp=1234567890
            )
            
            draft_policy = self.engine.process_offer(offer)
            self.assertEqual(draft_policy["retention"]["ttl"], expected_ttl)
    
    def test_finalize_consense_success(self):
        """Test successful consense finalization"""
        # First process an offer
        offer = ConsenseOffer(
            ddi={"statement": "test"},
            catalog=[{"path": "test.md"}],
            llc="session",
            controller="did:example:test",
            timestamp=1234567890
        )
        
        draft_policy = self.engine.process_offer(offer)
        
        # Extract offer ID from pending offers
        offer_id = list(self.engine.pending_offers.keys())[0]
        
        # Create valid approvals
        approvals = [
            {
                "role": "controller",
                "signer": "did:example:test",
                "timestamp": "2024-01-15T10:00:00Z",
                "signature": "mock_signature"
            }
        ]
        
        # Update policy to have proper approval structure
        policy = draft_policy.copy()
        policy["approvals"] = {
            "required": ["controller"],
            "threshold": 1
        }
        
        result = self.engine.finalize_consense(offer_id, approvals, policy)
        
        self.assertEqual(result["status"], "approved")
        self.assertIn("policy_id", result)
        self.assertIn("policy_hash", result)
        
        # Verify offer was cleaned up
        self.assertNotIn(offer_id, self.engine.pending_offers)
        
        # Verify policy was stored
        policy_id = result["policy_id"]
        self.assertIn(policy_id, self.engine.approved_policies)
    
    def test_finalize_consense_insufficient_approvals(self):
        """Test consense with insufficient approvals"""
        # Process offer first
        offer = ConsenseOffer(
            ddi={"statement": "test"},
            catalog=[{"path": "test.md"}],
            llc="session", 
            controller="did:example:test",
            timestamp=1234567890
        )
        
        self.engine.process_offer(offer)
        offer_id = list(self.engine.pending_offers.keys())[0]
        
        # Create policy requiring 2 approvals
        policy = {
            "approvals": {
                "required": ["controller", "steward"],
                "threshold": 2
            }
        }
        
        # Provide only 1 approval
        approvals = [
            {
                "role": "controller",
                "signer": "did:example:test", 
                "timestamp": "2024-01-15T10:00:00Z",
                "signature": "mock_signature"
            }
        ]
        
        result = self.engine.finalize_consense(offer_id, approvals, policy)
        
        self.assertEqual(result["status"], "insufficient_approvals")
        self.assertEqual(result["required"], 2)
        self.assertEqual(result["received"], 1)
    
    def test_finalize_consense_missing_required_role(self):
        """Test consense with missing required role"""
        # Process offer first
        offer = ConsenseOffer(
            ddi={"statement": "test"},
            catalog=[{"path": "test.md"}],
            llc="session",
            controller="did:example:test", 
            timestamp=1234567890
        )
        
        self.engine.process_offer(offer)
        offer_id = list(self.engine.pending_offers.keys())[0]
        
        # Create policy requiring steward role
        policy = {
            "approvals": {
                "required": ["controller", "steward"],
                "threshold": 2
            }
        }
        
        # Provide approvals without steward
        approvals = [
            {
                "role": "controller",
                "signer": "did:example:test",
                "timestamp": "2024-01-15T10:00:00Z", 
                "signature": "mock_signature"
            },
            {
                "role": "auditor",  # Wrong role
                "signer": "did:example:auditor",
                "timestamp": "2024-01-15T10:00:00Z",
                "signature": "mock_signature"
            }
        ]
        
        result = self.engine.finalize_consense(offer_id, approvals, policy)
        
        self.assertEqual(result["status"], "missing_required_roles")
        self.assertIn("steward", result["missing"])
    
    def test_get_policy(self):
        """Test policy retrieval"""
        # Create approved policy
        policy_id = "policy:consense:test123"
        policy_data = {"test": "data"}
        
        self.engine.approved_policies[policy_id] = {
            "policy": policy_data,
            "approved_at": 1234567890
        }
        
        retrieved = self.engine.get_policy(policy_id)
        self.assertEqual(retrieved["policy"], policy_data)
        
        # Test non-existent policy
        self.assertIsNone(self.engine.get_policy("non-existent"))
    
    def test_cleanup_expired_offers(self):
        """Test cleanup of expired offers"""
        import time
        
        # Add expired offer (created more than 1 hour ago)
        old_time = time.time() - 7200  # 2 hours ago
        
        expired_offer_id = "dkdc:offer:expired"
        self.engine.pending_offers[expired_offer_id] = {
            "offer": None,
            "created_at": old_time
        }
        
        # Add current offer
        current_offer_id = "dkdc:offer:current"
        self.engine.pending_offers[current_offer_id] = {
            "offer": None,
            "created_at": time.time()
        }
        
        # Run cleanup
        self.engine.cleanup_expired_offers()
        
        # Verify expired offer removed, current offer preserved
        self.assertNotIn(expired_offer_id, self.engine.pending_offers)
        self.assertIn(current_offer_id, self.engine.pending_offers)

if __name__ == "__main__":
    unittest.main()