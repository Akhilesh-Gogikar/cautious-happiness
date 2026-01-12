from enum import Enum
from typing import List, Set
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import models_db, auth, database_users


class Permission(str, Enum):
    """Granular permissions for different actions in the system."""
    TRADE_EXECUTE = "trade:execute"  # Place and cancel orders
    TRADE_VIEW = "trade:view"  # View own orders and positions
    ALL_TRADE_VIEW = "trade:view:all"  # View all users' orders and positions
    RISK_LIMIT_SET = "risk:limit:set"  # Configure risk and exposure limits
    SYSTEM_LOG_VIEW = "system:log:view"  # View system and action logs
    SYSTEM_DEBUG = "system:debug"  # Access system internals and developer tools


class Role(str, Enum):
    """User roles in the system."""
    TRADER = "trader"
    RISK_MANAGER = "risk_manager"
    DEVELOPER = "developer"
    AUDITOR = "auditor"
    PWD = "pwd"


# Role to Permission Mapping
ROLE_PERMISSIONS: dict[Role, Set[Permission]] = {
    Role.TRADER: {
        Permission.TRADE_EXECUTE,
        Permission.TRADE_VIEW,
    },
    Role.RISK_MANAGER: {
        Permission.TRADE_VIEW,
        Permission.ALL_TRADE_VIEW,
        Permission.RISK_LIMIT_SET,
    },
    Role.DEVELOPER: set(Permission),  # All permissions
    Role.AUDITOR: {
        Permission.ALL_TRADE_VIEW,
        Permission.SYSTEM_LOG_VIEW,
    },
    Role.PWD: {
        Permission.TRADE_VIEW,
    },
}


def get_user_permissions(user: models_db.User) -> Set[Permission]:
    """Get all permissions for a user based on their role."""
    if not user.profile:
        return set()
    
    try:
        user_role = Role(user.profile.role)
    except ValueError:
        # If role is not recognized, return empty set
        return set()
    
    return ROLE_PERMISSIONS.get(user_role, set())


def user_has_permission(user: models_db.User, permission: Permission) -> bool:
    """Check if a user has a specific permission."""
    user_permissions = get_user_permissions(user)
    return permission in user_permissions


class RequiresPermission:
    """Dependency to check if the current user has the required permission."""
    
    def __init__(self, permission: Permission):
        self.permission = permission
    
    async def __call__(
        self,
        current_user: models_db.User = Depends(auth.get_current_user)
    ) -> models_db.User:
        """Verify the user has the required permission."""
        if not user_has_permission(current_user, self.permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required permission: {self.permission.value}"
            )
        return current_user


# Convenience functions for common permission checks
def requires_trade_execute():
    """Dependency for routes that require trade execution permission."""
    return RequiresPermission(Permission.TRADE_EXECUTE)


def requires_trade_view():
    """Dependency for routes that require trade view permission."""
    return RequiresPermission(Permission.TRADE_VIEW)


def requires_all_trade_view():
    """Dependency for routes that require viewing all trades."""
    return RequiresPermission(Permission.ALL_TRADE_VIEW)


def requires_risk_limit_set():
    """Dependency for routes that require setting risk limits."""
    return RequiresPermission(Permission.RISK_LIMIT_SET)


def requires_system_log_view():
    """Dependency for routes that require viewing system logs."""
    return RequiresPermission(Permission.SYSTEM_LOG_VIEW)


def requires_system_debug():
    """Dependency for routes that require system debug access."""
    return RequiresPermission(Permission.SYSTEM_DEBUG)
