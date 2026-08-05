from fastapi import APIRouter

from control_plane_api.api.routes.auth import router as auth_router
from control_plane_api.api.routes.meta import router as meta_router
from control_plane_api.api.routes.monitoring_profiles import router as monitoring_profiles_router
from control_plane_api.api.routes.servers import router as servers_router
from control_plane_api.api.routes.specialist_agents import router as specialist_agents_router
from control_plane_api.api.routes.users import router as users_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(meta_router)
api_router.include_router(users_router)
api_router.include_router(servers_router)
api_router.include_router(monitoring_profiles_router)
api_router.include_router(specialist_agents_router)
