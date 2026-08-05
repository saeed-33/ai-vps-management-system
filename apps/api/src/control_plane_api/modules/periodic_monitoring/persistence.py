import json
from uuid import NAMESPACE_URL, UUID, uuid5

from sqlalchemy import text

from control_plane_api.core.config import Settings
from control_plane_api.core.database import get_session_maker
from control_plane_api.schemas.periodic_monitoring import (
    MonitoringMetricSample,
    PeriodicMonitoringCycleReport,
    ServerSubAgentReport,
)


def stable_uuid(value: str) -> UUID:
    return uuid5(NAMESPACE_URL, f"ai-vps-management-system:{value}")


def database_uuid(value: str) -> UUID:
    try:
        return UUID(value)
    except ValueError:
        return stable_uuid(value)


async def persist_periodic_monitoring_cycle(
    cycle: PeriodicMonitoringCycleReport,
    settings: Settings,
) -> bool:
    if not settings.database_url:
        return False

    session_maker = get_session_maker(settings)
    async with session_maker() as session:
        async with session.begin():
            cycle_uuid = stable_uuid(cycle.cycle_id)
            await session.execute(
                text(
                    """
                    INSERT INTO monitoring_cycles (
                        id, cycle_key, status, started_at, completed_at, triggered_by, summary
                    )
                    VALUES (
                        :id, :cycle_key, :status, :started_at, :completed_at, :triggered_by, CAST(:summary AS jsonb)
                    )
                    ON CONFLICT (cycle_key) DO NOTHING
                    """
                ),
                {
                    "id": cycle_uuid,
                    "cycle_key": cycle.cycle_id,
                    "status": cycle.status,
                    "started_at": cycle.started_at,
                    "completed_at": cycle.completed_at,
                    "triggered_by": cycle.trigger,
                    "summary": cycle.model_dump_json(exclude={"reports"}),
                },
            )

            for report in cycle.reports:
                server_uuid = database_uuid(report.server_id)
                await session.execute(
                    text(
                        """
                        INSERT INTO servers (
                            id, name, hostname, environment, status, metadata
                        )
                        VALUES (
                            :id, :name, :hostname, 'development', 'active', CAST(:metadata AS jsonb)
                        )
                        ON CONFLICT (id) DO UPDATE SET
                            name = EXCLUDED.name,
                            hostname = EXCLUDED.hostname,
                            updated_at = now()
                        """
                    ),
                    {
                        "id": server_uuid,
                        "name": report.server_name,
                        "hostname": report.server_name,
                        "metadata": '{"source":"periodic-monitoring-foundation"}',
                    },
                )

                report_uuid = stable_uuid(f"{cycle.cycle_id}:{report.server_id}")
                await session.execute(
                    text(
                        """
                        INSERT INTO periodic_monitoring_reports (
                            id, cycle_id, server_id, status, started_at, completed_at,
                            raw_snapshot, initial_analysis, final_analysis
                        )
                        VALUES (
                            :id, :cycle_id, :server_id, :status, :started_at, :completed_at,
                            CAST(:raw_snapshot AS jsonb), CAST(:initial_analysis AS jsonb), CAST(:final_analysis AS jsonb)
                        )
                        ON CONFLICT (cycle_id, server_id) DO NOTHING
                        """
                    ),
                    {
                        "id": report_uuid,
                        "cycle_id": cycle_uuid,
                        "server_id": server_uuid,
                        "status": report.status,
                        "started_at": report.started_at,
                        "completed_at": report.completed_at,
                        "raw_snapshot": json.dumps(report.raw_snapshot),
                        "initial_analysis": report.analysis.model_dump_json(),
                        "final_analysis": report.analysis.model_dump_json(),
                    },
                )

                for metric in report.metrics:
                    metric_uuid = stable_uuid(f"{cycle.cycle_id}:{report.server_id}:{metric.metric}:{metric.source_tool}")
                    await session.execute(
                        text(
                            """
                            INSERT INTO monitoring_metrics (
                                id, report_id, metric_key, metric_domain, collected_at, value, raw_output_ref
                            )
                            VALUES (
                                :id, :report_id, :metric_key, :metric_domain, :collected_at,
                                CAST(:value AS jsonb), :raw_output_ref
                            )
                            ON CONFLICT (id) DO NOTHING
                            """
                        ),
                        {
                            "id": metric_uuid,
                            "report_id": report_uuid,
                            "metric_key": metric.metric,
                            "metric_domain": metric.domain,
                            "collected_at": report.completed_at,
                            "value": metric.model_dump_json(),
                            "raw_output_ref": metric.source_tool,
                        },
                    )
    return True


