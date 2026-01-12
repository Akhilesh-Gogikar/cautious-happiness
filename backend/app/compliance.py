import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models_db import WhitelistedAddress, ComplianceCheck, User
from app.compliance_models import ComplianceResult, WhitelistRequest, ComplianceStatusResponse

logger = logging.getLogger(__name__)

class CustodyProviderClient:
    """
    Mock custody provider client simulating Fireblocks/Coinbase Custody API patterns.
    In production, replace with actual custody provider SDK.
    """
    
    def __init__(self, provider: str = "mock", api_key: str = "", api_secret: str = ""):
        self.provider = provider
        self.api_key = api_key
        self.api_secret = api_secret
        logger.info(f"Initialized custody provider client: {provider}")
    
    def verify_kyc_status(self, wallet_address: str) -> Dict[str, Any]:
        """
        Simulates KYC verification check with custody provider.
        
        In production, this would call:
        - Fireblocks: GET /v1/vault/accounts/{vaultAccountId}/kyc
        - Coinbase Custody: GET /api/v1/wallets/{wallet_id}/kyc
        """
        logger.info(f"[MOCK] Checking KYC status for wallet: {wallet_address}")
        
        # Mock response - in production, parse actual API response
        return {
            "verified": True,
            "verification_date": datetime.utcnow().isoformat(),
            "expiry_date": (datetime.utcnow() + timedelta(days=365)).isoformat(),
            "verification_level": "INSTITUTIONAL",  # BASIC, ENHANCED, INSTITUTIONAL
            "provider_reference": f"KYC-{wallet_address[:8]}"
        }
    
    def check_aml_screening(self, wallet_address: str) -> Dict[str, Any]:
        """
        Simulates AML screening check with custody provider.
        
        In production, this would call:
        - Fireblocks: POST /v1/screening/travel_rule
        - Coinbase Custody: POST /api/v1/compliance/screen
        """
        logger.info(f"[MOCK] Running AML screening for wallet: {wallet_address}")
        
        # Mock response - in production, parse actual screening results
        # Simulate flagging addresses containing "bad" for testing
        is_flagged = "bad" in wallet_address.lower() or "sanction" in wallet_address.lower()
        
        return {
            "status": "FLAGGED" if is_flagged else "APPROVED",
            "risk_score": 85 if is_flagged else 15,  # 0-100 scale
            "sanctions_match": is_flagged,
            "pep_match": False,  # Politically Exposed Person
            "adverse_media": False,
            "screening_date": datetime.utcnow().isoformat(),
            "provider_reference": f"AML-{wallet_address[:8]}"
        }
    
    def monitor_transaction(self, wallet_address: str, amount_usd: float) -> Dict[str, Any]:
        """
        Simulates real-time transaction monitoring.
        
        In production, this would call custody provider's transaction monitoring API.
        """
        logger.info(f"[MOCK] Monitoring transaction: {wallet_address} - ${amount_usd}")
        
        # Mock response - flag large transactions for demo
        is_suspicious = amount_usd > 50000
        
        return {
            "approved": not is_suspicious,
            "alert_triggered": is_suspicious,
            "alert_reason": "Large transaction threshold exceeded" if is_suspicious else None,
            "requires_manual_review": is_suspicious
        }


