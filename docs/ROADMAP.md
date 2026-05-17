# Production Roadmap

AEPL is a teaching lab. Every "production swap" below is intentional — you can read the lab code, then read this doc, then know exactly what to harden.

## Component-by-component

| Lab component | Production equivalent | Why we use the lab version |
|---|---|---|
| SQLite | PostgreSQL / CockroachDB | Zero-setup, one file, perfect for the demo |
| In-memory queue | Redis + Celery / RQ / Kafka | Avoids a second container in the smallest demo |
| Polling worker | Multiple worker pods + leader election | Polling is easy to read; real systems use long-poll or pub/sub |
| Static `envoy.yaml` generation | go-control-plane / xDS server | Static config is easier to inspect when learning |
| Python fallback proxy | Envoy / NGINX / HAProxy | Avoids the Envoy binary on machines without it |
| Mock LLM | OpenAI / Anthropic / Bedrock | Reproducible tests; no API key required |
| In-app approval flag | Slack / PagerDuty / GitHub PR | Lab keeps the loop short |
| File-based audit | Immutable log (S3 + Object Lock, Vault audit) | Files are easy to grep while learning |
| `print()` logging | OpenTelemetry → Jaeger + Loki + Prometheus | Structured logging hooks already in place |

## Phases

### Phase 1 · Make it real

- Swap SQLite → Postgres (alembic for migrations).
- Swap in-memory queue → Redis + RQ.
- Add `prometheus_client` + `/metrics`.

### Phase 2 · Multi-tenant

- OIDC on the broker (`fastapi-users`).
- Per-tenant rate limits in the renderer.
- Service quotas on `POST /api/services`.

### Phase 3 · Real edge

- Replace static `envoy.yaml` with an xDS server (go-control-plane).
- Add a `gateway-class` field on `ServiceInstance` to support multiple data planes.
- Wire TLS via cert-manager + ACME.

### Phase 4 · Operator-grade safety

- Sign and timestamp every `ProvisioningOperation`.
- Add drift detection (worker re-reads Envoy and reconciles).
- Move approvals out-of-band (Slack approve button → webhook).

### Phase 5 · Real agent

- Replace mock LLM with a real provider via `LLM_PROVIDER`.
- Cache prompts per service to cut tokens.
- Add tool-use loop: the agent can read service health before proposing a change.

### Phase 6 · Observability

- OpenTelemetry traces across broker → worker → renderer → Envoy.
- Service-graph view in Jaeger.
- Per-service SLOs computed from Envoy access logs.

## Stretch ideas

- Self-serve UI (Streamlit / Next.js) reading the same broker API.
- Importer that scans a Kubernetes namespace and proposes routes.
- Cost estimation — "this route will add ~X req/min of egress at $Y/mo".

## What's intentionally left out

- **Kubernetes operator** — out of scope. The broker is the source of truth; an operator could watch it and reconcile.
- **Service mesh sidecars** — different concern. AEPL is north-south, not east-west.
- **A custom LLM** — use a hosted model. The agent is the interesting bit, not the foundation model.
