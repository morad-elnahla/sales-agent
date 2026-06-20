"""
knowledge.py — Kayfa Knowledge Base + Semantic Search
======================================================
بيحمّل كل الداتا ويوفر:
  1. MASTER_CONTEXT   — نص كامل يتحط في system prompt
  2. search_courses() — keyword search في الـ 48 كورس
  3. search_roadmaps()— keyword search في الـ 13 مسار
  4. semantic_search()— vector search بـ text-embedding-004

الـ embeddings بتتحسب lazy (أول مرة بس) وبتتخزن في RAM.
"""

import json
import os
import math
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
JSON_DIR = DATA_DIR / "json"
TEXT_DIR = DATA_DIR / "text"

# ============================================================================
# 1. تحميل الـ JSON
# ============================================================================
def _load_json(name):
    with open(JSON_DIR / name, encoding="utf-8") as f:
        return json.load(f)

COURSES  = _load_json("kayfa_courses.json")   # 48 course
ROADMAPS = _load_json("kayfa_roadmaps.json")  # 13 roadmap

COURSES_BY_ID  = {c["id"]: c for c in COURSES}
ROADMAPS_BY_ID = {r["id"]: r for r in ROADMAPS}
TRACKS   = [r for r in ROADMAPS if "diploma" not in r["id"].lower()]
DIPLOMAS = [r for r in ROADMAPS if "diploma" in r["id"].lower()]

# ============================================================================
# 2. تحميل الـ Markdown
# ============================================================================
def _load_md(name):
    with open(TEXT_DIR / name, encoding="utf-8") as f:
        return f.read()

COMPANY_OVERVIEW  = _load_md("kayfa_company_overview.md")
POLICIES_FAQS     = _load_md("kayfa_policies_and_faqs.md")
PRIVACY_POLICY    = _load_md("kayfa_privacy_policy.md")
PAID_COURSES_MD   = _load_md("kayfa_paid_individual_courses.md")
PAID_TRACKS_MD    = _load_md("kayfa_paid_educational_tracks.md")
FREE_CONTENT_MD   = _load_md("kayfa_free_educational_content.md")
INSTRUCTORS_MD    = _load_md("kayfa_instructor_network.md")
DIPLOMA_AI        = _load_md("kayfa_ai_diploma.md")
DIPLOMA_DS        = _load_md("kayfa_data_science_diploma.md")
DIPLOMA_SOC       = _load_md("kayfa_soc_diploma.md")
DIPLOMA_PENTEST   = _load_md("Kayfa_PenTest_Diploma.md")
DIPLOMA_FULLSTACK = _load_md("Kayfa_Fullstack_Diploma.md")

# ============================================================================
# 3. MASTER CONTEXT — كل المعلومات في نص واحد للـ system prompt
# ============================================================================
MASTER_CONTEXT = """
=== KAYFA — COMPANY IDENTITY ===
منصة تعليمية عربية رائدة تأسست بهدف تأهيل المتعلمين لسوق العمل الرقمي.
معتمدة من IAO | شراكات: Microsoft, GIZ, Paymob | +15,000 متعلم | 25 مدرب خبير.
الجهة: Kayfa Digital Solutions | info@kayfa.io | support@kayfa.io
هاتف مصر: +201 05 502 3774 | الإمارات: +971 55 387 7671 | سوريا: +963 98 337 8448
المقر: دبي (رئيسي) · القاهرة (معادي) · حماة (سوريا)

=== CATALOG SNAPSHOT (استخدم الـ tools للتفاصيل الكاملة) ===
- 48 كورس فردي — أسعار $15–$65 — مجالات: Data, Cyber, Web, AI, Marketing
- 10 tracks مسجّلة — أسعار $25–$250 — بدون مواعيد ثابتة
- 3 دبلومات لايف (5–6 أشهر، شهادة معتمدة دولياً):
  - 📊 Data Science Diploma — Python, Power BI, SQL, ML, Capstone
  - 🤖 AI Diploma — GenAI, RAG, Agents, MLOps, Computer Vision
  - 🛡️ SOC Diploma — Splunk, QRadar, Threat Hunting, Incident Response
  - 🔴 PenTest Diploma — Ethical Hacking, Burp Suite, Nmap, Capstone Report
  - 💻 Fullstack Diploma — React, Next.js, Node.js, MongoDB, Docker (55 جلسة)
- محتوى مجاني: كورسات تمهيدية + 45 جلسة مجانية في مجالات متنوعة

=== POLICIES & FAQS ===
- الدفع: أونلاين بطاقة أو تحويل | الاشتراك سنوي يتجدد تلقائياً
- الاسترداد للكورسات المسجّلة: كامل لو ما فُتحت | لا استرداد بعد الوصول
- الاسترداد للبرامج اللايف: كامل قبل 7 أيام | 80% خلال أقل من 7 أيام | لا استرداد بعد البدء
- استبدال الكورس: بنفس القيمة أو أقل قبل البدء | الفرق يُدفع لو أعلى
- لا مواعيد تسليم في الكورسات المسجّلة | بعض الكورسات فيها preview مجاني
- شهادات: معترف بها من أصحاب العمل | الدبلومات: اعتماد دولي (Delaware, Leeds Academy)
- للمساعدة: support@kayfa.io
""".strip()

