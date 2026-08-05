from control_plane_api.modules.auth.rbac import get_rbac_catalog
from control_plane_api.schemas.auth import Principal
from control_plane_api.schemas.users import RoleSummary, RolesListResponse, UserSummary, UsersListResponse


def current_principal_to_user(principal: Principal) -> UserSummary:
    return UserSummary(
        id=principal.subject,
        email=principal.email,
        display_name=principal.display_name,
        status="active",
        roles=principal.roles,
        source="token",
    )


def list_bootstrap_users(principal: Principal) -> UsersListResponse:
    return UsersListResponse(users=[current_principal_to_user(principal)])


def list_roles() -> RolesListResponse:
    catalog = get_rbac_catalog()
    return RolesListResponse(
        roles=[
            RoleSummary(
                code=role.code,
                name=role.name,
                permission_count=len(role.permissions),
            )
            for role in catalog.roles
        ]
    )
