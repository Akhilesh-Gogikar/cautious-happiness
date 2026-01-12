import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from app.compliance import ComplianceService, CustodyProviderClient
from app.compliance_models import WhitelistRequest, ComplianceResult
from app.models_db import WhitelistedAddress, ComplianceCheck, User, UserProfile
from app.database_users import SessionLocal, engine, BaseUsers

# Setup test database
@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    BaseUsers.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    BaseUsers.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        email="test@example.com",
        hashed_password="hashed",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def compliance_service():
    """Create a compliance service instance."""
    return ComplianceService(custody_provider="mock")

def test_custody_provider_kyc_verification():
    """Test mock custody provider KYC verification."""
    client = CustodyProviderClient(provider="mock")
    result = client.verify_kyc_status("0x1234567890abcdef")
    
    assert result["verified"] is True
    assert "verification_date" in result
    assert "expiry_date" in result
    assert result["verification_level"] == "INSTITUTIONAL"

def test_custody_provider_aml_screening_clean():
    """Test AML screening for clean wallet."""
    client = CustodyProviderClient(provider="mock")
    result = client.check_aml_screening("0x1234567890abcdef")
    
    assert result["status"] == "APPROVED"
    assert result["sanctions_match"] is False
    assert result["risk_score"] < 50

def test_custody_provider_aml_screening_flagged():
    """Test AML screening for flagged wallet."""
    client = CustodyProviderClient(provider="mock")
    result = client.check_aml_screening("0xbadactor123")
    
    assert result["status"] == "FLAGGED"
    assert result["sanctions_match"] is True
    assert result["risk_score"] > 50

def test_validate_whitelisted_address_success(compliance_service, db_session, test_user):
    """Test successful validation of whitelisted address."""
    # Add wallet to whitelist
    whitelisted = WhitelistedAddress(
        user_id=test_user.id,
        wallet_address="0x1234567890abcdef",
        custody_provider="mock",
        kyc_verified=True,
        aml_status="APPROVED",
        verification_date=datetime.utcnow(),
        expiry_date=datetime.utcnow() + timedelta(days=365),
        is_active=True
    )
    db_session.add(whitelisted)
    db_session.commit()
    
    # Validate
    result = compliance_service.validate_wallet_address("0x1234567890abcdef", test_user.id, db_session)
    
    assert result.is_approved is True
    assert result.wallet_address == "0x1234567890abcdef"
    assert result.check_type == "PRE_TRADE"
    assert "passed" in result.reason.lower()

def test_validate_non_whitelisted_address_fails(compliance_service, db_session, test_user):
    """Test validation failure for non-whitelisted address."""
    result = compliance_service.validate_wallet_address("0xnotwhitelisted", test_user.id, db_session)
    
    assert result.is_approved is False
    assert result.check_type == "WHITELIST_CHECK"
    assert "not whitelisted" in result.reason.lower()

def test_validate_expired_kyc_fails(compliance_service, db_session, test_user):
    """Test validation failure for expired KYC."""
    # Add wallet with expired KYC
    whitelisted = WhitelistedAddress(
        user_id=test_user.id,
        wallet_address="0xexpired123",
        custody_provider="mock",
        kyc_verified=True,
        aml_status="APPROVED",
        verification_date=datetime.utcnow() - timedelta(days=400),
        expiry_date=datetime.utcnow() - timedelta(days=30),  # Expired 30 days ago
        is_active=True
    )
    db_session.add(whitelisted)
    db_session.commit()
    
    # Validate
    result = compliance_service.validate_wallet_address("0xexpired123", test_user.id, db_session)
    
    assert result.is_approved is False
    assert result.check_type == "KYC_EXPIRY_CHECK"
    assert "expired" in result.reason.lower()

def test_validate_aml_flagged_address_fails(compliance_service, db_session, test_user):
    """Test validation failure for AML-flagged address."""
    # Add wallet with flagged AML status
    whitelisted = WhitelistedAddress(
        user_id=test_user.id,
        wallet_address="0xflagged123",
        custody_provider="mock",
        kyc_verified=True,
        aml_status="FLAGGED",
        verification_date=datetime.utcnow(),
        expiry_date=datetime.utcnow() + timedelta(days=365),
        is_active=True
    )
    db_session.add(whitelisted)
    db_session.commit()
    
    # Validate
    result = compliance_service.validate_wallet_address("0xflagged123", test_user.id, db_session)
    
    assert result.is_approved is False
    assert result.check_type == "AML_CHECK"
    assert "FLAGGED" in result.reason

