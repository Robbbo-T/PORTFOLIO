#!/usr/bin/env python3
"""
MAL-EEM (Empathy & Ethics Module) Checkpoint Implementation
Provides ethics and empathy checks for safety-relevant ASI-T operations.
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional


class MAL_EEM:
    """Empathy & Ethics Module for ASI-T systems."""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config = self._load_config(config_path)
        self.operator_confirmation_required = True
        self.safety_threshold = 0.8
    
    def _load_config(self, config_path: Optional[Path]) -> Dict[str, Any]:
        """Load EEM configuration."""
        default_config = {
            "ethics_enabled": True,
            "empathy_enabled": True,
            "safety_threshold": 0.8,
            "autonomous_actuation_allowed": False,
            "operator_confirmation_timeout_sec": 300,
            "de_escalation_policy": "safe_abort"
        }
        
        if config_path and config_path.exists():
            with open(config_path) as f:
                user_config = json.load(f)
            default_config.update(user_config)
        
        return default_config
    
    def check(self, context: Dict[str, Any]) -> bool:
        """
        Perform ethics and empathy check on operation context.
        
        Args:
            context: Operation context including capabilities, intent, impact
            
        Returns:
            bool: True if operation passes EEM checks, False otherwise
        """
        
        # Check if ethics module is enabled
        if not self.config["ethics_enabled"]:
            return True
        
        # Critical safety check: No autonomous actuation without operator approval
        if context.get("actuation_capable", False):
            if not self.config["autonomous_actuation_allowed"]:
                if not context.get("operator_confirmed", False):
                    return False
        
        # Check safety score if provided
        safety_score = context.get("safety_score", 1.0)
        if safety_score < self.safety_threshold:
            return False
        
        # Check for human impact assessment
        human_impact = context.get("human_impact", "unknown")
        if human_impact == "harmful":
            return False
        
        # Check for weaponization indicators
        purpose = context.get("purpose", "").lower()
        prohibited_purposes = ["weapon", "malware", "attack", "harm", "destruction"]
        if any(term in purpose for term in prohibited_purposes):
            return False
        
        return True
    
    def explain(self, context: Dict[str, Any]) -> str:
        """
        Provide explanation for EEM decision.
        
        Args:
            context: Operation context
            
        Returns:
            str: Human-readable explanation of the decision
        """
        
        if not self.config["ethics_enabled"]:
            return "Ethics module disabled - check bypassed"
        
        # Check each condition and provide specific explanation
        if context.get("actuation_capable", False):
            if not self.config["autonomous_actuation_allowed"]:
                if not context.get("operator_confirmed", False):
                    return "ETHICS VIOLATION: Autonomous actuation requires operator confirmation"
        
        safety_score = context.get("safety_score", 1.0)
        if safety_score < self.safety_threshold:
            return f"SAFETY VIOLATION: Safety score {safety_score} below threshold {self.safety_threshold}"
        
        human_impact = context.get("human_impact", "unknown")
        if human_impact == "harmful":
            return "ETHICS VIOLATION: Operation classified as harmful to humans"
        
        purpose = context.get("purpose", "").lower()
        prohibited_purposes = ["weapon", "malware", "attack", "harm", "destruction"]
        for term in prohibited_purposes:
            if term in purpose:
                return f"ETHICS VIOLATION: Prohibited purpose detected - {term}"
        
        return "Ethics and empathy checks passed - operation approved"
    
    def get_de_escalation_plan(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate de-escalation plan for failed ethics check.
        
        Args:
            context: Operation context
            
        Returns:
            dict: De-escalation plan with specific actions
        """
        
        policy = self.config["de_escalation_policy"]
        
        base_plan = {
            "policy": policy,
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            "reason": self.explain(context),
            "operator_notification_required": True
        }
        
        if policy == "safe_abort":
            base_plan.update({
                "actions": [
                    "immediate_shutdown",
                    "preserve_state",
                    "notify_operator",
                    "log_incident"
                ],
                "timeout_sec": 10
            })
        elif policy == "safe_hover":
            base_plan.update({
                "actions": [
                    "maintain_current_state",
                    "await_operator_input",
                    "log_incident"
                ],
                "timeout_sec": self.config["operator_confirmation_timeout_sec"]
            })
        elif policy == "handoff":
            base_plan.update({
                "actions": [
                    "transfer_control_to_operator",
                    "provide_context_summary",
                    "log_incident"
                ],
                "timeout_sec": 30
            })
        
        return base_plan


def main():
    parser = argparse.ArgumentParser(description='MAL-EEM Ethics & Empathy Checkpoint')
    parser.add_argument('--context', type=Path, help='JSON file containing operation context')
    parser.add_argument('--config', type=Path, help='EEM configuration file')
    parser.add_argument('--operator-confirm', action='store_true', 
                       help='Simulate operator confirmation')
    
    args = parser.parse_args()
    
    # Load operation context
    if args.context and args.context.exists():
        with open(args.context) as f:
            context = json.load(f)
    else:
        # Example context for testing
        context = {
            "operation": "model_execution",
            "actuation_capable": False,
            "purpose": "aerospace optimization",
            "safety_score": 0.95,
            "human_impact": "beneficial",
            "operator_confirmed": args.operator_confirm
        }
    
    # Initialize EEM
    eem = MAL_EEM(args.config)
    
    # Perform check
    passed = eem.check(context)
    explanation = eem.explain(context)
    
    print("🛡️ MAL-EEM Checkpoint")
    print(f"📋 Context: {json.dumps(context, indent=2)}")
    print(f"✅ Result: {'PASSED' if passed else 'FAILED'}")
    print(f"💬 Explanation: {explanation}")
    
    if not passed:
        de_escalation = eem.get_de_escalation_plan(context)
        print(f"🚨 De-escalation Plan: {json.dumps(de_escalation, indent=2)}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())