from control_plane_api.schemas.servers import ServerDetail, ServersListResponse, ServersSummaryResponse, ServerSummary

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
    return next((server for server in FOUNDATION_SERVERS if server.id == server_id), None)
