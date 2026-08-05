from collections import Counter

from control_plane_api.schemas.allowed_tools import (
    AllowedToolDetail,
    AllowedToolsListResponse,
    AllowedToolsSummaryResponse,
    ToolGuardrail,
)

FOUNDATION_TOOLS = [
    AllowedToolDetail(
        id="tool-uptime",
        code="uptime",
        name="Uptime",
        category="system",
        version=1,
        status="active",
        execution_scope="server_readonly",
        read_only=True,
        used_by=["profile-linux-baseline", "cpu-memory-specialist"],
        source="foundation-fixture",
        description="Reads uptime and load averages without mutating system state.",
        command_shape="uptime",
        guardrails=[
            ToolGuardrail(rule="No arguments are accepted.", reason="The command has enough baseline signal as-is."),
            ToolGuardrail(rule="Read-only execution only.", reason="Monitoring must not mutate the server."),
        ],
        output_contract=["uptime", "load_1m", "load_5m", "load_15m"],
    ),
    AllowedToolDetail(
        id="tool-df",
        code="df",
        name="Disk Free",
        category="storage",
        version=1,
        status="active",
        execution_scope="server_readonly",
        read_only=True,
        used_by=["profile-linux-baseline", "storage-specialist"],
        source="foundation-fixture",
        description="Reads filesystem capacity and usage.",
        command_shape="df -P -T",
        guardrails=[
            ToolGuardrail(rule="Use portable output mode.", reason="Parsers need stable columns."),
            ToolGuardrail(rule="No delete or cleanup command is bundled.", reason="Cleanup is a solution, not a tool read."),
        ],
        output_contract=["filesystem", "type", "size", "used", "available", "usage_percent", "mountpoint"],
    ),
    AllowedToolDetail(
        id="tool-systemctl-status",
        code="systemctl_status",
        name="Systemctl Status",
        category="services",
        version=1,
        status="active",
        execution_scope="server_readonly",
        read_only=True,
        used_by=["profile-linux-baseline", "nginx-health-specialist"],
        source="foundation-fixture",
        description="Reads service state without starting, stopping, restarting, or reloading services.",
        command_shape="systemctl status <approved-unit> --no-pager",
        guardrails=[
            ToolGuardrail(rule="Unit name must be approved by profile or specialist agent.", reason="Avoid broad probing."),
            ToolGuardrail(rule="Disallow start, stop, restart, reload, enable, and disable.", reason="Those are mutations."),
        ],
        output_contract=["unit", "load_state", "active_state", "sub_state", "recent_log_excerpt"],
    ),
    AllowedToolDetail(
        id="tool-journalctl-readonly",
        code="journalctl_readonly",
        name="Journalctl Readonly",
        category="logs",
        version=1,
        status="active",
        execution_scope="server_readonly",
        read_only=True,
        used_by=["nginx-health-specialist"],
        source="foundation-fixture",
        description="Reads bounded service logs for monitoring analysis.",
        command_shape="journalctl -u <approved-unit> --since <bounded-window> --no-pager",
        guardrails=[
            ToolGuardrail(rule="Require bounded time window.", reason="Avoid excessive log reads."),
            ToolGuardrail(rule="Require approved unit.", reason="Limit data access to intended monitoring scope."),
        ],
        output_contract=["unit", "time_window", "entries", "error_count", "warning_count"],
    ),
    AllowedToolDetail(
        id="tool-nginx-test-config",
        code="nginx_test_config",
        name="Nginx Config Test",
        category="web",
        version=1,
        status="draft",
        execution_scope="server_readonly",
        read_only=True,
        used_by=["profile-nginx-health", "nginx-health-specialist"],
        source="foundation-fixture",
        description="Validates Nginx configuration syntax without reloading the service.",
        command_shape="nginx -t",
        guardrails=[
            ToolGuardrail(rule="Do not pair with reload.", reason="Validation is allowed, mutation is not."),
            ToolGuardrail(rule="Capture stderr safely.", reason="Nginx writes validation details to stderr."),
        ],
        output_contract=["valid", "message", "config_path"],
    ),
]


def list_allowed_tools() -> AllowedToolsListResponse:
    return AllowedToolsListResponse(tools=FOUNDATION_TOOLS)


def summarize_allowed_tools() -> AllowedToolsSummaryResponse:
    by_category = Counter(tool.category for tool in FOUNDATION_TOOLS)
    by_scope = Counter(tool.execution_scope for tool in FOUNDATION_TOOLS)
    return AllowedToolsSummaryResponse(
        total=len(FOUNDATION_TOOLS),
        active=sum(1 for tool in FOUNDATION_TOOLS if tool.status == "active"),
        draft=sum(1 for tool in FOUNDATION_TOOLS if tool.status == "draft"),
        read_only=sum(1 for tool in FOUNDATION_TOOLS if tool.read_only),
        by_category=dict(sorted(by_category.items())),
        by_scope=dict(sorted(by_scope.items())),
    )


def get_allowed_tool(tool_id: str) -> AllowedToolDetail | None:
    return next((tool for tool in FOUNDATION_TOOLS if tool.id == tool_id or tool.code == tool_id), None)
