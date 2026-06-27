"""
monitoring.py — Part 2 Admin Monitoring Dashboard
  Monitor A — Cost (per message / conversation / user)
  Monitor B — Behaviour & Response Trace
  Monitor C — Close the Loop (Optimization)
"""
from __future__ import annotations
import streamlit as st


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _fmt_cost(usd: float) -> str:
    if usd == 0:
        return "$0.000000"
    return f"${usd:.6f}"


def _fmt_ts(ts: str) -> str:
    return str(ts)[:16].replace("T", " ") if ts else "—"


_TONES = {
    "purple": ("#F1E9FE", "#8B5CF6"),
    "blue":   ("#E8F0FE", "#3D7BFE"),
    "green":  ("#E7F8EF", "#16A34A"),
    "red":    ("#FEF2F2", "#DC2626"),
    "indigo": ("var(--blue-l)", "var(--blue)"),
}


def _metric_card(icon: str, label: str, value, tone: str = "purple",
                  trend: str | None = None, info: str | None = None) -> str:
    """بيرجّع HTML لكارت متريك واحد (badge دائري + label + value)."""
    bg, fg = _TONES.get(tone, _TONES["purple"])
    trend_html = (
        f'<div class="metric-trend" style="background:{bg};color:{fg};">{trend}</div>'
        if trend else ""
    )
    info_html = f'<span class="metric-info" title="{info}">ⓘ</span>' if info else ""
    return (
        '<div class="metric-card">'
        '<div class="metric-card-top">'
        f'<div class="metric-badge" style="background:{bg};color:{fg};">{icon}</div>'
        f'{trend_html}'
        '</div>'
        f'<div class="metric-label">{label} {info_html}</div>'
        f'<div class="metric-value">{value}</div>'
        '</div>'
    )


def _metric_row(cards: list[str]):
    st.markdown('<div class="metric-row">' + "".join(cards) + '</div>', unsafe_allow_html=True)


def _badge(label: str, color: str = "#3D3DB4", bg: str = "#EDEDFA") -> str:
    return (
        f'<span style="background:{bg};color:{color};padding:2px 10px;'
        f'border-radius:999px;font-size:12px;font-weight:600;">{label}</span>'
    )


# ─────────────────────────────────────────────────────────────────────────────
# Monitor A — Cost
# ─────────────────────────────────────────────────────────────────────────────

