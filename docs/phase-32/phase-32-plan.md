# Phase 32: Instruction-Driven Monitoring Profiles

## Required Work

- Remove threshold-based monitoring profile design from active code.
- Make monitoring profiles define read-only execution instructions.
- Let the user define periodic monitoring instructions from the admin panel.
- Use an agent orchestration library instead of a hand-written orchestration loop.
- Keep final report analysis LLM-only.

## Design Decisions

- Monitoring profiles are not rule engines.
- A monitoring profile defines what evidence the agent should collect.
- The LLM is responsible for interpreting evidence and producing the final diagnostic report.
- Numeric values can be evidence, but they are not encoded as threshold rules in the system model.
- Periodic monitoring orchestration now uses LangGraph so later specialist-agent stages can be added as graph nodes.

## Implementation Plan

- Replace `thresholds` with `monitoring_instructions`.
- Replace `thresholds_count` with `instructions_count`.
- Add a `POST /api/v1/monitoring-profiles` endpoint.
- Store custom profile definitions in `monitoring_profile_versions.definition`.
- Pass profile instructions into the agent during periodic monitoring.
- Build SSH command policy from profile instructions.
- Add LangGraph to the agent package and use it in `PeriodicMonitoringAgent`.
- Update tests, UI, and documentation.
