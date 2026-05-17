"""Agent workflow state machine (LangGraph-style, dependency-free implementation)."""
from dataclasses import dataclass, field

from .safety import is_safe_config, is_safe_message
from .tools import (
    create_provisioning_request,
    propose_service_config,
    validate_service_config,
)


@dataclass
class AgentState:
    raw_message: str
    parsed_intent: dict | None = None
    proposed_config: dict | None = None
    validation_errors: list[str] = field(default_factory=list)
    risk_level: str = "low"
    approval_status: str = "pending"
    operation_id: str | None = None
    final_response: str | None = None


def run_agent_workflow(user_message: str) -> AgentState:
    """Execute the full agent pipeline:
    parse_user_intent -> propose_config -> validate_config ->
    risk_check -> create_provisioning_request -> explain_result
    """
    state = AgentState(raw_message=user_message)

    msg_safe, msg_reason = is_safe_message(user_message)
    if not msg_safe:
        state.validation_errors.append(msg_reason or "unsafe message")
        state.final_response = "Request rejected by safety: " + "; ".join(state.validation_errors)
        return state

    parsed = propose_service_config(user_message)
    state.parsed_intent = parsed["parsed"]
    state.proposed_config = parsed["parsed"].get("proposed")

    if state.proposed_config:
        val = validate_service_config(state.proposed_config)
        if not val["valid"]:
            state.validation_errors.append(val["reason"])

        safe, reason = is_safe_config(state.proposed_config)
        if not safe:
            state.validation_errors.append(reason or "unsafe config")
    else:
        state.validation_errors.append("Could not parse a valid service config from the request.")

    if not state.validation_errors and state.proposed_config:
        result = create_provisioning_request(state.proposed_config)
        state.operation_id = result["operation_id"]
        state.final_response = (
            f"Provisioned successfully. Operation ID: {state.operation_id}. "
            f"Test with: curl http://localhost:10000/orders"
        )
    else:
        state.final_response = "Request rejected: " + "; ".join(state.validation_errors)

    return state
