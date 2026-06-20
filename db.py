"""
db.py — MongoDB CRM Layer
chat messages   → kayfa_sales.chat_messages   (منفصلة)
CRM tickets     → kayfa_sales.crm_tickets     (منفصلة)
"""
import os
from datetime import datetime, timezone
from pymongo import MongoClient, DESCENDING, ASCENDING

_client   = None
_db       = None

def _get_db():
    global _client, _db
    if _db is None:
        _client = MongoClient(os.environ["MONGODB_URI"])
        _db     = _client["kayfa_sales"]
    return _db

# ── CRM Tickets ───────────────────────────────────────────────────────────────

def save_crm_ticket(ticket: dict) -> str:
    col    = _get_db()["crm_tickets"]
    result = col.insert_one(ticket)
    return str(result.inserted_id)

def load_all_tickets() -> list[dict]:
    col     = _get_db()["crm_tickets"]
    tickets = list(col.find({}).sort("created_at", DESCENDING))
    for t in tickets:
        t["_id"] = str(t["_id"])
    return tickets

# ── Chat Messages ─────────────────────────────────────────────────────────────

def save_chat_turn(session_id: str, role: str, content: str):
    col = _get_db()["chat_messages"]
    col.create_index([("session_id", ASCENDING), ("created_at", ASCENDING)])
    col.insert_one({
        "session_id": session_id,
        "role":       role,
        "content":    content,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })

def load_session_history() -> list[dict]:
    """آخر 20 محادثة مع أول رسالة كـ title."""
    col = _get_db()["chat_messages"]
    pipeline = [
        {"$sort":  {"created_at": 1}},
        {"$group": {
            "_id":       "$session_id",
            "first_msg": {"$first": "$content"},
            "last_at":   {"$last":  "$created_at"},
        }},
        {"$sort":  {"last_at": -1}},
        {"$limit": 20},
    ]
    return list(col.aggregate(pipeline))

def load_session_messages(session_id: str) -> list[dict]:
    col  = _get_db()["chat_messages"]
    docs = list(col.find({"session_id": session_id}).sort("created_at", ASCENDING))
    return [{"role": d["role"], "content": d["content"]} for d in docs]

def delete_session(session_id: str):
    """Delete all messages belonging to a session."""
    col = _get_db()["chat_messages"]
    col.delete_many({"session_id": session_id})
    # Also remove any saved name
    _get_db()["session_names"].delete_one({"session_id": session_id})


def save_session_name(session_id: str, name: str):
    """Persist a custom name for a session in MongoDB."""
    col = _get_db()["session_names"]
    col.update_one(
        {"session_id": session_id},
        {"$set": {"name": name}},
        upsert=True,
    )


def load_session_names() -> dict:
    """Return {session_id: name} for all named sessions."""
    col = _get_db()["session_names"]
    return {doc["session_id"]: doc["name"] for doc in col.find({})}
