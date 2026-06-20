<div align="center">

[![Typing SVG](https://readme-typing-svg.demolab.com?font=Syne&weight=800&size=36&pause=1000&color=3D3DB4&center=true&vCenter=true&width=700&lines=Kayfa+AI+Sales+Agent+🤖;Arabic+%2B+English+·+RTL;Agentic+AI+·+RAG+·+MongoDB)](https://git.io/typing-svg)

[![Python](https://img.shields.io/badge/Python-3.10-E8FF47?style=for-the-badge&logo=python&logoColor=black&labelColor=0a0c10)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-Live-E8FF47?style=for-the-badge&logo=streamlit&logoColor=black&labelColor=0a0c10)](https://streamlit.io)
[![Groq](https://img.shields.io/badge/Groq-LLM-E8FF47?style=for-the-badge&logo=groq&logoColor=black&labelColor=0a0c10)](https://groq.com)
[![MongoDB](https://img.shields.io/badge/MongoDB-CRM-E8FF47?style=for-the-badge&logo=mongodb&logoColor=black&labelColor=0a0c10)](https://mongodb.com)

> **52 courses. 13 roadmaps. One agent that listens, understands intent, and turns conversations into enrollments.**

| 🌍 Languages | 🤖 Agent Type | 🗃️ Knowledge Base | 📋 CRM |
|:-----------:|:-------------:|:-----------------:|:------:|
| **Arabic + English** | **Agentic RAG** | **52 courses · 13 roadmaps** | **MongoDB** |

**[🚀 Try the Live App →](https://sales-agent-kayfa.streamlit.app/)**

</div>

---

## ✦ App Preview

### 💬 Chat Agent — Arabic RTL
<p align="center">
  <img src="1.png" width="95%">
</p>
<p align="center">
  <img src="2.png" width="95%">
</p>
<p align="center">
  <img src="3.png" width="95%">
</p>

### 📋 CRM Dashboard — Lead Tickets
<p align="center">
  <img src="4.png" width="95%">
</p>

---

## ✦ What is This?

An agentic AI sales assistant built for the **Kayfa AI & Data Analytics Internship · Week 3 Task**.

> *"Which track fits me? Is the SOC diploma worth it? Can I get a refund?"*

A human sales rep could convert hesitant visitors — but reps can't be online 24/7, in three Arabic dialects, answering instantly. This agent can.

It does two things at once: **guides visitors** toward the right Kayfa course or diploma, and **captures qualified leads** as CRM tickets the sales team can act on — without the visitor feeling like they're filling out a form.

---

## ✦ Project Structure

```
week3-sales-agent-groq/
│
├── 🤖  appp.py              ← Streamlit app (Chat + CRM pages)
├── 🧠  agent.py             ← Pydantic-AI agent + tool definitions
├── 📚  knowledge.py         ← RAG: keyword + semantic search
├── 🗃️  db.py                ← MongoDB layer (tickets + chat history)
│
├── 📁  data/
│   ├── kayfa_courses.json       ← 52 courses
│   ├── kayfa_roadmaps.json      ← 13 learning paths
│   └── text/                    ← Markdown knowledge base
│       ├── kayfa_company_overview.md
│       ├── kayfa_policies_and_faqs.md
│       ├── kayfa_paid_individual_courses.md
│       ├── kayfa_paid_educational_tracks.md
│       ├── kayfa_free_educational_content.md
│       ├── kayfa_ai_diploma.md
│       ├── kayfa_data_science_diploma.md
│       ├── kayfa_soc_diploma.md
│       ├── Kayfa_PenTest_Diploma.md
│       └── Kayfa_Fullstack_Diploma.md
│
├── 🖼️  logo.png · logo_icon.png
├── 📋  requirements.txt
└── 📁  .streamlit/
    └── secrets.toml
```

---

## ✦ How the Agent Works

| Step | What Happens |
|:-----|:-------------|
| **1. Read Intent** | Classifies visitor as Browsing / Comparing / Price-Sensitive / Hesitant / Ready |
| **2. Search Knowledge Base** | RAG over 52 courses + 13 roadmaps — keyword + semantic |
| **3. Recommend** | Maps goal → real Kayfa product with accurate price, duration, link |
| **4. Persuade** | Handles objections using real policies, social proof, diploma pitch lines |
| **5. Detect Buying Signal** | Monitors for payment questions, enrollment intent, 3+ engaged messages |
| **6. Capture Lead** | Collects name + WhatsApp + email + city naturally in conversation |
| **7. Save CRM Ticket** | Writes Arabic ticket to MongoDB with summary + recommended action |

---

## ✦ Agent Tools

| Tool | Purpose |
|:-----|:--------|
| `search_courses_tool` | Keyword search across 52 courses by skill, track, or level |
| `search_roadmaps_tool` | Search 13 learning paths and live diplomas |
| `semantic_search_tool` | Deep Gemini-embedding search for complex queries |
| `save_lead_tool` | Save qualified lead as CRM ticket in MongoDB |

---

## ✦ Knowledge Base

| Layer | Files | Best For |
|:------|:------|:---------|
| **Structured** | `kayfa_courses.json` · `kayfa_roadmaps.json` | Price, duration, prerequisites, links |
| **Sales Pitches** | Diploma `.md` files | Objection handling, closing lines |
| **Pricing** | `kayfa_paid_*.md` · `kayfa_free_*.md` | Quick price / duration answers |
| **Trust & Ops** | Company overview · Policies · Privacy · Instructors | FAQs, refunds, contacts |

---

## ✦ Product Tiers the Agent Can Recommend

| Tier | Price | Sales Angle |
|:-----|:-----:|:------------|
| 🆓 Free content | $0 | Entry point for hesitant visitors |
| 📘 Individual courses | $15 – $65 | Low-commitment opener |
| 🗺️ On-demand tracks | $25 – $250 | Structured learning path |
| 🎓 Live diplomas | Program-specific | **Main closing target** |

---

## ✦ CRM Ticket — What Gets Captured

Every ticket is written **in Arabic**, stored in MongoDB, built for the sales team:

| Field | What It Contains |
|:------|:----------------|
| 👤 **Who** | Name · Phone/WhatsApp · Email · City · Language/Dialect |
| 🎯 **What** | Products of interest · Goal · Current level · Prerequisites |
| 🌡️ **Temperature** | Hot 🔥 · Warm 🌤 · Cold ❄️ + buying signals + objections |
| 📝 **Summary** | Arabic conversation summary + recommended rep action + timestamp |

---

## ✦ App Pages

**Page 1 — Chat Agent**
- Clean RTL chat UI
- Arabic / English with correct text direction
- Conversation memory across turns
- Sidebar: chat history, rename, delete

**Page 2 — CRM Dashboard**
- All captured leads from MongoDB
- Filter by temperature (Hot / Warm / Cold)
- Full ticket details: client info, interest, summary, recommended action

---

## ✦ Arabic Dialects Supported

| Dialect | |
|:--------|:-|
| العربية المصرية | Egyptian |
| العربية السورية | Syrian |
| العربية السعودية | Saudi |
| English | LTR as-is |

---

## ✦ Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/your-username/week3-sales-agent-groq
cd week3-sales-agent-groq

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your keys
cp .env.example .env
# Fill in GROQ_API_KEY, GEMINI_API_KEY, MONGODB_URI

# 4. Run
streamlit run appp.py
```

App opens at `http://localhost:8501`  
Default password: `kayfa2026`

---

## ✦ Deploy to Streamlit Cloud

```
1. Push repo to GitHub
2. Go to share.streamlit.io
3. Connect repo → main file: appp.py → Deploy
4. In app Settings → Secrets, paste your secrets.toml content
5. Get a login-protected live link in ~2 minutes
```

`.streamlit/secrets.toml`:
```toml
APP_PASSWORD  = "your_password"
GROQ_API_KEY  = "gsk_..."
GEMINI_API_KEY = "..."
MONGODB_URI   = "mongodb+srv://..."
```

---

## ✦ Tech Stack

| Layer | Technology |
|:------|:-----------|
| 🐍 Language | Python 3.10 |
| 🤖 Agent Framework | Pydantic-AI |
| ⚡ LLM | Groq API — OpenAI-compatible model |
| 🔍 Embeddings | Google Gemini |
| 🗃️ Database | MongoDB Atlas |
| 🎛️ UI | Streamlit · RTL CSS · IBM Plex Sans Arabic |
| 📚 Knowledge | JSON + Markdown RAG |

---

<div align="center">

Built with ⚡ for **Kayfa AI & Data Analytics Internship · Week 3**

*كيف — مساعد مبيعات ذكي يفهم، يرشد، ويحوّل الزوار لعملاء.*

</div>
