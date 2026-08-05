from collections import Counter

from control_plane_api.schemas.monitoring_profiles import (
    MonitoringProfileDetail,
    MonitoringProfilesListResponse,
    MonitoringProfilesSummaryResponse,
    MonitoringThreshold,
    MonitoringTool,
)

FOUNDATION_PROFILES = [
    MonitoringProfileDetail(
        id="profile-linux-baseline",
        name="Linux Baseline",
        domain="system",
        version=1,
        status="active",
        assigned_servers=1,
        thresholds_count=5,
        specialist_agents=["cpu-memory-specialist", "storage-specialist"],
        source="foundation-fixture",
        description="Read-only baseline profile for CPU, memory, load, disk, and service health.",
        thresholds=[
            MonitoringThreshold(
                metric="cpu_usage_percent",
                warning=75,
                critical=90,
                unit="percent",
                interpretation_note="Low CPU can still be suspicious when paired with stalled workers or queue growth.",
            ),
            MonitoringThreshold(
                metric="memory_usage_percent",
                warning=80,
                critical=92,
                unit="percent",
                interpretation_note="Available memory trend matters more than one isolated sample.",
            ),
            MonitoringThreshold(
                metric="load_1m_per_core",
                warning=1.5,
                critical=2.5,
                unit="ratio",
                interpretation_note="Compare load with runnable processes and IO wait before declaring CPU pressure.",
            ),
            MonitoringThreshold(
                metric="root_disk_usage_percent",
                warning=80,
                critical=92,
                unit="percent",
                interpretation_note="Growth rate can make a lower usage value urgent.",
            ),
            MonitoringThreshold(
                metric="failed_systemd_units",
                warning=1,
                critical=3,
                unit="count",
                interpretation_note="Any critical service failure should trigger specialist analysis.",
            ),
        ],
        tools=[
            MonitoringTool(code="uptime", purpose="Read load average and uptime.", read_only=True),
            MonitoringTool(code="free", purpose="Read memory pressure.", read_only=True),
            MonitoringTool(code="df", purpose="Read filesystem utilization.", read_only=True),
            MonitoringTool(code="systemctl_status", purpose="Read service state.", read_only=True),
        ],
        analysis_guidelines=[
            "Treat thresholds as signals, not final decisions.",
            "Compare values with recent trend and service symptoms.",
            "Trigger specialist agents only for domains with suspicious evidence.",
        ],
    ),
    MonitoringProfileDetail(
        id="profile-nginx-health",
        name="Nginx Health",
        domain="web",
        version=1,
        status="draft",
        assigned_servers=0,
        thresholds_count=4,
        specialist_agents=["nginx-health-specialist"],
        source="foundation-fixture",
        description="Read-only profile for Nginx availability, config validity, ports, and error logs.",
        thresholds=[
            MonitoringThreshold(
                metric="nginx_active_state",
                warning=None,
                critical=0,
                unit="boolean",
                interpretation_note="Inactive Nginx is critical only when the server is expected to serve web traffic.",
            ),
            MonitoringThreshold(
                metric="http_5xx_rate_percent",
                warning=2,
                critical=8,
                unit="percent",
                interpretation_note="A low rate can still be urgent on high-value endpoints.",
            ),
            MonitoringThreshold(
                metric="listen_port_80_443_count",
                warning=1,
                critical=0,
                unit="count",
                interpretation_note="Port state must be interpreted against configured virtual hosts.",
            ),
            MonitoringThreshold(
                metric="recent_error_log_count",
                warning=20,
                critical=100,
                unit="count",
                interpretation_note="New error patterns matter more than repeated known benign lines.",
            ),
        ],
        tools=[
            MonitoringTool(code="systemctl_status", purpose="Read Nginx service state.", read_only=True),
            MonitoringTool(code="nginx_test_config", purpose="Validate Nginx config syntax.", read_only=True),
            MonitoringTool(code="ss", purpose="Read listening ports.", read_only=True),
            MonitoringTool(code="journalctl_readonly", purpose="Read recent service logs.", read_only=True),
        ],
        analysis_guidelines=[
            "Validate service expectation before reporting outage.",
            "Use config test and logs together before proposing a fix.",
            "Never reload or restart Nginx in this phase.",
        ],
    ),
]


def list_monitoring_profiles() -> MonitoringProfilesListResponse:
    return MonitoringProfilesListResponse(
        profiles=[
            profile.model_copy(
                update={
                    "thresholds_count": len(profile.thresholds),
                }
            )
            for profile in FOUNDATION_PROFILES
        ]
    )


def summarize_monitoring_profiles() -> MonitoringProfilesSummaryResponse:
    by_domain = Counter(profile.domain for profile in FOUNDATION_PROFILES)
    return MonitoringProfilesSummaryResponse(
        total=len(FOUNDATION_PROFILES),
        active=sum(1 for profile in FOUNDATION_PROFILES if profile.status == "active"),
        draft=sum(1 for profile in FOUNDATION_PROFILES if profile.status == "draft"),
        by_domain=dict(sorted(by_domain.items())),
    )


def get_monitoring_profile(profile_id: str) -> MonitoringProfileDetail | None:
    return next((profile for profile in FOUNDATION_PROFILES if profile.id == profile_id), None)
