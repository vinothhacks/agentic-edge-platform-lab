import pytest
from fastapi.testclient import TestClient

from apps.broker.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_catalog_returns_services(client):
    resp = client.get("/v2/catalog")
    assert resp.status_code == 200
    data = resp.json()
    assert "services" in data
    assert len(data["services"]) >= 1


def test_create_service(client):
    payload = {
        "name": "test-orders",
        "domain": "test.localhost",
        "upstream_url": "http://orders-service:8080",
        "auth_required": True,
        "rate_limit": "200/min",
    }
    resp = client.post("/api/services", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "test-orders"
    assert "instance_id" in body
