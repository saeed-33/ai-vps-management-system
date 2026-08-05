from fastapi import APIRouter, Depends, HTTPException, status

from control_plane_api.api.dependencies import get_current_principal
from control_plane_api.modules.servers.service import (
    get_server,
    list_servers,
    summarize_servers,
    update_server_ssh_access,
)
from control_plane_api.schemas.auth import Principal
from control_plane_api.schemas.servers import (
    ServerDetail,
    ServerSshAccessPublic,
    ServerSshAccessUpdate,
    ServersListResponse,
    ServersSummaryResponse,
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
async def servers(principal: Principal = Depends(get_current_principal)) -> ServersListResponse:
    require_servers_read(principal)
    return list_servers()


@router.get("/summary", response_model=ServersSummaryResponse)
async def servers_summary(principal: Principal = Depends(get_current_principal)) -> ServersSummaryResponse:
    require_servers_read(principal)
    return summarize_servers()


@router.get("/{server_id}", response_model=ServerDetail)
async def server_detail(
    server_id: str,
    principal: Principal = Depends(get_current_principal),
) -> ServerDetail:
    require_servers_read(principal)
    server = get_server(server_id)
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
) -> ServerSshAccessPublic:
    require_servers_write(principal)
    ssh_access = update_server_ssh_access(server_id, payload)
    if ssh_access is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Server not found",
        )
    return ssh_access
