# AI VPS Agent

Agent runtime foundation for the AI VPS Management System.

## Current Scope

This package provides the periodic monitoring agent foundation:

- Periodic monitoring orchestrator.
- Logical server sub-agent per server.
- LangGraph-based orchestration for periodic monitoring cycles.
- Read-only baseline collector contract.
- Fixture collector for development.
- SSH command policy and read-only SSH client foundation.
- Instruction-driven command policy from monitoring profiles.
- Baseline parsers for read-only Linux commands.
- Periodic report models.

It does not yet provide MCP, specialist agents, issue workflows, solutions, or sandbox execution.

## Run Tests

```bash
uv run pytest
```

If the environment was not synced with dev dependencies yet:

```bash
uv run --extra dev pytest
```
