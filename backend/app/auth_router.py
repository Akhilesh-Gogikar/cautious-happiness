from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from . import database, models_db, auth, models, database_users
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["auth"])

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    security_question: str
    security_answer: str

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    email: str
    password: str

class RecoverInitRequest(BaseModel):
    email: str

class RecoverVerifyRequest(BaseModel):
    email: str
    answer: str
    new_password: str

@router.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(database_users.get_db)):
    db_user = db.query(models_db.User).filter(models_db.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 1. Create User
    hashed_pw = auth.get_password_hash(user.password)
    new_user = models_db.User(email=user.email, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 2. Create Profile
    new_profile = models_db.UserProfile(user_id=new_user.id, full_name=user.full_name)
    db.add(new_profile)

    # 3. Create Security Question
    hashed_ans = auth.get_password_hash(user.security_answer.lower().strip()) # Normalize answer
    new_sq = models_db.SecurityQuestion(user_id=new_user.id, question=user.security_question, hashed_answer=hashed_ans)
    db.add(new_sq)

    # 4. Log Action
    log = models_db.ActionLog(user_id=new_user.id, action="REGISTER", metadata_json={"method": "email"})
    db.add(log)

    db.commit()

    # Login automatically
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": new_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login(login_req: LoginRequest, db: Session = Depends(database_users.get_db)):
    # Note: OAuth2PasswordRequestForm is standard, but keeping JSON for simplicity with frontend as requested plan
    user = db.query(models_db.User).filter(models_db.User.email == login_req.email).first()
    if not user or not auth.verify_password(login_req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Log login
    log = models_db.ActionLog(user_id=user.id, action="LOGIN")
    db.add(log) # Async optimization: This could be background task
    db.commit()

    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/recover-init")
def recover_init(req: RecoverInitRequest, db: Session = Depends(database_users.get_db)):
    user = db.query(models_db.User).filter(models_db.User.email == req.email).first()
    if not user:
         # Generic message to prevent enumeration
         raise HTTPException(status_code=404, detail="User not found")
    
    if not user.security_question:
        raise HTTPException(status_code=400, detail="No security question set")

    return {"question": user.security_question.question}

@router.post("/recover-verify")
def recover_verify(req: RecoverVerifyRequest, db: Session = Depends(database_users.get_db)):
    user = db.query(models_db.User).filter(models_db.User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if not user.security_question:
         raise HTTPException(status_code=400, detail="No security question set")

    # Verify answer
    if not auth.verify_password(req.answer.lower().strip(), user.security_question.hashed_answer):
        # Log failed attempt?
        raise HTTPException(status_code=400, detail="Incorrect answer")

    # Reset Password
    user.hashed_password = auth.get_password_hash(req.new_password)
    
    log = models_db.ActionLog(user_id=user.id, action="PASSWORD_RESET")
    db.add(log)
    db.commit()

    return {"status": "success", "message": "Password reset successfully"}

@router.get("/me")
def read_users_me(current_user: models_db.User = Depends(auth.get_current_user)):
    return {
        "email": current_user.email, 
        "full_name": current_user.profile.full_name if current_user.profile else "",
        "role": current_user.profile.role if current_user.profile else "user"
    }

@router.get("/chat-history", response_model=List[models.ChatMessage])
def get_chat_history(
    current_user: models_db.User = Depends(auth.get_current_user),
    db: Session = Depends(database_users.get_db)
):
    history = db.query(models_db.ChatHistory).filter(models_db.ChatHistory.user_id == current_user.id).order_by(models_db.ChatHistory.timestamp.asc()).all()
    return history
