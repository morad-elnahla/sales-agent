"""
db.py — MongoDB Layer (Part 1 + Part 2)
collections:
  users           → signup/login
  chat_messages   → conversation history
  crm_tickets     → qualified leads
  session_names   → custom chat titles
  usage_logs      → token usage + cost + traces (Part 2)
"""
import os
from datetime import datetime, timezone
from pymongo import MongoClient, DESCENDING, ASCENDING

_client = None
_db     = None


def _get_db():
    global _client, _db
    if _db is None:
        try:
            import streamlit as st
            uri = st.secrets["MONGODB_URI"]
        except Exception:
            uri = os.environ["MONGODB_URI"]
        _client = MongoClient(uri)
        _db     = _client["kayfa_sales"]
    return _db


# ── Users (Auth) ──────────────────────────────────────────────────────────────

def create_user(username: str, password_hash: str, salt: str, role: str) -> bool:
    col = _get_db()["users"]
    if col.find_one({"username": username}):
        return False
    col.insert_one({
        "username":      username,
        "password_hash": password_hash,
        "salt":          salt,
        "role":          role,
        "created_at":    datetime.now(timezone.utc).isoformat(),
    })
    return True


def find_user(username: str) -> dict | None:
    return _get_db()["users"].find_one({"username": username})


# ── CRM Tickets ───────────────────────────────────────────────────────────────

def save_crm_ticket(ticket: dict) -> str:
    result = _get_db()["crm_tickets"].insert_one(ticket)
    return str(result.inserted_id)


def load_all_tickets() -> list[dict]:
    tickets = list(_get_db()["crm_tickets"].find({}).sort("created_at", DESCENDING))
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
    docs = list(
        _get_db()["chat_messages"]
        .find({"session_id": session_id})
        .sort("created_at", ASCENDING)
    )
    return [{"role": d["role"], "content": d["content"]} for d in docs]


def delete_session(session_id: str):
    _get_db()["chat_messages"].delete_many({"session_id": session_id})
    _get_db()["session_names"].delete_one({"session_id": session_id})


def save_session_name(session_id: str, name: str):
    _get_db()["session_names"].update_one(
        {"session_id": session_id},
        {"$set": {"name": name}},
        upsert=True,
    )


def load_session_names() -> dict:
    return {
        doc["session_id"]: doc["name"]
        for doc in _get_db()["session_names"].find({})
    }


# ── Usage Logs (Part 2) ───────────────────────────────────────────────────────

def save_usage_log(log: dict) -> str:
    """
    log schema:
      user_id, conversation_id, user_prompt, model, provider,
      input_tokens, output_tokens,
      embedding_model, embedding_provider, embedding_tokens,
      tool_calls: [{tool_name, args, result, tool_call_id}],
      final_response, llm_cost_usd, embedding_cost_usd, total_cost_usd,
      latency_ms, timestamp
    """
    col    = _get_db()["usage_logs"]
    col.create_index([("user_id", ASCENDING), ("timestamp", DESCENDING)])
    col.create_index([("conversation_id", ASCENDING), ("timestamp", ASCENDING)])
    result = col.insert_one(log)
    return str(result.inserted_id)


def load_usage_logs(
    user_id: str | None = None,
    conversation_id: str | None = None,
    limit: int = 200,
) -> list[dict]:
    col    = _get_db()["usage_logs"]
    query  = {}
    if user_id:
        query["user_id"] = user_id
    if conversation_id:
        query["conversation_id"] = conversation_id
    docs = list(col.find(query).sort("timestamp", DESCENDING).limit(limit))
    for d in docs:
        d["_id"] = str(d["_id"])
    return docs


def get_cost_by_user() -> list[dict]:
    """Returns [{user_id, total_cost_usd, total_messages, total_input_tokens, total_output_tokens}]"""
    pipeline = [
        {"$group": {
            "_id":                 "$user_id",
            "total_cost_usd":      {"$sum": "$total_cost_usd"},
            "total_messages":      {"$sum": 1},
            "total_input_tokens":  {"$sum": "$input_tokens"},
            "total_output_tokens": {"$sum": "$output_tokens"},
            "total_embed_tokens":  {"$sum": "$embedding_tokens"},
        }},
        {"$sort": {"total_cost_usd": -1}},
    ]
    return list(_get_db()["usage_logs"].aggregate(pipeline))


def get_cost_by_conversation(user_id: str | None = None) -> list[dict]:
    match = {}
    if user_id:
        match["user_id"] = user_id
    pipeline = [
        *([ {"$match": match} ] if match else []),
        {"$sort": {"timestamp": 1}},     
        {"$group": {
            "_id":            "$conversation_id",
            "user_id":        {"$first": "$user_id"},
            "total_cost_usd": {"$sum":   "$total_cost_usd"},
            "message_count":  {"$sum":   1},
            "first_prompt":   {"$first": "$user_prompt"},
            "last_ts":        {"$last":  "$timestamp"},
        }},
        {"$sort": {"last_ts": -1}},
        {"$limit": 50},
    ]
    return list(_get_db()["usage_logs"].aggregate(pipeline))
