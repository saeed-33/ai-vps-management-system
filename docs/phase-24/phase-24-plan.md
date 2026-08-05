# Phase 24: Periodic Monitoring Report Analysis

## Objective

Move from report collection only to a usable first layer of periodic monitoring report analysis.

This phase intentionally keeps the analysis deterministic and rule-based. No LLM, RAG, specialist agent, or solution execution is introduced here. The goal is to make every periodic monitoring report explainable, storable, and visible in the admin panel before adding deeper AI analysis.

## Required Work

- Add an analysis object to every server sub-agent report.
- Detect basic warning and critical findings from collected metrics.
- Store the analysis with periodic monitoring reports in PostgreSQL.
- Load stored analysis when reading monitoring cycles.
- Show report analysis in the admin panel.
- Remove development notes from the admin panel user-facing text.
- Update tests and documentation.

## Analysis Scope

The current analysis checks:

- CPU usage percentage.
- Memory usage percentage.
- Root disk usage percentage.
- Load average normalized per core.
- Failed systemd units.
- Metric collection failure.

## Out Of Scope

- RAG analysis.
- LLM-generated diagnosis.
- Specialist monitoring agents.
- Solution recommendation.
- Sandbox execution.
- Automatic remediation.

These remain later phases after periodic monitoring reports are stable.
