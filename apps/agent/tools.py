"""Agent tools (function calling style)."""
from typing import Any

from .llm import mock_llm
from .safety import is_safe_config


def inspect_catalog() -> dict[str, Any]:
    return {"catalog": "edge-route-basic available"}


def propose_service_config(user_message: str) -> dict[str, Any]:
    parsed = mock_llm(user_message)
    safe, reason = is_safe_config(parsed.get("proposed", {}))
    return {"parsed": parsed, "safe": safe, "reason": reason}


def validate_service_config(config: dict[str, Any]) -> dict[str, Any]:
    safe, reason = is_safe_config(config)
    return {"valid": safe, "reason": reason or "ok"}


def create_provisioning_request(config: dict[str, Any]) -> dict[str, Any]:
    return {"operation_id": "op-demo-123", "status": "pending"}
