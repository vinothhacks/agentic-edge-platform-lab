# ADR-0001 · FastAPI + SQLModel for the broker

## Status
Accepted

## Context

The broker has two jobs: speak HTTP to developers and persist state. A teaching lab needs both jobs to be **legible at a glance** — a reader should grasp the request flow and the data model in five minutes.

Candidates evaluated:

| Stack | Verdict |
|---|---|
| Flask + SQLAlchemy | Familiar, but request validation is hand-rolled |
| Django + DRF | Powerful, but heavy for a six-endpoint broker |
| FastAPI + Pydantic + SQLAlchemy | Best validation, but two model layers |
| FastAPI + SQLModel | Single model layer, automatic OpenAPI docs |

## Decision

**FastAPI + SQLModel.** A `SQLModel` class is both the table and the Pydantic schema. Less ceremony, fewer lines, identical types end-to-end.

## Consequences

**Good**
- One model definition → table + request body + response body.
- `/docs` Swagger UI is free and always accurate.
- Migration to Postgres is one connection-string change.

**Bad**
- SQLModel is younger than SQLAlchemy; advanced features (complex joins, query expressions) still need raw SQLAlchemy.
- Mixing table + API models can leak DB concerns into the wire format if you're not careful — we mitigate by using `response_model=` explicitly on routes that diverge.