class ComplianceService:
    """
    Service for managing KYC/AML compliance and wallet whitelisting.
    Integrates with custody providers to ensure institutional AML policy compliance.
    """
    
    def __init__(self, custody_provider: str = "mock", api_key: str = "", api_secret: str = ""):
        self.custody_client = CustodyProviderClient(custody_provider, api_key, api_secret)
        self.provider = custody_provider
    
    def validate_wallet_address(self, wallet_address: str, user_id: int, db: Session) -> ComplianceResult:
        """
        Validates if a wallet address is whitelisted and compliant.
        
        Args:
            wallet_address: The wallet address to validate
            user_id: The user ID making the request
            db: Database session
            
        Returns:
            ComplianceResult with approval status and reason
        """
        logger.info(f"Validating wallet address: {wallet_address} for user: {user_id}")
        
        # Check if wallet is whitelisted
        whitelisted = db.query(WhitelistedAddress).filter(
            WhitelistedAddress.wallet_address == wallet_address,
            WhitelistedAddress.is_active == True
        ).first()
        
        if not whitelisted:
            result = ComplianceResult(
                is_approved=False,
                wallet_address=wallet_address,
                check_type="WHITELIST_CHECK",
                reason="Wallet address not whitelisted. Please add to whitelist before trading.",
                metadata={"whitelisted": False}
            )
            self.log_compliance_check(user_id, wallet_address, "PRE_TRADE", "REJECTED", 
                                     reason=result.reason, db=db)
            return result
        
        # Check if KYC is verified
        if not whitelisted.kyc_verified:
            result = ComplianceResult(
                is_approved=False,
                wallet_address=wallet_address,
                check_type="KYC_CHECK",
                reason="KYC verification not completed for this wallet.",
                metadata={"whitelisted": True, "kyc_verified": False}
            )
            self.log_compliance_check(user_id, wallet_address, "PRE_TRADE", "REJECTED",
                                     reason=result.reason, db=db)
            return result
        
        # Check if KYC has expired
        if whitelisted.expiry_date and whitelisted.expiry_date < datetime.utcnow():
            result = ComplianceResult(
                is_approved=False,
                wallet_address=wallet_address,
                check_type="KYC_EXPIRY_CHECK",
                reason=f"KYC verification expired on {whitelisted.expiry_date.strftime('%Y-%m-%d')}. Re-verification required.",
                metadata={"whitelisted": True, "kyc_verified": True, "kyc_expired": True}
            )
            self.log_compliance_check(user_id, wallet_address, "PRE_TRADE", "REJECTED",
                                     reason=result.reason, db=db)
            return result
        
        # Check AML status
        if whitelisted.aml_status not in ["APPROVED", "PENDING"]:
            result = ComplianceResult(
                is_approved=False,
                wallet_address=wallet_address,
                check_type="AML_CHECK",
                reason=f"AML screening status: {whitelisted.aml_status}. Trading not permitted.",
                metadata={"whitelisted": True, "kyc_verified": True, "aml_status": whitelisted.aml_status}
            )
            self.log_compliance_check(user_id, wallet_address, "PRE_TRADE", "REJECTED",
                                     reason=result.reason, db=db)
            return result
        
        # All checks passed
        result = ComplianceResult(
            is_approved=True,
            wallet_address=wallet_address,
            check_type="PRE_TRADE",
            reason="All compliance checks passed.",
            metadata={
                "whitelisted": True,
                "kyc_verified": True,
                "aml_status": whitelisted.aml_status,
                "custody_provider": whitelisted.custody_provider
            }
        )
        self.log_compliance_check(user_id, wallet_address, "PRE_TRADE", "APPROVED",
                                 reason=result.reason, db=db)
        return result
    
    def check_custody_provider_status(self, wallet_address: str) -> Dict[str, Any]:
        """
        Checks wallet status with custody provider.
        
        Args:
            wallet_address: The wallet address to check
            
        Returns:
            Dictionary with KYC and AML status from custody provider
        """
        kyc_result = self.custody_client.verify_kyc_status(wallet_address)
        aml_result = self.custody_client.check_aml_screening(wallet_address)
        
        return {
            "kyc": kyc_result,
            "aml": aml_result,
            "provider": self.provider
        }
    
    def log_compliance_check(self, user_id: int, wallet_address: str, check_type: str, 
                            check_result: str, trade_signal_id: Optional[str] = None,
                            reason: Optional[str] = None, metadata: Dict = None, db: Session = None):
        """
        Creates an immutable audit log entry for a compliance check.
        
        Args:
            user_id: User ID
            wallet_address: Wallet address checked
            check_type: Type of check (PRE_TRADE, KYC_VERIFICATION, AML_SCREENING)
            check_result: Result (APPROVED, REJECTED, PENDING)
            trade_signal_id: Optional trade signal reference
            reason: Optional reason for the result
            metadata: Optional additional metadata
            db: Database session
        """
        if not db:
            logger.warning("No database session provided for compliance logging")
            return
        
        log_entry = ComplianceCheck(
            user_id=user_id,
            wallet_address=wallet_address,
            check_type=check_type,
            check_result=check_result,
            trade_signal_id=trade_signal_id,
            reason=reason,
            timestamp=datetime.utcnow(),
            metadata_json=metadata or {}
        )
        
        db.add(log_entry)
        db.commit()
        logger.info(f"Compliance check logged: {check_type} - {check_result} for {wallet_address}")
    
    def add_whitelisted_address(self, user_id: int, request: WhitelistRequest, db: Session) -> WhitelistedAddress:
        """
        Adds a new wallet address to the whitelist.
        
        Args:
            user_id: User ID
            request: Whitelist request with wallet details
            db: Database session
            
        Returns:
            Created WhitelistedAddress object
        """
        # Check if wallet already exists
        existing = db.query(WhitelistedAddress).filter(
            WhitelistedAddress.wallet_address == request.wallet_address
        ).first()
        
        if existing:
            raise ValueError(f"Wallet address {request.wallet_address} already whitelisted")
        
        # Get custody provider status
        custody_status = self.check_custody_provider_status(request.wallet_address)
        
        # Determine verification status from custody provider
        kyc_verified = custody_status["kyc"].get("verified", request.kyc_verified)
        aml_status = custody_status["aml"].get("status", request.aml_status)
        
        verification_date = datetime.utcnow() if kyc_verified else None
        expiry_date = None
        if kyc_verified and request.expiry_days:
            expiry_date = datetime.utcnow() + timedelta(days=request.expiry_days)
        
        whitelisted = WhitelistedAddress(
            user_id=user_id,
            wallet_address=request.wallet_address,
            custody_provider=request.custody_provider,
            kyc_verified=kyc_verified,
            aml_status=aml_status,
            verification_date=verification_date,
            expiry_date=expiry_date,
            is_active=True,
            metadata_json=custody_status
        )
        
        db.add(whitelisted)
        db.commit()
        db.refresh(whitelisted)
        
        # Log the whitelisting action
        self.log_compliance_check(
            user_id, request.wallet_address, "WHITELIST_ADDITION", "APPROVED",
            reason="Wallet added to whitelist",
            metadata={"custody_provider": request.custody_provider},
            db=db
        )
        
        logger.info(f"Added wallet to whitelist: {request.wallet_address} for user {user_id}")
        return whitelisted
    
    def remove_whitelisted_address(self, wallet_address: str, user_id: int, db: Session) -> bool:
        """
        Removes (deactivates) a wallet address from the whitelist.
        
        Args:
            wallet_address: Wallet address to remove
            user_id: User ID (for authorization)
            db: Database session
            
        Returns:
            True if successful, False if not found
        """
        whitelisted = db.query(WhitelistedAddress).filter(
            WhitelistedAddress.wallet_address == wallet_address,
            WhitelistedAddress.user_id == user_id
        ).first()
        
        if not whitelisted:
            return False
        
        whitelisted.is_active = False
        whitelisted.updated_at = datetime.utcnow()
        db.commit()
        
        # Log the removal
        self.log_compliance_check(
            user_id, wallet_address, "WHITELIST_REMOVAL", "APPROVED",
            reason="Wallet removed from whitelist",
            db=db
        )
        
        logger.info(f"Removed wallet from whitelist: {wallet_address}")
        return True
    
    def get_wallet_compliance_status(self, wallet_address: str, db: Session) -> Optional[ComplianceStatusResponse]:
        """
        Gets the current compliance status for a wallet.
        
        Args:
            wallet_address: Wallet address to check
            db: Database session
            
        Returns:
            ComplianceStatusResponse or None if not found
        """
        whitelisted = db.query(WhitelistedAddress).filter(
            WhitelistedAddress.wallet_address == wallet_address
        ).first()
        
        if not whitelisted:
            return ComplianceStatusResponse(
                wallet_address=wallet_address,
                is_whitelisted=False,
                kyc_verified=False,
                aml_status="UNKNOWN",
                is_active=False,
                custody_provider="none"
            )
        
        return ComplianceStatusResponse(
            wallet_address=wallet_address,
            is_whitelisted=True,
            kyc_verified=whitelisted.kyc_verified,
            aml_status=whitelisted.aml_status,
            verification_date=whitelisted.verification_date,
            expiry_date=whitelisted.expiry_date,
            is_active=whitelisted.is_active,
            custody_provider=whitelisted.custody_provider
        )
