from fastapi import FastAPI

from control_plane_api import __version__
from control_plane_api.api.router import api_router
from control_plane_api.api.routes.health import health_router
from control_plane_api.core.config import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()

    app = FastAPI(
        title=app_settings.app_name,
        version=__version__,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    app.state.settings = app_settings

    app.include_router(health_router)
    app.include_router(api_router, prefix=app_settings.api_v1_prefix)

    @app.get("/", tags=["system"])
    async def root() -> dict[str, str]:
        return {
            "service": app_settings.app_name,
            "version": __version__,
            "environment": app_settings.app_env,
        }

    return app


app = create_app()
