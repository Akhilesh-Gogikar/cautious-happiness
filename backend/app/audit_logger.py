import hashlib
import json
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models_db import AuditLog

logger = logging.getLogger(__name__)

class AuditLogger:
    """
    Implements a tamper-evident audit log using a simplified blockchain-like hash chain.
    """
    
    @staticmethod
    def _compute_hash(timestamp: datetime, event_type: str, payload: dict, previous_hash: str) -> str:
        """
        Computes SHA-256 hash of the record data including the previous hash.
        Timestamp is formatted to ISO string for consistency.
        Payload is sorted by keys to ensure deterministic JSON serialization.
        """
        ts_str = timestamp.isoformat()
        payload_str = json.dumps(payload, sort_keys=True)
        
        data_string = f"{ts_str}|{event_type}|{payload_str}|{previous_hash}"
        return hashlib.sha256(data_string.encode('utf-8')).hexdigest()

    def log_event(self, db: Session, event_type: str, payload: dict, user_id: int = None) -> AuditLog:
        """
        Logs a new event to the immutable ledger.
        This method MUST be serialized in a real production environment to avoid race conditions 
        on 'last_record'. In this Postgres/SQLAlchemy implementations, explicit table locking 
        or serializable isolation level is recommended for high integrity. 
        """
        # 1. Get the last record to link the chain
        last_record = db.query(AuditLog).order_by(AuditLog.id.desc()).first()
        
        if last_record:
            previous_hash = last_record.record_hash
        else:
            previous_hash = "0" * 64 # Genesis block hash
            
        timestamp = datetime.utcnow()
        
        # 2. Compute current hash
        current_hash = self._compute_hash(timestamp, event_type, payload, previous_hash)
        
        # 3. Create Record
        log_entry = AuditLog(
            timestamp=timestamp,
            event_type=event_type,
            payload=payload,
            user_id=user_id,
            previous_hash=previous_hash,
            record_hash=current_hash
        )
        
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        logger.info(f"AUDIT LOG [{event_type}]: {current_hash[:8]}...")
        return log_entry

    def verify_chain(self, db: Session) -> bool:
        """
        Verifies the integrity of the entire audit log chain.
        Returns True if valid, False if tampering is detected.
        """
        logs = db.query(AuditLog).order_by(AuditLog.id.asc()).all()
        
        if not logs:
            return True
            
        expected_prev_hash = "0" * 64
        
        for i, log in enumerate(logs):
            # 1. Check previous hash link
            if log.previous_hash != expected_prev_hash:
                logger.error(f"INTEGRITY FAILURE at ID {log.id}: Previous hash mismatch.")
                logger.error(f"Expected: {expected_prev_hash}")
                logger.error(f"Found:    {log.previous_hash}")
                return False
            
            # 2. Re-compute hash to verify data integrity
            calculated_hash = self._compute_hash(log.timestamp, log.event_type, log.payload, log.previous_hash)
            
            if calculated_hash != log.record_hash:
                logger.error(f"INTEGRITY FAILURE at ID {log.id}: Data tampering detected.")
                logger.error(f"Stored Hash: {log.record_hash}")
                logger.error(f"Calc Hash:   {calculated_hash}")
                return False
                
            expected_prev_hash = log.record_hash
            
        logger.info(f"Audit Log Chain Verified: {len(logs)} records ok.")
        return True
