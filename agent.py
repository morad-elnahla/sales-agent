"""
agent.py — Kayfa AI Sales Agent (Groq LLaMA 3.3 + Gemini Embeddings)
"""

import os
import re
import time
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
    ToolCallPart,
    ToolReturnPart,
)
from openai import AsyncOpenAI

import knowledge as kb
from db import save_crm_ticket as db_save

load_dotenv()

# ── Pricing (illustrative — update with live rates) ──────────────────────────
PRICING = {
    "llm": {
        "model":           "openai/gpt-oss-120b",
        "provider":        "Groq",
        "input_per_1m":    0.15,   # USD per 1M input tokens
        "output_per_1m":   0.60,   # USD per 1M output tokens
    },
    "embedding": {
        "model":           "gemini-embedding-001",
        "provider":        "Google",
        "per_1m":          0.13,   # USD per 1M tokens
    },
}

def _calc_cost(input_tok: int, output_tok: int, embed_tok: int) -> tuple[float, float, float]:
    """Returns (llm_cost, embed_cost, total_cost) in USD."""
    llm   = (input_tok * PRICING["llm"]["input_per_1m"] +
             output_tok * PRICING["llm"]["output_per_1m"]) / 1_000_000
    embed = embed_tok * PRICING["embedding"]["per_1m"] / 1_000_000
    return round(llm, 8), round(embed, 8), round(llm + embed, 8)

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
❌ لا تقارن Kayfa بالمنافسين بأسلوب سلبي.
💬 لو الزبون بعت small talk أو نكتة أو سؤال بره النطاق → تفاعل معاه بخفة ودفء جملة واحدة، ثم أعده للموضوع بسلاسة.
   مثال: لو طلب نكتة → احكيها بإيجاز ثم قل "بس أنا أمهر في Data Science من النكت 😄 — إيه المجال اللي بتفكر فيه؟"
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

━━━━━━━━━━━━━━━━━━━━━━━━━━━
 التحقق من البيانات قبل الحفظ (إلزامي)
━━━━━━━━━━━━━━━━━━━━━━━━━━━
قبل استدعاء save_lead_tool، تأكد من صحة هذه الحقول:

✅ الاسم: حرفان على الأقل، ليس أرقاماً فقط.
✅ الإيميل: صيغة صحيحة (user@domain.com). إذا قدّم العميل إيميلاً غير واضح → اطلب منه تأكيده.
✅ رقم الهاتف: 7-15 رقماً، ويُفضّل مع كود الدولة (+20...). إذا ناقص كود الدولة → اسأل.
✅ المدينة/الدولة: ليست فارغة.

لو أي حقل مشكوك فيه → اطلب من العميل تأكيده قبل الحفظ:
"تأكيداً، إيميلك هو X ورقمك Y صح؟"

قواعد استخراج البيانات عند حفظ الـ ticket (مهم جداً):
- استخرج الاسم والهاتف والإيميل والمدينة من تاريخ المحادثة كله — حتى لو أرسلهم الزبون في رسالة واحدة
- مثال: لو الزبون كتب "morad +201024011971 moradelnahla@gmail.com egypt" فـ:
  name="Morad", phone="+201024011971", email="moradelnahla@gmail.com", city="Egypt"
- لا تترك email أو city فارغَين أبداً لو الزبون ذكرهم في أي رسالة سابقة
- راجع تاريخ المحادثة بالكامل قبل استدعاء save_lead_tool

━━━━━━━━━━━━━━━━━━━━━━━━━━━
 قواعد حفظ بيانات الـ CRM Ticket
━━━━━━━━━━━━━━━━━━━━━━━━━━━
عند استدعاء save_lead_tool، التزم بهذه القواعد تماماً:

📝 conversation_summary:
- اكتبه بالعربي دائماً — حتى لو المحادثة كانت بالإنجليزي.
- لخّص في 2-3 جمل دقيقة: ماذا طلب الزبون + ما الكورسات/المسارات التي عُرضت عليه + قراره أو ردّه الفعلي.
- كن دقيقاً في التفاصيل: لو اختار كورساً بعينه اذكره، لو طلب الأول اذكر "أول كورس في المسار" وليس "أول يوم".
- لا تكتب معلومات خاطئة أو مخمّنة — اعتمد فقط على ما قاله الزبون فعلاً.
- مثال صحيح: "اهتم الزبون بمسار Data Analysis وعُرضت عليه 3 كورسات، طلب التسجيل في أول كورس في المسار وأبدى رغبته في معرفة تفاصيل الدفع."
- مثال خاطئ: "أبدى المستخدم اهتماماً وطلب التسجيل في أول يوم." ← غير دقيق ومبهم

