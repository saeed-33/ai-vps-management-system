from fastapi import APIRouter, Depends, HTTPException, status

from control_plane_api.api.dependencies import get_current_principal
from control_plane_api.modules.users.service import current_principal_to_user, list_bootstrap_users, list_roles
from control_plane_api.schemas.auth import Principal
from control_plane_api.schemas.users import RolesListResponse, UserSummary, UsersListResponse

router = APIRouter(prefix="/users", tags=["users"])


def require_users_read(principal: Principal) -> None:
    if "users.read" not in principal.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )


@router.get("", response_model=UsersListResponse)
async def users(principal: Principal = Depends(get_current_principal)) -> UsersListResponse:
    require_users_read(principal)
    return list_bootstrap_users(principal)


@router.get("/me", response_model=UserSummary)
async def me(principal: Principal = Depends(get_current_principal)) -> UserSummary:
    return current_principal_to_user(principal)


@router.get("/roles", response_model=RolesListResponse)
async def roles(principal: Principal = Depends(get_current_principal)) -> RolesListResponse:
    require_users_read(principal)
    return list_roles()
