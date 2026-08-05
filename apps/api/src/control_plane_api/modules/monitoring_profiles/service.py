from collections import Counter
import json

from sqlalchemy import text

from control_plane_api.core.config import Settings
from control_plane_api.core.database import get_session_maker
from control_plane_api.schemas.monitoring_profiles import (
    MonitoringInstruction,
    MonitoringProfileCreate,
    MonitoringProfileDetail,
    MonitoringProfilesListResponse,
    MonitoringProfilesSummaryResponse,
    MonitoringTool,
)

MEMORY_PROFILE_STORE: dict[str, MonitoringProfileDetail] = {}

FOUNDATION_PROFILES = [
    MonitoringProfileDetail(
        id="profile-linux-baseline",
        name="Linux Baseline",
        domain="system",
        version=1,
        status="active",
        assigned_servers=1,
        instructions_count=4,
        specialist_agents=["cpu-memory-specialist", "storage-specialist"],
        source="foundation-fixture",
        description="Read-only baseline profile for collecting Linux CPU, memory, load, disk, and service evidence.",
        tools=[
            MonitoringTool(code="uptime", purpose="Read load average and uptime.", read_only=True),
            MonitoringTool(code="free_m", purpose="Read memory pressure.", read_only=True),
            MonitoringTool(code="df_portable", purpose="Read filesystem utilization.", read_only=True),
            MonitoringTool(code="systemctl_failed", purpose="Read failed service units.", read_only=True),
        ],
        monitoring_instructions=[
            MonitoringInstruction(
                id="linux-baseline-uptime",
                title="Collect load average and uptime",
                tool_code="uptime",
                command="uptime",
                purpose="Capture uptime and load averages as context for the LLM analysis.",
                parser="uptime",
                expected_evidence=["uptime", "load average"],
            ),
            MonitoringInstruction(
                id="linux-baseline-memory",
                title="Collect memory usage",
                tool_code="free_m",
                command="free -m",
                purpose="Capture memory totals, used memory, free memory, and buffers/cache.",
                parser="free_m",
                expected_evidence=["Mem", "Swap"],
            ),
            MonitoringInstruction(
                id="linux-baseline-filesystems",
                title="Collect mounted filesystem usage",
                tool_code="df_portable",
                command="df -P -T",
                purpose="Capture portable filesystem usage evidence, including root filesystem usage.",
                parser="df_portable",
                expected_evidence=["Filesystem", "Mounted on"],
            ),
            MonitoringInstruction(
                id="linux-baseline-failed-units",
                title="Collect failed systemd units",
                tool_code="systemctl_failed",
                command="systemctl --failed --no-pager",
                purpose="Capture failed system services without mutating server state.",
                parser="systemctl_failed",
                expected_evidence=["failed units", "0 loaded units listed"],
            ),
        ],
        analysis_instructions=[
            "Use raw command evidence first, then parsed metrics as a compact index.",
            "Do not infer an incident from a single number alone.",
            "Mention missing commands, failed commands, or incomplete evidence as confidence limitations.",
        ],
    ),
    MonitoringProfileDetail(
        id="profile-nginx-health",
        name="Nginx Health",
        domain="web",
        version=1,
        status="draft",
        assigned_servers=0,
        instructions_count=4,
        specialist_agents=["nginx-health-specialist"],
        source="foundation-fixture",
        description="Read-only profile for collecting Nginx availability, config, port, and recent log evidence.",
        tools=[
            MonitoringTool(code="systemctl_status", purpose="Read Nginx service state.", read_only=True),
            MonitoringTool(code="nginx_test_config", purpose="Validate Nginx config syntax.", read_only=True),
            MonitoringTool(code="ss", purpose="Read listening ports.", read_only=True),
            MonitoringTool(code="journalctl_readonly", purpose="Read recent service logs.", read_only=True),
        ],
        monitoring_instructions=[
            MonitoringInstruction(
                id="nginx-service-state",
                title="Collect Nginx service state",
                tool_code="systemctl_status",
                command="systemctl status nginx --no-pager",
                purpose="Capture service activity and recent unit status without restarting or reloading Nginx.",
                parser=None,
                expected_evidence=["Active", "Loaded"],
            ),
            MonitoringInstruction(
                id="nginx-config-test",
                title="Validate Nginx config syntax",
                tool_code="nginx_test_config",
                command="nginx -t",
                purpose="Capture config validation output as evidence.",
                parser=None,
                expected_evidence=["syntax is ok", "test is successful"],
            ),
            MonitoringInstruction(
                id="nginx-listen-ports",
                title="Collect listening ports",
                tool_code="ss",
                command="ss -ltnp",
                purpose="Capture listening TCP ports and owning processes.",
                parser=None,
                expected_evidence=[":80", ":443", "LISTEN"],
            ),
            MonitoringInstruction(
                id="nginx-recent-logs",
                title="Collect recent Nginx logs",
                tool_code="journalctl_readonly",
                command="journalctl -u nginx --since '30 minutes ago' --no-pager -n 120",
                purpose="Capture recent Nginx service logs for LLM analysis.",
                parser=None,
                expected_evidence=["nginx"],
            ),
        ],
        analysis_instructions=[
            "Validate whether this server is expected to run Nginx before concluding outage.",
            "Use service state, config test, ports, and logs together.",
            "Never propose reload or restart as an automatic action in this phase.",
        ],
    ),
]


