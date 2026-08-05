import json
import re
from uuid import UUID

from ai_vps_agent.server_access.models import SshServerAccess
from ai_vps_agent.server_access.ssh_client import SshCommandClient
from ai_vps_agent.tools.registry import baseline_command_policy
from sqlalchemy import text

from control_plane_api.core.config import Settings
from control_plane_api.core.database import get_session_maker
from control_plane_api.modules.periodic_monitoring.persistence import stable_uuid
from control_plane_api.schemas.servers import (
    ServerCreate,
    ServerDetail,
    ServerSshAccessPublic,
    ServerSshAccessUpdate,
    ServerSshConnectionTestResult,
    ServersListResponse,
    ServersSummaryResponse,
    ServerSummary,
    ServerUpdate,
)


SSH_ACCESS_STORE: dict[str, ServerSshAccessUpdate] = {}
MEMORY_SERVER_STORE: dict[str, ServerDetail] = {}

FOUNDATION_SERVERS = [
    ServerDetail(
        id="srv-foundation-001",
        name="foundation-vps",
        hostname="foundation-vps.local",
        ip_address="127.0.0.1",
        os_family="linux",
        environment="development",
        status="active",
        monitoring_status="not_configured",
        source="foundation-fixture",
        metadata={"purpose": "Placeholder server until PostgreSQL repositories are connected"},
        assigned_monitoring_profiles=[],
        ssh_access=ServerSshAccessPublic(enabled=False),
    )
]


async def list_servers(settings: Settings) -> ServersListResponse:
    database_servers = await _try_database_list_servers(settings)
    servers = database_servers if database_servers is not None else _memory_servers()
    return ServersListResponse(
        servers=[
            ServerSummary(
                id=server.id,
                name=server.name,
                hostname=server.hostname,
                ip_address=server.ip_address,
                os_family=server.os_family,
                environment=server.environment,
                status=server.status,
                monitoring_status=server.monitoring_status,
                source=server.source,
            )
            for server in servers
        ]
    )


async def summarize_servers(settings: Settings) -> ServersSummaryResponse:
    database_servers = await _try_database_list_servers(settings)
    servers = database_servers if database_servers is not None else _memory_servers()
    by_environment: dict[str, int] = {}
    active = disabled = maintenance = 0

    for server in servers:
        by_environment[server.environment] = by_environment.get(server.environment, 0) + 1
        if server.status == "active":
            active += 1
        elif server.status == "disabled":
            disabled += 1
        elif server.status == "maintenance":
            maintenance += 1

    return ServersSummaryResponse(
        total=len(servers),
        active=active,
        disabled=disabled,
        maintenance=maintenance,
        by_environment=by_environment,
    )


async def get_server(settings: Settings, server_id: str) -> ServerDetail | None:
    database_server = await _try_database_get_server(settings, server_id)
    if database_server is not None:
        return database_server
    return _memory_server(server_id)


async def create_server(settings: Settings, payload: ServerCreate) -> ServerDetail:
    database_server = await _try_database_create_server(settings, payload)
    if database_server is not None:
        return database_server

    server_id = _new_memory_server_id(payload.name)
    server = ServerDetail(
        id=server_id,
        name=payload.name,
        hostname=payload.hostname,
        ip_address=payload.ip_address,
        os_family=payload.os_family,
        environment=payload.environment,
        status=payload.status,
        monitoring_status="not_configured",
        source="memory-fallback",
        metadata=payload.metadata,
        assigned_monitoring_profiles=payload.assigned_monitoring_profiles,
        ssh_access=ServerSshAccessPublic(enabled=False),
    )
    MEMORY_SERVER_STORE[server_id] = server
    return server


async def update_server(settings: Settings, server_id: str, payload: ServerUpdate) -> ServerDetail | None:
    database_server = await _try_database_update_server(settings, server_id, payload)
    if database_server is not None:
        return database_server

    server = _memory_server(server_id)
    if server is None:
        return None
    update = payload.model_dump(exclude_unset=True)
    updated_server = server.model_copy(update=update)
    if server_id in MEMORY_SERVER_STORE:
        MEMORY_SERVER_STORE[server_id] = updated_server
    else:
        MEMORY_SERVER_STORE[server_id] = updated_server.model_copy(update={"source": "memory-fallback"})
    return updated_server


