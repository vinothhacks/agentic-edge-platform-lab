"""End-to-end smoke test against a live local broker.

Boots nothing on its own — assumes the broker is running on http://localhost:8000.
Verifies: healthz, /v2/catalog, safe agent flow, unsafe agent rejection,
direct POST /api/services, and config rendering on disk.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import httpx

BASE = "http://127.0.0.1:8000"
TIMEOUT = 10.0


def step(n: int, label: str) -> None:
    print(f"\n[{n}] {label}")


def expect(cond: bool, msg: str) -> None:
    print(f"    {'OK' if cond else 'FAIL'}  {msg}")
    if not cond:
        sys.exit(1)


def main() -> None:
    with httpx.Client(base_url=BASE, timeout=TIMEOUT) as c:
        step(1, "GET /healthz")
        r = c.get("/healthz")
        expect(r.status_code == 200, f"status={r.status_code}")
        expect(r.json().get("status") == "ok", f"body={r.json()}")

        step(2, "GET /v2/catalog")
        r = c.get("/v2/catalog")
        expect(r.status_code == 200, f"status={r.status_code}")
        services = r.json().get("services", [])
        expect(len(services) > 0, f"services count={len(services)}")
        print(f"    plans: {[s['name'] for s in services]}")

        step(3, "POST /api/agent/chat (safe request)")
        safe_payload = {
            "message": "Expose the orders service on orders.localhost with auth and 100 req/min"
        }
        r = c.post("/api/agent/chat", json=safe_payload)
        expect(r.status_code == 200, f"status={r.status_code}")
        body = r.json()
        print(f"    response: {body}")
        expect(body.get("validation_passed") is True, "safe request should pass validation")
        op_id = body.get("operation_id")
        expect(op_id is not None, "operation_id should be present")

        step(4, "POST /api/agent/chat (unsafe wildcard)")
        unsafe_payload = {"message": "Expose *.evil.com with rate 5000/min"}
        r = c.post("/api/agent/chat", json=unsafe_payload)
        expect(r.status_code == 200, f"status={r.status_code}")
        body = r.json()
        print(f"    response: {body}")
        expect(body.get("validation_passed") is False, "unsafe request must be rejected")
        expect(body.get("operation_id") is None, "no operation should be created")

        step(5, "POST /api/services (direct provisioning)")
        provisioning = {
            "name": "billing-direct",
            "domain": "billing.localhost",
            "upstream_url": "http://billing-service:8080",
            "rate_limit": "200/min",
            "auth_required": True,
        }
        r = c.post("/api/services", json=provisioning)
        expect(r.status_code in (200, 201, 202), f"status={r.status_code}")
        direct_op = r.json()
        print(f"    response: {direct_op}")
        expect(bool(direct_op.get("instance_id")), "broker should return instance_id")

        step(6, "Poll last_operation until terminal state")
        instance_id = direct_op["instance_id"]
        final_state = None
        for i in range(20):
            r = c.get(f"/v2/service_instances/{instance_id}/last_operation")
            if r.status_code == 200:
                op = r.json()
                state = (op.get("state") or "").upper()
                print(f"    [{i:02d}] state={state} desc={op.get('description')}")
                if state in ("SUCCEEDED", "FAILED"):
                    final_state = state
                    break
            time.sleep(1)
        expect(final_state == "SUCCEEDED", f"final state should be SUCCEEDED, got {final_state}")

        step(7, "Verify rendered envoy config exists")
        gen = Path(__file__).resolve().parents[1] / "generated"
        if gen.exists():
            files = sorted(p.name for p in gen.iterdir() if p.is_file())
            print(f"    generated/: {files}")
            expect(any(f.endswith(".yaml") for f in files), "at least one .yaml should exist")

    print("\nE2E PASS")


if __name__ == "__main__":
    main()
