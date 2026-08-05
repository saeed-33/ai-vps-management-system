from fastapi import APIRouter, Depends, HTTPException, status

from control_plane_api.api.dependencies import get_current_principal
from control_plane_api.modules.allowed_tools.service import (
    get_allowed_tool,
    list_allowed_tools,
    summarize_allowed_tools,
)
from control_plane_api.schemas.allowed_tools import (
    AllowedToolDetail,
    AllowedToolsListResponse,
    AllowedToolsSummaryResponse,
)
from control_plane_api.schemas.auth import Principal

router = APIRouter(prefix="/allowed-tools", tags=["allowed-tools"])


def require_tools_read(principal: Principal) -> None:
    if "tools.read" not in principal.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )


@router.get("", response_model=AllowedToolsListResponse)
async def allowed_tools(principal: Principal = Depends(get_current_principal)) -> AllowedToolsListResponse:
    require_tools_read(principal)
    return list_allowed_tools()


@router.get("/summary", response_model=AllowedToolsSummaryResponse)
async def allowed_tools_summary(
    principal: Principal = Depends(get_current_principal),
) -> AllowedToolsSummaryResponse:
    require_tools_read(principal)
    return summarize_allowed_tools()


@router.get("/{tool_id}", response_model=AllowedToolDetail)
async def allowed_tool_detail(
    tool_id: str,
    principal: Principal = Depends(get_current_principal),
) -> AllowedToolDetail:
    require_tools_read(principal)
    tool = get_allowed_tool(tool_id)
    if tool is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Allowed tool not found",
        )
    return tool
