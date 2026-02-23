
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.core.security import verify_password, create_access_token, decode_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.services.user_service import user_service
from app.models import Token, User, UserInDB
from datetime import timedelta

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token:
        # Return mock admin user for demo purposes since frontend doesn't send token yet
        return User(username="demo_admin", email="aki@onenew.ai", role="admin", disabled=False)
        
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    username: str = payload.get("sub")
    if username is None:
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