async def list_monitoring_profiles(settings: Settings | None = None) -> MonitoringProfilesListResponse:
    profiles = await _profiles(settings)
    return MonitoringProfilesListResponse(
        profiles=[
            profile.model_copy(
                update={
                    "instructions_count": len(profile.monitoring_instructions),
                }
            )
            for profile in profiles
        ]
    )


async def summarize_monitoring_profiles(settings: Settings | None = None) -> MonitoringProfilesSummaryResponse:
    profiles = await _profiles(settings)
    by_domain = Counter(profile.domain for profile in profiles)
    return MonitoringProfilesSummaryResponse(
        total=len(profiles),
        active=sum(1 for profile in profiles if profile.status == "active"),
        draft=sum(1 for profile in profiles if profile.status == "draft"),
        by_domain=dict(sorted(by_domain.items())),
    )


async def get_monitoring_profile(profile_id: str, settings: Settings | None = None) -> MonitoringProfileDetail | None:
    profiles = await _profiles(settings)
    return next((profile for profile in profiles if profile.id == profile_id), None)


def get_foundation_monitoring_profile(profile_id: str) -> MonitoringProfileDetail | None:
    return next((profile for profile in [*FOUNDATION_PROFILES, *MEMORY_PROFILE_STORE.values()] if profile.id == profile_id), None)


async def create_monitoring_profile(settings: Settings, payload: MonitoringProfileCreate) -> MonitoringProfileDetail:
    profile = _profile_from_payload(payload, source="database" if settings.database_url else "memory-fallback")
    if settings.database_url:
        stored = await _try_database_create_profile(settings, profile)
        if stored is None:
            raise MonitoringProfilePersistenceError("Database is configured but the monitoring profile could not be persisted.")
        return stored
    if profile.id in {existing.id for existing in FOUNDATION_PROFILES} or profile.id in MEMORY_PROFILE_STORE:
        raise MonitoringProfilePersistenceError("Monitoring profile already exists.")
    MEMORY_PROFILE_STORE[profile.id] = profile
    return profile


async def get_monitoring_instructions(
    profile_ids: list[str],
    settings: Settings | None = None,
) -> list[MonitoringInstruction]:
    instructions: list[MonitoringInstruction] = []
    seen_tool_codes: set[str] = set()
    profiles_by_id = {profile.id: profile for profile in await _profiles(settings)}
    for profile_id in profile_ids:
        profile = profiles_by_id.get(profile_id)
        if profile is None:
            continue
        for instruction in profile.monitoring_instructions:
            if instruction.tool_code in seen_tool_codes:
                continue
            instructions.append(instruction)
            seen_tool_codes.add(instruction.tool_code)
    return instructions


class MonitoringProfilePersistenceError(RuntimeError):
    pass


async def _profiles(settings: Settings | None = None) -> list[MonitoringProfileDetail]:
    database_profiles = await _try_database_list_profiles(settings) if settings and settings.database_url else []
    profiles = [*FOUNDATION_PROFILES, *MEMORY_PROFILE_STORE.values()]
    existing_ids = {profile.id for profile in profiles}
    profiles.extend(profile for profile in database_profiles if profile.id not in existing_ids)
    return profiles


