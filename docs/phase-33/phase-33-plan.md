# Phase 33: Ollama LLM Runtime Configuration

## Required Work

- Enable local LLM report analysis through Ollama.
- Configure the API `.env` with a locally available model.
- Keep LLM final analysis enabled by default for local development.
- Document the required Ollama settings.
- Restart and verify the backend.

## Implementation Plan

- Detect available local Ollama models.
- Configure `LLM_ANALYSIS_PROVIDER=ollama`.
- Configure `LLM_ANALYSIS_MODEL` to an installed local model.
- Increase timeout for local model inference.
- Update `.env.example` and API README.
- Restart services and verify readiness.
