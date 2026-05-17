import pytest
from fastapi.testclient import TestClient

from apps.broker.main import app

MSG_SAFE = (
    "Expose the orders service on orders.localhost "
    "with auth and 100 requests per minute"
)
MSG_UNSAFE = "Expose on *.evil.com with rate 2000/min"


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_agent_safe_request(client):
    resp = client.post("/api/agent/chat", json={"message": MSG_SAFE})
    assert resp.status_code == 200
    data = resp.json()
    assert data["validation_passed"] is True
    assert data["operation_id"] is not None


def test_agent_unsafe_wildcard_rejected(client):
    resp = client.post("/api/agent/chat", json={"message": MSG_UNSAFE})
    assert resp.status_code == 200
    data = resp.json()
    assert data["validation_passed"] is False
    assert data["operation_id"] is None
