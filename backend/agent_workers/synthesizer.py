"""Final Synthesizer agent — exact system prompt from JSON llmAgentflow_3, streaming."""
import os

from typing import AsyncGenerator
from agents import Agent, Runner, ModelSettings
from agents.stream_events import RawResponsesStreamEvent
from models.state import ExecutionState
from agent_workers.software_engineer import _extract_text_delta

# Exact system prompt from JSON llmAgentflow_3.inputs.llmMessages[0].content
SYSTEM_PROMPT = """You are generating the final consolidated engineering delivery report.

Combine:
- Final implementation
- Reviewer feedback
- Architectural improvements
- Security/performance recommendations
- Production-readiness assessment

Generate a polished engineering handoff document."""

# Exact user message from JSON llmAgentflow_3.inputs.llmUserMessage
USER_MESSAGE = """Generate a complete engineering delivery package including:

1. Executive Summary
2. Architecture Overview
3. Final Production Code
4. Reviewer Findings
5. Risks and Mitigations
6. Recommended Next Steps
7. Production Deployment Considerations
8. Future Scalability Improvements"""


def build_synthesizer(model: str = os.getenv("MODEL_NAME", "gpt-4o-mini")) -> Agent:
    return Agent(
        name="FinalSynthesizer",
        instructions=SYSTEM_PROMPT,
        model=model,
        model_settings=ModelSettings(temperature=0.9),
    )


async def stream_synthesizer(
    state: ExecutionState, rag_context: str, model: str = os.getenv("MODEL_NAME", "gpt-4o-mini")
) -> AsyncGenerator[str, None]:
    agent = build_synthesizer(model)
    context_block = f"KNOWLEDGE BASE CONTEXT:\n{rag_context}\n\n---\n\n" if rag_context else ""

    history_text = ""
    if state.conversation_history:
        history_text = "FULL WORKFLOW HISTORY:\n"
        for entry in state.conversation_history:
            history_text += f"\n### {entry['agent']}\n{entry['output']}\n"

    prompt = (
        f"{context_block}"
        f"Original Request: {state.user_input}\n\n"
        f"Execution Plan: {state.plan}\n\n"
        f"Review Status: {state.review_status}\n"
        f"Quality Score: {state.quality_score}/10\n"
        f"Iterations: {state.iteration_count}\n\n"
        f"{history_text}\n\n"
        f"{USER_MESSAGE}"
    )

    result = Runner.run_streamed(agent, prompt)
    collected = []

    async for event in result.stream_events():
        if isinstance(event, RawResponsesStreamEvent):
            chunk = _extract_text_delta(event.data)
            if chunk:
                collected.append(chunk)
                yield chunk

    state.final_report = "".join(collected)
