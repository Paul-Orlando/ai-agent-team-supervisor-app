"""Code Reviewer agent — exact system prompt from JSON llmAgentflow_2, streaming."""
from typing import AsyncGenerator
from agents import Agent, Runner, ModelSettings
from agents.stream_events import RawResponsesStreamEvent
from models.state import ExecutionState
from agent_workers.software_engineer import _extract_text_delta

# Exact system prompt from JSON llmAgentflow_2.inputs.llmMessages[0].content
SYSTEM_PROMPT = """You are a Principal Software Architect and QA Reviewer.

REVIEW CRITERIA:
- Code quality
- Scalability
- Maintainability
- Security
- Performance
- Reliability
- Architecture alignment
- Edge case handling
- Production readiness

RESPONSE FORMAT:
1. Review Summary
2. Risks Identified
3. Required Changes
4. Suggested Improvements
5. Approval Status (APPROVED or CHANGES_REQUIRED)
6. Quality Score (1-10)

Provide actionable and specific feedback."""


def build_reviewer(model: str = "gpt-4o-mini") -> Agent:
    return Agent(
        name="CodeReviewer",
        instructions=SYSTEM_PROMPT,
        model=model,
        model_settings=ModelSettings(temperature=0.2),
    )


async def stream_reviewer(
    state: ExecutionState, rag_context: str, model: str = "gpt-4o-mini"
) -> AsyncGenerator[str, None]:
    agent = build_reviewer(model)
    context_block = f"KNOWLEDGE BASE CONTEXT:\n{rag_context}\n\n---\n\n" if rag_context else ""

    # User message template: "Supervisor Instructions\n\n{{$flow.state.instructions}}"
    prompt = (
        f"{context_block}"
        f"Supervisor Instructions\n\n{state.instructions}\n\n"
        f"Implementation to Review:\n{state.last_output}"
    )

    result = Runner.run_streamed(agent, prompt)
    collected = []

    async for event in result.stream_events():
        if isinstance(event, RawResponsesStreamEvent):
            chunk = _extract_text_delta(event.data)
            if chunk:
                collected.append(chunk)
                yield chunk

    review_text = "".join(collected)
    state.last_output = review_text
    state.conversation_history.append({
        "agent": "CodeReviewer",
        "output": review_text,
    })

    # Parse approval status and quality score from reviewer output
    _parse_review_metadata(state, review_text)


def _parse_review_metadata(state: ExecutionState, review_text: str) -> None:
    text_upper = review_text.upper()
    if "CHANGES_REQUIRED" in text_upper:
        state.review_status = "CHANGES_REQUIRED"
    elif "APPROVED" in text_upper:
        state.review_status = "APPROVED"

    import re
    score_match = re.search(r"quality\s+score[:\s]+(\d+)", review_text, re.IGNORECASE)
    if score_match:
        state.quality_score = int(score_match.group(1))
