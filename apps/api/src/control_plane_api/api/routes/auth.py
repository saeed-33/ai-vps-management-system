from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status

from control_plane_api.api.dependencies import get_app_settings, get_current_principal
from control_plane_api.core.config import Settings
from control_plane_api.core.security import create_access_token, verify_password
from control_plane_api.modules.auth.rbac import get_rbac_catalog, permissions_for_roles
from control_plane_api.schemas.auth import Principal, RbacCatalog, TokenRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=TokenResponse)
async def create_token(
    payload: TokenRequest,
    settings: Settings = Depends(get_app_settings),
) -> TokenResponse:
    if (
        not settings.auth_secret_key
        or not settings.bootstrap_admin_email
        or not settings.bootstrap_admin_password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Bootstrap auth is not configured",
        )

    if payload.email.lower() != settings.bootstrap_admin_email.lower():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not verify_password(payload.password, settings.bootstrap_admin_password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    roles = ["owner"]
    expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    token = create_access_token(
        subject=settings.bootstrap_admin_email,
        secret_key=settings.auth_secret_key,
        expires_delta=expires_delta,
        claims={
            "email": settings.bootstrap_admin_email,
            "display_name": "Bootstrap Admin",
            "roles": roles,
        },
    )
    return TokenResponse(
        access_token=token,
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.get("/me", response_model=Principal)
async def me(principal: Principal = Depends(get_current_principal)) -> Principal:
    return principal


@router.get("/rbac", response_model=RbacCatalog)
async def rbac_catalog(
    principal: Principal = Depends(get_current_principal),
) -> RbacCatalog:
    if "audit.read" not in principal.permissions and "users.read" not in principal.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    return get_rbac_catalog()
