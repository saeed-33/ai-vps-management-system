# Phase 31: Claude Project Evidence Alignment

## Required Work

- Inspect `E:\AI_VPS_Mamgment\claude_project`.
- Extract useful monitoring and reporting ideas from the old MCP implementation.
- Align periodic monitoring reports with the old evidence-rich report model.
- Keep final report analysis LLM-only.
- Preserve raw command evidence for LLM prompts, UI review, and database persistence.

## Findings From Claude Project

- The old project was an MCP server named `vps-monitor-complete`.
- It stored VMs, monitor profiles, and reports in local JSON files.
- Monitor profiles were structured as profile, aspects, and commands per aspect.
- Monitoring reports contained raw command output grouped by profile and aspect.
- Analysis reports were separate records from monitoring reports.
- The old reports gave the analyzer strong evidence, including command failures such as missing `mpstat`.

## Implementation Plan

- Add a structured collection result in the agent containing both parsed metrics and raw evidence.
- Capture SSH command results in `raw_snapshot.command_results`.
- Include raw evidence in the LLM analysis prompt.
- Persist `raw_snapshot` in PostgreSQL.
- Load `raw_snapshot` back when listing historical monitoring cycles.
- Display raw command evidence in the admin panel report view.
- Add a database migration for existing deployments.
- Run tests and build checks.
