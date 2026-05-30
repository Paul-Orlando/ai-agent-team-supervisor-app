import asyncio
from datetime import datetime, timedelta
from models.state import ExecutionState

_sessions: dict[str, tuple[ExecutionState, datetime]] = {}
SESSION_TTL_MINUTES = 30


def get_or_create(session_id: str) -> ExecutionState:
    now = datetime.utcnow()
    if session_id in _sessions:
        state, _ = _sessions[session_id]
        _sessions[session_id] = (state, now)
        return state
    state = ExecutionState()
    _sessions[session_id] = (state, now)
    return state


def update(session_id: str, state: ExecutionState) -> None:
    _sessions[session_id] = (state, datetime.utcnow())


def get(session_id: str) -> ExecutionState | None:
    if session_id not in _sessions:
        return None
    state, _ = _sessions[session_id]
    return state


def remove(session_id: str) -> None:
    _sessions.pop(session_id, None)


def cleanup_expired() -> int:
    cutoff = datetime.utcnow() - timedelta(minutes=SESSION_TTL_MINUTES)
    expired = [sid for sid, (_, ts) in _sessions.items() if ts < cutoff]
    for sid in expired:
        del _sessions[sid]
    return len(expired)


async def cleanup_loop() -> None:
    while True:
        await asyncio.sleep(300)  # run every 5 minutes
        cleanup_expired()
