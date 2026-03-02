from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import AuditLog
import json
from datetime import datetime

async def log_user_action(db: AsyncSession, user_id: str, action: str, ip_address: str = None, details: dict = None):
    try:
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            ip_address=ip_address,
            details=details,
            timestamp=datetime.utcnow()
        )
        db.add(audit_log)
        await db.commit()
    except Exception as e:
        # Avoid breaking the main flow if audit logging fails
        print(f"Failed to log audit action: {e}")
