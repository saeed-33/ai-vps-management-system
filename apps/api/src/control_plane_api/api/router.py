from fastapi import APIRouter

from control_plane_api.api.routes.meta import router as meta_router

api_router = APIRouter()
api_router.include_router(meta_router)
