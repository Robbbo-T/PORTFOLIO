#!/usr/bin/env python3
"""
DKDC Context Parcelizer
Handles context bundling, redaction, and minimal disclosure
"""

import re
import json
import hashlib
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class ContextParcel:
    """A minimal context bundle"""
    path: str
    hash: str
    content: str
    metadata: Dict
    redacted: bool = False
    
class ContextParcelizer:
    """Parcelizes context with redaction and minimal disclosure"""
    
    def __init__(self):
        self.redaction_patterns = {
            "emails": r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}',
            "tokens": r'(?:token|key|secret|password)\s*[:=]\s*["\']?([A-Za-z0-9+/=]{20,})["\']?',
            "credentials": r'(?:api[-_]?key|access[-_]?token|secret[-_]?key|password)\s*[:=]\s*["\']?([^\s"\']+)["\']?',
            "secrets": r'(?:BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY|ssh-rsa|ssh-ed25519)',
            "personal": r'(?:SSN|social.security|phone.number|address).*?[:=]\s*([^\n\r]+)',
        }
        
        self.canary_templates = [
            "DKDC-CANARY-{random}",
            "SENTINEL-{random}-DKDC",
            "TRACE-{random}-CONTEXT"
        ]
    
    def create_parcels(self, context_paths: List[str], recipient: str, 
                      scopes: List[str], redaction_vectors: List[str] = None) -> List[Dict]:
        """Create context parcels for specified paths and recipient"""
        
        parcels = []
        
        for path in context_paths:
            # Check scope authorization
            if not self._is_path_authorized(path, scopes):
                continue
                
            try:
                # Read content
                content = self._read_context_file(path)
                
                # Apply redactions
                redacted_content, redacted = self._apply_redactions(
                    content, redaction_vectors or []
                )
                
                # Add canary tokens for tracking
                canary_content = self._add_canary_tokens(redacted_content)
                
                # Calculate hash
                content_hash = hashlib.sha256(canary_content.encode()).hexdigest()
                
                # Build metadata
                metadata = {
                    "original_path": path,
                    "recipient": recipient,
                    "scopes_used": [s for s in scopes if self._scope_covers_path(s, path)],
                    "redaction_applied": redacted,
                    "redaction_vectors": redaction_vectors or [],
                    "processing_timestamp": self._get_timestamp(),
                    "utcs_mi": f"EstándarUniversal:DKDC-Parcel-{content_hash[:8]}"
                }
                
                # Create parcel
                parcel = {
                    "path": path,
                    "hash": f"sha256-{content_hash}",
                    "content": canary_content,
                    "metadata": metadata,
                    "redacted": redacted
                }
                
                parcels.append(parcel)
                
            except Exception as e:
                # Log error but continue with other parcels
                print(f"Error processing {path}: {e}")
                continue
        
        return parcels
    
    def _read_context_file(self, path: str) -> str:
        """Read context file content"""
        try:
            # Handle different path formats
            if path.startswith("git+https://"):
                # Git URL format - extract path
                parts = path.split("#")[0].split("/")
                local_path = "/".join(parts[4:])  # Skip protocol and domain
            else:
                local_path = path
            
            # Make path absolute if relative
            if not os.path.isabs(local_path):
                base_path = Path(__file__).parent.parent.parent.parent.parent  # Go to repo root
                full_path = base_path / local_path
            else:
                full_path = Path(local_path)
            
            # Read file
            return full_path.read_text(encoding='utf-8', errors='ignore')
            
        except Exception as e:
            raise Exception(f"Cannot read context file {path}: {e}")
    
    def _apply_redactions(self, content: str, redaction_vectors: List[str]) -> tuple:
        """Apply redaction patterns to content"""
        redacted_content = content
        redaction_applied = False
        
        for vector in redaction_vectors:
            # Handle path-based redactions
            if vector.startswith("/"):
                # Skip path-based redactions in content processing
                continue
            
            # Handle selector-based redactions
            if vector in self.redaction_patterns:
                pattern = self.redaction_patterns[vector]
                if re.search(pattern, redacted_content, re.IGNORECASE):
                    redacted_content = re.sub(
                        pattern, "[REDACTED]", redacted_content, flags=re.IGNORECASE
                    )
                    redaction_applied = True
            
            # Handle custom patterns
            elif "," in vector:
                # Multiple selectors (e.g., "emails, tokens, secrets")
                selectors = [s.strip() for s in vector.split(",")]
                for selector in selectors:
                    if selector in self.redaction_patterns:
                        pattern = self.redaction_patterns[selector]
                        if re.search(pattern, redacted_content, re.IGNORECASE):
                            redacted_content = re.sub(
                                pattern, "[REDACTED]", redacted_content, flags=re.IGNORECASE
                            )
                            redaction_applied = True
        
        return redacted_content, redaction_applied
    
    def _add_canary_tokens(self, content: str) -> str:
        """Add canary tokens to content for tracking"""
        import random
        import string
        
        # Generate random canary
        random_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        canary = f"DKDC-CANARY-{random_id}"
        
        # Add as comment at end of content
        if content.strip().endswith("}"):
            # JSON-like content
            return content + f'\n// {canary}'
        elif "# " in content[:100]:  # Markdown or YAML
            return content + f'\n<!-- {canary} -->'
        else:
            return content + f'\n# {canary}'
    
    def _is_path_authorized(self, path: str, scopes: List[str]) -> bool:
        """Check if path is authorized by scopes"""
        for scope in scopes:
            if self._scope_covers_path(scope, path):
                return True
        return False
    
    def _scope_covers_path(self, scope: str, path: str) -> bool:
        """Check if scope covers the given path"""
        # Parse scope (e.g., "read:repo:0-STRATEGY/GOVERNANCE.md")
        parts = scope.split(":", 2)
        if len(parts) < 3:
            return False
        
        action, resource, pattern = parts
        
        # For repo resources, check path pattern
        if resource == "repo":
            import fnmatch
            return fnmatch.fnmatch(path, pattern)
        
        return False
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def redact_text(self, text: str, selectors: List[str] = None) -> str:
        """Standalone function to redact text"""
        if not selectors:
            selectors = list(self.redaction_patterns.keys())
        
        redacted_text = text
        
        for selector in selectors:
            if selector in self.redaction_patterns:
                pattern = self.redaction_patterns[selector]
                redacted_text = re.sub(
                    pattern, "[REDACTED]", redacted_text, flags=re.IGNORECASE
                )
        
        return redacted_text
    
    def validate_parcel_integrity(self, parcel: Dict) -> bool:
        """Validate parcel integrity using hash"""
        try:
            content_hash = hashlib.sha256(parcel["content"].encode()).hexdigest()
            expected_hash = parcel["hash"].replace("sha256-", "")
            return content_hash == expected_hash
        except:
            return False