# AI VPS Agent

Agent runtime foundation for the AI VPS Management System.

## Current Scope

This package provides the periodic monitoring agent foundation:

- Periodic monitoring orchestrator.
- Logical server sub-agent per server.
- Read-only baseline collector contract.
- Fixture collector for development.
- Periodic report models.

It does not yet provide SSH, MCP, specialist agents, issue analysis, solutions, or sandbox execution.

## Run Tests

```bash
uv run pytest
```

If the environment was not synced with dev dependencies yet:

```bash
uv run --extra dev pytest
```
