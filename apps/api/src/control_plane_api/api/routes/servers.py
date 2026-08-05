from fastapi import APIRouter, Depends, HTTPException, status

from control_plane_api.api.dependencies import get_app_settings, get_current_principal
from control_plane_api.core.config import Settings
from control_plane_api.modules.servers.service import (
    ServerPersistenceError,
    create_server,
    get_server,
    list_servers,
    summarize_servers,
    test_server_ssh_access,
    update_server,
    update_server_ssh_access,
)
from control_plane_api.schemas.auth import Principal
from control_plane_api.schemas.servers import (
    ServerCreate,
    ServerDetail,
    ServerSshAccessPublic,
    ServerSshAccessUpdate,
    ServerSshConnectionTestResult,
    ServersListResponse,
    ServersSummaryResponse,
    ServerUpdate,
)

router = APIRouter(prefix="/servers", tags=["servers"])


def require_servers_read(principal: Principal) -> None:
    if "servers.read" not in principal.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )


def require_servers_write(principal: Principal) -> None:
    if "servers.write" not in principal.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )


@router.get("", response_model=ServersListResponse)
async def servers(
    principal: Principal = Depends(get_current_principal),
    settings: Settings = Depends(get_app_settings),
) -> ServersListResponse:
    require_servers_read(principal)
    return await list_servers(settings)


@router.get("/summary", response_model=ServersSummaryResponse)
async def servers_summary(
    principal: Principal = Depends(get_current_principal),
    settings: Settings = Depends(get_app_settings),
) -> ServersSummaryResponse:
    require_servers_read(principal)
    return await summarize_servers(settings)


@router.post("", response_model=ServerDetail, status_code=status.HTTP_201_CREATED)
async def server_create(
    payload: ServerCreate,
    principal: Principal = Depends(get_current_principal),
    settings: Settings = Depends(get_app_settings),
) -> ServerDetail:
    require_servers_write(principal)
    try:
        return await create_server(settings, payload)
    except ServerPersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router.get("/{server_id}", response_model=ServerDetail)
async def server_detail(
    server_id: str,
    principal: Principal = Depends(get_current_principal),
    settings: Settings = Depends(get_app_settings),
) -> ServerDetail:
    require_servers_read(principal)
    server = await get_server(settings, server_id)
    if server is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Server not found",
        )
    return server


@router.put("/{server_id}", response_model=ServerDetail)
async def server_update(
    server_id: str,
    payload: ServerUpdate,
    principal: Principal = Depends(get_current_principal),
    settings: Settings = Depends(get_app_settings),
) -> ServerDetail:
    require_servers_write(principal)
    try:
        server = await update_server(settings, server_id, payload)
    except ServerPersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    if server is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Server not found",
        )
    return server


@router.put("/{server_id}/ssh-access", response_model=ServerSshAccessPublic)
async def server_ssh_access_update(
    server_id: str,
    payload: ServerSshAccessUpdate,
    principal: Principal = Depends(get_current_principal),
    settings: Settings = Depends(get_app_settings),
) -> ServerSshAccessPublic:
    require_servers_write(principal)
    try:
        ssh_access = await update_server_ssh_access(settings, server_id, payload)
    except ServerPersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    if ssh_access is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Server not found",
        )
    return ssh_access


@router.post("/{server_id}/ssh-access/test", response_model=ServerSshConnectionTestResult)
async def server_ssh_access_test(
    server_id: str,
    principal: Principal = Depends(get_current_principal),
    settings: Settings = Depends(get_app_settings),
) -> ServerSshConnectionTestResult:
    require_servers_write(principal)
    result = await test_server_ssh_access(settings, server_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Server not found",
        )
    return result
