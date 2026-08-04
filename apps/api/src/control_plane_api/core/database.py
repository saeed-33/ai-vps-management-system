from functools import lru_cache

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from control_plane_api.core.config import Settings
from control_plane_api.schemas.health import ComponentStatus


def normalize_async_database_url(database_url: str) -> str:
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return database_url


@lru_cache
def get_engine(database_url: str) -> AsyncEngine:
    return create_async_engine(
        normalize_async_database_url(database_url),
        pool_pre_ping=True,
    )


def get_session_maker(settings: Settings) -> async_sessionmaker:
    return async_sessionmaker(
        get_engine(settings.database_url),
        expire_on_commit=False,
    )


async def check_database(settings: Settings) -> ComponentStatus:
    if not settings.database_url:
        return ComponentStatus(
            name="postgres",
            ok=False,
            detail="DATABASE_URL is not configured",
        )

    try:
        engine = get_engine(settings.database_url)
        async with engine.connect() as connection:
            await connection.execute(text("select 1"))
    except Exception as exc:  # pragma: no cover - exact driver errors vary by host.
        return ComponentStatus(
            name="postgres",
            ok=False,
            detail=f"{exc.__class__.__name__}: {exc}",
        )

    return ComponentStatus(
        name="postgres",
        ok=True,
        detail="database connection succeeded",
    )
