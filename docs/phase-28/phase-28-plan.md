# Phase 28: Optional LLM Analysis Enrichment

## Objective

Add an optional LLM analysis adapter before moving to the chat phase.

The LLM layer enriches periodic analysis reports with a deeper narrative, hypotheses, questions, and limitations. It does not replace rule-based analysis and it does not execute any solution.

## Required Work

- Add LLM analysis settings.
- Add an adapter boundary for LLM enrichment.
- Support disabled mode as the default.
- Support local Ollama enrichment.
- Preserve rule-based analysis when LLM enrichment fails.
- Store enrichment status inside the analysis report.
- Show LLM enrichment status in the admin panel.
- Document setup and fallback behavior.

## Out Of Scope

- Chat UI.
- RAG.
- OpenAI/Claude hosted provider integration.
- Specialist agent execution.
- Solution generation or remediation.

## Runtime Settings

```env
LLM_ANALYSIS_ENABLED=false
LLM_ANALYSIS_PROVIDER=disabled
LLM_ANALYSIS_MODEL=llama3.1
LLM_ANALYSIS_BASE_URL=http://127.0.0.1:11434
LLM_ANALYSIS_TIMEOUT_SECONDS=20
```

To use local Ollama:

```env
LLM_ANALYSIS_ENABLED=true
LLM_ANALYSIS_PROVIDER=ollama
LLM_ANALYSIS_MODEL=llama3.1
```
