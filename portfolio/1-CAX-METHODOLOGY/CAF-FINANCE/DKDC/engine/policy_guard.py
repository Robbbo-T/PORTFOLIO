#!/usr/bin/env python3
"""
DKDC Policy Guard
OPA/Rego-style policy enforcement for CCT tokens
"""

import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class PolicyViolation:
    """Policy enforcement violation"""
    rule: str
    message: str
    severity: str = "error"  # error, warning, info

class PolicyGuard:
    """Policy enforcement engine for DKDC"""
    
    def __init__(self):
        self.rules = {
            "scope_authorization": self._check_scope_authorization,
            "export_controls": self._check_export_controls,
            "token_expiry": self._check_token_expiry,
            "revocation_status": self._check_revocation_status,
            "llc_compliance": self._check_llc_compliance,
            "redaction_enforcement": self._check_redaction_enforcement
        }
    
    def evaluate(self, input_data: Dict) -> List[PolicyViolation]:
        """Evaluate policy rules against input"""
        violations = []
        
        for rule_name, rule_func in self.rules.items():
            try:
                violation = rule_func(input_data)
                if violation:
                    violations.append(violation)
            except Exception as e:
                violations.append(PolicyViolation(
                    rule=rule_name,
                    message=f"Rule evaluation error: {e}",
                    severity="error"
                ))
        
        return violations
    
    def _check_scope_authorization(self, input_data: Dict) -> Optional[PolicyViolation]:
        """Check if requested scopes are authorized"""
        request = input_data.get("request", {})
        cct = input_data.get("cct", {})
        
        requested_scopes = request.get("scopes", [])
        if isinstance(requested_scopes, str):
            requested_scopes = [requested_scopes]
        
        authorized_scopes = cct.get("dkdc", {}).get("scopes", [])
        
        for scope in requested_scopes:
            if not self._scope_authorized(scope, authorized_scopes):
                return PolicyViolation(
                    rule="scope_authorization",
                    message=f"Scope '{scope}' not authorized by CCT"
                )
        
        return None
    
    def _check_export_controls(self, input_data: Dict) -> Optional[PolicyViolation]:
        """Check export control compliance"""
        request = input_data.get("request", {})
        cct = input_data.get("cct", {})
        
        action = request.get("action", "")
        export_controls = cct.get("dkdc", {}).get("export", {})
        
        # Check internet export
        if action == "export:internet":
            if not export_controls.get("internet", False):
                return PolicyViolation(
                    rule="export_controls",
                    message="Internet export disabled by CCT"
                )
        
        # Check third-party export
        if action == "export:third_party":
            if not export_controls.get("third_party", False):
                return PolicyViolation(
                    rule="export_controls", 
                    message="Third-party export disabled by CCT"
                )
        
        # Check model-to-model sharing
        if action == "share:model":
            if not export_controls.get("model_to_model", True):
                return PolicyViolation(
                    rule="export_controls",
                    message="Model-to-model sharing disabled by CCT"
                )
        
        return None
    
    def _check_token_expiry(self, input_data: Dict) -> Optional[PolicyViolation]:
        """Check token expiration"""
        cct = input_data.get("cct", {})
        now = input_data.get("now", time.time())
        
        exp = cct.get("exp", 0)
        
        if now > exp:
            return PolicyViolation(
                rule="token_expiry",
                message="CCT token has expired"
            )
        
        return None
    
    def _check_revocation_status(self, input_data: Dict) -> Optional[PolicyViolation]:
        """Check if token is revoked"""
        cct = input_data.get("cct", {})
        revoked_tokens = input_data.get("revoked_tokens", set())
        
        jti = cct.get("jti", "")
        
        if jti in revoked_tokens:
            return PolicyViolation(
                rule="revocation_status",
                message="CCT token has been revoked"
            )
        
        return None
    
    def _check_llc_compliance(self, input_data: Dict) -> Optional[PolicyViolation]:
        """Check Lifecycle Level Context compliance"""
        request = input_data.get("request", {})
        cct = input_data.get("cct", {})
        
        requested_llc = request.get("llc", "")
        authorized_llc = cct.get("dkdc", {}).get("llc", "")
        
        # Define LLC hierarchy (higher levels include lower)
        llc_hierarchy = ["ephemeral", "session", "project", "portfolio"]
        
        if requested_llc and authorized_llc:
            try:
                req_level = llc_hierarchy.index(requested_llc)
                auth_level = llc_hierarchy.index(authorized_llc)
                
                if req_level > auth_level:
                    return PolicyViolation(
                        rule="llc_compliance",
                        message=f"Requested LLC '{requested_llc}' exceeds authorized '{authorized_llc}'"
                    )
            except ValueError:
                return PolicyViolation(
                    rule="llc_compliance",
                    message=f"Invalid LLC value: {requested_llc or authorized_llc}"
                )
        
        return None
    
    def _check_redaction_enforcement(self, input_data: Dict) -> Optional[PolicyViolation]:
        """Check redaction enforcement"""
        request = input_data.get("request", {})
        cct = input_data.get("cct", {})
        
        content = request.get("content", "")
        redaction_vectors = cct.get("dkdc", {}).get("redaction_vectors", [])
        
        # Check if sensitive patterns are present (simplified)
        sensitive_patterns = {
            "/secrets": r"(?:secret|password|token|key)\s*[:=]",
            "/personal": r"(?:ssn|phone|address|email)\s*[:=]",
            "/credentials": r"(?:api[-_]?key|access[-_]?token)"
        }
        
        for vector in redaction_vectors:
            if vector in sensitive_patterns:
                import re
                pattern = sensitive_patterns[vector]
                if re.search(pattern, content, re.IGNORECASE):
                    return PolicyViolation(
                        rule="redaction_enforcement",
                        message=f"Sensitive data detected, redaction required: {vector}",
                        severity="warning"
                    )
        
        return None
    
    def _scope_authorized(self, requested: str, authorized: List[str]) -> bool:
        """Check if requested scope is authorized"""
        for auth_scope in authorized:
            # Exact match
            if requested == auth_scope:
                return True
            
            # Wildcard match
            if "*" in auth_scope:
                import fnmatch
                if fnmatch.fnmatch(requested, auth_scope):
                    return True
        
        return False
    
    def create_rego_policy(self) -> str:
        """Generate Rego policy equivalent"""
        return """
package dkdc.guard

# Deny any tool call that goes beyond declared scope
violation[msg] {
    input.request.scope == s
    not s in input.cct.dkdc.scopes
    msg := sprintf("scope %v not permitted", [s])
}

# Block internet export unless explicitly allowed
violation[msg] {
    input.request.action == "export:internet"
    not input.cct.dkdc.export.internet
    msg := "internet export disabled by CCT"
}

# Block third-party export unless explicitly allowed
violation[msg] {
    input.request.action == "export:third_party"
    not input.cct.dkdc.export.third_party
    msg := "third-party export disabled by CCT"
}

# Enforce LLC retention windows
violation[msg] {
    input.now > input.cct.exp
    msg := "token expired"
}

# Check token revocation
violation[msg] {
    input.cct.jti in input.revoked_tokens
    msg := "token has been revoked"
}

# Enforce redaction requirements
violation[msg] {
    input.request.content != ""
    vector in input.cct.dkdc.redaction_vectors
    contains(input.request.content, sensitive_pattern(vector))
    msg := sprintf("redaction required for %v", [vector])
}

sensitive_pattern(vector) = pattern {
    patterns := {
        "/secrets": "(?:secret|password|token|key)",
        "/personal": "(?:ssn|phone|address|email)",
        "/credentials": "(?:api[-_]?key|access[-_]?token)"
    }
    pattern := patterns[vector]
}

# Allow by default if no violations
allow {
    count(violation) == 0
}
"""

