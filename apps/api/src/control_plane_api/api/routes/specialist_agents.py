from fastapi import APIRouter, Depends, HTTPException, status

from control_plane_api.api.dependencies import get_current_principal
from control_plane_api.modules.specialist_agents.service import (
    get_specialist_agent,
    list_specialist_agents,
    summarize_specialist_agents,
)
from control_plane_api.schemas.auth import Principal
from control_plane_api.schemas.specialist_agents import (
    SpecialistAgentDetail,
    SpecialistAgentsListResponse,
    SpecialistAgentsSummaryResponse,
)

router = APIRouter(prefix="/specialist-agents", tags=["specialist-agents"])


def require_specialist_agents_read(principal: Principal) -> None:
    if "specialist_agents.read" not in principal.permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )


@router.get("", response_model=SpecialistAgentsListResponse)
async def specialist_agents(
    principal: Principal = Depends(get_current_principal),
) -> SpecialistAgentsListResponse:
    require_specialist_agents_read(principal)
    return list_specialist_agents()


@router.get("/summary", response_model=SpecialistAgentsSummaryResponse)
async def specialist_agents_summary(
    principal: Principal = Depends(get_current_principal),
) -> SpecialistAgentsSummaryResponse:
    require_specialist_agents_read(principal)
    return summarize_specialist_agents()


@router.get("/{agent_id}", response_model=SpecialistAgentDetail)
async def specialist_agent_detail(
    agent_id: str,
    principal: Principal = Depends(get_current_principal),
) -> SpecialistAgentDetail:
    require_specialist_agents_read(principal)
    agent = get_specialist_agent(agent_id)
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specialist agent not found",
        )
    return agent
