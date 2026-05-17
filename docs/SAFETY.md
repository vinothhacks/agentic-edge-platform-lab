# Safety system

AEPL treats the agent as **adversarial by default**. Three independent checks must all pass before a service is provisioned. Each check lives in a different file so a bug in one can't disable the others.

## Threat model

| Threat | Why it matters | Mitigation |
|---|---|---|
| Wildcard domain (`*.example.com`) | Lets an attacker steal traffic for any sibling host | Pre-LLM regex + renderer guard |
| Rate-limit bomb (`100000/min`) | DoS amplification through your edge | Renderer caps at `1000/min` |
| Secret leak in prompt (`AWS_SECRET=...`) | Logs end up in observability stack | Raw message scan rejects `AWS_`, `SECRET_`, `API_KEY`, `password` |
| Malformed config bypass | Worker writes bad YAML, Envoy reloads broken state | Pydantic schema + try/except in renderer |
| LLM hallucination | Agent invents an impossible upstream | Renderer rejects unresolvable host:port |
| Prompt injection | User text manipulates the agent | Raw scan runs *before* the LLM is invoked |

## Three layers

### Layer 1 — Raw message scan (`apps/agent/safety.py`)

Runs **before** the LLM is touched. Regex matches against the user prompt itself.

```python
UNSAFE_PATTERNS = [
    (r"\*",                                "Wildcard domains are not allowed"),
    (r"(?:AWS_|SECRET_|API_KEY|password)", "Potential secret leak detected"),
    (r"(?:2000|5000|10000)/min",           "Rate limit too high (max 1000/min)"),
]
```

This layer is dumb on purpose. It catches the obvious cases without consuming LLM tokens.

### Layer 2 — Schema validation (`apps/broker/schemas/service.py`)

Pydantic with `pattern=r"^[a-z0-9-]+$"` on service names, `pattern=r"^\d+/(min|sec)$"` on rate limits. Bad shapes never reach the renderer.

### Layer 3 — Renderer safety (`apps/broker/services/config_renderer.py`)

The last line of defence. Even if both upstream layers were bypassed, the renderer refuses to write `envoy.yaml` for:

- Any domain containing `*`
- `int(rate_limit.split("/")[0]) > 1000`
- Malformed `rate_limit` that can't be parsed

## Tests

Each layer has a unit test:

| Test | Asserts |
|---|---|
| `test_agent_unsafe_wildcard_rejected` | Layer 1 stops `*.evil.com` |
| `test_render_rejects_wildcard` | Layer 3 stops the same payload if Layer 1 is removed |
| `test_render_rejects_high_rate_limit` | Layer 3 stops `5000/min` |
| `test_create_service` (payload validation) | Layer 2 enforces shape |

Add a new threat → add a regex/check + add a test. The pattern is intentionally simple.

## What we don't do (yet)

- **No RBAC** — anyone with broker access can provision anything. Production: bolt on OIDC + service accounts.
- **No audit trail beyond the DB** — operations are logged in `provisioning_operations`, but not signed. Production: ship to an immutable log.
- **No drift detection** — if someone edits Envoy config out-of-band, the broker won't know.

See [ROADMAP.md](ROADMAP.md) for how to grow each of these into production-grade safety.