from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from control_plane_api.core.config import Settings
from control_plane_api.core.security import TokenError, decode_access_token
from control_plane_api.modules.auth.rbac import permissions_for_roles
from control_plane_api.schemas.auth import Principal

bearer_scheme = HTTPBearer(auto_error=False)


def get_app_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_current_principal(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> Principal:
    settings = get_app_settings(request)
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )

    try:
        payload = decode_access_token(credentials.credentials, secret_key=settings.auth_secret_key)
    except TokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    roles = payload.get("roles", [])
    if not isinstance(roles, list):
        roles = []

    email = payload.get("email")
    if not isinstance(email, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing email",
        )

    return Principal(
        subject=str(payload.get("sub", email)),
        email=email,
        display_name=str(payload.get("display_name", email)),
        roles=[str(role) for role in roles],
        permissions=permissions_for_roles([str(role) for role in roles]),
    )
