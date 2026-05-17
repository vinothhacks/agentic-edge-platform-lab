"""Jinja2-based Envoy config renderer with safety checks."""
from dataclasses import dataclass
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from ..models.service import ServiceInstance


@dataclass
class RenderResult:
    success: bool
    config_path: str | None = None
    error: str | None = None


class ConfigRenderer:
    def __init__(self, template_dir: str = "apps/broker/templates"):
        self.env = Environment(loader=FileSystemLoader(template_dir), autoescape=False)

    def render(self, service: ServiceInstance) -> RenderResult:
        try:
            template = self.env.get_template("envoy.yaml.j2")
        except TemplateNotFound:
            return RenderResult(success=False, error="Template not found")

        if "*" in service.domain:
            return RenderResult(success=False, error="Wildcard domains are not allowed")
        try:
            rate_int = int(service.rate_limit.split("/")[0])
        except (ValueError, IndexError):
            return RenderResult(success=False, error="Invalid rate_limit format")
        if rate_int > 1000:
            return RenderResult(success=False, error="Rate limit too high (max 1000/min)")

        upstream = service.upstream_url.replace("http://", "").split(":")
        upstream_host = upstream[0]
        upstream_port = int(upstream[1]) if len(upstream) > 1 else 8080

        config = template.render(
            service={
                "name": service.name,
                "domain": service.domain,
                "upstream_host": upstream_host,
                "upstream_port": upstream_port,
                "auth_required": service.auth_required,
                "rate_limit": service.rate_limit,
            }
        )

        out_dir = Path("generated")
        out_dir.mkdir(exist_ok=True)
        out_path = out_dir / f"{service.name}.yaml"
        out_path.write_text(config, encoding="utf-8")

        return RenderResult(success=True, config_path=str(out_path))
