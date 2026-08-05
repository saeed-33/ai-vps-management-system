from uuid import NAMESPACE_URL, UUID, uuid5

from sqlalchemy import text

from control_plane_api.core.config import Settings
from control_plane_api.core.database import get_session_maker
from control_plane_api.schemas.periodic_monitoring import PeriodicMonitoringCycleReport


def stable_uuid(value: str) -> UUID:
    return uuid5(NAMESPACE_URL, f"ai-vps-management-system:{value}")


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
                server_uuid = stable_uuid(report.server_id)
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
                            id, cycle_id, server_id, status, started_at, completed_at, initial_analysis, final_analysis
                        )
                        VALUES (
                            :id, :cycle_id, :server_id, :status, :started_at, :completed_at,
                            CAST(:initial_analysis AS jsonb), CAST(:final_analysis AS jsonb)
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
                        "initial_analysis": "{}",
                        "final_analysis": "{}",
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
