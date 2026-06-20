"""
agent.py — Kayfa AI Sales Agent (Groq LLaMA 3.3 + Gemini Embeddings)
"""

import os
from dataclasses import dataclass
from datetime import datetime, timezone

from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.messages import (
    ModelRequest,
    ModelResponse,
    UserPromptPart,
    TextPart,
)
from openai import AsyncOpenAI

import knowledge as kb
from db import save_crm_ticket as db_save

load_dotenv()

@dataclass
class SalesDeps:
    session_id: str = ""

SYSTEM_PROMPT = f"""
أنت "كيف" — مساعد مبيعات ذكي لمنصة Kayfa التعليمية.

━━━━━━━━━━━━━━━━━━━━━━━━━━━
 هويتك
━━━━━━━━━━━━━━━━━━━━━━━━━━━
- اسمك "كيف" — مستوحى من اسم المنصة.
- مهمتان في آنٍ واحد:
  ① ترشد الزوار لأنسب كورس/مسار بأسلوب مفيد وصادق.
  ② لما تحس بـ buying signal → تجمع بيانات الزبون وتحفظها CRM ticket.

━━━━━━━━━━━━━━━━━━━━━━━━━━━
 اللغة
━━━━━━━━━━━━━━━━━━━━━━━━━━━
- الرد الافتراضي: عربي فصيح مبسط — طبيعي ومريح.
- لو الزبون كتب إنجليزي أو خلّط → رد بنفس اللغة.
- اللهجات (مصري / سوري / سعودي) → افهمها وارد بالفصيح.
- أسماء الأدوات والتقنيات → خلّيها إنجليزي كما هي:
  Python, Power BI, SQL, SOC, Splunk, Docker, React …

━━━━━━━━━━━━━━━━━━━━━━━━━━━
 فهم نية الزبون (Intent)
━━━━━━━━━━━━━━━━━━━━━━━━━━━
صنّف كل رسالة وكيّف ردودك:

🔍 BROWSING   → اسأل عن هدفه ومستواه، ارشده للمجال الصح
🤔 COMPARING  → قدّم مقارنة واضحة وأمينة
💰 PRICE_SENS → ابدأ بالمجاني، ثم كورسات فردية، ثم tracks
😟 HESITANT   → طمّنه: لا deadlines، في preview مجاني، استرداد واضح
🔥 READY      → انتقل بسلاسة لجمع بياناته وحفظ الـ CRM ticket

━━━━━━━━━━━━━━━━━━━━━━━━━━━
 استراتيجية المبيعات
━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. ابدأ من حيث يرتاح الزبون:
   مجاني ($0) → كورسات ($15–$65) → Tracks ($25–$250) → Diplomas
2. اهدف للـ Diploma مع الـ leads الجادة — أعلى قيمة.
3. استخدم الـ social proof الحقيقي:
   "+15,000 متعلم" | "معتمد من IAO" | "شراكة Microsoft وGIZ"
4. عالج الاعتراضات بصدق من الداتا الحقيقية فقط.

━━━━━━━━━━━━━━━━━━━━━━━━━━━
 قواعد صارمة
━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ لا تخترع سعراً أو كورساً أو معلومة — من الـ knowledge base بس.
❌ لو ما عرفتش → "دعني أوصلك بالفريق: support@kayfa.io"
❌ لا تخرج من دور مساعد مبيعات Kayfa.
❌ لا تقارن Kayfa بالمنافسين بأسلوب سلبي.
━━━━━━━━━━━━━━━━━━━━━━━━━━━
 طريقة الرد على أسئلة التعلم
━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ لما أي شخص يسأل عن مجال أو تقنية، استدعِ الـ tools أولاً ثم قدّم الرد بهذا الشكل الثابت:

**[اسم المسار أو الدبلومة]**
🎯 المستهدف: [من يناسبه]
📚 المحتوى: [3-4 نقاط قصيرة أهم ما ستتعلمه]
⏱️ المدة: [المدة]
💰 السعر: [السعر بالدولار]
🔗 [رابط التسجيل]

ثم سطر واحد فقط للتحفيز + سؤال قصير للمتابعة.

قواعد الصياغة:
- اسم المسار دايماً **bold** وكبير
- نقاط قصيرة — مش فقرات طويلة
- سعر حقيقي من الداتا — مش تقريبي
- سؤال واحد في النهاية بس مش أكثر
- ممنوع فقرات نثرية طويلة
- ممنوع "زور الموقع" — ضع الرابط مباشرة

━━━━━━━━━━━━━━━━━━━━━━━━━━━
 متى تجمع بيانات الـ Lead؟
━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ سأل عن الدفع أو موعد البدء أو التقسيط
✅ طلب مقارنة تفصيلية بين برنامجين
✅ قال "عايز أسجّل" أو "كيف أشترك"
✅ سأل عن الشهادة أو التوظيف
✅ بعد 3+ رسائل مهتمة بدون نية المغادرة

اجمع بسلاسة في سياق الكلام — اطلب الأربعة مع بعض:
"عشان أقدر أبعتلك تفاصيل التسجيل، ممكن تعطيني اسمك، رقم واتساب، إيميلك، ومدينتك/دولتك؟"

قواعد استخراج البيانات عند حفظ الـ ticket (مهم جداً):
- استخرج الاسم والهاتف والإيميل والمدينة من تاريخ المحادثة كله — حتى لو أرسلهم الزبون في رسالة واحدة
- مثال: لو الزبون كتب "morad +201024011971 moradelnahla@gmail.com egypt" فـ:
  name="Morad", phone="+201024011971", email="moradelnahla@gmail.com", city="Egypt"
- لا تترك email أو city فارغَين أبداً لو الزبون ذكرهم في أي رسالة سابقة
- راجع تاريخ المحادثة بالكامل قبل استدعاء save_lead_tool

━━━━━━━━━━━━━━━━━━━━━━━━━━━
 KNOWLEDGE BASE
━━━━━━━━━━━━━━━━━━━━━━━━━━━
{kb.MASTER_CONTEXT}
""".strip()

