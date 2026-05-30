"""Planner agent — decomposes user request into execution plan (from workflow.png)."""
from agents import Agent, Runner, ModelSettings

SYSTEM_PROMPT = """You are a strategic AI Task Planner.

RESPONSIBILITIES:
1. Decompose the user request into specific, actionable implementation tasks.
2. Define measurable success criteria for each task.
3. Identify required technical skills and tools.
4. Estimate complexity and potential risks.
5. Structure output for Supervisor consumption.

OUTPUT FORMAT:
1. Execution Plan (numbered tasks)
2. Success Criteria
3. Required Skills
4. Complexity Assessment (Low / Medium / High)
5. Risk Factors"""


def build_planner(model: str = "gpt-4o-mini") -> Agent:
    return Agent(
        name="Planner",
        instructions=SYSTEM_PROMPT,
        model=model,
        model_settings=ModelSettings(temperature=0.7),
    )


async def run_planner(user_input: str, rag_context: str, model: str = "gpt-4o-mini") -> str:
    agent = build_planner(model)
    context_block = f"KNOWLEDGE BASE CONTEXT:\n{rag_context}\n\n---\n\n" if rag_context else ""
    prompt = f"{context_block}User Request:\n{user_input}"
    result = await Runner.run(agent, prompt)
    return result.final_output or ""
