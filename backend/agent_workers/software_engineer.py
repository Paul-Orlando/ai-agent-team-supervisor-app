"""Software Engineer agent — exact system prompt from JSON llmAgentflow_1, streaming."""
import os

from typing import AsyncGenerator
from agents import Agent, Runner, ModelSettings
from agents.stream_events import RawResponsesStreamEvent
from models.state import ExecutionState

# Exact system prompt from JSON llmAgentflow_1.inputs.llmMessages[0].content
SYSTEM_PROMPT = """You are a Senior Full Stack Software Engineer.

RESPONSIBILITIES:
- Implement production-ready solutions.
- Follow clean architecture principles.
- Include error handling, validation, and scalability considerations.
- Explain tradeoffs and implementation decisions.
- Return complete, structured implementation details.

OUTPUT FORMAT:
1. Architecture Summary
2. Implementation Plan
3. Production-Ready Code
4. Edge Cases
5. Performance Considerations
6. Security Considerations
7. Testing Recommendations"""


def build_engineer(model: str = os.getenv("MODEL_NAME", "gpt-4o-mini")) -> Agent:
    return Agent(
        name="SoftwareEngineer",
        instructions=SYSTEM_PROMPT,
        model=model,
        model_settings=ModelSettings(temperature=0.4),
    )


async def stream_engineer(
    state: ExecutionState, rag_context: str, model: str = os.getenv("MODEL_NAME", "gpt-4o-mini")
) -> AsyncGenerator[str, None]:
    agent = build_engineer(model)
    context_block = f"KNOWLEDGE BASE CONTEXT:\n{rag_context}\n\n---\n\n" if rag_context else ""

    # User message template: "Supervisor Instructions\n\n{{$flow.state.instructions}}"
    prompt = f"{context_block}Supervisor Instructions\n\n{state.instructions}"

    result = Runner.run_streamed(agent, prompt)
    collected = []

    async for event in result.stream_events():
        if isinstance(event, RawResponsesStreamEvent):
            data = event.data
            chunk = _extract_text_delta(data)
            if chunk:
                collected.append(chunk)
                yield chunk

    state.last_output = "".join(collected)
    state.conversation_history.append({
        "agent": "SoftwareEngineer",
        "output": state.last_output,
    })


def _extract_text_delta(data) -> str:
    """Extract text delta from a raw streaming event regardless of API version."""
    # Responses API format
    if hasattr(data, "type"):
        if data.type in ("response.output_text.delta", "response.text.delta"):
            return getattr(data, "delta", "") or ""
    # Chat Completions streaming fallback
    if hasattr(data, "choices"):
        choices = data.choices
        if choices and hasattr(choices[0], "delta"):
            delta = choices[0].delta
            return getattr(delta, "content", "") or ""
    # Generic delta attribute
    if hasattr(data, "delta"):
        delta = data.delta
        if isinstance(delta, str):
            return delta
        if hasattr(delta, "content"):
            content = delta.content
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                return "".join(
                    getattr(p, "text", "") for p in content if hasattr(p, "text")
                )
    return ""
