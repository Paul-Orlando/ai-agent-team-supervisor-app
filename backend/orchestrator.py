"""
Main orchestration loop — translates Flowise graph to Python.

Flow:
  user_input
    → Planner (plan)
    → while iteration < max_iterations:
          Supervisor (SupervisorDecision) → next={SOFTWARE|REVIEWER|FINISH}
          if SOFTWARE → SoftwareEngineer (stream)
          elif REVIEWER → CodeReviewer (stream)
          elif FINISH → break
          if iterations >= max_iterations → Fallback
    → FinalSynthesizer (stream)
"""
import json
import uuid
from typing import AsyncGenerator
from datetime import datetime

from models.state import ExecutionState
from models.schemas import RunAgentsRequest
from agent_workers.planner import run_planner
from agent_workers.supervisor import run_supervisor
from agent_workers.software_engineer import stream_engineer
from agent_workers.code_reviewer import stream_reviewer
from agent_workers.synthesizer import stream_synthesizer
from agent_workers.fallback import run_fallback
from rag import store as rag_store
from sessions import manager as session_manager


def _event(type_: str, **kwargs) -> str:
    return json.dumps({"type": type_, **kwargs})


async def run_pipeline(
    request: RunAgentsRequest,
    session_id: str,
) -> AsyncGenerator[str, None]:

    state = ExecutionState(
        execution_id=str(uuid.uuid4()),
        user_input=request.user_input,
        model=request.model,
        max_iterations=request.max_iterations,
    )
    state.record_timestamp("pipeline_start")

    # ── RAG context helper ──────────────────────────────────────────
    async def get_rag_context(query: str) -> str:
        chunks = await rag_store.query(query, n_results=3)
        if not chunks:
            return ""
        return "\n\n".join(f"[Context {i+1}]\n{c}" for i, c in enumerate(chunks))

    # ── 1. PLANNER ──────────────────────────────────────────────────
    yield _event("agent_start", agent="planner", message="🔄 Planner thinking...")
    yield _event("state_update", state=state.to_dict())

    rag_ctx = await get_rag_context(request.user_input)
    state.plan = await run_planner(request.user_input, rag_ctx, request.model)
    state.add_tokens(len(state.plan) // 4)
    state.record_timestamp("planner_complete")

    yield _event("agent_complete", agent="planner", output=state.plan)
    yield _event("state_update", state=state.to_dict())

    # ── 2. SUPERVISOR LOOP ──────────────────────────────────────────
    # Flowise loop: max 3 per loop node, user-configurable up to max_iterations
    loop_limit = min(state.max_iterations, 10)

    while state.iteration_count < loop_limit:
        yield _event("agent_start", agent="supervisor", message="🔄 Supervisor routing...")

        rag_ctx = await get_rag_context(f"{request.user_input} {state.current_task}")
        decision = await run_supervisor(state, rag_ctx, request.model)
        state.add_tokens(len(decision.instructions) // 4)

        # Apply decision to state (mirrors Flowise llmUpdateState)
        state.next = decision.next
        state.instructions = decision.instructions
        state.current_task = decision.currentTask
        state.review_status = decision.reviewStatus
        state.record_timestamp(f"supervisor_iter_{state.iteration_count}")

        yield _event(
            "agent_complete",
            agent="supervisor",
            output=f"→ {decision.next}: {decision.currentTask}",
        )
        yield _event("state_update", state=state.to_dict())
        yield _event("review_status", status=state.review_status)

        # ── Condition check (Flowise conditionAgentflow_0) ──────────
        if decision.next == "SOFTWARE":
            state.iteration_count += 1
            yield _event("agent_start", agent="engineer", message="🔄 Engineer building...")

            rag_ctx = await get_rag_context(state.instructions)
            async for chunk in stream_engineer(state, rag_ctx, request.model):
                yield _event("stream_chunk", content=chunk, agent="engineer")

            state.record_timestamp(f"engineer_iter_{state.iteration_count}")
            yield _event("agent_complete", agent="engineer", output="[implementation complete]")
            yield _event("state_update", state=state.to_dict())

        elif decision.next == "REVIEWER":
            state.iteration_count += 1
            yield _event("agent_start", agent="reviewer", message="🔄 Reviewer checking...")

            rag_ctx = await get_rag_context(state.instructions)
            async for chunk in stream_reviewer(state, rag_ctx, request.model):
                yield _event("stream_chunk", content=chunk, agent="reviewer")

            state.record_timestamp(f"reviewer_iter_{state.iteration_count}")
            yield _event("agent_complete", agent="reviewer", output="[review complete]")
            yield _event("review_status", status=state.review_status)
            yield _event("state_update", state=state.to_dict())

        elif decision.next == "FINISH":
            yield _event("agent_start", agent="supervisor", message="✅ Supervisor: FINISH")
            break

        else:
            # Unknown routing — treat as FINISH
            break

    # ── Fallback on exhausted iterations ───────────────────────────
    if state.iteration_count >= loop_limit and state.next != "FINISH":
        yield _event("agent_start", agent="fallback", message="⚠️ Fallback: max iterations reached")
        fallback_out = await run_fallback(state, request.model)
        yield _event("agent_complete", agent="fallback", output=fallback_out)
        yield _event("state_update", state=state.to_dict())

    # ── 3. FINAL SYNTHESIZER ────────────────────────────────────────
    yield _event("agent_start", agent="synthesizer", message="🔄 Synthesizing final report...")

    rag_ctx = await get_rag_context(request.user_input)
    async for chunk in stream_synthesizer(state, rag_ctx, request.model):
        yield _event("stream_chunk", content=chunk, agent="synthesizer")

    state.record_timestamp("pipeline_complete")

    # Persist state so /download-report can retrieve it
    session_manager.update(session_id, state)

    yield _event("agent_complete", agent="synthesizer", message="✅ Synthesis complete")
    yield _event("state_update", state=state.to_dict())
    yield _event(
        "complete",
        report=state.final_report,
        execution_id=state.execution_id,
        session_id=session_id,
        tokens=state.cost_tokens,
        quality_score=state.quality_score,
        iterations=state.iteration_count,
    )
