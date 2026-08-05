from fastapi import APIRouter, Depends

from control_plane_api import __version__
from control_plane_api.api.dependencies import get_app_settings
from control_plane_api.core.config import Settings
from control_plane_api.schemas.meta import ModuleStatus, ServiceMetadata

router = APIRouter(prefix="/meta", tags=["meta"])


@router.get("", response_model=ServiceMetadata)
async def meta(settings: Settings = Depends(get_app_settings)) -> ServiceMetadata:
    return ServiceMetadata(
        service=settings.app_name,
        environment=settings.app_env,
        version=__version__,
        api_prefix=settings.api_v1_prefix,
        modules=[
            ModuleStatus(name="auth", status="foundation-ready"),
            ModuleStatus(name="users", status="foundation-ready"),
            ModuleStatus(name="servers", status="foundation-ready"),
            ModuleStatus(name="monitoring_profiles", status="foundation-ready"),
            ModuleStatus(name="specialist_agents", status="planned"),
            ModuleStatus(name="issues", status="planned"),
            ModuleStatus(name="reports", status="planned"),
            ModuleStatus(name="allowed_tools", status="planned"),
            ModuleStatus(name="allowed_solutions", status="planned"),
            ModuleStatus(name="documents", status="planned"),
            ModuleStatus(name="chat", status="planned"),
            ModuleStatus(name="mcp", status="planned"),
            ModuleStatus(name="policy_engine", status="planned"),
            ModuleStatus(name="health", status="foundation-ready"),
        ],
    )
