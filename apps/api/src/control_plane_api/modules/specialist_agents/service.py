from collections import Counter

from control_plane_api.schemas.specialist_agents import (
    SpecialistAgentDetail,
    SpecialistAgentsListResponse,
    SpecialistAgentsSummaryResponse,
    SpecialistAgentToolPolicy,
    SpecialistAgentTrigger,
)

FOUNDATION_AGENTS = [
    SpecialistAgentDetail(
        id="cpu-memory-specialist",
        name="CPU and Memory Specialist",
        domain="system",
        version=1,
        status="active",
        execution_mode="read_only_analysis",
        trigger_profiles=["profile-linux-baseline"],
        allowed_tools_count=3,
        source="foundation-fixture",
        description="Investigates CPU, load, memory pressure, process symptoms, and suspicious low-utilization states.",
        triggers=[
            SpecialistAgentTrigger(
                profile_id="profile-linux-baseline",
                domain="system",
                trigger_condition="CPU, load, memory, or process behavior looks abnormal after baseline analysis.",
            )
        ],
        allowed_tools=[
            SpecialistAgentToolPolicy(tool_code="uptime", purpose="Read load and uptime.", required=True),
            SpecialistAgentToolPolicy(tool_code="free", purpose="Read memory pressure.", required=True),
            SpecialistAgentToolPolicy(tool_code="ps_readonly", purpose="Inspect process state without mutation.", required=True),
        ],
        analysis_contract=[
            "Compare CPU, load, memory, and runnable process evidence together.",
            "Flag low utilization as suspicious when workers are stalled or queues are growing.",
            "Do not recommend restarts unless a permitted solution exists later.",
        ],
        output_contract=[
            "specialist_summary",
            "evidence",
            "confidence",
            "suspected_root_cause",
            "recommended_next_step",
        ],
    ),
    SpecialistAgentDetail(
        id="storage-specialist",
        name="Storage Specialist",
        domain="storage",
        version=1,
        status="active",
        execution_mode="read_only_analysis",
        trigger_profiles=["profile-linux-baseline"],
        allowed_tools_count=3,
        source="foundation-fixture",
        description="Investigates disk usage, inode pressure, mount status, and fast growth risk.",
        triggers=[
            SpecialistAgentTrigger(
                profile_id="profile-linux-baseline",
                domain="storage",
                trigger_condition="Disk usage, inode pressure, mount state, or growth rate indicates possible storage risk.",
            )
        ],
        allowed_tools=[
            SpecialistAgentToolPolicy(tool_code="df", purpose="Read filesystem utilization.", required=True),
            SpecialistAgentToolPolicy(tool_code="du_limited", purpose="Read bounded directory size samples.", required=False),
            SpecialistAgentToolPolicy(tool_code="mount_readonly", purpose="Read mounted filesystem state.", required=False),
        ],
        analysis_contract=[
            "Treat growth rate as a first-class signal.",
            "Separate full disk, inode exhaustion, and missing mount cases.",
            "Never delete files or rotate logs in this phase.",
        ],
        output_contract=[
            "specialist_summary",
            "evidence",
            "risk_level",
            "suspected_root_cause",
            "safe_investigation_steps",
        ],
    ),
    SpecialistAgentDetail(
        id="nginx-health-specialist",
        name="Nginx Health Specialist",
        domain="web",
        version=1,
        status="draft",
        execution_mode="read_only_analysis",
        trigger_profiles=["profile-nginx-health"],
        allowed_tools_count=4,
        source="foundation-fixture",
        description="Investigates Nginx service state, config validity, listening ports, and recent error patterns.",
        triggers=[
            SpecialistAgentTrigger(
                profile_id="profile-nginx-health",
                domain="web",
                trigger_condition="Nginx service, config, port, or error-log evidence suggests a web-layer issue.",
            )
        ],
        allowed_tools=[
            SpecialistAgentToolPolicy(tool_code="systemctl_status", purpose="Read Nginx service state.", required=True),
            SpecialistAgentToolPolicy(tool_code="nginx_test_config", purpose="Validate config syntax.", required=True),
            SpecialistAgentToolPolicy(tool_code="ss", purpose="Read listening sockets.", required=True),
            SpecialistAgentToolPolicy(tool_code="journalctl_readonly", purpose="Read recent logs.", required=False),
        ],
        analysis_contract=[
            "Confirm whether the server is expected to serve traffic before reporting outage.",
            "Use config, service state, socket state, and logs as a combined evidence set.",
            "Never reload or restart Nginx in this phase.",
        ],
        output_contract=[
            "specialist_summary",
            "evidence",
            "config_health",
            "service_health",
            "recommended_next_step",
        ],
    ),
]


def list_specialist_agents() -> SpecialistAgentsListResponse:
    return SpecialistAgentsListResponse(
        agents=[
            agent.model_copy(update={"allowed_tools_count": len(agent.allowed_tools)}) for agent in FOUNDATION_AGENTS
        ]
    )


def summarize_specialist_agents() -> SpecialistAgentsSummaryResponse:
    by_domain = Counter(agent.domain for agent in FOUNDATION_AGENTS)
    by_execution_mode = Counter(agent.execution_mode for agent in FOUNDATION_AGENTS)
    return SpecialistAgentsSummaryResponse(
        total=len(FOUNDATION_AGENTS),
        active=sum(1 for agent in FOUNDATION_AGENTS if agent.status == "active"),
        draft=sum(1 for agent in FOUNDATION_AGENTS if agent.status == "draft"),
        by_domain=dict(sorted(by_domain.items())),
        by_execution_mode=dict(sorted(by_execution_mode.items())),
    )


def get_specialist_agent(agent_id: str) -> SpecialistAgentDetail | None:
    return next((agent for agent in FOUNDATION_AGENTS if agent.id == agent_id), None)
