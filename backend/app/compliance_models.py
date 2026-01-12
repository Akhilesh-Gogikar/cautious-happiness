from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ComplianceResult(BaseModel):
    """Result of a compliance validation check."""
    is_approved: bool
    wallet_address: str
    check_type: str
    reason: Optional[str] = None
    metadata: dict = {}

class WhitelistRequest(BaseModel):
    """Request to add a wallet to the whitelist."""
    wallet_address: str
    custody_provider: str = "mock"
    kyc_verified: bool = False
    aml_status: str = "PENDING"
    expiry_days: Optional[int] = 365  # KYC validity period

class ComplianceStatusResponse(BaseModel):
    """Response for compliance status queries."""
    wallet_address: str
    is_whitelisted: bool
    kyc_verified: bool
    aml_status: str
    verification_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    is_active: bool
    custody_provider: str
