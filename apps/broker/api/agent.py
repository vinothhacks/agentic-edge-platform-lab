"""Agent chat endpoint (mounted in main)."""
from fastapi import APIRouter
from pydantic import BaseModel

from apps.agent.graph import AgentState, run_agent_workflow

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    interpreted: str
    proposed: dict
    validation_passed: bool
    operation_id: str | None
    next_command: str


@router.post("/api/agent/chat", response_model=ChatResponse)
def agent_chat(req: ChatRequest):
    state: AgentState = run_agent_workflow(req.message)
    intent = "unknown"
    if state.parsed_intent:
        intent = state.parsed_intent.get("intent", "unknown")
    return ChatResponse(
        interpreted=intent,
        proposed=state.proposed_config or {},
        validation_passed=len(state.validation_errors) == 0,
        operation_id=state.operation_id,
        next_command=state.final_response or "",
    )
