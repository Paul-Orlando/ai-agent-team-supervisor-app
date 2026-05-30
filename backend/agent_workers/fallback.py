"""Fallback/Escalation agent — triggers on max iterations (from workflow.png)."""
from agents import Agent, Runner, ModelSettings
from models.state import ExecutionState

# Fallback message exact from JSON loopAgentflow_0.inputs.fallbackMessage
FALLBACK_MESSAGE = (
    "Workflow stopped after exceeding maximum iterations. "
    "Manual review recommended to prevent recursive execution loops."
)

SYSTEM_PROMPT = """You are the Fallback Escalation handler for a multi-agent workflow.

Maximum retry limit has been reached. Assess the failure, summarize what was attempted,
explain why it failed, and recommend the best escalation path:

- NOTIFY: Alert user, provide summary of what was accomplished
- HUMAN_IN_THE_LOOP: Pause for human review with specific questions
- ALTERNATIVE_APPROACH: Describe a different strategy to try
- ABORT: Explain clearly why the task cannot be completed as specified

Always include:
- What was accomplished so far
- Why the iterations were exhausted
- Specific actionable next steps"""


def build_fallback(model: str = "gpt-4o-mini") -> Agent:
    return Agent(
        name="FallbackHandler",
        instructions=SYSTEM_PROMPT,
        model=model,
        model_settings=ModelSettings(temperature=0.3),
    )


async def run_fallback(state: ExecutionState, model: str = "gpt-4o-mini") -> str:
    agent = build_fallback(model)

    history_summary = ""
    if state.conversation_history:
        history_summary = "HISTORY:\n" + "\n".join(
            f"[{e['agent']}]: {str(e['output'])[:300]}" for e in state.conversation_history[-4:]
        )

    prompt = (
        f"SYSTEM MESSAGE: {FALLBACK_MESSAGE}\n\n"
        f"User Request: {state.user_input}\n"
        f"Iterations Used: {state.iteration_count}/{state.max_iterations}\n"
        f"Last Review Status: {state.review_status}\n"
        f"Quality Score: {state.quality_score}/10\n\n"
        f"{history_summary}\n\n"
        "Provide escalation assessment and next steps."
    )

    result = await Runner.run(agent, prompt)
    output = result.final_output or FALLBACK_MESSAGE
    state.last_output = output
    state.conversation_history.append({"agent": "FallbackHandler", "output": output})
    return output
