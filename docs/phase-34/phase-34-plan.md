# Phase 34: Robust Ollama Analysis Payload Parsing

## Required Work

- Fix Ollama analysis failures caused by valid JSON with unexpected list item shapes.
- Keep LLM final analysis enabled without failing the whole report on minor response-shape drift.
- Make prompt schema clearer for string-only list fields.
- Remove outdated rule-signal wording from LLM failure text.

## Implementation Plan

- Normalize string-list fields returned by the LLM.
- Convert object items in `next_actions`, limitations, hypotheses, questions, and specialist-agent lists into safe JSON strings.
- Add a regression test for object-shaped `next_actions`.
- Re-run periodic monitoring API tests.
