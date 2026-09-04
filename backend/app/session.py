from typing import Dict
from .models import SessionData
from datetime import datetime

_sessions: Dict[str, SessionData] = {}

def get_session(session_id: str) -> SessionData:
    if session_id not in _sessions:
        _sessions[session_id] = SessionData(session_id=session_id)
    return _sessions[session_id]

def update_session(session_id: str, session_data: SessionData) -> SessionData:
    session_data.updated_at = datetime.utcnow()
    _sessions[session_id] = session_data
    return session_data

def reset_session(session_id: str) -> None:
    if session_id in _sessions:
        del _sessions[session_id]
