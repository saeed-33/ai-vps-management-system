from control_plane_api.schemas.servers import (
    ServerDetail,
    ServerSshAccessPublic,
    ServerSshAccessUpdate,
    ServersListResponse,
    ServersSummaryResponse,
    ServerSummary,
)


SSH_ACCESS_STORE: dict[str, ServerSshAccessUpdate] = {}

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


def list_servers() -> ServersListResponse:
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
            for server in FOUNDATION_SERVERS
        ]
    )


def summarize_servers() -> ServersSummaryResponse:
    by_environment: dict[str, int] = {}
    active = disabled = maintenance = 0

    for server in FOUNDATION_SERVERS:
        by_environment[server.environment] = by_environment.get(server.environment, 0) + 1
        if server.status == "active":
            active += 1
        elif server.status == "disabled":
            disabled += 1
        elif server.status == "maintenance":
            maintenance += 1

    return ServersSummaryResponse(
        total=len(FOUNDATION_SERVERS),
        active=active,
        disabled=disabled,
        maintenance=maintenance,
        by_environment=by_environment,
    )


def get_server(server_id: str) -> ServerDetail | None:
    server = next((server for server in FOUNDATION_SERVERS if server.id == server_id), None)
    if server is None:
        return None
    return server.model_copy(update={"ssh_access": get_server_ssh_access(server_id)})


def get_server_ssh_access(server_id: str) -> ServerSshAccessPublic:
    config = SSH_ACCESS_STORE.get(server_id)
    if config is None:
        return ServerSshAccessPublic(enabled=False)
    return _public_ssh_access(config)


def get_server_ssh_access_config(server_id: str) -> ServerSshAccessUpdate | None:
    return SSH_ACCESS_STORE.get(server_id)


def update_server_ssh_access(server_id: str, payload: ServerSshAccessUpdate) -> ServerSshAccessPublic | None:
    if not any(server.id == server_id for server in FOUNDATION_SERVERS):
        return None
    SSH_ACCESS_STORE[server_id] = payload
    return _public_ssh_access(payload)


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