async def update_server_ssh_access(
    settings: Settings,
    server_id: str,
    payload: ServerSshAccessUpdate,
) -> ServerSshAccessPublic | None:
    if await get_server(settings, server_id) is None:
        return None

    database_ssh = await _try_database_update_ssh_access(settings, server_id, payload)
    SSH_ACCESS_STORE[server_id] = payload
    return database_ssh if database_ssh is not None else _public_ssh_access(payload)


async def get_server_ssh_access_config(settings: Settings, server_id: str) -> ServerSshAccessUpdate | None:
    database_access = await _try_database_get_ssh_access(settings, server_id)
    if database_access is not None:
        return database_access
    return SSH_ACCESS_STORE.get(server_id)


async def test_server_ssh_access(settings: Settings, server_id: str) -> ServerSshConnectionTestResult | None:
    if await get_server(settings, server_id) is None:
        return None

    access = await get_server_ssh_access_config(settings, server_id)
    if access is None or not access.enabled:
        return ServerSshConnectionTestResult(
            ok=False,
            server_id=server_id,
            detail="SSH access is not enabled for this server.",
        )
    if not access.host or not access.username:
        return ServerSshConnectionTestResult(
            ok=False,
            server_id=server_id,
            detail="SSH host and username are required.",
        )

    client = SshCommandClient(
        SshServerAccess(
            host=access.host,
            port=access.port,
            username=access.username,
            private_key_path=access.private_key_path,
            password=access.password,
            command_timeout_seconds=5,
            connect_timeout_seconds=5,
            max_output_bytes=4096,
        ),
        baseline_command_policy(),
    )
    try:
        result = await client.run_tool("uptime")
    except Exception as exc:  # pragma: no cover - depends on external SSH hosts.
        return ServerSshConnectionTestResult(
            ok=False,
            server_id=server_id,
            command="uptime",
            detail=f"{exc.__class__.__name__}: {exc}",
        )

    return ServerSshConnectionTestResult(
        ok=result.exit_status == 0,
        server_id=server_id,
        command=result.command,
        exit_status=result.exit_status,
        detail=result.stdout.strip() or result.stderr.strip() or "SSH command completed.",
    )


async def get_active_agent_servers(settings: Settings) -> list[ServerDetail]:
    database_servers = await _try_database_list_servers(settings)
    servers = database_servers if database_servers is not None else _memory_servers()
    return [server for server in servers if server.status == "active"]


def _memory_servers() -> list[ServerDetail]:
    servers = [server.model_copy(update={"ssh_access": get_memory_server_ssh_access(server.id)}) for server in FOUNDATION_SERVERS]
    servers.extend(MEMORY_SERVER_STORE.values())
    return servers


def _memory_server(server_id: str) -> ServerDetail | None:
    server = MEMORY_SERVER_STORE.get(server_id)
    if server is not None:
        return server.model_copy(update={"ssh_access": get_memory_server_ssh_access(server_id)})
    foundation = next((server for server in FOUNDATION_SERVERS if server.id == server_id), None)
    if foundation is None:
        return None
    return foundation.model_copy(update={"ssh_access": get_memory_server_ssh_access(server_id)})


def get_memory_server_ssh_access(server_id: str) -> ServerSshAccessPublic:
    config = SSH_ACCESS_STORE.get(server_id)
    if config is None:
        return ServerSshAccessPublic(enabled=False)
    return _public_ssh_access(config)


def _public_ssh_access(config: ServerSshAccessUpdate) -> ServerSshAccessPublic:
    if not config.enabled:
        return ServerSshAccessPublic(enabled=False)
    auth_method = "private_key" if config.private_key_path else "password" if config.password else "none"
    return ServerSshAccessPublic(
        enabled=True,
        host=config.host,
        port=config.port,
        username=config.username,
        auth_method=auth_method,
        has_password=bool(config.password),
        private_key_path=config.private_key_path,
    )