⚡ recommended_action:
- اكتبه بالعربي دائماً — حتى لو المحادثة كانت بالإنجليزي.
- جملة واحدة قصيرة — إجراء محدد وعملي لفريق المبيعات.
- مثال صحيح: "إرسال تفاصيل تسجيل دبلومة Fullstack فوراً."
- مثال خاطئ: "send registration details"

🌡️ temperature:
- hot   → مستعد للشراء الآن (سأل عن الدفع أو موعد البدء صراحةً)
- warm  → مهتم وعنده نية لكن لم يقرر بعد
- cold  → مجرد استفسار عام بدون نية واضحة

📌 buying_signals و objections:
- اكتبهم بالعربي — جمل قصيرة تعكس ما قاله الزبون فعلاً.
- لو ما في objections → اتركها فارغة ("").

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


_ARABIC_CHAR_RE = re.compile(r"[\u0600-\u06FF]")
_LETTER_RE = re.compile(r"[^\W\d_]", re.UNICODE)


def _is_mostly_arabic(text: str) -> bool:
    """يرجع True لو أغلب الحروف في النص عربي. نص فاضي يعتبر عربي (مفيش حاجة نترجمها)."""
    if not text or not text.strip():
        return True
    letters = _LETTER_RE.findall(text)
    if not letters:
        return True
    arabic_letters = _ARABIC_CHAR_RE.findall(text)
    return len(arabic_letters) >= 0.4 * len(letters)


async def _force_arabic(text: str) -> str:
    """
    شبكة أمان: لو الموديل كتب الملخص/الإجراء بالإنجليزي بالغلط رغم تعليمات
    الـ system prompt، نترجمه فوراً بنفسنا قبل التخزين في الـ CRM — بدل ما
    نعتمد بس على التزام الموديل بالتعليمات.
    """
    if _is_mostly_arabic(text):
        return text
    try:
        resp = await _groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            temperature=0,
            max_tokens=200,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "ترجم النص التالي للعربية الفصحى المبسطة. "
                        "رجّع الترجمة فقط بدون أي شرح أو علامات تنصيص."
                    ),
                },
                {"role": "user", "content": text},
            ],
        )
        translated = resp.choices[0].message.content.strip()
        return translated if translated else text
    except Exception as e:
        print(f"⚠️ DEBUG: فشلت ترجمة النص لعربي ({e}) — استخدام النص الأصلي.")
        return text


