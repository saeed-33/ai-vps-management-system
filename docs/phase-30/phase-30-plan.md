# Phase 30: LLM-Only Periodic Analysis

## Objective

Change periodic report analysis so the final analysis is produced exclusively by an LLM.

Rule-based threshold checks remain available only as internal signals sent to the LLM. They are no longer emitted as final diagnostic analysis.

## Required Work

- Make LLM the only source of final periodic analysis.
- Keep rule-based profile checks as prompt input only.
- Stop preserving rule-based output when LLM is disabled or fails.
- Return an explicit unavailable/failed analysis status when no LLM analysis is produced.
- Update tests and documentation.

## Out Of Scope

- Chat UI.
- RAG.
- Specialist agent execution.
- Solution execution.