async def _try_database_list_servers(settings: Settings) -> list[ServerDetail] | None:
    if not settings.database_url:
        return None
    try:
        session_maker = get_session_maker(settings)
        async with session_maker() as session:
            rows = (
                await session.execute(
                    text(
                        """
                        SELECT
                            s.id::text AS id,
                            s.name,
                            s.hostname,
                            s.ip_address::text AS ip_address,
                            s.os_family,
                            s.environment,
                            s.status,
                            s.metadata,
                            c.secret_ref,
                            c.status AS credential_status
                        FROM servers s
                        LEFT JOIN LATERAL (
                            SELECT secret_ref, status
                            FROM server_credentials
                            WHERE server_id = s.id
                            ORDER BY created_at DESC
                            LIMIT 1
                        ) c ON true
                        ORDER BY s.created_at DESC
                        """
                    )
                )
            ).mappings()
            return [_server_from_row(row) for row in rows]
    except Exception:
        return None


async def _try_database_get_server(settings: Settings, server_id: str) -> ServerDetail | None:
    if not settings.database_url:
        return None
    try:
        server_uuid = _database_server_uuid(server_id)
        session_maker = get_session_maker(settings)
        async with session_maker() as session:
            row = (
                await session.execute(
                    text(
                        """
                        SELECT
                            s.id::text AS id,
                            s.name,
                            s.hostname,
                            s.ip_address::text AS ip_address,
                            s.os_family,
                            s.environment,
                            s.status,
                            s.metadata,
                            c.secret_ref,
                            c.status AS credential_status
                        FROM servers s
                        LEFT JOIN LATERAL (
                            SELECT secret_ref, status
                            FROM server_credentials
                            WHERE server_id = s.id
                            ORDER BY created_at DESC
                            LIMIT 1
                        ) c ON true
                        WHERE s.id = :server_id
                        """
                    ),
                    {"server_id": server_uuid},
                )
            ).mappings().first()
        return _server_from_row(row) if row is not None else None
    except Exception:
        return None


async def _try_database_create_server(settings: Settings, payload: ServerCreate) -> ServerDetail | None:
    if not settings.database_url:
        return None
    try:
        metadata = dict(payload.metadata)
        metadata["assigned_monitoring_profiles"] = payload.assigned_monitoring_profiles
        session_maker = get_session_maker(settings)
        async with session_maker() as session:
            async with session.begin():
                row = (
                    await session.execute(
                        text(
                            """
                            INSERT INTO servers (
                                name, hostname, ip_address, os_family, environment, status, metadata
                            )
                            VALUES (
                                :name, :hostname, CAST(:ip_address AS inet), :os_family, :environment, :status,
                                CAST(:metadata AS jsonb)
                            )
                            RETURNING id::text
                            """
                        ),
                        {
                            "name": payload.name,
                            "hostname": payload.hostname,
                            "ip_address": payload.ip_address,
                            "os_family": payload.os_family,
                            "environment": payload.environment,
                            "status": payload.status,
                            "metadata": json.dumps(metadata),
                        },
                    )
                ).mappings().one()
        return await _try_database_get_server(settings, str(row["id"]))
    except Exception:
        return None


async def _try_database_update_server(settings: Settings, server_id: str, payload: ServerUpdate) -> ServerDetail | None:
    if not settings.database_url:
        return None
    try:
        current = await _try_database_get_server(settings, server_id)
        if current is None:
            return None
        update = payload.model_dump(exclude_unset=True)
        metadata = update.pop("metadata", current.metadata)
        assigned_profiles = update.pop("assigned_monitoring_profiles", current.assigned_monitoring_profiles)
        metadata = dict(metadata)
        metadata["assigned_monitoring_profiles"] = assigned_profiles
        data = {
            "server_id": _database_server_uuid(server_id),
            "name": update.get("name", current.name),
            "hostname": update.get("hostname", current.hostname),
            "ip_address": update.get("ip_address", current.ip_address),
            "os_family": update.get("os_family", current.os_family),
            "environment": update.get("environment", current.environment),
            "status": update.get("status", current.status),
            "metadata": json.dumps(metadata),
        }
        session_maker = get_session_maker(settings)
        async with session_maker() as session:
            async with session.begin():
                await session.execute(
                    text(
                        """
                        UPDATE servers
                        SET
                            name = :name,
                            hostname = :hostname,
                            ip_address = CAST(:ip_address AS inet),
                            os_family = :os_family,
                            environment = :environment,
                            status = :status,
                            metadata = CAST(:metadata AS jsonb),
                            updated_at = now()
                        WHERE id = :server_id
                        """
                    ),
                    data,
                )
        return await _try_database_get_server(settings, server_id)
    except Exception:
        return None


