# Phase 25: Profile-Aware Periodic Report Analysis

## Objective

Continue periodic report analysis by using monitoring profile definitions as the source of analysis rules.

Phase 24 added a deterministic analysis layer with fixed baseline thresholds. Phase 25 moves that logic closer to the intended architecture: monitoring profiles define thresholds, interpretation notes, and related specialist agents. The control plane evaluates periodic reports against those profile definitions.

## Required Work

- Evaluate collected metrics against thresholds from assigned monitoring profiles.
- Include the profile id and interpretation note in each finding.
- Record profile coverage gaps when a profile expects metrics that are not present in the report.
- Suggest specialist agents as analysis metadata only.
- Show richer analysis metadata in the admin panel.
- Keep specialist agent execution, solution generation, and remediation out of scope.
- Update tests and documentation.

## Out Of Scope

- Running specialist agents.
- RAG or LLM analysis.
- Historical trend analysis.
- Automated issue creation.
- Any solution execution.
