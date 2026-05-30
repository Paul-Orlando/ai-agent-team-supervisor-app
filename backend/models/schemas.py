from pydantic import BaseModel
from typing import Literal, Optional


class SupervisorDecision(BaseModel):
    """Structured output for Supervisor routing — matches JSON llmStructuredOutput."""
    next: Literal["SOFTWARE", "REVIEWER", "FINISH"]
    instructions: str
    currentTask: str
    reviewStatus: Literal["PENDING", "CHANGES_REQUIRED", "APPROVED"]


class RunAgentsRequest(BaseModel):
    user_input: str
    session_id: Optional[str] = None
    model: str = "gpt-4o-mini"
    max_iterations: int = 5


class UploadPdfResponse(BaseModel):
    status: str
    filename: str
    chunks: int
    message: str


class HealthResponse(BaseModel):
    status: str
    rag_chunks: int
    model: str = "openai-agents-sdk"


class SSEEvent(BaseModel):
    type: str
    agent: Optional[str] = None
    message: Optional[str] = None
    output: Optional[str] = None
    content: Optional[str] = None
    state: Optional[dict] = None
    status: Optional[str] = None
    report: Optional[str] = None
    error: Optional[str] = None