# ============================================================================
# 4. Keyword Search Helpers
# ============================================================================
def search_courses(query="", track="", level="", max_results=5):
    q = query.lower()
    out = []
    for c in COURSES:
        ctracks = c.get("track", [])
        if isinstance(ctracks, str):
            ctracks = [ctracks]
        if track and track.lower() not in [t.lower() for t in ctracks]:
            continue
        if level and c.get("level","").lower() != level.lower():
            continue
        if q:
            blob = (c.get("name","") + " " + c.get("summary","") + " " + " ".join(ctracks)).lower()
            if q not in blob:
                continue
        out.append({
            "id": c["id"], "name": c["name"], "track": ctracks,
            "level": c.get("level","N/A"), "duration": c.get("duration","N/A"),
            "prerequisites": c.get("prerequisites","None"),
            "summary": c.get("summary","")[:200], "link": c.get("link",""),
        })
        if len(out) >= max_results:
            break
    return out


def search_roadmaps(query="", roadmap_type="", max_results=5):
    q = query.lower()
    pool = {"track": TRACKS, "diploma": DIPLOMAS}.get(roadmap_type, ROADMAPS)
    out = []
    for r in pool:
        if q:
            blob = (r.get("name","") + " " +
                    " ".join(r.get("skills",[])) + " " +
                    " ".join(r.get("tools",[]))).lower()
            if q not in blob:
                continue
        out.append({
            "id": r["id"], "name": r["name"],
            "summary": r.get("summary","")[:200],
            "duration": r.get("duration","N/A"),
            "courses_count": r.get("courses_count", 0),
            "skills": r.get("skills",[])[:6],
            "tools": r.get("tools",[])[:6],
            "link": r.get("link",""),
            "type": "diploma" if r in DIPLOMAS else "track",
        })
        if len(out) >= max_results:
            break
    return out


def get_courses_in_roadmap(roadmap_id):
    rm = ROADMAPS_BY_ID.get(roadmap_id)
    if not rm:
        return []
    return [
        {"name": COURSES_BY_ID[cid]["name"],
         "duration": COURSES_BY_ID[cid].get("duration","N/A"),
         "level": COURSES_BY_ID[cid].get("level","N/A"),
         "link": COURSES_BY_ID[cid].get("link","")}
        for cid in rm.get("courses_list",[])
        if cid in COURSES_BY_ID
    ]

# ============================================================================
# 5. Semantic Search بـ text-embedding-004
#    الـ chunks بتتبنى مرة واحدة عند أول استخدام (lazy init)
# ============================================================================

_chunks: list[dict] | None = None      # {"text": ..., "meta": ...}
_embeddings: list[list[float]] | None = None

