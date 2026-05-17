"""Safety guardrails for agent actions."""
import re
from typing import Any

# Patterns that must never appear in domain, rate_limit, or the raw user message
UNSAFE_PATTERNS = [
    (r"\*", "Wildcard domains are not allowed"),
    (r"(?:AWS_|SECRET_|API_KEY|password)", "Potential secret leak detected"),
    (r"(?:2000|5000|10000)/min", "Rate limit too high (max 1000/min)"),
]


def is_safe_config(config: dict[str, Any]) -> tuple[bool, str | None]:
    """Return (True, None) if the config is safe; otherwise (False, reason)."""
    domain = config.get("domain", "")
    rate = config.get("rate_limit", "")
    combined = f"{domain} {rate}"
    for pattern, reason in UNSAFE_PATTERNS:
        if re.search(pattern, combined, re.IGNORECASE):
            return False, reason
    return True, None


def is_safe_message(message: str) -> tuple[bool, str | None]:
    """Scan the raw user message for obvious unsafe intent before LLM parsing."""
    for pattern, reason in UNSAFE_PATTERNS:
        if re.search(pattern, message, re.IGNORECASE):
            return False, f"Unsafe request detected in message: {reason}"
    return True, None
