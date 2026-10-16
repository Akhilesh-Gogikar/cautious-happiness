import asyncio
import json
import os
import secrets
from datetime import timedelta
from typing import Optional

from fastapi import Depends, HTTPException, Header, Request, WebSocket, WebSocketDisconnect, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.audit import log_user_action
from app.core.security import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, decode_access_token, verify_password
from app.db.models import ApiKey, IpWhitelist
from app.db.session import get_db
from app.models import Token, User, UserInDB
from app.services.user_service import user_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)


def demo_auth_enabled() -> bool:
    return os.getenv("ALLOW_DEMO_AUTH", "false").lower() in {"1", "true", "yes", "on"}


def _demo_user() -> User:
    return User(username="demo_admin", email="aki@onenew.ai", role="admin", disabled=False)


def user_for_token(token: str) -> Optional[UserInDB]:
    """The account an access token signs in as, or None if the token is invalid or expired or names no user."""
    payload = decode_access_token(token)
    username = payload.get("sub") if payload else None
    return user_service.get_user(username) if username else None


async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    x_api_key: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token and not x_api_key:
        if demo_auth_enabled():
            return _demo_user()
        raise credentials_exception

    username = None

    if x_api_key:
        import hashlib

        api_key_hash = hashlib.sha256(x_api_key.encode()).hexdigest()

        result = await db.execute(select(ApiKey).where(ApiKey.key_hash == api_key_hash, ApiKey.is_active == True))
        db_api_key = result.scalar_one_or_none()
        if not db_api_key:
            raise credentials_exception
        username = db_api_key.user_id

        client_ip = request.client.host
        whitelist_result = await db.execute(select(IpWhitelist).where(IpWhitelist.user_id == username))
        whitelisted_ips = whitelist_result.scalars().all()

        if whitelisted_ips:
            allowed_ips = [ip.ip_address for ip in whitelisted_ips]
            if client_ip not in allowed_ips and "127.0.0.1" not in allowed_ips:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="IP Address not whitelisted")

    elif token:
        user = user_for_token(token)
        if user is None:
            raise credentials_exception
        return user

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


# Browsers cannot set headers on a WebSocket, and a token in the URL would end up in
# access logs, so a socket's client sends {"type": "auth", "token": "<access token>"}
# as its first message.
WS_AUTH_TIMEOUT_SECONDS = 10.0
# 4000-4999 are application close codes; these follow HTTP 401 and 403.
WS_CLOSE_UNAUTHORIZED = 4401
WS_CLOSE_FORBIDDEN = 4403
# The standard "policy violation" code, for a first message that isn't an auth message.
WS_CLOSE_POLICY_VIOLATION = 1008


class WebSocketAuthError(Exception):
    def __init__(self, code: int, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


async def authenticate_websocket(websocket: WebSocket) -> User:
    """The signed-in user of an accepted WebSocket, by the same rules as get_current_active_user.

    Raises WebSocketAuthError, with the close code to use, when no auth message arrives
    within WS_AUTH_TIMEOUT_SECONDS or its token is missing or rejected.
    """
    try:
        message = json.loads(await asyncio.wait_for(websocket.receive_text(), WS_AUTH_TIMEOUT_SECONDS))
    except (asyncio.TimeoutError, ValueError, KeyError, TypeError, WebSocketDisconnect):
        # KeyError or TypeError: a binary frame, which has no text (or None, on some servers).
        message = None
    if not isinstance(message, dict) or message.get("type") != "auth":
        raise WebSocketAuthError(WS_CLOSE_POLICY_VIOLATION, "Expected a sign-in message first.")

    token = message.get("token")
    if not token and demo_auth_enabled():
        return _demo_user()
    user = user_for_token(token) if isinstance(token, str) and token else None
    if user is None:
        raise WebSocketAuthError(WS_CLOSE_UNAUTHORIZED, "Your session has ended. Sign in again.")
    if user.disabled:
        raise WebSocketAuthError(WS_CLOSE_FORBIDDEN, "This account is disabled.")
    return user


async def get_current_admin_user(current_user: User = Depends(get_current_active_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
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
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")
