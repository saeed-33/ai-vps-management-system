from control_plane_api.schemas.auth import PermissionDefinition, RbacCatalog, RoleDefinition

PERMISSIONS = [
    PermissionDefinition(code="users.read", description="View users"),
    PermissionDefinition(code="users.write", description="Create and update users"),
    PermissionDefinition(code="servers.read", description="View servers"),
    PermissionDefinition(code="servers.write", description="Create and update servers"),
    PermissionDefinition(code="monitoring.read", description="View monitoring data"),
    PermissionDefinition(code="monitoring.write", description="Manage monitoring profiles"),
    PermissionDefinition(code="specialist_agents.read", description="View specialist agents"),
    PermissionDefinition(code="specialist_agents.write", description="Manage specialist agents"),
    PermissionDefinition(code="issues.read", description="View issues"),
    PermissionDefinition(code="issues.write", description="Manage issues"),
    PermissionDefinition(code="reports.read", description="View reports"),
    PermissionDefinition(code="audit.read", description="View audit logs"),
    PermissionDefinition(code="solutions.approve", description="Approve allowed solutions"),
    PermissionDefinition(code="tools.read", description="View allowed tools"),
    PermissionDefinition(code="tools.manage", description="Manage allowed tools"),
    PermissionDefinition(code="documents.manage", description="Manage RAG documents and links"),
    PermissionDefinition(code="chat.use", description="Use agent chat"),
]

OWNER_PERMISSIONS = [permission.code for permission in PERMISSIONS]
ADMIN_PERMISSIONS = [
    "users.read",
    "servers.read",
    "servers.write",
    "monitoring.read",
    "monitoring.write",
    "specialist_agents.read",
    "specialist_agents.write",
    "issues.read",
    "issues.write",
    "reports.read",
    "audit.read",
    "solutions.approve",
    "tools.read",
    "tools.manage",
    "documents.manage",
    "chat.use",
]
OPERATOR_PERMISSIONS = [
    "servers.read",
    "monitoring.read",
    "specialist_agents.read",
    "issues.read",
    "issues.write",
    "reports.read",
    "tools.read",
    "chat.use",
]
VIEWER_PERMISSIONS = [
    "servers.read",
    "monitoring.read",
    "specialist_agents.read",
    "issues.read",
    "reports.read",
    "tools.read",
]
AUDITOR_PERMISSIONS = [
    "servers.read",
    "monitoring.read",
    "specialist_agents.read",
    "issues.read",
    "reports.read",
    "audit.read",
    "tools.read",
]

ROLES = [
    RoleDefinition(code="owner", name="Owner", permissions=OWNER_PERMISSIONS),
    RoleDefinition(code="admin", name="Admin", permissions=ADMIN_PERMISSIONS),
    RoleDefinition(code="operator", name="Operator", permissions=OPERATOR_PERMISSIONS),
    RoleDefinition(code="viewer", name="Viewer", permissions=VIEWER_PERMISSIONS),
    RoleDefinition(code="auditor", name="Auditor", permissions=AUDITOR_PERMISSIONS),
]


def get_rbac_catalog() -> RbacCatalog:
    return RbacCatalog(roles=ROLES, permissions=PERMISSIONS)


def permissions_for_roles(roles: list[str]) -> list[str]:
    permissions: set[str] = set()
    for role in ROLES:
        if role.code in roles:
            permissions.update(role.permissions)
    return sorted(permissions)
