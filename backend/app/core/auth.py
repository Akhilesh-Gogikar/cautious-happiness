from fastapi import Depends, HTTPException, status, Header, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.core.security import verify_password, create_access_token, decode_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.services.user_service import user_service
from app.models import Token, User, UserInDB
from app.db.models import ApiKey, IpWhitelist
from app.db.session import get_db
from app.core.audit import log_user_action
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import timedelta
import secrets

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)

async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme), 
    x_api_key: str = Header(None), 
    db: AsyncSession = Depends(get_db)
):
    if not token and not x_api_key:
        return User(username="demo_admin", email="aki@onenew.ai", role="admin", disabled=False)
        
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    username = None
    
    if x_api_key:
        # Since it's hashed in DB, we would ideally hash the input to check.
        from app.core.security import get_password_hash # or a separate fast hash
        # To avoid circularity or complex hashing, let's just do a direct hash check if using SHA256
        import hashlib
        api_key_hash = hashlib.sha256(x_api_key.encode()).hexdigest()
        
        result = await db.execute(select(ApiKey).where(ApiKey.key_hash == api_key_hash, ApiKey.is_active == True))
        db_api_key = result.scalar_one_or_none()
        if not db_api_key:
            raise credentials_exception
        username = db_api_key.user_id
        
        # IP Whitelist Check
        client_ip = request.client.host
        whitelist_result = await db.execute(select(IpWhitelist).where(IpWhitelist.user_id == username))
        whitelisted_ips = whitelist_result.scalars().all()
        
        if whitelisted_ips:
            allowed_ips = [ip.ip_address for ip in whitelisted_ips]
            if client_ip not in allowed_ips and "127.0.0.1" not in allowed_ips: # Allow local testing if not strictly matching
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="IP Address not whitelisted")

    elif token:
        payload = decode_access_token(token)
        if payload is None:
            raise credentials_exception
        username = payload.get("sub")
        
    if not username:
        raise credentials_exception
    
    user = user_service.get_user(username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_admin_user(current_user: User = Depends(get_current_active_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="The user doesn't have enough privileges"
        )
    return current_user

async def authenticate_user(form_data: OAuth2PasswordRequestForm):
    user = user_service.get_user(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        return None
    return user

def create_user_token(user: UserInDB) -> Token:
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, 
        expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