async def _try_database_update_ssh_access(
    settings: Settings,
    server_id: str,
    payload: ServerSshAccessUpdate,
) -> ServerSshAccessPublic | None:
    if not settings.database_url:
        return None
    try:
        server_uuid = _database_server_uuid(server_id)
        credential_type = "ssh_key" if payload.private_key_path else "password"
        session_maker = get_session_maker(settings)
        async with session_maker() as session:
            async with session.begin():
                await session.execute(
                    text(
                        """
                        UPDATE server_credentials
                        SET status = 'disabled', updated_at = now()
                        WHERE server_id = :server_id
                        """
                    ),
                    {"server_id": server_uuid},
                )
                await session.execute(
                    text(
                        """
                        INSERT INTO server_credentials (
                            server_id, credential_type, secret_ref, username, port, status
                        )
                        VALUES (
                            :server_id, :credential_type, :secret_ref, :username, :port, :status
                        )
                        """
                    ),
                    {
                        "server_id": server_uuid,
                        "credential_type": credential_type,
                        "secret_ref": _ssh_payload_to_secret_ref(payload),
                        "username": payload.username,
                        "port": payload.port,
                        "status": "active" if payload.enabled else "disabled",
                    },
                )
        return _public_ssh_access(payload)
    except Exception:
        return None


async def _try_database_get_ssh_access(settings: Settings, server_id: str) -> ServerSshAccessUpdate | None:
    if not settings.database_url:
        return None
    try:
        server_uuid = _database_server_uuid(server_id)
        session_maker = get_session_maker(settings)
        async with session_maker() as session:
            row = (
                await session.execute(
                    text(
                        """
                        SELECT secret_ref
                        FROM server_credentials
                        WHERE server_id = :server_id
                        ORDER BY created_at DESC
                        LIMIT 1
                        """
                    ),
                    {"server_id": server_uuid},
                )
            ).mappings().first()
        return _ssh_access_from_secret_ref(row["secret_ref"]) if row is not None else None
    except Exception:
        return None


def _server_from_row(row: object) -> ServerDetail:
    mapping = dict(row)  # type: ignore[arg-type]
    metadata = mapping.get("metadata") or {}
    if isinstance(metadata, str):
        metadata = json.loads(metadata)
    ssh_access = _ssh_access_from_secret_ref(mapping.get("secret_ref"))
    return ServerDetail(
        id=str(mapping["id"]),
        name=str(mapping["name"]),
        hostname=str(mapping["hostname"]),
        ip_address=mapping.get("ip_address"),
        os_family=mapping.get("os_family"),
        environment=str(mapping["environment"]),
        status=str(mapping["status"]),
        monitoring_status="configured" if ssh_access and ssh_access.enabled else "not_configured",
        source="database",
        metadata={key: str(value) for key, value in metadata.items() if key != "assigned_monitoring_profiles"},
        assigned_monitoring_profiles=list(metadata.get("assigned_monitoring_profiles") or []),
        ssh_access=_public_ssh_access(ssh_access) if ssh_access else ServerSshAccessPublic(enabled=False),
    )


def _ssh_payload_to_secret_ref(payload: ServerSshAccessUpdate) -> str:
    return json.dumps(payload.model_dump(), separators=(",", ":"))


def _ssh_access_from_secret_ref(secret_ref: object) -> ServerSshAccessUpdate | None:
    if not secret_ref:
        return None
    try:
        payload = json.loads(str(secret_ref))
        return ServerSshAccessUpdate.model_validate(payload)
    except (TypeError, ValueError):
        return None


def _database_server_uuid(server_id: str) -> UUID:
    try:
        return UUID(server_id)
    except ValueError:
        return stable_uuid(server_id)


def _new_memory_server_id(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "server"
    candidate = f"srv-{slug}"
    suffix = 2
    existing = {server.id for server in FOUNDATION_SERVERS} | set(MEMORY_SERVER_STORE)
    while candidate in existing:
        candidate = f"srv-{slug}-{suffix}"
        suffix += 1
    return candidate