def render_monitor_a():
    st.markdown("### 💰 Monitor A — Cost Tracker")
    st.markdown(
        "تتبّع كل دولار: per message → per conversation → per user "
        "— LLM + Embeddings من كل provider."
    )

    try:
        from db import get_cost_by_user, get_cost_by_conversation, load_usage_logs
    except Exception as e:
        st.error(f"DB error: {e}")
        return

    # ── Top-level metrics ──
    all_logs = load_usage_logs(limit=500)
    if not all_logs:
        st.info("لا توجد بيانات بعد — ابدأ محادثة أولاً.")
        return

    total_cost  = sum(d.get("total_cost_usd", 0) for d in all_logs)
    total_msgs  = len(all_logs)
    avg_msg     = total_cost / total_msgs if total_msgs else 0
    total_in    = sum(d.get("input_tokens", 0)  for d in all_logs)
    total_out   = sum(d.get("output_tokens", 0) for d in all_logs)
    total_embed = sum(d.get("embedding_tokens", 0) for d in all_logs)

    _metric_row([
        _metric_card("💵", "Total Cost",    _fmt_cost(total_cost), tone="purple"),
        _metric_card("💬", "Messages",      f"{total_msgs:,}",     tone="blue"),
        _metric_card("📊", "Avg / Message", _fmt_cost(avg_msg),    tone="green"),
        _metric_card("🔤", "Total Tokens",  f"{(total_in + total_out + total_embed):,}", tone="indigo"),
    ])

    st.markdown("---")

    # ── Per-User table ──
    st.markdown("#### 👥 Cost per User")
    user_rows = get_cost_by_user()
    if not user_rows:
        st.info("No data yet.")
        return

    for row in user_rows:
        uid   = row.get("_id") or "anonymous"
        cost  = row.get("total_cost_usd", 0)
        msgs  = row.get("total_messages", 0)
        tok_i = row.get("total_input_tokens", 0)
        tok_o = row.get("total_output_tokens", 0)
        tok_e = row.get("total_embed_tokens", 0)

        with st.expander(f"👤 {uid}  ·  {_fmt_cost(cost)}  ·  {msgs} messages"):
            _metric_row([
                _metric_card("💵", "Total Cost",    _fmt_cost(cost), tone="purple"),
                _metric_card("💬", "Messages",      f"{msgs:,}",     tone="blue"),
                _metric_card("📊", "Avg / Message", _fmt_cost(cost / msgs if msgs else 0), tone="green"),
            ])
            _metric_row([
                _metric_card("📥", "Input Tokens",  f"{tok_i:,}", tone="indigo"),
                _metric_card("📤", "Output Tokens", f"{tok_o:,}", tone="blue"),
                _metric_card("🧮", "Embed Tokens",  f"{tok_e:,}", tone="green"),
            ])

            # ── Per-conversation drill-down ──
            convs = get_cost_by_conversation(user_id=uid)
            if convs:
                st.markdown("**Conversations:**")
                for conv in convs[:10]:
                    cid    = conv.get("_id", "")[:16] + "…"
                    ccost  = conv.get("total_cost_usd", 0)
                    cmsgs  = conv.get("message_count", 0)
                    prompt = (conv.get("first_prompt") or "")[:60]
                    ts     = _fmt_ts(conv.get("last_ts", ""))
                    st.markdown(
                        f'<div style="padding:6px 10px;margin:4px 0;background:#F5F5FD;'
                        f'border-radius:8px;font-size:13px;direction:rtl;text-align:right;">'
                        f'<strong>{_fmt_cost(ccost)}</strong> · {cmsgs} msg · {ts}<br>'
                        f'<span style="color:#6B6B8A;">{prompt}</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

    st.markdown("---")

    # ── Per-message table ──
    st.markdown("#### 📨 Recent Messages (most expensive first)")
    n = st.slider("عدد الرسائل المعروضة", 10, 100, 20, key="msg_slider")
    sorted_logs = sorted(all_logs, key=lambda x: x.get("total_cost_usd", 0), reverse=True)

    rows_html = ""
    for log in sorted_logs[:n]:
        prompt   = (log.get("user_prompt") or "")[:60]
        tot      = _fmt_cost(log.get("total_cost_usd", 0))
        llm_c    = _fmt_cost(log.get("llm_cost_usd", 0))
        emb_c    = _fmt_cost(log.get("embedding_cost_usd", 0))
        in_tok   = log.get("input_tokens", 0)
        out_tok  = log.get("output_tokens", 0)
        emb_tok  = log.get("embedding_tokens", 0)
        lat      = log.get("latency_ms", 0)
        n_tools  = len(log.get("tool_calls", []))
        uid      = log.get("user_id", "—")
        ts       = _fmt_ts(log.get("timestamp", ""))

        rows_html += (
            f"<tr>"
            f"<td>{ts}</td>"
            f"<td>{uid}</td>"
            f"<td style='direction:rtl;max-width:200px;overflow:hidden;'>{prompt}</td>"
            f"<td style='font-weight:600;color:#3D3DB4;'>{tot}</td>"
            f"<td>{llm_c}</td>"
            f"<td>{emb_c}</td>"
            f"<td>{in_tok:,}</td>"
            f"<td>{out_tok:,}</td>"
            f"<td>{emb_tok:,}</td>"
            f"<td>{n_tools}</td>"
            f"<td>{lat} ms</td>"
            f"</tr>"
        )

    st.markdown(
        f"""<div style="overflow-x:auto;">
        <table style="width:100%;font-size:12px;border-collapse:collapse;">
          <thead>
            <tr style="background:#EDEDFA;color:#3D3DB4;font-weight:600;">
              <th style="padding:6px 8px;text-align:left;">Timestamp</th>
              <th style="padding:6px 8px;">User</th>
              <th style="padding:6px 8px;">Prompt</th>
              <th style="padding:6px 8px;">Total $</th>
              <th style="padding:6px 8px;">LLM $</th>
              <th style="padding:6px 8px;">Embed $</th>
              <th style="padding:6px 8px;">In Tok</th>
              <th style="padding:6px 8px;">Out Tok</th>
              <th style="padding:6px 8px;">Emb Tok</th>
              <th style="padding:6px 8px;">Tools</th>
              <th style="padding:6px 8px;">Latency</th>
            </tr>
          </thead>
          <tbody>{rows_html}</tbody>
        </table></div>""",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Monitor B — Behaviour & Response Trace
# ─────────────────────────────────────────────────────────────────────────────

def render_monitor_b():
    st.markdown("### 🔍 Monitor B — Behaviour & Response Trace")
    st.markdown(
        "اختار محادثة وشوف replay كامل لكل خطوة: "
        "**Think → Tool Call → Tool Result → Final Answer**"
    )

    try:
        from db import load_usage_logs, get_cost_by_user
    except Exception as e:
        st.error(f"DB error: {e}")
        return

    # ── User selector ──
    user_rows = get_cost_by_user()
    if not user_rows:
        st.info("لا توجد بيانات بعد.")
        return

    users = [r.get("_id") or "anonymous" for r in user_rows]
    sel_user = st.selectbox("👤 اختار المستخدم", users, key="trace_user")

    # ── Load conversations for user ──
    user_logs = load_usage_logs(user_id=sel_user, limit=200)
    if not user_logs:
        st.info("لا توجد رسائل لهذا المستخدم.")
        return

    # Group by conversation
    convs: dict[str, list] = {}
    for log in reversed(user_logs):
        cid = log.get("conversation_id", "unknown")
        convs.setdefault(cid, []).append(log)

    conv_labels = {
        cid: f"{(msgs[0].get('user_prompt') or 'محادثة')[:40]} ({len(msgs)} msg) · {_fmt_ts(msgs[0].get('timestamp',''))}"
        for cid, msgs in convs.items()
    }
    sel_conv = st.selectbox(
        "💬 اختار المحادثة",
        list(convs.keys()),
        format_func=lambda k: conv_labels.get(k, k[:20]),
        key="trace_conv",
    )

    conv_msgs = convs.get(sel_conv, [])
    msg_labels = [
        f"[{i+1}] {(m.get('user_prompt') or '')[:50]}"
        for i, m in enumerate(conv_msgs)
    ]

    # key فيه sel_conv عشان لو غيّرت المحادثة، الـ widget يتعامل كعنصر جديد
    # ويرجع لأول رسالة بدل ما يفضل عالق على index قديم من محادثة تانية.
    sel_idx = st.selectbox(
        "📨 اختار الرسالة",
        range(len(conv_msgs)),
        format_func=lambda i: msg_labels[i],
        key=f"trace_msg_{sel_conv}",
    )

    log = conv_msgs[sel_idx]
    st.markdown("---")

    # ── Trace viewer ──
    prompt   = log.get("user_prompt", "")
    response = log.get("final_response", "")
    tools    = log.get("tool_calls", [])
    in_tok   = log.get("input_tokens", 0)
    out_tok  = log.get("output_tokens", 0)
    emb_tok  = log.get("embedding_tokens", 0)
    total_c  = _fmt_cost(log.get("total_cost_usd", 0))
    lat      = log.get("latency_ms", 0)

    # User prompt
    st.markdown(
        f'<div style="background:#E8E8FF;border-radius:14px;padding:12px 18px;'
        f'margin:8px 0;direction:rtl;text-align:right;">'
        f'<span style="font-size:11px;color:#6B6B8A;font-weight:600;">👤 USER PROMPT</span><br>'
        f'<span style="font-size:15px;">{prompt}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Think step (implicit from the model deciding what tools to call)
    if tools:
        st.markdown(
            f'<div style="background:#FEF9E7;border-radius:10px;padding:10px 16px;'
            f'margin:8px 0;border-left:3px solid #F39C12;">'
            f'<span style="font-size:11px;color:#8B6914;font-weight:600;">🧠 THINK</span><br>'
            f'<span style="font-size:13px;color:#5D4037;">'
            f'Agent decided to call <strong>{len(tools)} tool(s)</strong> '
            f'to answer this query before generating the final response.'
            f'</span></div>',
            unsafe_allow_html=True,
        )

    # Tool calls
    for i, tc in enumerate(tools):
        tname   = tc.get("tool_name", "unknown")
        args    = tc.get("args", {})
        result  = tc.get("result") or "—"

        st.markdown(
            f'<div style="background:#F0F4F9;border-radius:10px;padding:10px 16px;'
            f'margin:6px 0;border-left:3px solid #3D3DB4;">'
            f'<span style="font-size:11px;color:#3D3DB4;font-weight:600;">🔧 TOOL CALL {i+1}</span><br>'
            f'<code style="background:#E8E8FF;padding:2px 8px;border-radius:4px;font-size:13px;">'
            f'{tname}({", ".join(f"{k}={repr(v)}" for k, v in args.items())})'
            f'</code>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div style="background:#F5F5F5;border-radius:10px;padding:10px 16px;'
            f'margin:4px 0 10px 24px;border-left:3px solid #95A5A6;">'
            f'<span style="font-size:11px;color:#666;font-weight:600;">📦 TOOL RESULT</span><br>'
            f'<span style="font-size:12px;white-space:pre-wrap;font-family:monospace;">'
            f'{result[:400]}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Final response
    st.markdown(
        f'<div style="background:#F0F4F9;border-radius:14px;padding:12px 18px;'
        f'margin:8px 0;">'
        f'<span style="font-size:11px;color:#3D3DB4;font-weight:600;">💬 FINAL RESPONSE</span><br>'
        f'<span style="font-size:14px;direction:rtl;text-align:right;display:block;">'
        f'{response}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Metadata row
    st.markdown(
        f'<div style="background:#F8F8FF;border-radius:8px;padding:8px 14px;'
        f'margin-top:10px;font-size:12px;color:#6B6B8A;">'
        f'🔢 {in_tok:,} in · {out_tok:,} out · {emb_tok:,} embed · '
        f'🔧 {len(tools)} tool calls · ⏱ {lat} ms · 💵 {total_c}'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Hallucination check
    if not tools and response:
        st.info(
            "ℹ️ **بدون tool calls** — تم الرد مباشرة من المعلومات الثابتة في الـ system prompt "
            "(زي السياسات، التواصل، معلومات الشركة). هذا متوقّع وسليم للأسئلة العامة بفضل "
            "تحسين Selective RAG، وليس بالضرورة خطأ. لكن لو الرد ده فيه **سعر كورس أو تفاصيل "
            "تسجيل محددة** بدون أي tool call، يستحق تتأكد إنها مش مُخمَّنة."
        )
    elif tools:
        st.markdown(
                f'<div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:10px;'
                f'padding:10px 16px;margin-top:10px;direction:rtl;text-align:right;">'
                f'✅ الرد مبني على <strong>{len(tools)}</strong> tool call من الـ knowledge base.'
                f'</div>',
                unsafe_allow_html=True,
            )


# ─────────────────────────────────────────────────────────────────────────────
# Monitor C — Close the Loop / Optimization
# ─────────────────────────────────────────────────────────────────────────────

def render_monitor_c():
    st.markdown("### ⚡ Monitor C — Close the Loop · Optimize")
    st.markdown(
        "اكتشف السلوك المُكلف وقيس الفرق قبل وبعد التحسين: "
        "**Measure → Spot → Fix → Re-measure**"
    )

    try:
        from db import load_usage_logs
        from agent import PRICING
    except Exception as e:
        st.error(f"DB error: {e}")
        return

    all_logs = load_usage_logs(limit=500)

    # ── Analysis: find waste ──
    st.markdown("#### 🔍 Analysis — Waste Detection")

    with_semantic  = [l for l in all_logs if l.get("embedding_tokens", 0) > 50]
    without_semantic = [l for l in all_logs if l.get("embedding_tokens", 0) <= 50]
    multi_tool = [l for l in all_logs if len(l.get("tool_calls", [])) >= 3]

    _metric_row([
        _metric_card("📡", "Calls using semantic search", len(with_semantic), tone="purple",
                     info="Calls that triggered Gemini embedding (costly)"),
        _metric_card("🔑", "Calls — keyword only", len(without_semantic), tone="blue",
                     info="Calls answered by keyword search alone (cheap)"),
        _metric_card("🔁", "Calls with 3+ tool rounds", len(multi_tool), tone="green",
                     info="Multi-step calls — each round re-bills full context"),
    ])

    st.markdown("---")

    # ── Optimization 1: System Prompt Trimming ──
    st.markdown("#### 🛠️ Optimization 1 — System Prompt Trimming")

    with st.expander("📖 Explanation", expanded=True):
        st.markdown("""
**المشكلة:** الـ system prompt الحالي يحتوي على `MASTER_CONTEXT` كامل (≈ 1,400 token).
هذا السياق يُعاد إرساله وفوترته مع **كل خطوة** من خطوات الـ agent.

في محادثة فيها 3 tool calls، يعني هذا:
- 3 × 1,400 = **4,200 token زيادة** من الـ MASTER_CONTEXT وحده.

**الحل:** نحتفظ بالـ MASTER_CONTEXT كـ "catalog snapshot" مختصر (~400 token)
ونحذف منه تفاصيل الأسعار والكورسات التفصيلية لأن الـ tools تعالجها.
        """)

    # Calculate from real data
    if all_logs:
        avg_in_before = sum(l.get("input_tokens", 0) for l in all_logs) / len(all_logs)

        # Estimate: trimming MASTER_CONTEXT saves ~1000 tokens per call
        TOKENS_SAVED_PER_CALL = 1_000
        est_saved_tokens = int(TOKENS_SAVED_PER_CALL * len(all_logs))
        est_saved_cost   = est_saved_tokens * PRICING["llm"]["input_per_1m"] / 1_000_000
        total_before     = sum(l.get("llm_cost_usd", 0) for l in all_logs)
        total_after      = total_before - est_saved_cost

        _metric_row([
            _metric_card("📥", "Avg Input Tokens (Before)", f"{int(avg_in_before):,}", tone="purple"),
            _metric_card("📤", "Avg Input Tokens (After)",
                         f"{int(avg_in_before - TOKENS_SAVED_PER_CALL):,}", tone="blue",
                         trend=f"↓ -{TOKENS_SAVED_PER_CALL:,}"),
            _metric_card("💰", "Estimated LLM Saving", _fmt_cost(est_saved_cost), tone="green"),
        ])

        st.markdown(
            f"""| Metric | Before | After | Saving |
|--------|--------|-------|--------|
| Avg input tokens/call | {int(avg_in_before):,} | {int(avg_in_before - TOKENS_SAVED_PER_CALL):,} | **-{TOKENS_SAVED_PER_CALL:,}** |
| LLM cost (total) | {_fmt_cost(total_before)} | {_fmt_cost(max(0, total_after))} | **{_fmt_cost(est_saved_cost)}** |
| Cost reduction % | — | — | **{100*est_saved_cost/max(total_before,1e-9):.1f}%** |
"""
        )
    else:
        st.info("أضف محادثات أولاً لرؤية الحسابات الفعلية.")

    st.markdown("---")

    # ── Optimization 2: Skip Semantic Search for Simple Queries ──
    st.markdown("#### 🛠️ Optimization 2 — Selective RAG (Skip Embedding for Simple Queries)")

    with st.expander("📖 Explanation", expanded=True):
        st.markdown("""
**المشكلة:** الـ agent يستدعي `semantic_search_tool` حتى في أسئلة بسيطة
(\"ما رقم التواصل؟\" / \"ما سياسة الاسترداد؟\") بينما `search_courses_tool`
و `search_roadmaps_tool` تجيب عليها بالكلمات المفتاحية بدون تكلفة embedding.

**الحل:** Prompt engineering — نعدّل توجيهات الـ tools في الـ system prompt
ليعرف الـ agent متى يُفضّل الـ keyword search على الـ semantic search.
        """)

    if with_semantic and all_logs:
        avg_embed_cost_with  = sum(
            l.get("embedding_cost_usd", 0) for l in with_semantic
        ) / len(with_semantic)
        avg_embed_cost_total = sum(
            l.get("embedding_cost_usd", 0) for l in all_logs
        ) / len(all_logs)

        # Estimate: 40% of semantic calls could be replaced by keyword search
        reducible = int(len(with_semantic) * 0.4)
        saved_embed = reducible * avg_embed_cost_with

        _metric_row([
            _metric_card("📡", "Calls using semantic search", len(with_semantic), tone="purple"),
            _metric_card("🎯", "Reducible calls (~40%)",       reducible,         tone="blue"),
            _metric_card("💰", "Embedding cost saving",        _fmt_cost(saved_embed), tone="green"),
        ])
    else:
        st.info("بيانات غير كافية — ابدأ محادثات تحتوي على semantic search.")

    st.markdown("---")

    # ── Before vs After summary ──
    st.markdown("#### 📊 Combined Before vs After")


    if all_logs:
        total_cost_before = sum(l.get("total_cost_usd", 0) for l in all_logs)
        opt1_saving = est_saved_cost if all_logs else 0
        opt2_saving = saved_embed if (with_semantic and all_logs) else 0
        total_saving = opt1_saving + opt2_saving
        total_cost_after = total_cost_before - total_saving

        st.markdown(
            f"""| | Before | After |
|---|---|---|
| Total cost | **{_fmt_cost(total_cost_before)}** | **{_fmt_cost(max(0, total_cost_after))}** |
| Saving | — | **{_fmt_cost(total_saving)}** ({100*total_saving/max(total_cost_before,1e-9):.1f}%) |
| Applied optimizations | — | Prompt trim + Selective RAG |
"""
        )

        st.markdown(
            f'<div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:10px;'
            f'padding:10px 16px;margin-top:10px;direction:rtl;text-align:right;">'
            f'<span style="font-size:13px;color:#15803D;">'
            f'✅ بتطبيق الـ 2 optimizations، التكلفة الكلية تنخفض بـ '
            f'<strong>{_fmt_cost(total_saving)}</strong> '
            f'({100*total_saving/max(total_cost_before,1e-9):.1f}% saving).'
            f'</span></div>',
            unsafe_allow_html=True,
)
    else:
        st.info("أضف محادثات أولاً.")


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def render_monitoring_page():
    col_title, _ = st.columns([4, 1])
    with col_title:
        st.markdown("## 📊 Admin Monitoring Dashboard")
        st.markdown(
            '<span style="font-family:Inter,sans-serif;font-size:13px;font-weight:700;'
            'letter-spacing:1.2px;text-transform:uppercase;background:#EDEDFA;color:#3D3DB4;'
            'padding:7px 20px;border-radius:999px;border:1.5px solid #C7C7F5;display:inline-block;">'
            'Week 3 · Part 2 · Kayfa Internship</span>',
            unsafe_allow_html=True,
        )

    st.markdown('<hr style="border:none;border-top:1px solid #E8E8F4;margin:12px 0 18px 0;">', unsafe_allow_html=True)

    tab_a, tab_b, tab_c = st.tabs([
        "💰 Monitor A — Cost",
        "🔍 Monitor B — Trace",
        "⚡ Monitor C — Optimize",
    ])

    with tab_a:
        render_monitor_a()

    with tab_b:
        render_monitor_b()

    with tab_c:
        render_monitor_c()