def test_validate_unverified_kyc_fails(compliance_service, db_session, test_user):
    """Test validation failure for unverified KYC."""
    # Add wallet without KYC verification
    whitelisted = WhitelistedAddress(
        user_id=test_user.id,
        wallet_address="0xunverified123",
        custody_provider="mock",
        kyc_verified=False,
        aml_status="PENDING",
        is_active=True
    )
    db_session.add(whitelisted)
    db_session.commit()
    
    # Validate
    result = compliance_service.validate_wallet_address("0xunverified123", test_user.id, db_session)
    
    assert result.is_approved is False
    assert result.check_type == "KYC_CHECK"
    assert "not completed" in result.reason.lower()

def test_compliance_audit_log_created(compliance_service, db_session, test_user):
    """Test that compliance checks are logged to audit trail."""
    # Validate a non-whitelisted address (will fail)
    result = compliance_service.validate_wallet_address("0xauditlog123", test_user.id, db_session)
    
    # Check that audit log was created
    logs = db_session.query(ComplianceCheck).filter(
        ComplianceCheck.wallet_address == "0xauditlog123"
    ).all()
    
    assert len(logs) == 1
    assert logs[0].check_type == "PRE_TRADE"
    assert logs[0].check_result == "REJECTED"
    assert logs[0].user_id == test_user.id

def test_add_whitelisted_address(compliance_service, db_session, test_user):
    """Test adding a new wallet to whitelist."""
    request = WhitelistRequest(
        wallet_address="0xnewwallet123",
        custody_provider="mock",
        kyc_verified=False,
        aml_status="PENDING",
        expiry_days=365
    )
    
    whitelisted = compliance_service.add_whitelisted_address(test_user.id, request, db_session)
    
    assert whitelisted.wallet_address == "0xnewwallet123"
    assert whitelisted.user_id == test_user.id
    assert whitelisted.is_active is True
    # Mock custody provider returns verified=True
    assert whitelisted.kyc_verified is True

def test_add_duplicate_wallet_fails(compliance_service, db_session, test_user):
    """Test that adding duplicate wallet raises error."""
    # Add first wallet
    request = WhitelistRequest(
        wallet_address="0xduplicate123",
        custody_provider="mock"
    )
    compliance_service.add_whitelisted_address(test_user.id, request, db_session)
    
    # Try to add same wallet again
    with pytest.raises(ValueError, match="already whitelisted"):
        compliance_service.add_whitelisted_address(test_user.id, request, db_session)

def test_remove_whitelisted_address(compliance_service, db_session, test_user):
    """Test removing a wallet from whitelist."""
    # Add wallet
    whitelisted = WhitelistedAddress(
        user_id=test_user.id,
        wallet_address="0xremoveme123",
        custody_provider="mock",
        kyc_verified=True,
        aml_status="APPROVED",
        is_active=True
    )
    db_session.add(whitelisted)
    db_session.commit()
    
    # Remove wallet
    success = compliance_service.remove_whitelisted_address("0xremoveme123", test_user.id, db_session)
    
    assert success is True
    
    # Verify it's deactivated
    db_session.refresh(whitelisted)
    assert whitelisted.is_active is False

def test_get_wallet_compliance_status(compliance_service, db_session, test_user):
    """Test getting compliance status for a wallet."""
    # Add wallet
    whitelisted = WhitelistedAddress(
        user_id=test_user.id,
        wallet_address="0xstatus123",
        custody_provider="fireblocks",
        kyc_verified=True,
        aml_status="APPROVED",
        verification_date=datetime.utcnow(),
        expiry_date=datetime.utcnow() + timedelta(days=365),
        is_active=True
    )
    db_session.add(whitelisted)
    db_session.commit()
    
    # Get status
    status = compliance_service.get_wallet_compliance_status("0xstatus123", db_session)
    
    assert status.is_whitelisted is True
    assert status.kyc_verified is True
    assert status.aml_status == "APPROVED"
    assert status.custody_provider == "fireblocks"
    assert status.is_active is True

def test_get_status_for_non_whitelisted_wallet(compliance_service, db_session):
    """Test getting status for non-whitelisted wallet."""
    status = compliance_service.get_wallet_compliance_status("0xnotfound123", db_session)
    
    assert status.is_whitelisted is False
    assert status.kyc_verified is False
    assert status.aml_status == "UNKNOWN"
    assert status.custody_provider == "none"
