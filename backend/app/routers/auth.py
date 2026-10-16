from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.models import Token, User
from app.core.auth import authenticate_user, create_user_token, get_current_active_user

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return create_user_token(user)


@router.get("/me", response_model=User)
async def read_current_user(current_user: User = Depends(get_current_active_user)):
    """The signed-in user (username, email, role); the frontend's source of truth."""
    return current_user
