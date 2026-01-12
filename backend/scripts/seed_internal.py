
import sys
import os
from sqlalchemy.orm import Session
from passlib.context import CryptContext

# Adjust path to import app modules
sys.path.append('/app')

from app import models_db, database_users

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def seed_internal():
    print("Connecting to DB...")
    db = database_users.SessionLocal()
    
    roles_and_users = [
        {"email": "trader@alphasignals.com", "password": "trader", "full_name": "Active Trader", "role": "trader"},
        {"email": "risk_manager@alphasignals.com", "password": "risk_manager", "full_name": "Risk Manager", "role": "risk_manager"},
        {"email": "developer@alphasignals.com", "password": "developer", "full_name": "Core Developer", "role": "developer"},
        {"email": "auditor@alphasignals.com", "password": "auditor", "full_name": "Compliance Auditor", "role": "auditor"}
    ]

    for user_data in roles_and_users:
        print(f"Processing {user_data['email']}...")
        existing = db.query(models_db.User).filter(models_db.User.email == user_data['email']).first()
        if existing:
            print(f"  User {user_data['email']} already exists. Updating...")
            existing.hashed_password = get_password_hash(user_data['password'])
            # Ensure profile exists
            if not existing.profile:
                profile = models_db.UserProfile(user_id=existing.id, full_name=user_data['full_name'], role=user_data['role'])
                db.add(profile)
            else:
                existing.profile.role = user_data['role']
                existing.profile.full_name = user_data['full_name']
        else:
            print(f"  Creating new user {user_data['email']}...")
            hashed_pw = get_password_hash(user_data['password'])
            new_user = models_db.User(email=user_data['email'], hashed_password=hashed_pw)
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            profile = models_db.UserProfile(user_id=new_user.id, full_name=user_data['full_name'], role=user_data['role'])
            db.add(profile)
            
            # Security Question
            hashed_ans = get_password_hash("blue")
            sq = models_db.SecurityQuestion(user_id=new_user.id, question="What is your favorite color?", hashed_answer=hashed_ans)
            db.add(sq)
            
    db.commit()
    print("Seeding Complete.")
    db.close()

if __name__ == "__main__":
    seed_internal()