def _profile_from_payload(payload: MonitoringProfileCreate, *, source: str) -> MonitoringProfileDetail:
    return MonitoringProfileDetail(
        id=payload.id,
        name=payload.name,
        domain=payload.domain,
        version=1,
        status=payload.status,
        assigned_servers=0,
        instructions_count=len(payload.monitoring_instructions),
        specialist_agents=payload.specialist_agents,
        source=source,
        description=payload.description,
        tools=[
            MonitoringTool(code=instruction.tool_code, purpose=instruction.purpose, read_only=instruction.read_only)
            for instruction in payload.monitoring_instructions
        ],
        monitoring_instructions=payload.monitoring_instructions,
        analysis_instructions=payload.analysis_instructions,
    )


async def _try_database_list_profiles(settings: Settings | None) -> list[MonitoringProfileDetail]:
    if settings is None or not settings.database_url:
        return []
    try:
        session_maker = get_session_maker(settings)
        async with session_maker() as session:
            rows = (
                await session.execute(
                    text(
                        """
                        SELECT
                            p.code,
                            p.name,
                            p.category,
                            p.status,
                            p.current_version,
                            v.definition
                        FROM monitoring_profiles p
                        JOIN monitoring_profile_versions v
                            ON v.profile_id = p.id AND v.version = p.current_version
                        ORDER BY p.created_at DESC
                        """
                    )
                )
            ).mappings().all()
        return [_profile_from_database_row(row) for row in rows]
    except Exception:
        return []


async def _try_database_create_profile(
    settings: Settings,
    profile: MonitoringProfileDetail,
) -> MonitoringProfileDetail | None:
    try:
        definition = {
            "description": profile.description,
            "tools": [tool.model_dump() for tool in profile.tools],
            "monitoring_instructions": [instruction.model_dump() for instruction in profile.monitoring_instructions],
            "analysis_instructions": profile.analysis_instructions,
            "specialist_agents": profile.specialist_agents,
        }
        session_maker = get_session_maker(settings)
        async with session_maker() as session:
            async with session.begin():
                row = (
                    await session.execute(
                        text(
                            """
                            INSERT INTO monitoring_profiles (code, name, category, status)
                            VALUES (:code, :name, :category, :status)
                            RETURNING id
                            """
                        ),
                        {
                            "code": profile.id,
                            "name": profile.name,
                            "category": profile.domain,
                            "status": profile.status,
                        },
                    )
                ).mappings().one()
                await session.execute(
                    text(
                        """
                        INSERT INTO monitoring_profile_versions (profile_id, version, definition, changelog)
                        VALUES (:profile_id, 1, CAST(:definition AS jsonb), :changelog)
                        """
                    ),
                    {
                        "profile_id": row["id"],
                        "definition": json.dumps(definition),
                        "changelog": "Initial monitoring instruction profile.",
                    },
                )
                await session.execute(
                    text(
                        """
                        UPDATE monitoring_profiles
                        SET current_version = 1, updated_at = now()
                        WHERE id = :profile_id
                        """
                    ),
                    {"profile_id": row["id"]},
                )
        return profile
    except Exception:
        return None


def _profile_from_database_row(row: object) -> MonitoringProfileDetail:
    mapping = dict(row)  # type: ignore[arg-type]
    definition = mapping.get("definition") or {}
    if isinstance(definition, str):
        definition = json.loads(definition)
    instructions = [
        MonitoringInstruction.model_validate(instruction)
        for instruction in definition.get("monitoring_instructions", [])
    ]
    tools = [
        MonitoringTool.model_validate(tool)
        for tool in definition.get("tools", [])
    ] or [
        MonitoringTool(code=instruction.tool_code, purpose=instruction.purpose, read_only=instruction.read_only)
        for instruction in instructions
    ]
    return MonitoringProfileDetail(
        id=str(mapping["code"]),
        name=str(mapping["name"]),
        domain=str(mapping["category"]),
        version=int(mapping["current_version"] or 1),
        status=str(mapping["status"]),
        assigned_servers=0,
        instructions_count=len(instructions),
        specialist_agents=list(definition.get("specialist_agents") or []),
        source="database",
        description=str(definition.get("description") or ""),
        tools=tools,
        monitoring_instructions=instructions,
        analysis_instructions=list(definition.get("analysis_instructions") or []),
    )