import streamlit as st

def _get_secret(key):
    try:
        return st.secrets[key]
    except Exception:
        return os.environ.get(key, "")

_groq_client = AsyncOpenAI(
    api_key=_get_secret("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

_groq_model = OpenAIModel(
    "openai/gpt-oss-120b",
    provider=OpenAIProvider(openai_client=_groq_client),
)

sales_agent = Agent(
    model=_groq_model,
    deps_type=SalesDeps,
    system_prompt=SYSTEM_PROMPT,
)


@sales_agent.tool
def search_courses_tool(
    ctx: RunContext[SalesDeps],
    query: str = "",
    track: str = "",
    level: str = "",
) -> str:
    """Search Kayfa course catalog by keyword. Use for specific skills or technologies like python, sql, linux, power bi.

    Args:
        query: Keyword to search for (e.g. "python", "sql"). Leave empty if filtering only by track/level.
        track: Optional track name to filter by (e.g. "Data Science", "Cybersecurity"). Leave empty if not filtering.
        level: Optional course level to filter by (e.g. "Beginner", "Intermediate", "Advanced"). Leave empty if not filtering.
    """
    results = kb.search_courses(query=query, track=track, level=level, max_results=5)
    if not results:
        return f"No courses found for '{query}'."
    lines = [f"Found {len(results)} courses:\n"]
    for c in results:
        t = ", ".join(c["track"]) if isinstance(c["track"], list) else c["track"]
        lines.append(
            f"• {c['name']}\n"
            f"  Level: {c['level']} | Duration: {c['duration']}\n"
            f"  Track: {t}\n"
            f"  Prerequisites: {c['prerequisites']}\n"
            f"  {c['summary']}\n"
            f"  🔗 {c['link']}\n"
        )
    return "\n".join(lines)


@sales_agent.tool
def search_roadmaps_tool(
    ctx: RunContext[SalesDeps],
    query: str = "",
    roadmap_type: str = "",
) -> str:
    """Search Kayfa learning tracks and diplomas. Use for full learning paths like data science, cybersecurity, web development.

    Args:
        query: Keyword to search for (e.g. "data science", "cybersecurity"). Leave empty if filtering only by roadmap_type.
        roadmap_type: Optional filter — "track" for self-paced tracks, "diploma" for live diplomas. Leave empty for both.
    """
    results = kb.search_roadmaps(query=query, roadmap_type=roadmap_type, max_results=5)
    if not results:
        return f"No roadmaps found for '{query}'."
    lines = [f"Found {len(results)} roadmaps:\n"]
    for r in results:
        label = "🎓 Live Diploma" if r["type"] == "diploma" else "📚 Self-Paced Track"
        lines.append(
            f"• {r['name']} — {label}\n"
            f"  Duration: {r['duration']} | Courses: {r['courses_count']}\n"
            f"  Skills: {', '.join(r['skills'][:4])}\n"
            f"  Tools: {', '.join(r['tools'][:4])}\n"
            f"  {r['summary']}\n"
            f"  🔗 {r['link']}\n"
        )
    return "\n".join(lines)


@sales_agent.tool
def semantic_search_tool(ctx: RunContext[SalesDeps], query: str) -> str:
    """Deep semantic search across all Kayfa content. Use for complex or descriptive queries that keyword search cannot handle."""
    results = kb.semantic_search(query=query, top_k=4)
    if not results:
        return "Semantic search unavailable."
    lines = [f"Top {len(results)} semantic results:\n"]
    for r in results:
        lines.append(f"• [{r['type'].upper()}] {r['name']}\n  {r['text'][:300]}\n")
    return "\n".join(lines)


@sales_agent.tool
def save_lead_tool(
    ctx: RunContext[SalesDeps],
    name: str,
    phone: str,
    email: str,
    city: str,
    interest: str,
    goal: str,
    current_level: str,
    temperature: str,
    buying_signals: str,
    objections: str,
    conversation_summary: str,
    recommended_action: str,
    preferred_language: str,
) -> str:
    """Save a qualified lead as a CRM ticket in MongoDB. Call this once you have the customer name and phone number."""
    ticket = {
        "session_id":           ctx.deps.session_id,
        "name":                 name,
        "phone":                phone,
        "email":                email,
        "city":                 city,
        "interest":             interest,
        "goal":                 goal,
        "current_level":        current_level,
        "temperature":          temperature,
        "buying_signals":       buying_signals,
        "objections":           objections,
        "conversation_summary": conversation_summary,
        "recommended_action":   recommended_action,
        "preferred_language":   preferred_language,
        "created_at":           datetime.now(timezone.utc).isoformat(),
    }
    db_save(ticket)
    return f"✅ CRM ticket saved — {name} | {interest} | {temperature}"


def rebuild_message_history(stored_messages: list[dict]) -> list:
    """
    حوّل اللي محفوظ في MongoDB (role/content بس) لصيغة pydantic-ai
    الصحيحة (ModelRequest/ModelResponse) عشان الموديل يقدر يفتكر
    المحادثة لما المستخدم يفتح شات قديم من الـ sidebar.
    """
    history: list = []
    for msg in stored_messages:
        role = msg.get("role")
        content = msg.get("content", "")
        if role == "user":
            history.append(ModelRequest(parts=[UserPromptPart(content=content)]))
        elif role == "assistant":
            history.append(ModelResponse(parts=[TextPart(content=content)]))
    return history


def get_agent_reply(
    user_message: str,
    message_history: list,
    session_id: str = "",
) -> tuple[str, list]:
    print(f"📨 DEBUG: incoming history length = {len(message_history)}")  # ← ضيف السطر ده
    result = sales_agent.run_sync(
        user_message,
        deps=SalesDeps(session_id=session_id),
        message_history=message_history,
    )
    return result.output, result.all_messages()