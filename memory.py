import uuid

# In-memory sessions — migrate to Redis for persistence:
#
#   import redis, json
#   r = redis.Redis(host="localhost", port=6379, db=1)
#   def get_session(sid): history = r.get(f"session:{sid}"); return sid, json.loads(history) if history else []
#   def add_message(sid, role, content): ...

SESSIONS: dict[str, list[dict]] = {}


def get_session(session_id: str | None = None) -> tuple[str, list[dict]]:
    if not session_id:
        session_id = str(uuid.uuid4())
    if session_id not in SESSIONS:
        SESSIONS[session_id] = []
    return session_id, SESSIONS[session_id]


def add_message(session_id: str, role: str, content: str) -> None:
    SESSIONS[session_id].append({"role": role, "content": content})


def get_history(session_id: str) -> list[dict]:
    return SESSIONS.get(session_id, [])


def session_count() -> int:
    return len(SESSIONS)