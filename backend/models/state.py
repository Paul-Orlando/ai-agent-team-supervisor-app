from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import uuid


@dataclass
class ExecutionState:
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_input: str = ""
    plan: str = ""

    # Flowise flow.state variables (exact keys from JSON startState)
    next: str = ""
    instructions: str = ""
    current_task: str = ""
    review_status: str = "PENDING"        # PENDING | CHANGES_REQUIRED | APPROVED
    implementation_notes: str = ""
    quality_score: int = 0                # 1–10
    iteration_count: int = 0
    retries: int = 0

    artifacts: list = field(default_factory=list)
    cost_tokens: int = 0
    conversation_history: list = field(default_factory=list)
    timestamps: dict = field(default_factory=dict)
    last_output: str = ""
    final_report: str = ""

    # Model chosen by user
    model: str = "gpt-4o-mini"
    max_iterations: int = 5

    def to_dict(self) -> dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "user_input": self.user_input,
            "plan": self.plan,
            "next": self.next,
            "instructions": self.instructions,
            "current_task": self.current_task,
            "review_status": self.review_status,
            "implementation_notes": self.implementation_notes,
            "quality_score": self.quality_score,
            "iteration_count": self.iteration_count,
            "retries": self.retries,
            "artifacts": self.artifacts,
            "cost_tokens": self.cost_tokens,
            "model": self.model,
            "max_iterations": self.max_iterations,
        }

    def record_timestamp(self, key: str) -> None:
        self.timestamps[key] = datetime.utcnow().isoformat()

    def add_tokens(self, count: int) -> None:
        self.cost_tokens += count
