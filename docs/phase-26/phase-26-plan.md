# Phase 26: Separate Periodic Analysis Reports

## Objective

Close the remaining gap before moving to chat: periodic monitoring analysis must be available as separate analysis reports, not only as embedded fields inside server monitoring reports.

## Required Work

- Add an API model for standalone periodic monitoring analysis reports.
- Add an endpoint that returns analysis reports separately from raw monitoring reports.
- Keep the analysis report linked to:
  - source cycle,
  - source server report,
  - server,
  - generated timestamp.
- Show separate analysis reports in the admin panel.
- Add tests proving that running a periodic cycle produces a separate analysis report.

## Out Of Scope

- LLM/RAG chat over reports.
- Issue creation.
- Specialist agent execution.
- Remediation or solution generation.
