# ADR-0002 · Mock LLM by default

## Status
Accepted

## Context

The agent is the headline feature, but a teaching lab must run **without API keys** for two reasons:

1. CI cannot ship secrets. Every PR must pass tests deterministically.
2. New contributors should be able to `docker compose up` and see the agent work — without paying OpenAI.

A real LLM is non-deterministic, costs money, and rate-limits. None of those properties belong in unit tests.

## Decision

Ship a **mock LLM** as the default `LLM_PROVIDER`. It's a small intent parser that maps the prompt to one of a handful of provisioning shapes. Real providers (OpenAI, Anthropic, Ollama) are drop-in via env var.

```python
LLM_PROVIDER=mock       # default
LLM_PROVIDER=openai     # OPENAI_API_KEY=...
LLM_PROVIDER=anthropic  # ANTHROPIC_API_KEY=...
LLM_PROVIDER=ollama     # OLLAMA_URL=http://localhost:11434
```

## Consequences

**Good**
- Tests are deterministic and free.
- New users hit the happy path without setup.
- The agent's *workflow* is the lesson — not the model.

**Bad**
- Mock intent parsing is shallow; obviously can't generalise.
- Risk of demos looking too magical because the mock always succeeds. We mitigate by including unsafe-rejection examples in the README.
