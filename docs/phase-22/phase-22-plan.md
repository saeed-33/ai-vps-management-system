# Phase 22: Periodic Monitoring Server UUID Persistence Fix

## Goal

Fix duplicate server insertion during periodic monitoring report persistence for database-backed servers.

## Required Work

- Preserve real UUID server ids.
- Keep stable UUID mapping for text fixture ids.
- Add regression coverage.
