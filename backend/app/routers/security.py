from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Dict, Any
import hashlib
import secrets
import datetime
from app.db.session import get_db
from app.core.auth import get_current_active_user
from app.db.models import ApiKey, IpWhitelist, AuditLog
from app.models import User
from pydantic import BaseModel
from app.core.audit import log_user_action

router = APIRouter(prefix="/security", tags=["security"])

class ApiKeyCreate(BaseModel):
    name: str
    
class IpWhitelistCreate(BaseModel):
    ip_address: str
    description: str = None

@router.post("/api-keys")
async def create_api_key(
    request: Request,
    req: ApiKeyCreate, 
    user: User = Depends(get_current_active_user), 
    db: AsyncSession = Depends(get_db)
):
    raw_key = secrets.token_urlsafe(32)
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    
    db_api_key = ApiKey(
        user_id=user.username,
        name=req.name,
        key_hash=key_hash,
        prefix=raw_key[:8]
    )
    db.add(db_api_key)
    await db.commit()
    await db.refresh(db_api_key)
    
    await log_user_action(db, user.username, "API_KEY_CREATED", request.client.host, {"name": req.name})
    
    return {"id": db_api_key.id, "name": db_api_key.name, "prefix": db_api_key.prefix, "raw_key": raw_key}

@router.get("/api-keys")
async def list_api_keys(user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ApiKey).where(ApiKey.user_id == user.username, ApiKey.is_active == True))
    keys = result.scalars().all()
    return [{"id": k.id, "name": k.name, "prefix": k.prefix, "created_at": k.created_at} for k in keys]

@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    request: Request,
    key_id: str, 
    user: User = Depends(get_current_active_user), 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(ApiKey).where(ApiKey.id == key_id, ApiKey.user_id == user.username))
    db_api_key = result.scalar_one_or_none()
    if not db_api_key:
        raise HTTPException(status_code=404, detail="API Key not found")
        
    db_api_key.is_active = False
    await db.commit()
    
    await log_user_action(db, user.username, "API_KEY_REVOKED", request.client.host, {"key_id": key_id})
    return {"status": "success"}

@router.post("/ip-whitelist")
async def add_ip_whitelist(
    request: Request,
    req: IpWhitelistCreate, 
    user: User = Depends(get_current_active_user), 
    db: AsyncSession = Depends(get_db)
):
    whitelist_entry = IpWhitelist(
        user_id=user.username,
        ip_address=req.ip_address,
        description=req.description
    )
    db.add(whitelist_entry)
    await db.commit()
    await db.refresh(whitelist_entry)
    
    await log_user_action(db, user.username, "IP_WHITELIST_ADDED", request.client.host, {"ip": req.ip_address})
    return {"id": whitelist_entry.id, "ip_address": whitelist_entry.ip_address, "description": whitelist_entry.description}

@router.get("/ip-whitelist")
async def list_ip_whitelists(user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(IpWhitelist).where(IpWhitelist.user_id == user.username))
    ips = result.scalars().all()
    return [{"id": ip.id, "ip_address": ip.ip_address, "description": ip.description, "created_at": ip.created_at} for ip in ips]

@router.delete("/ip-whitelist/{ip_id}")
async def remove_ip_whitelist(
    request: Request,
    ip_id: str, 
    user: User = Depends(get_current_active_user), 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(IpWhitelist).where(IpWhitelist.id == ip_id, IpWhitelist.user_id == user.username))
    ip_entry = result.scalar_one_or_none()
    if not ip_entry:
        raise HTTPException(status_code=404, detail="IP whitelist entry not found")
        
    await db.delete(ip_entry)
    await db.commit()
    
    await log_user_action(db, user.username, "IP_WHITELIST_REMOVED", request.client.host, {"ip_id": ip_id})
    return {"status": "success"}

@router.get("/audit-logs")
async def get_audit_logs(user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AuditLog).where(AuditLog.user_id == user.username).order_by(AuditLog.timestamp.desc()).limit(50))
    logs = result.scalars().all()
    return [{"id": l.id, "action": l.action, "ip_address": l.ip_address, "details": l.details, "timestamp": l.timestamp} for l in logs]
