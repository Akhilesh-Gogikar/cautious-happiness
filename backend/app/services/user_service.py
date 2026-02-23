
from typing import Optional, Dict
from app.models import UserInDB
from app.core.security import get_password_hash

# Mock User DB - In a real app this would be a database connection
# Strictly defined roles: admin, trader, analyst, risk_manager
USERS_DB: Dict[str, dict] = {
    "admin": {
        "username": "admin",
        "email": "admin@example.com",
        "hashed_password": get_password_hash("secret"),
        "role": "admin",
        "disabled": False,
    },
    "trader": {
        "username": "trader",
        "email": "trader@example.com",
        "hashed_password": get_password_hash("trader123"),
        "role": "trader",
        "disabled": False,
    },
    "analyst": {
        "username": "analyst",
        "email": "analyst@example.com",
        "hashed_password": get_password_hash("analyst123"),
        "role": "analyst",
        "disabled": False,
    },
    "risk": {
        "username": "risk",
        "email": "risk@example.com",
        "hashed_password": get_password_hash("risk123"),
        "role": "risk_manager",
        "disabled": False,
    }
}

class UserService:
    def get_user(self, username: str) -> Optional[UserInDB]:
        if username in USERS_DB:
            user_dict = USERS_DB[username]
            return UserInDB(**user_dict)
        return None

user_service = UserService()