def _build_chunks() -> list[dict]:
    """بيحوّل الكتالوج كله لـ chunks نصية قابلة للـ embedding."""
    chunks = []

    # كل كورس = chunk
    for c in COURSES:
        ctracks = c.get("track", [])
        if isinstance(ctracks, str):
            ctracks = [ctracks]
        text = (
            f"Course: {c['name']}\n"
            f"Track: {', '.join(ctracks)}\n"
            f"Level: {c.get('level','')}\n"
            f"Duration: {c.get('duration','')}\n"
            f"Prerequisites: {c.get('prerequisites','')}\n"
            f"Summary: {c.get('summary','')}\n"
            f"Link: {c.get('link','')}"
        )
        chunks.append({"text": text, "type": "course",
                        "name": c["name"], "link": c.get("link","")})

    # كل roadmap = chunk
    for r in ROADMAPS:
        r_type = "diploma" if r in DIPLOMAS else "track"
        text = (
            f"{'Diploma' if r_type=='diploma' else 'Track'}: {r['name']}\n"
            f"Duration: {r.get('duration','')}\n"
            f"Courses: {r.get('courses_count',0)}\n"
            f"Skills: {', '.join(r.get('skills',[]))}\n"
            f"Tools: {', '.join(r.get('tools',[]))}\n"
            f"Summary: {r.get('summary','')}\n"
            f"Link: {r.get('link','')}"
        )
        chunks.append({"text": text, "type": r_type,
                        "name": r["name"], "link": r.get("link","")})

    # الـ diploma briefs كـ chunks
    diploma_mds = [
        ("AI Diploma", DIPLOMA_AI),
        ("Data Science Diploma", DIPLOMA_DS),
        ("SOC Diploma", DIPLOMA_SOC),
        ("PenTest Diploma", DIPLOMA_PENTEST),
        ("Fullstack Diploma", DIPLOMA_FULLSTACK),
    ]
    for name, md in diploma_mds:
        chunks.append({"text": md[:2000], "type": "diploma_brief",
                        "name": name, "link": ""})

    # Company + Policies كـ chunks
    for label, text in [("Company Overview", COMPANY_OVERVIEW),
                         ("Policies & FAQs", POLICIES_FAQS)]:
        chunks.append({"text": text[:2000], "type": "policy",
                        "name": label, "link": ""})

    return chunks


def _cosine(a: list[float], b: list[float]) -> float:
    dot  = sum(x*y for x,y in zip(a,b))
    norm = math.sqrt(sum(x*x for x in a)) * math.sqrt(sum(y*y for y in b))
    return dot / norm if norm else 0.0


def semantic_search(query: str, top_k: int = 4) -> list[dict]:
    """
    بيدور في الكتالوج بـ cosine similarity على embeddings.
    بيرجع top_k chunks الأقرب للسؤال.
    بيحتاج GEMINI_API_KEY في الـ environment.
    """
    global _chunks, _embeddings

    try:
        import google.genai as genai
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    except Exception:
        return []  # لو مفيش API key، بيرجع فاضي وبيفضل الـ keyword search

    # ── Lazy init: بناء الـ chunks وحساب الـ embeddings مرة واحدة ──
    if _chunks is None:
        _chunks = _build_chunks()
        batch_texts = [c["text"] for c in _chunks]
        resp = client.models.embed_content(
            model="gemini-embedding-001",
            contents=batch_texts,
            config={"task_type": "RETRIEVAL_DOCUMENT"},
        )
        _embeddings = [e.values for e in resp.embeddings]

    # ── Embed الـ query ──
    q_resp = client.models.embed_content(
        model="gemini-embedding-001",
        contents=[query],
        config={"task_type": "RETRIEVAL_QUERY"},
    )
    q_vec = q_resp.embeddings[0].values

    # ── Rank بـ cosine similarity ──
    scored = sorted(
        enumerate(_chunks),
        key=lambda x: _cosine(q_vec, _embeddings[x[0]]),
        reverse=True,
    )

    return [_chunks[i] for i, _ in scored[:top_k]]


CATALOG_STATS = {
    "total_courses": len(COURSES),
    "total_roadmaps": len(ROADMAPS),
    "total_tracks": len(TRACKS),
    "total_diplomas": len(DIPLOMAS),
    "total_instructors": 25,
}

if __name__ == "__main__":
    for k, v in CATALOG_STATS.items():
        print(f"  {k}: {v}")
    print(f"\nMaster context: {len(MASTER_CONTEXT):,} chars")
    print(f"Chunks ready to embed: {len(_build_chunks())}")
    print("\nsearch_courses('python'):")
    for c in search_courses("python", max_results=3):
        print(f"  • {c['name']} ({c['level']})")