async def load_periodic_monitoring_cycles(
    settings: Settings,
    *,
    limit: int = 10,
) -> list[PeriodicMonitoringCycleReport] | None:
    if not settings.database_url:
        return None

    session_maker = get_session_maker(settings)
    async with session_maker() as session:
        cycle_rows = (
            await session.execute(
                text(
                    """
                    SELECT
                        id::text AS id,
                        cycle_key,
                        status,
                        started_at,
                        completed_at,
                        triggered_by,
                        summary
                    FROM monitoring_cycles
                    ORDER BY completed_at DESC NULLS LAST, created_at DESC
                    LIMIT :limit
                    """
                ),
                {"limit": limit},
            )
        ).mappings().all()

        cycles: list[PeriodicMonitoringCycleReport] = []
        for cycle_row in cycle_rows:
            report_rows = (
                await session.execute(
                    text(
                        """
                        SELECT
                            r.id::text AS report_id,
                            r.status,
                            r.started_at,
                            r.completed_at,
                            r.raw_snapshot,
                            r.final_analysis,
                            s.id::text AS server_id,
                            s.name AS server_name,
                            s.metadata AS server_metadata
                        FROM periodic_monitoring_reports r
                        JOIN servers s ON s.id = r.server_id
                        WHERE r.cycle_id = :cycle_id
                        ORDER BY r.created_at ASC
                        """
                    ),
                    {"cycle_id": cycle_row["id"]},
                )
            ).mappings().all()

            reports: list[ServerSubAgentReport] = []
            for report_row in report_rows:
                metric_rows = (
                    await session.execute(
                        text(
                            """
                            SELECT value
                            FROM monitoring_metrics
                            WHERE report_id = :report_id
                            ORDER BY created_at ASC
                            """
                        ),
                        {"report_id": report_row["report_id"]},
                    )
                ).mappings().all()
                metadata = _json_object(report_row.get("server_metadata"))
                reports.append(
                    ServerSubAgentReport(
                        sub_agent_id=f"server-sub-agent-{report_row['server_id']}",
                        server_id=str(report_row["server_id"]),
                        server_name=str(report_row["server_name"]),
                        status=str(report_row["status"]),
                        started_at=report_row["started_at"],
                        completed_at=report_row["completed_at"],
                        monitoring_profiles=list(metadata.get("assigned_monitoring_profiles") or []),
                        metrics=[MonitoringMetricSample.model_validate(_json_object(row["value"])) for row in metric_rows],
                        raw_snapshot=_extract_raw_snapshot(report_row.get("raw_snapshot")),
                        analysis=_json_object(report_row.get("final_analysis")),
                        collection_summary="Baseline metrics loaded from PostgreSQL.",
                    )
                )

            summary = _json_object(cycle_row["summary"])
            cycles.append(
                PeriodicMonitoringCycleReport(
                    cycle_id=str(cycle_row["cycle_key"]),
                    trigger=str(cycle_row["triggered_by"]),
                    status=str(cycle_row["status"]),
                    started_at=cycle_row["started_at"],
                    completed_at=cycle_row["completed_at"],
                    servers_planned=int(summary.get("servers_planned", len(reports))),
                    servers_checked=int(summary.get("servers_checked", len(reports))),
                    reports_count=int(summary.get("reports_count", len(reports))),
                    reports=reports,
                    scope_note=str(summary.get("scope_note", "Loaded from PostgreSQL.")),
                )
            )
    return cycles


def _json_object(value: object) -> dict[str, object]:
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        import json

        return dict(json.loads(value))
    return dict(value)  # type: ignore[arg-type]


def _extract_raw_snapshot(value: object) -> dict[str, object]:
    raw = _json_object(value)
    nested = raw.get("raw_snapshot")
    if isinstance(nested, dict):
        return nested
    return raw
