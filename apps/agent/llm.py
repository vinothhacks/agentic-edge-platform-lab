"""Mock LLM provider (default). Real providers can be swapped in."""
from typing import Any


def mock_llm(prompt: str) -> dict[str, Any]:
    """Very simple intent parser for demo."""
    if "orders" in prompt.lower():
        return {
            "intent": "provision_route",
            "proposed": {
                "name": "orders-api",
                "domain": "orders.localhost",
                "upstream_url": "http://orders-service:8080",
                "auth_required": True,
                "rate_limit": "100/min",
            },
        }
    return {"intent": "unknown", "proposed": {}}
