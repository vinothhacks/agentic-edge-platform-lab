# ADR-0003 · Envoy primary, Python fallback proxy

## Status
Accepted

## Context

We want learners to see a **real** edge proxy — Envoy is the industry default. But Envoy is heavy: a binary, a config schema, and a learning curve of its own. Some readers will want to skip it.

## Decision

Ship **both** data planes:

- **Envoy** is wired into `docker-compose.yml` and is the default. It consumes the YAML the renderer writes to `generated/`.
- **A tiny Python fallback** (`apps/gateway/local_proxy.py`) — ~80 lines of `httpx` — can be used when Envoy isn't available or when you want to step through the proxy logic in a debugger.

The `ServiceInstance` model is gateway-agnostic. The renderer just produces an Envoy YAML today; tomorrow it could produce a NGINX config or call a Python config-loader. Choosing the data plane is a deployment concern, not a code concern.

## Consequences

**Good**
- Real-world artifact (Envoy YAML) for advanced readers.
- Zero-cost on-ramp via the Python proxy for beginners.
- Forces the renderer to stay clean — it must produce a config any proxy can consume.

**Bad**
- Two data-plane code paths means two test surfaces.
- Envoy and Python proxy will drift in features unless we keep both feature-locked to the `ServiceInstance` schema.
