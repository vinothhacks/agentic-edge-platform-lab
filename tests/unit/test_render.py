from pathlib import Path

import pytest

from apps.broker.models.service import ServiceInstance
from apps.broker.services.config_renderer import ConfigRenderer


@pytest.fixture()
def renderer(tmp_path, monkeypatch):
    """Renderer whose output goes into tmp_path/generated/."""
    monkeypatch.chdir(tmp_path)
    return ConfigRenderer(template_dir=str(Path(__file__).parents[2] / "apps/broker/templates"))


def test_render_success(renderer, tmp_path):
    svc = ServiceInstance(
        instance_id="r1",
        name="orders-api",
        domain="orders.localhost",
        upstream_url="http://orders-service:8080",
        auth_required=True,
        rate_limit="100/min",
    )
    result = renderer.render(svc)
    assert result.success, result.error
    assert result.config_path is not None
    content = Path(result.config_path).read_text()
    assert "orders.localhost" in content
    assert "orders-service" in content


def test_render_rejects_wildcard(renderer):
    svc = ServiceInstance(
        instance_id="bad1",
        name="bad",
        domain="*.evil.com",
        upstream_url="http://bad:8080",
    )
    result = renderer.render(svc)
    assert not result.success
    assert "Wildcard" in (result.error or "")


def test_render_rejects_high_rate_limit(renderer):
    svc = ServiceInstance(
        instance_id="bad2",
        name="ratelimit-test",
        domain="ok.localhost",
        upstream_url="http://ok:8080",
        rate_limit="5000/min",
    )
    result = renderer.render(svc)
    assert not result.success
    assert "Rate limit" in (result.error or "")
