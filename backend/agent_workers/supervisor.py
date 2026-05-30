"""Supervisor agent — exact system prompt from JSON llmAgentflow_0, structured output."""
from agents import Agent, Runner, ModelSettings
from models.schemas import SupervisorDecision
from models.state import ExecutionState

# Exact system prompt from JSON llmAgentflow_0.inputs.llmMessages[0].content
SYSTEM_PROMPT = """You are a senior AI engineering supervisor coordinating a structured multi-agent software delivery workflow.

TEAM:
- SOFTWARE: Senior Software Engineer
- REVIEWER: Senior Code Reviewer and QA Engineer

YOUR RESPONSIBILITIES:
1. Break user requests into clear implementation tasks.
2. Assign precise, scoped work instructions.
3. Track review outcomes and implementation quality.
4. Minimize unnecessary loops and retries.
5. Ensure production-grade software quality.

WORKFLOW RULES:
- SOFTWARE implements features and fixes.
- REVIEWER validates architecture, code quality, scalability, edge cases, and security.
- If reviewer finds issues, route back to SOFTWARE with actionable fixes.
- If reviewer approves and solution is complete, return FINISH.

DECISION LOGIC:
- Use SOFTWARE first for implementation.
- Use REVIEWER after implementation.
- Use FINISH only when implementation and review are complete.

OUTPUT REQUIREMENTS:
Return structured JSON only."""


def build_supervisor(model: str = "gpt-4o-mini") -> Agent:
    return Agent(
        name="Supervisor",
        instructions=SYSTEM_PROMPT,
        model=model,
        model_settings=ModelSettings(temperature=0.9),
        output_type=SupervisorDecision,
    )


async def run_supervisor(
    state: ExecutionState, rag_context: str, model: str = "gpt-4o-mini"
) -> SupervisorDecision:
    agent = build_supervisor(model)
    context_block = f"KNOWLEDGE BASE CONTEXT:\n{rag_context}\n\n---\n\n" if rag_context else ""

    history_summary = ""
    if state.conversation_history:
        last_entries = state.conversation_history[-6:]
        history_summary = "RECENT HISTORY:\n" + "\n".join(
            f"[{e['agent']}]: {str(e['output'])[:400]}" for e in last_entries
        ) + "\n\n"

    prompt = (
        f"{context_block}"
        f"{history_summary}"
        f"Original User Request: {state.user_input}\n\n"
        f"Execution Plan:\n{state.plan}\n\n"
        f"Current State:\n"
        f"  iteration_count: {state.iteration_count}\n"
        f"  review_status: {state.review_status}\n"
        f"  quality_score: {state.quality_score}\n"
        f"  last_output_preview: {state.last_output[:500] if state.last_output else 'none'}\n\n"
        "Based on the above, decide the next worker and provide precise instructions."
    )
    result = await Runner.run(agent, prompt)
    decision: SupervisorDecision = result.final_output
    return decision
