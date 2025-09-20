#!/usr/bin/env python3
"""
DKDC Digital Evidence Twin (DET) Integration
Provides tamper-evident audit trails for DKDC operations
"""

import json
import hashlib
import time
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass 
class DETRecord:
    """Digital Evidence Twin record"""
    det_id: str
    operation: str  # consense, token_issue, parcel_delivery, revocation
    policy_id: Optional[str] = None
    token_id: Optional[str] = None
    cpl_hash: Optional[str] = None
    participants: List[str] = None
    signatures: List[Dict] = None
    timestamp: float = 0
    block_hash: Optional[str] = None
    utcs_mi: Optional[str] = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()
        if self.participants is None:
            self.participants = []
        if self.signatures is None:
            self.signatures = []

class DETAnchor:
    """Digital Evidence Twin anchor for DKDC audit trails"""
    
    def __init__(self):
        self.records = {}  # In production, use blockchain or distributed ledger
        self.chain = []    # Simplified chain for demonstration
        
    def record_consense(self, policy_id: str, policy_hash: str, 
                       approvals: List[Dict]) -> str:
        """Record consense approval in DET"""
        
        # Generate DET ID
        det_id = f"det:tx:{hashlib.sha256(f'{policy_id}:{time.time()}'.encode()).hexdigest()[:16]}"
        
        # Extract participants
        participants = [approval.get('signer', '') for approval in approvals]
        
        # Create DET record
        record = DETRecord(
            det_id=det_id,
            operation="consense",
            policy_id=policy_id,
            cpl_hash=policy_hash,
            participants=participants,
            signatures=approvals,
            utcs_mi=f"EstándarUniversal:DET-CONSENSE-{policy_id.split(':')[-1]}"
        )
        
        # Add to chain
        self._add_to_chain(record)
        
        return det_id
    
    def record_token_issuance(self, token_id: str, policy_id: str, 
                             controller: str, processors: List[str]) -> str:
        """Record CCT token issuance in DET"""
        
        det_id = f"det:tx:{hashlib.sha256(f'{token_id}:{time.time()}'.encode()).hexdigest()[:16]}"
        
        participants = [controller] + processors
        
        record = DETRecord(
            det_id=det_id,
            operation="token_issue",
            policy_id=policy_id,
            token_id=token_id,
            participants=participants,
            utcs_mi=f"EstándarUniversal:DET-TOKEN-{token_id[:8]}"
        )
        
        self._add_to_chain(record)
        
        return det_id
    
    def record_parcel_delivery(self, token_id: str, recipient: str, 
                              parcel_hashes: List[str]) -> str:
        """Record context parcel delivery in DET"""
        
        det_id = f"det:tx:{hashlib.sha256(f'{token_id}:{recipient}:{time.time()}'.encode()).hexdigest()[:16]}"
        
        # Create evidence of delivery
        delivery_proof = {
            "token_id": token_id,
            "recipient": recipient,
            "parcel_count": len(parcel_hashes),
            "parcel_hashes": parcel_hashes,
            "delivered_at": datetime.now().isoformat()
        }
        
        record = DETRecord(
            det_id=det_id,
            operation="parcel_delivery", 
            token_id=token_id,
            participants=[recipient],
            signatures=[{"type": "delivery_proof", "data": delivery_proof}],
            utcs_mi=f"EstándarUniversal:DET-DELIVERY-{token_id[:8]}"
        )
        
        self._add_to_chain(record)
        
        return det_id
    
    def record_revocation(self, token_id: str, reason: str) -> str:
        """Record token revocation in DET"""
        
        det_id = f"det:tx:{hashlib.sha256(f'{token_id}:revoke:{time.time()}'.encode()).hexdigest()[:16]}"
        
        revocation_proof = {
            "token_id": token_id,
            "reason": reason,
            "revoked_at": datetime.now().isoformat()
        }
        
        record = DETRecord(
            det_id=det_id,
            operation="revocation",
            token_id=token_id,
            signatures=[{"type": "revocation_proof", "data": revocation_proof}],
            utcs_mi=f"EstándarUniversal:DET-REVOKE-{token_id[:8]}"
        )
        
        self._add_to_chain(record)
        
        return det_id
    
    def get_audit_trail(self, det_id: str) -> Dict:
        """Retrieve audit trail for DET ID"""
        
        if det_id not in self.records:
            raise Exception(f"DET record not found: {det_id}")
        
        record = self.records[det_id]
        
        # Build comprehensive audit trail
        audit_data = {
            "det_id": det_id,
            "record": asdict(record),
            "chain_position": self._get_chain_position(det_id),
            "verification": self._verify_record_integrity(record),
            "related_records": self._get_related_records(record)
        }
        
        return audit_data
    
    def get_policy_audit_trail(self, policy_id: str) -> List[Dict]:
        """Get all DET records related to a policy"""
        related_records = []
        
        for record in self.records.values():
            if record.policy_id == policy_id:
                related_records.append(asdict(record))
        
        # Sort by timestamp
        related_records.sort(key=lambda x: x['timestamp'])
        
        return related_records
    
    def get_token_audit_trail(self, token_id: str) -> List[Dict]:
        """Get all DET records related to a token"""
        related_records = []
        
        for record in self.records.values():
            if record.token_id == token_id:
                related_records.append(asdict(record))
        
        # Sort by timestamp
        related_records.sort(key=lambda x: x['timestamp'])
        
        return related_records
    
    def _add_to_chain(self, record: DETRecord):
        """Add record to the DET chain"""
        
        # Calculate previous block hash
        if self.chain:
            prev_hash = self.chain[-1]["block_hash"]
        else:
            prev_hash = "genesis"
        
        # Create block
        block_data = {
            "det_id": record.det_id,
            "record": asdict(record),
            "previous_hash": prev_hash,
            "timestamp": record.timestamp
        }
        
        # Calculate block hash
        block_hash = hashlib.sha256(
            json.dumps(block_data, sort_keys=True).encode()
        ).hexdigest()
        
        block_data["block_hash"] = block_hash
        record.block_hash = block_hash
        
        # Add to chain and records
        self.chain.append(block_data)
        self.records[record.det_id] = record
    
    def _get_chain_position(self, det_id: str) -> int:
        """Get position of record in chain"""
        for i, block in enumerate(self.chain):
            if block["det_id"] == det_id:
                return i
        return -1
    
    def _verify_record_integrity(self, record: DETRecord) -> Dict:
        """Verify record integrity"""
        try:
            # Find block in chain
            block = next(b for b in self.chain if b["det_id"] == record.det_id)
            
            # Recalculate hash
            block_copy = block.copy()
            stored_hash = block_copy.pop("block_hash")
            
            calculated_hash = hashlib.sha256(
                json.dumps(block_copy, sort_keys=True).encode()
            ).hexdigest()
            
            return {
                "integrity_valid": stored_hash == calculated_hash,
                "stored_hash": stored_hash,
                "calculated_hash": calculated_hash
            }
        except:
            return {"integrity_valid": False, "error": "Record not found in chain"}
    
    def _get_related_records(self, record: DETRecord) -> List[str]:
        """Get IDs of related records"""
        related = []
        
        for det_id, other_record in self.records.items():
            if det_id == record.det_id:
                continue
                
            # Same policy
            if (record.policy_id and other_record.policy_id == record.policy_id):
                related.append(det_id)
            
            # Same token  
            elif (record.token_id and other_record.token_id == record.token_id):
                related.append(det_id)
        
        return related
    
    def export_audit_report(self, format: str = "json") -> str:
        """Export complete audit report"""
        
        report_data = {
            "generated_at": datetime.now().isoformat(),
            "total_records": len(self.records),
            "chain_length": len(self.chain),
            "records": [asdict(record) for record in self.records.values()],
            "chain_integrity": self._verify_chain_integrity()
        }
        
        if format == "json":
            return json.dumps(report_data, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _verify_chain_integrity(self) -> bool:
        """Verify entire chain integrity"""
        if not self.chain:
            return True
        
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]
            
            if current["previous_hash"] != previous["block_hash"]:
                return False
        
        return True