def example_policy_enforcement():
    """Example policy enforcement"""
    print("=== DKDC Policy Enforcement Example ===\n")
    
    guard = PolicyGuard()
    
    # Valid request
    print("1. Testing valid request...")
    valid_input = {
        "request": {
            "scopes": ["read:repo:0-STRATEGY/GOVERNANCE.md"],
            "action": "read:content"
        },
        "cct": {
            "iss": "did:example:consense-engine",
            "sub": "did:example:amedeo",
            "exp": int(time.time()) + 3600,  # Valid for 1 hour
            "jti": "test-token-123",
            "dkdc": {
                "scopes": ["read:repo:0-STRATEGY/GOVERNANCE.md", "write:suggestions:pull-requests"],
                "export": {"internet": False, "model_to_model": True, "third_party": False},
                "llc": "project"
            }
        },
        "now": int(time.time()),
        "revoked_tokens": set()
    }
    
    violations = guard.evaluate(valid_input)
    print(f"   Violations: {len(violations)}")
    
    # Invalid scope request
    print("\n2. Testing unauthorized scope...")
    invalid_scope_input = valid_input.copy()
    invalid_scope_input["request"]["scopes"] = ["read:repo:secret-config.yaml"]
    
    violations = guard.evaluate(invalid_scope_input)
    print(f"   Violations: {len(violations)}")
    for v in violations:
        print(f"   - {v.rule}: {v.message}")
    
    # Export control violation
    print("\n3. Testing export control violation...")
    export_violation_input = valid_input.copy()
    export_violation_input["request"]["action"] = "export:internet"
    
    violations = guard.evaluate(export_violation_input)
    print(f"   Violations: {len(violations)}")
    for v in violations:
        print(f"   - {v.rule}: {v.message}")
    
    # Expired token
    print("\n4. Testing expired token...")
    expired_token_input = valid_input.copy()
    expired_token_input["cct"]["exp"] = int(time.time()) - 3600  # Expired 1 hour ago
    
    violations = guard.evaluate(expired_token_input)
    print(f"   Violations: {len(violations)}")
    for v in violations:
        print(f"   - {v.rule}: {v.message}")
    
    print("\n=== Policy Enforcement Complete ===")

if __name__ == "__main__":
    example_policy_enforcement()