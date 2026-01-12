/**
 * Permission utilities for frontend RBAC
 */

export enum Role {
    TRADER = "trader",
    RISK_MANAGER = "risk_manager",
    DEVELOPER = "developer",
    AUDITOR = "auditor",
}

export enum Permission {
    TRADE_EXECUTE = "trade:execute",
    TRADE_VIEW = "trade:view",
    ALL_TRADE_VIEW = "trade:view:all",
    RISK_LIMIT_SET = "risk:limit:set",
    SYSTEM_LOG_VIEW = "system:log:view",
    SYSTEM_DEBUG = "system:debug",
}

const ROLE_PERMISSIONS: Record<Role, Permission[]> = {
    [Role.TRADER]: [Permission.TRADE_EXECUTE, Permission.TRADE_VIEW],
    [Role.RISK_MANAGER]: [
        Permission.TRADE_VIEW,
        Permission.ALL_TRADE_VIEW,
        Permission.RISK_LIMIT_SET,
    ],
    [Role.DEVELOPER]: Object.values(Permission),
    [Role.AUDITOR]: [Permission.ALL_TRADE_VIEW, Permission.SYSTEM_LOG_VIEW],
};

export function hasPermission(userRole: string | undefined, permission: Permission): boolean {
    if (!userRole) return false;

    const role = userRole as Role;
    const permissions = ROLE_PERMISSIONS[role];

    return permissions ? permissions.includes(permission) : false;
}

export function hasAnyPermission(userRole: string | undefined, permissions: Permission[]): boolean {
    return permissions.some(permission => hasPermission(userRole, permission));
}

export function hasAllPermissions(userRole: string | undefined, permissions: Permission[]): boolean {
    return permissions.every(permission => hasPermission(userRole, permission));
}

export function canExecuteTrades(userRole: string | undefined): boolean {
    return hasPermission(userRole, Permission.TRADE_EXECUTE);
}

export function canViewTrades(userRole: string | undefined): boolean {
    return hasPermission(userRole, Permission.TRADE_VIEW);
}

export function canViewAllTrades(userRole: string | undefined): boolean {
    return hasPermission(userRole, Permission.ALL_TRADE_VIEW);
}

export function canSetRiskLimits(userRole: string | undefined): boolean {
    return hasPermission(userRole, Permission.RISK_LIMIT_SET);
}

export function canViewSystemLogs(userRole: string | undefined): boolean {
    return hasPermission(userRole, Permission.SYSTEM_LOG_VIEW);
}

export function canDebugSystem(userRole: string | undefined): boolean {
    return hasPermission(userRole, Permission.SYSTEM_DEBUG);
}