@sales_agent.tool
async def save_lead_tool(
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
    """Save a qualified lead as a CRM ticket in MongoDB. Call this once you have the customer name and phone number.

    Args:
        name: Customer's full name.
        phone: Customer's phone number with country code.
        email: Customer's email address.
        city: Customer's city/country.
        interest: The course/track/diploma the customer is interested in.
        goal: The customer's stated learning or career goal.
        current_level: Customer's current skill level (beginner/intermediate/advanced).
        temperature: Lead temperature — "hot", "warm", or "cold".
        buying_signals: Short phrases (in Arabic) reflecting buying signals the customer expressed.
        objections: Short phrases (in Arabic) reflecting objections, or "" if none.
        conversation_summary: MUST be written in Arabic only, even if the conversation was in English.
            1-2 sentences summarizing what the customer asked for and what was offered.
            Example: "أبدى المستخدم اهتماماً بدبلومة Fullstack وطلب تفاصيل التسجيل."
        recommended_action: MUST be written in Arabic only, even if the conversation was in English.
            One short, concrete next action for the sales team.
            Example: "إرسال تفاصيل تسجيل دبلومة Fullstack فوراً."
        preferred_language: The language the customer prefers to be contacted in (e.g. "Arabic", "English").
    """
    # ══════════════════════════════════════════════════
    # Validation — تحقق من صحة البيانات قبل الحفظ
    # ══════════════════════════════════════════════════
    errors = []

    # 1. الاسم: حرفين على الأقل، لا يحتوي على أرقام فقط
    _name = name.strip() if name else ""
    if len(_name) < 2:
        errors.append("• الاسم يجب أن يكون حرفين على الأقل.")
    elif re.fullmatch(r'[\d\s]+', _name):
        errors.append("• الاسم لا يمكن أن يكون أرقاماً فقط.")

    # 2. البريد الإلكتروني: صيغة email صحيحة
    _email = email.strip() if email else ""
    _email_re = re.compile(
        r'^[a-zA-Z0-9_.+\-]+@[a-zA-Z0-9\-]+\.[a-zA-Z0-9\-.]+$'
    )
    if not _email:
        errors.append("• البريد الإلكتروني مطلوب.")
    elif not _email_re.match(_email):
        errors.append(f"• البريد الإلكتروني «{_email}» غير صحيح — يجب أن يكون بصيغة example@domain.com.")

    # 3. رقم الهاتف: أرقام + رمز الدولة (يبدأ بـ + أو 00 أو 0)
    _phone = re.sub(r'[\s\-\(\)]+', '', phone or '')
    _phone_re = re.compile(r'^(\+|00)?[0-9]{7,15}$')
    if not _phone:
        errors.append("• رقم الهاتف مطلوب.")
    elif not _phone_re.match(_phone):
        errors.append(f"• رقم الهاتف «{phone}» غير صحيح — يجب أن يحتوي على 7–15 رقماً ويفضّل أن يبدأ برمز الدولة (مثال: +20...).")

    # 4. المدينة/الدولة: ليست فارغة
    _city = city.strip() if city else ""
    if not _city:
        errors.append("• المدينة أو الدولة مطلوبة.")

    if errors:
        err_msg = (
            "⚠️ **لم يتم حفظ البيانات** — يرجى مراجعة المعلومات التالية مع العميل:\n\n"
            + "\n".join(errors)
            + "\n\nاطلب من العميل تصحيح هذه البيانات ثم حاول الحفظ مجدداً."
        )
        return err_msg

    # ══════════════════════════════════════════════════
    # شبكة أمان لغوية — تتأكد إن الملخص والإجراء عربي فعلاً قبل التخزين
    conversation_summary = await _force_arabic(conversation_summary)
    recommended_action = await _force_arabic(recommended_action)

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


def _extract_tool_calls(messages) -> list[dict]:
    """
    Extracts tool calls + results from pydantic-ai new_messages().
    Matches ToolCallPart (in ModelResponse) with ToolReturnPart (in ModelRequest)
    by tool_call_id.
    """
    pending: dict[str, dict] = {}   # tool_call_id → call dict
    ordered: list[dict] = []

    for msg in messages:
        if isinstance(msg, ModelResponse):
            for part in msg.parts:
                if isinstance(part, ToolCallPart):
                    try:
                        args = part.args_as_dict()
                    except Exception:
                        args = {"raw": str(part.args)[:300]}
                    entry = {
                        "tool_name":    part.tool_name,
                        "args":         args,
                        "result":       None,
                        "tool_call_id": part.tool_call_id,
                    }
                    pending[part.tool_call_id] = entry
                    ordered.append(entry)
        elif isinstance(msg, ModelRequest):
            for part in msg.parts:
                if isinstance(part, ToolReturnPart):
                    if part.tool_call_id in pending:
                        pending[part.tool_call_id]["result"] = str(part.content)[:600]

    return ordered


def get_agent_reply(
    user_message: str,
    message_history: list,
    session_id: str = "",
    user_id: str = "anonymous",
) -> tuple[str, list]:
    print(f"📨 DEBUG: incoming history length = {len(message_history)}")
    t0 = time.time()

    result = sales_agent.run_sync(
        user_message,
        deps=SalesDeps(session_id=session_id),
        message_history=message_history,
    )

    latency_ms = int((time.time() - t0) * 1000)

    # ── Token usage ──
    try:
        usage        = result.usage()
        input_tokens  = usage.input_tokens  or 0
        output_tokens = usage.output_tokens or 0
    except Exception:
        input_tokens = output_tokens = 0

    # ── Embedding tokens (from knowledge.py counter) ──
    embed_tokens = kb.get_and_reset_embedding_tokens()

    # ── Tool call trace ──
    tool_calls = _extract_tool_calls(result.new_messages())

    # ── Cost ──
    llm_cost, embed_cost, total_cost = _calc_cost(
        input_tokens, output_tokens, embed_tokens
    )

    # ── Save usage log ──
    try:
        from db import save_usage_log
        save_usage_log({
            "user_id":            user_id,
            "conversation_id":    session_id,
            "user_prompt":        user_message[:500],
            "model":              PRICING["llm"]["model"],
            "provider":           PRICING["llm"]["provider"],
            "input_tokens":       input_tokens,
            "output_tokens":      output_tokens,
            "embedding_model":    PRICING["embedding"]["model"],
            "embedding_provider": PRICING["embedding"]["provider"],
            "embedding_tokens":   embed_tokens,
            "tool_calls":         tool_calls,
            "final_response":     result.output[:2000],
            "llm_cost_usd":       llm_cost,
            "embedding_cost_usd": embed_cost,
            "total_cost_usd":     total_cost,
            "latency_ms":         latency_ms,
            "timestamp":          datetime.now(timezone.utc).isoformat(),
        })
    except Exception as e:
        print(f"⚠️ usage_log save failed: {e}")

    return result.output, result.all_messages()