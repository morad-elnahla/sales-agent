"""
app.py — Kayfa AI Sales Agent
GPT/Gemini-style UI · RTL Arabic
Persistent sidebar toggle (arrow always visible) · Chat rename/delete
WhatsApp tight-shadow bubbles · Clean Gemini pill input
"""
import uuid
import streamlit as st

def _get_page_icon():
    """Use logo_icon.png as the browser-tab favicon; fall back to an emoji if missing."""
    try:
        from PIL import Image
        return Image.open("logo_icon.png")
    except Exception:
        return "🎓"

st.set_page_config(
    page_title="كيف — Kayfa AI",
    page_icon=_get_page_icon(),
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');

/* ══ FORCE WHITE BACKGROUND EVERYWHERE ══ */
html {
  background: #FFFFFF !important;
  color-scheme: light !important;
}
* {
  color-scheme: light !important;
}
body {
  background: #FFFFFF !important;
}
#root, .stApp, [data-testid="stAppViewContainer"] {
  background: #FFFFFF !important;
}
[data-testid="stHeader"] {
  background: #FFFFFF !important;
}

:root {
  --blue:       #3D3DB4;
  --blue-d:     #2E2E9A;
  --blue-l:     #EDEDFA;
  --blue-ll:    #F5F5FD;
  --user-bg:    #E8E8FF;
  --ai-bg:      #F0F4F9;
  --bg:         #FFFFFF;
  --side-bg:    #EEEEF6;
  --border:     #E8E8F4;
  --text:       #1A1A3E;
  --muted:      #6B6B8A;
  --radius:     14px;
  --radius-msg: 18px;
}

html, body, * {
  font-family: 'IBM Plex Sans Arabic', 'Tahoma', 'Segoe UI', 'Arial', 'Inter', sans-serif !important;
  box-sizing: border-box;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stHeader"],
[data-testid="stStatusWidget"] { display: none !important; }

/* ── App background ── */
.stApp { background: #FFFFFF !important; }
[data-testid="stAppViewContainer"] > .main { background: #FFFFFF !important; }
.main .block-container {
  max-width:  760px !important;
  padding:    0 24px 140px 24px !important;
  margin:     0 auto !important;
}

/* ══ SIDEBAR ══ */
[data-testid="stSidebar"] {
  background:   var(--side-bg) !important;
  border-left:  1px solid var(--border) !important;
  border-right: none !important;
  direction:    rtl !important;
  padding-top:  0 !important;
}

[data-testid="stSidebar"] > div:first-child {
  padding-top: 0 !important;
  margin-top:  0 !important;
}
[data-testid="stSidebarUserContent"] {
  padding-top: 0 !important;
  margin-top:  -3rem !important;
}
[data-testid="stSidebarUserContent"] > div:first-child {
  padding-top: 0 !important;
  margin-top:  0 !important;
}

[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
  gap: 0 !important;
}
[data-testid="stSidebar"] [data-testid="element-container"] {
  margin-bottom: 0 !important;
  margin-top:    0 !important;
}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {
  padding-top:    0 !important;
  padding-bottom: 0 !important;
}

/* ══ SIDEBAR TOGGLE ══ */
[data-testid="stSidebarCollapseButton"] {
  display:         flex !important;
  visibility:      visible !important;
  opacity:         1 !important;
  position:        fixed !important;
  top:             50% !important;
  left:            258px !important;
  transform:       translateY(-50%) !important;
  z-index:         99999 !important;
  background:      #fff !important;
  border:          1.5px solid var(--border) !important;
  border-radius:   50% !important;
  width:           28px !important;
  height:          28px !important;
  box-shadow:      0 2px 10px rgba(0,0,0,.12) !important;
  align-items:     center !important;
  justify-content: center !important;
  cursor:          pointer !important;
  padding:         0 !important;
  overflow:        hidden !important;
}
[data-testid="stSidebarCollapseButton"] button svg,
[data-testid="stSidebarCollapseButton"] button span,
[data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"] {
  display: none !important;
}
[data-testid="stSidebarCollapseButton"] button {
  background:    transparent !important;
  border:        none !important;
  padding:       0 !important;
  width:         28px !important;
  height:        28px !important;
  min-height:    0 !important;
  box-shadow:    none !important;
  border-radius: 50% !important;
  position:      relative !important;
  color:         transparent !important;
  font-size:     0 !important;
}
[data-testid="stSidebarCollapseButton"] button::after {
  content:     "‹";
  position:    absolute;
  top:         50%;
  left:        50%;
  transform:   translate(-50%, -50%);
  font-size:   18px;
  font-weight: 600;
  color:       var(--muted);
  line-height: 1;
}
[data-testid="stSidebarCollapseButton"]:hover,
[data-testid="stSidebarCollapseButton"] button:hover {
  background: var(--blue-ll) !important;
}
[data-testid="stSidebarCollapseButton"] button:hover::after { color: var(--blue); }

[data-testid="collapsedControl"] {
  display:         flex !important;
  visibility:      visible !important;
  opacity:         1 !important;
  position:        fixed !important;
  top:             50% !important;
  left:            4px !important;
  transform:       translateY(-50%) !important;
  z-index:         99999 !important;
  background:      #fff !important;
  border:          1.5px solid var(--border) !important;
  border-radius:   50% !important;
  width:           28px !important;
  height:          28px !important;
  box-shadow:      0 2px 10px rgba(0,0,0,.12) !important;
  align-items:     center !important;
  justify-content: center !important;
  cursor:          pointer !important;
  padding:         0 !important;
  clip:            unset !important;
  overflow:        hidden !important;
}
[data-testid="collapsedControl"] button svg,
[data-testid="collapsedControl"] button span,
[data-testid="collapsedControl"] [data-testid="stIconMaterial"] { display: none !important; }
[data-testid="collapsedControl"] button {
  background:    transparent !important;
  border:        none !important;
  padding:       0 !important;
  width:         28px !important;
  height:        28px !important;
  min-height:    0 !important;
  box-shadow:    none !important;
  border-radius: 50% !important;
  position:      relative !important;
  color:         transparent !important;
  font-size:     0 !important;
}
[data-testid="collapsedControl"] button::after {
  content:     "›";
  position:    absolute;
  top:         50%;
  left:        50%;
  transform:   translate(-50%, -50%);
  font-size:   18px;
  font-weight: 600;
  color:       var(--muted);
  line-height: 1;
}
[data-testid="collapsedControl"]:hover,
[data-testid="collapsedControl"] button:hover { background: var(--blue-ll) !important; }
[data-testid="collapsedControl"] button:hover::after { color: var(--blue); }

/* ── Sidebar ghost buttons (history) ── */
[data-testid="stSidebar"] .stButton > button {
  background:      transparent !important;
  color:           var(--text) !important;
  border:          none !important;
  border-radius:   8px !important;
  text-align:      right !important;
  font-weight:     400 !important;
  font-size:       13px !important;
  padding:         5px 10px !important;
  box-shadow:      none !important;
  width:           100% !important;
  justify-content: flex-end !important;
  transition:      background .15s, color .15s !important;
  direction:       rtl !important;
  line-height:     1.3 !important;
  min-height:      30px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: var(--blue-l) !important;
  color:      var(--blue) !important;
}

/* New-chat button — targeted via real st-key class (div-wrap trick doesn't
   actually nest in the DOM, so we hook the button's own keyed container) */
[data-testid="stSidebar"] div[class*="st-key-new_chat"] {
  margin: 10px 0 15px 0 !important;
}
[data-testid="stSidebar"] div[class*="st-key-new_chat"] button {
  background:      var(--blue) !important;
  color:           #fff !important;
  border-radius:   999px !important;
  font-weight:     600 !important;
  font-size:       13px !important;
  padding:         7px 16px !important;
  box-shadow:      0 2px 10px rgba(61,61,180,.25) !important;
  width:           100% !important;
  justify-content: center !important;
  min-height:      34px !important;
  direction:       ltr !important;
}
[data-testid="stSidebar"] div[class*="st-key-new_chat"] button:hover {
  background: var(--blue-d) !important;
}

/* Nav items — LTR icon+label rows, hooked the same way */
[data-testid="stSidebar"] div[class*="st-key-nav_chat"] button,
[data-testid="stSidebar"] div[class*="st-key-nav_crm"] button,
[data-testid="stSidebar"] div[class*="st-key-nav_monitor"] button {
  background:      transparent !important;
  color:           var(--text) !important;
  border:          none !important;
  border-radius:   8px !important;
  font-size:       14px !important;
  font-weight:     500 !important;
  padding:         9px 14px !important;
  text-align:      left !important;
  justify-content: flex-start !important;
  direction:       ltr !important;
  transition:      background .15s !important;
  width:           100% !important;
  min-height:      38px !important;
}
[data-testid="stSidebar"] div[class*="st-key-nav_chat"] button:hover,
[data-testid="stSidebar"] div[class*="st-key-nav_crm"] button:hover,
[data-testid="stSidebar"] div[class*="st-key-nav_monitor"] button:hover {
  background: var(--blue-l) !important;
  color:      var(--blue) !important;
}

/* Active nav — left accent bar (key gets an "_active" suffix when that page
   is the current one — see _sidebar() in the Python code below) */
[data-testid="stSidebar"] div[class*="st-key-nav_"][class*="_active"] button {
  background:    #FFFFFF !important;
  color:         var(--blue) !important;
  font-weight:   700 !important;
  border-radius: 0 8px 8px 0 !important;
  border-left:   3px solid var(--blue) !important;
  margin-left:   -3px !important;
  box-shadow:    0 1px 4px rgba(26,26,62,.08) !important;
}

/* Divider */
.k-divider {
  border:     none;
  border-top: 1px solid var(--border);
  margin:     10px 0;
}

/* ══ METRIC CARDS — icon badge style ══ */
.metric-row {
  display:   flex;
  gap:       16px;
  margin:    14px 0 22px 0;
  flex-wrap: wrap;
  direction: ltr; /* الكروت بترتيب ثابت بصرف النظر عن RTL */
}
.metric-card {
  flex:          1 1 180px;
  background:    #FFFFFF;
  border:        1px solid var(--border);
  border-radius: 18px;
  padding:       18px 20px;
  box-shadow:    0 1px 2px rgba(26,26,62,.04), 0 4px 14px rgba(26,26,62,.05);
  direction:     rtl;
  text-align:    right;
}
.metric-card-top {
  display:         flex;
  align-items:     center;
  justify-content: space-between;
  margin-bottom:   14px;
}
.metric-badge {
  width:           42px;
  height:          42px;
  border-radius:   50%;
  display:         flex;
  align-items:     center;
  justify-content: center;
  font-size:       19px;
  flex-shrink:     0;
}
.metric-trend {
  font-size:     11px;
  font-weight:   700;
  padding:       3px 9px;
  border-radius: 999px;
  white-space:   nowrap;
}
.metric-label {
  font-size:     13px;
  color:         var(--muted);
  font-weight:   500;
  margin-bottom: 4px;
}
.metric-info {
  cursor:      help;
  opacity:     .6;
  font-size:   12px;
}
.metric-value {
  font-size:   26px;
  font-weight: 700;
  color:       var(--text);
  line-height: 1.15;
}
@media (max-width: 640px) {
  .metric-row  { flex-direction: column; }
  .metric-card { flex: 1 1 auto; }
}

[data-testid="stSidebar"] [class*="st-key-chat_card_"] [data-testid="stHorizontalBlock"] {
  align-items:     center !important;
  display:         flex !important;
  flex-direction:  row !important;
  flex-wrap:       nowrap !important;
  gap:             4px !important;
}

/* Icons column — far left, zero padding */
[data-testid="stSidebar"] [class*="st-key-chat_card_"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:first-child {
  flex:          0 0 auto !important;
  width:         auto !important;
  max-width:     none !important;
  min-width:     0 !important;
  order:         1 !important;
  padding-left:  0 !important;
  padding-right: 2px !important;
}

/* Title column — takes remaining space */
[data-testid="stSidebar"] [class*="st-key-chat_card_"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child {
  flex:      1 1 auto !important;
  min-width: 0 !important;
  order:     2 !important;
  padding-left: 4px !important;
}

/* Inner horizontal block (the two icon buttons) */
[data-testid="stSidebar"] div[class*="st-key-rename_"],
[data-testid="stSidebar"] div[class*="st-key-del_"] {
  width: 36px !important;
  flex:  0 0 36px !important;
}
[data-testid="stSidebar"] [class*="st-key-chat_card_"] [data-testid="stColumn"]:first-child [data-testid="stHorizontalBlock"] {
  gap:             6px !important;
  justify-content: flex-start !important;
  padding-left:    0 !important;
  margin-left:     0 !important;
}

/* Icon buttons — style */
[data-testid="stSidebar"] div[class*="st-key-rename_"] button,
[data-testid="stSidebar"] div[class*="st-key-del_"] button {
  font-size:            0 !important;
  color:                transparent !important;
  line-height:          1 !important;
  padding:              0 !important;
  min-height:           36px !important;
  height:               36px !important;
  width:                36px !important;
  min-width:            36px !important;
  max-width:            36px !important;
  border-radius:        10px !important;
  box-shadow:           none !important;
  margin:               0 !important;
  display:              flex !important;
  align-items:          center !important;
  justify-content:      center !important;
  background-repeat:    no-repeat !important;
  background-position:  center !important;
  background-size:      18px 18px !important;
}
[data-testid="stSidebar"] div[class*="st-key-rename_"] button *,
[data-testid="stSidebar"] div[class*="st-key-del_"] button * {
  display: none !important;
}
[data-testid="stSidebar"] div[class*="st-key-del_"] button {
  background-color: #FEF2F2 !important;
  border: 1px solid #FEE2E2 !important;
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="%23DC2626" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>') !important;
}
[data-testid="stSidebar"] div[class*="st-key-rename_"] button {
  background-color: #EFF3FF !important;
  border: 1px solid #E0E7FF !important;
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="%232E4BF2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/><path d="m15 5 4 4"/></svg>') !important;
}
[data-testid="stSidebar"] div[class*="st-key-del_"] button:hover    { background-color: #FEE2E2 !important; }
[data-testid="stSidebar"] div[class*="st-key-rename_"] button:hover { background-color: #E0E7FF !important; }

/* ══ Previous-chat card ══ */
[data-testid="stSidebar"] [class*="st-key-chat_card_"] {
  background:    #fff !important;
  border-radius: 10px !important;
  box-shadow:    0 1px 3px rgba(30,30,60,.07) !important;
  margin:        0 2px 10px 2px !important;
  padding:       6px 10px 6px 0px !important;
}

/* ══ History Label ══ */
.hist-label {
  font-size: 11px !important;
  font-weight: 600 !important;
  color: var(--muted) !important;
  padding: 0 !important;
  margin-top: 25px !important;
  margin-bottom: 12px !important;
  text-transform: uppercase !important;
  letter-spacing: 0.5px !important;
  text-align: center !important;
  width: 100% !important;
}

/* ══ LOGO ══ */
[data-testid="stSidebar"] img,
.welcome-logo img {
  mix-blend-mode: multiply !important;
  background:     transparent !important;
}

/* ── Welcome Screen ── */
.welcome-wrap {
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  justify-content: center !important;
  text-align: center !important;
  width: 100% !important;
  margin-top: 6rem !important;
}
.welcome-logo {
  display: flex !important;
  justify-content: center !important;
  width: 100% !important;
  margin-bottom: 1.5rem !important;
}
.welcome-title {
  font-size: 36px !important;
  font-weight: 800 !important;
  color: var(--blue) !important;
  margin-bottom: 0.5rem !important;
  width: 100% !important;
}
.welcome-sub {
  font-size: 18px !important;
  color: var(--muted) !important;
  line-height: 1.6 !important;
  width: 100% !important;
}

/* ══ CHAT BUBBLES ══ */
[data-testid="stChatMessage"] {
  background:    transparent !important;
  border:        none !important;
  box-shadow:    none !important;
  padding:       1px 0 !important;
  margin-bottom: 1px !important;
}
[data-testid="stChatMessage"] [data-testid="chatAvatarIcon-user"],
[data-testid="stChatMessage"] [data-testid="chatAvatarIcon-assistant"] {
  display: none !important;
}

.user-bubble {
  background:    var(--user-bg);
  color:         var(--text);
  border-radius: var(--radius-msg) var(--radius-msg) 4px var(--radius-msg);
  padding:       10px 15px;
  max-width:     68%;
  margin:        3px 0 3px auto;
  font-size:     15px;
  line-height:   1.7;
  word-wrap:     break-word;
  box-shadow:    0 2px 8px rgba(61,61,180,.22),
                 0 0   0 1.5px rgba(61,61,180,.13);
  display:       table;
}

.ai-bubble {
  background:    var(--ai-bg);
  color:         var(--text);
  border-radius: var(--radius-msg) var(--radius-msg) var(--radius-msg) 4px;
  padding:       10px 15px;
  max-width:     78%;
  margin:        3px auto 3px 0;
  font-size:     15px;
  line-height:   1.8;
  word-wrap:     break-word;
  box-shadow:    0 1px 2px rgba(0,0,0,.10),
                 0 0   0 1px rgba(0,0,0,.05);
  display:       table;
}

.rtl { direction: rtl; text-align: right; }
.ltr { direction: ltr; text-align: left; }

/* ══ CHAT INPUT ══ */
[data-testid="stChatInput"] {
  border-radius: 24px !important;
  border:        1.5px solid var(--border) !important;
  background:    #fff !important;
  box-shadow:    0 2px 16px rgba(0,0,0,.07),
                 0 0   0 1px rgba(61,61,180,.05) !important;
  padding:       10px 20px !important;
  max-width:     760px !important;
  margin:        0 auto !important;
  transition:    box-shadow .2s, border-color .2s !important;
}
[data-testid="stChatInput"]:focus-within {
  border-color: var(--blue) !important;
  box-shadow:   0 4px 24px rgba(61,61,180,.14),
                0 0   0 1px rgba(61,61,180,.12) !important;
}
[data-testid="stChatInput"] textarea {
  font-size:   15px !important;
  color:       var(--text) !important;
  background:  transparent !important;
  direction:   rtl !important;
  line-height: 1.6 !important;
  outline:     none !important;
  border:      none !important;
  box-shadow:  none !important;
}

[data-testid="stExpander"] {
  border:        1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  margin-bottom: 10px !important;
}

/* ══ FIX: hide "_arrow" literal text from expander, replace with CSS arrow ══ */
[data-testid="stExpander"] summary [data-testid="stIconMaterial"] {
  font-size:  0 !important;
  color:      transparent !important;
  width:      20px !important;
  height:     20px !important;
  display:    inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  flex-shrink: 0 !important;
}
[data-testid="stExpander"] summary [data-testid="stIconMaterial"]::after {
  content:   "▾";
  font-size: 18px;
  color:     var(--muted);
  display:   block;
}
[data-testid="stExpander"] details[open] summary [data-testid="stIconMaterial"]::after {
  content: "▴";
}

/* ══ FIX: force RTL on plain markdown text inside expanders (e.g. Monitoring
   "📖 Explanation" boxes) so mixed Arabic/English text + `code` + parentheses
   doesn't get reordered by the browser's default LTR bidi algorithm ══ */
[data-testid="stExpander"] [data-testid="stMarkdownContainer"] {
  direction:  rtl !important;
  text-align: right !important;
}

[data-testid="stSpinner"] p { color:var(--blue) !important; font-size:13px !important; }

/* ══ MD RENDERING INSIDE AI BUBBLE ══ */
.ai-bubble h1,.ai-bubble h2,.ai-bubble h3 {
  color: var(--blue); font-weight:700; margin: 8px 0 4px;
}
.ai-bubble h1 { font-size:18px; }
.ai-bubble h2 { font-size:16px; }
.ai-bubble h3 { font-size:15px; }
.ai-bubble ul, .ai-bubble ol {
  margin: 4px 0 4px 0; padding-right:18px; padding-left:0;
}
.ai-bubble li { margin-bottom:3px; line-height:1.7; }
.ai-bubble table {
  border-collapse:collapse; width:100%; margin:8px 0; font-size:13px;
}
.ai-bubble th {
  background:var(--blue-l); color:var(--blue);
  padding:6px 10px; border:1px solid var(--border); font-weight:600;
}
.ai-bubble td {
  padding:5px 10px; border:1px solid var(--border);
}
.ai-bubble tr:nth-child(even) td { background:var(--blue-ll); }
.ai-bubble code {
  background:#F0F0FA; border-radius:4px; padding:1px 5px;
  font-size:13px; font-family:monospace; color:#2E2E9A;
}
.ai-bubble pre {
  background:#F0F0FA; border-radius:8px; padding:10px 14px;
  overflow-x:auto; margin:6px 0;
}
.ai-bubble pre code { background:none; padding:0; }
.ai-bubble strong { color:var(--blue); font-weight:700; }
.ai-bubble a { color:var(--blue); text-decoration:underline; }

[data-testid="stSidebar"] [data-testid="stTextInput"] input {
  font-size:13px !important; direction:rtl !important;
  border-radius:8px !important; padding:6px 10px !important;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# Session state initialiser
# ══════════════════════════════════════════════════════════════════════════════
def _init_state():
    defaults = {
        "page":          "chat",
        "session_id":    str(uuid.uuid4()),
        "messages":      [],
        "history":       [],
        "chat_names":    {},
        "renaming_sid":  None,
        "_names_loaded": False,
        "current_user":  None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    if not st.session_state._names_loaded:
        try:
            from db import load_session_names
            saved = load_session_names()
            st.session_state.chat_names = {**saved, **st.session_state.chat_names}
        except Exception:
            pass
        st.session_state._names_loaded = True


# ══════════════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════════════
def _is_arabic(t: str) -> bool:
    ar = sum(1 for c in t if '\u0600' <= c <= '\u06FF')
    en = sum(1 for c in t if c.isascii() and c.isalpha())
    return ar > en

import re

def _md_to_html(text: str) -> str:
    """Convert markdown to HTML with full MD support (tables, lists, headers, code…)."""
    try:
        import markdown as _md_lib
        html = _md_lib.markdown(
            text,
            extensions=["tables", "fenced_code", "nl2br", "sane_lists"],
        )
        # convert bare URLs to clickable links
        # lookbehind: only match after > or whitespace (skips URLs already in href="...")
        html = re.sub(
            r'(?<=[>\s])(https?://\S+?)(?=[\s<]|$)',
            r'<a href="\1" target="_blank" style="color:#3D3DB4;text-decoration:underline;word-break:break-all;">\1</a>',
            html,
        )
        return html
    except ImportError:
        # fallback — basic conversion
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', text)
        text = re.sub(
            r'(https?://[^\s<]+[^\s<.,!?؟،])',
            r'<a href="\1" target="_blank" style="color:#3D3DB4;text-decoration:underline;">\1</a>',
            text,
        )
        text = text.replace("\n", "<br>")
        return text

def _user_bubble(content: str):
    cls = "rtl" if _is_arabic(content) else "ltr"
    st.markdown(f'<div class="user-bubble {cls}">{content}</div>', unsafe_allow_html=True)

def _ai_bubble(content: str):
    cls = "rtl" if _is_arabic(content) else "ltr"
    st.markdown(f'<div class="ai-bubble {cls}">{content.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)

def _try_save_turn(session_id, role, content):
    try:
        from db import save_chat_turn
        save_chat_turn(session_id, role, content)
    except Exception:
        pass

def _load_sessions():
    try:
        from db import load_session_history
        return load_session_history()
    except Exception:
        return []

def _delete_session(sid: str):
    try:
        from db import delete_session
        delete_session(sid)
    except Exception:
        pass
    if st.session_state.get("session_id") == sid:
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages   = []
        st.session_state.history    = []
    st.session_state.chat_names.pop(sid, None)


# ══════════════════════════════════════════════════════════════════════════════
# Sidebar
# ══════════════════════════════════════════════════════════════════════════════
def _sidebar(active: str):
    with st.sidebar:
        st.markdown('<div style="padding:14px 14px 6px;margin-top:-3rem;text-align:left;">', unsafe_allow_html=True)
        try:
            st.image("logo.png", width=130)
        except Exception:
            st.markdown(
                '<div style="font-size:22px;font-weight:700;color:#3D3DB4;direction:ltr;text-align:left;">'
                'كيف</div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

        # ── User info + logout ──
        user = st.session_state.get("current_user")
        if user:
            uname = user.get("username", "")
            role  = user.get("role", "user")
            badge_color = "#BE185D" if role == "admin" else "#3D3DB4"
            badge_bg    = "#FCE7F3" if role == "admin" else "#EDEDFA"
            st.markdown(
                f'<div style="padding:4px 14px 10px;direction:ltr;display:flex;'
                f'align-items:center;gap:8px;">'
                f'<span style="font-size:13px;color:#1A1A3E;font-weight:600;">{uname}</span>'
                f'<span style="background:{badge_bg};color:{badge_color};padding:2px 10px;'
                f'border-radius:999px;font-size:10px;font-weight:700;">{role.upper()}</span>'
                f'<span style="margin-left:auto;display:flex;align-items:center;">'
                f'<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6B6B8A" '
                f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
                f'<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>'
                f'</svg></span>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown('<hr class="k-divider">', unsafe_allow_html=True)

        chat_key = "nav_chat_active" if active == "chat" else "nav_chat"
        if st.button("💬  Chat", use_container_width=True, key=chat_key):
            st.session_state.page = "chat"
            st.rerun()

        if user and user.get("role") == "admin":
            crm_key = "nav_crm_active" if active == "crm" else "nav_crm"
            if st.button("📋  CRM", use_container_width=True, key=crm_key):
                st.session_state.page = "crm"
                st.rerun()

            mon_key = "nav_monitor_active" if active == "monitor" else "nav_monitor"
            if st.button("📊  Monitoring", use_container_width=True, key=mon_key):
                st.session_state.page = "monitor"
                st.rerun()

        if active == "chat":
            if st.button("✦  New Chat", use_container_width=True, key="new_chat"):
                for k in ["session_id", "messages", "history"]:
                    st.session_state.pop(k, None)
                st.session_state.renaming_sid = None
                st.rerun()

            st.markdown('<div class="hist-label">Previous Chats</div>', unsafe_allow_html=True)
            sessions = _load_sessions()
            cur      = st.session_state.get("session_id", "")

            if not sessions:
                st.markdown(
                    '<div style="font-size:12px;color:#9CA3AF;padding:4px 2px;direction:rtl;text-align:center;">'
                    'لا توجد محادثات بعد</div>',
                    unsafe_allow_html=True,
                )
            else:
                for s in sessions:
                    sid   = s.get("_id", "") or ""
                    title = st.session_state.chat_names.get(
                        sid, (s.get("first_msg") or "محادثة")[:32]
                    )

                    # ── Rename mode ──
                    if st.session_state.renaming_sid == sid:
                        new_name = st.text_input(
                            "اسم جديد", value=title,
                            key=f"rename_input_{sid}",
                            label_visibility="collapsed",
                        )
                        sc, cc = st.columns(2)
                        with sc:
                            if st.button("✔ حفظ", key=f"save_rename_{sid}",
                                         use_container_width=True):
                                if new_name.strip():
                                    name_to_save = new_name.strip()
                                    st.session_state.chat_names[sid] = name_to_save
                                    try:
                                        from db import save_session_name
                                        save_session_name(sid, name_to_save)
                                    except Exception:
                                        pass
                                st.session_state.renaming_sid = None
                                st.rerun()
                        with cc:
                            if st.button("✖ إلغاء", key=f"cancel_rename_{sid}",
                                         use_container_width=True):
                                st.session_state.renaming_sid = None
                                st.rerun()
                        continue

                    # ── Normal row ──
                    icon = "▶ " if (sid == cur) else ""
                    with st.container(key=f"chat_card_{sid}"):
                        btns_col, row_col = st.columns([2, 6])

                        with btns_col:
                            b1, b2 = st.columns(2, gap="small")
                            with b1:
                                if st.button("🗑", key=f"del_{sid}", help="Delete"):
                                    _delete_session(sid)
                                    st.rerun()
                            with b2:
                                if st.button("✏", key=f"rename_{sid}", help="Rename"):
                                    st.session_state.renaming_sid = sid
                                    st.rerun()

                        with row_col:
                            if st.button(f"{icon}{title}", key=f"hist_{sid}",
                                        use_container_width=True):
                                try:
                                    from db import load_session_messages
                                    from agent import rebuild_message_history
                                    st.session_state.session_id = sid
                                    loaded = load_session_messages(sid)
                                    st.session_state.messages   = loaded
                                    st.session_state.history    = rebuild_message_history(loaded)
                                except Exception:
                                    pass
                                st.rerun()

        elif active == "crm":
            st.markdown('<hr class="k-divider">', unsafe_allow_html=True)
            st.markdown("**🔽 تصفية**")
            filt = st.selectbox(
                "الحرارة", ["الكل", "hot 🔥", "warm 🌤", "cold ❄️"],
                label_visibility="collapsed", key="crm_filter"
            )
            st.session_state.crm_filter_val = filt

        # ── Logout ──
        st.markdown('<div style="margin-top:12px;"></div>', unsafe_allow_html=True)
        if st.button("🚪 تسجيل الخروج", use_container_width=True, key="logout_btn"):
            for k in ["current_user", "messages", "history", "session_id",
                      "chat_names", "_names_loaded"]:
                st.session_state.pop(k, None)
            st.rerun()

        st.markdown(
            '<div style="position:fixed;bottom:0;width:220px;padding:8px 16px;'
            'font-size:11px;color:#C0C0D8;text-align:center;background:var(--side-bg);'
            'border-top:1px solid var(--border);direction:rtl;">'
            'Powered by Groq · Kayfa © 2026'
            '</div>',
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════════════════════
# Page: Chat
# ══════════════════════════════════════════════════════════════════════════════
def page_chat():
    msgs = st.session_state.messages

    if not msgs:
        try:
            import base64, pathlib
            img_bytes = pathlib.Path("logo.png").read_bytes()
            b64 = base64.b64encode(img_bytes).decode()
            logo_html = (
                f'<img src="data:image/png;base64,{b64}" '
                f'style="height:80px;mix-blend-mode:multiply;background:transparent;" />'
            )
        except Exception:
            logo_html = '<div style="font-size:40px;font-weight:800;color:#3D3DB4;">كيف</div>'

        st.markdown(f"""
        <div class="welcome-wrap">
            <div class="welcome-logo">{logo_html}</div>
            <div class="welcome-title">مرحباً بك في كيف</div>
            <div class="welcome-sub">اسألني عن أي كورس، مسار، أو دبلومة<br>وأنا أرشدك للمسار الأنسب لك</div>
            <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;700&display=swap" rel="stylesheet"><div style="margin-top:1.4rem;display:inline-block;font-family:'Plus Jakarta Sans',Inter,sans-serif;font-size:13px;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;background:#EDEDFA;color:#3D3DB4;padding:7px 20px;border-radius:999px;border:1.5px solid #C7C7F5;">Week 3 · Part 1 · Kayfa Internship</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        try:
            import base64, pathlib
            _logo_b64 = base64.b64encode(pathlib.Path("logo_icon.png").read_bytes()).decode()
            _ai_avatar_html = (
                f'<img src="data:image/png;base64,{_logo_b64}" '
                f'style="width:32px;height:32px;object-fit:contain;'
                f'mix-blend-mode:multiply;background:transparent;border-radius:6px;" />'
            )
        except Exception:
            _ai_avatar_html = "🤖"

        for msg in msgs:
            if msg["role"] == "user":
                st.markdown(
                    f'<div style="display:flex;align-items:flex-end;justify-content:flex-end;gap:8px;margin:3px 0;">'
                    f'<div class="user-bubble {("rtl" if _is_arabic(msg["content"]) else "ltr")}">{_md_to_html(msg["content"])}</div>'
                    f'<div style="font-size:26px;line-height:1;flex-shrink:0;">👤</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div style="display:flex;align-items:flex-end;justify-content:flex-start;gap:8px;margin:3px 0;">'
                    f'<div style="flex-shrink:0;width:32px;height:32px;">{_ai_avatar_html}</div>'
                    f'<div class="ai-bubble {("rtl" if _is_arabic(msg["content"]) else "ltr")}">{_md_to_html(msg["content"])}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    if prompt := st.chat_input("اكتب سؤالك… أو type in English"):
        try:
            import base64, pathlib
            _logo_b64 = base64.b64encode(pathlib.Path("logo_icon.png").read_bytes()).decode()
            _ai_avatar_html = (
                f'<img src="data:image/png;base64,{_logo_b64}" '
                f'style="width:32px;height:32px;object-fit:contain;'
                f'mix-blend-mode:multiply;background:transparent;border-radius:6px;" />'
            )
        except Exception:
            _ai_avatar_html = "🤖"

        st.markdown(
            f'<div style="display:flex;align-items:flex-end;justify-content:flex-end;gap:8px;margin:3px 0;">'
            f'<div class="user-bubble {("rtl" if _is_arabic(prompt) else "ltr")}">{_md_to_html(prompt)}</div>'
            f'<div style="font-size:26px;line-height:1;flex-shrink:0;">👤</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        msgs.append({"role": "user", "content": prompt})
        _try_save_turn(st.session_state.session_id, "user", prompt)

        with st.spinner("جاري التفكير…"):
            try:
                from agent import get_agent_reply
                user_id = (st.session_state.get("current_user") or {}).get("username", "anonymous")
                reply, new_hist = get_agent_reply(
                    prompt,
                    st.session_state.history,
                    st.session_state.session_id,
                    user_id=user_id,
                )
                st.session_state.history = new_hist
            except Exception as e:
                import traceback
                reply = f"⚠️ خطأ: `{str(e)[:400]}`"
                print(traceback.format_exc())

        st.markdown(
            f'<div style="display:flex;align-items:flex-end;justify-content:flex-start;gap:8px;margin:3px 0;">'
            f'<div style="flex-shrink:0;width:32px;height:32px;">{_ai_avatar_html}</div>'
            f'<div class="ai-bubble {("rtl" if _is_arabic(reply) else "ltr")}">{_md_to_html(reply)}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        msgs.append({"role": "assistant", "content": reply})
        _try_save_turn(st.session_state.session_id, "assistant", reply)
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# Page: CRM
# ══════════════════════════════════════════════════════════════════════════════
def page_crm():
    col_title, col_btn = st.columns([4, 1])
    with col_title:
        st.markdown("## 📋 CRM Dashboard")
        st.markdown(
            '<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@700&display=swap" rel="stylesheet">'
            '<span style="font-family:\'Plus Jakarta Sans\',Inter,sans-serif;font-size:13px;font-weight:700;'
            'letter-spacing:1.2px;text-transform:uppercase;background:#EDEDFA;color:#3D3DB4;'
            'padding:7px 20px;border-radius:999px;border:1.5px solid #C7C7F5;display:inline-block;">'
            'Week 3 · Part 1 · Kayfa Internship</span>',
            unsafe_allow_html=True,
        )
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 تحديث", key="crm_refresh"):
            st.session_state.pop("crm_cache", None)

    st.markdown('<hr class="k-divider">', unsafe_allow_html=True)

    if "crm_cache" not in st.session_state:
        try:
            from db import load_all_tickets
            st.session_state.crm_cache = load_all_tickets()
        except Exception as e:
            st.error(f"⚠️ MongoDB: {e}")
            st.session_state.crm_cache = []

    all_t = st.session_state.crm_cache
    hot   = sum(1 for t in all_t if str(t.get("temperature","")).lower() == "hot")
    warm  = sum(1 for t in all_t if str(t.get("temperature","")).lower() == "warm")
    cold  = sum(1 for t in all_t if str(t.get("temperature","")).lower() == "cold")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📊 الإجمالي",  len(all_t))
    c2.metric("🔥 ساخن",    hot)
    c3.metric("🌤 دافئ",   warm)
    c4.metric("❄️ بارد",   cold)
    st.markdown("<br>", unsafe_allow_html=True)

    filt     = st.session_state.get("crm_filter_val", "الكل")
    filtered = all_t
    if filt and filt != "الكل":
        key      = filt.split()[0]
        filtered = [t for t in all_t if str(t.get("temperature","")).lower() == key]

    if not filtered:
        st.info("لا يوجد عملاء بعد — ابدأ محادثة من صفحة المحادثة!")
        return

    TEMP_STYLE = {
        "hot":  ("#FEE2E2", "#B91C1C", "🔥"),
        "warm": ("#FEF3C7", "#92400E", "🌤"),
        "cold": ("#DBEAFE", "#1E40AF", "❄️"),
    }
    TEMP_AR = {
        "hot": "ساخن",
        "warm": "دافئ",
        "cold": "بارد",
    }

    for t in filtered:
        temp         = str(t.get("temperature", "warm")).lower()
        bg, tc, icon = TEMP_STYLE.get(temp, ("#F3F4F6", "#374151", "📋"))
        temp_ar      = TEMP_AR.get(temp, temp)
        date         = str(t.get("created_at", ""))[:16].replace("T", " ")
        name         = t.get("name", "—")
        interest     = t.get("interest", "—")

        with st.expander(f"{icon}  {name}  ·  {interest}  ·  {date}"):
            st.markdown(
                f'<span style="background:{bg};color:{tc};padding:3px 14px;'
                f'border-radius:999px;font-size:12px;font-weight:600;">{icon} {temp_ar}</span>',
                unsafe_allow_html=True,
            )
            st.markdown("<br>", unsafe_allow_html=True)
            r, l = st.columns(2)

            def row(label, val, col):
                if val:
                    col.markdown(
                        f'<div style="padding:5px 0;border-bottom:1px solid #F0F0FA;font-size:14px;direction:rtl;text-align:right;">'
                        f'<span style="color:#6B6B8A;">{label}:</span> '
                        f'<strong style="color:#1A1A3E;">{val}</strong></div>',
                        unsafe_allow_html=True,
                    )
            with r:
                st.markdown('<div style="direction:rtl;text-align:right;"><strong>👤 بيانات العميل</strong></div>', unsafe_allow_html=True)
                row("الاسم",          t.get("name",""),  r)
                row("الهاتف",         t.get("phone",""), r)
                row("البريد الإلكتروني", t.get("email",""), r)
                row("المدينة",        t.get("city",""),  r)
            with l:
                st.markdown('<div style="direction:rtl;text-align:right;"><strong>🎯 الاهتمام</strong></div>', unsafe_allow_html=True)
                row("المنتج",       t.get("interest",""),       l)
                row("الهدف",        t.get("goal",""),           l)
                row("المستوى",      t.get("current_level",""),  l)
                row("الإشارات",     t.get("buying_signals",""), l)
                row("الاعتراضات",   t.get("objections",""),     l)

            if t.get("conversation_summary"):
                st.markdown('<div style="direction:rtl;text-align:right;"><strong>📝 ملخص المحادثة</strong></div>', unsafe_allow_html=True)
                st.markdown(
                    f'<div class="rtl" style="background:#F5F5FD;padding:14px;'
                    f'border-radius:var(--radius);font-size:14px;line-height:1.9;'
                    f'border-right:3px solid #3D3DB4;direction:rtl;text-align:right;">'
                    f'{t["conversation_summary"]}</div>',
                    unsafe_allow_html=True,
                )
            if t.get("recommended_action"):
                st.markdown(
                    f'<div style="margin-top:10px;background:#FEF3C7;padding:11px 16px;'
                    f'border-radius:var(--radius);font-size:13px;color:#92400E;direction:rtl;text-align:right;">'
                    f'<strong>الإجراء المقترح:</strong> {t["recommended_action"]}</div>',
                    unsafe_allow_html=True,
                )


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════
def main():
    _init_state()

    # ── Ensure default admin exists ──
    try:
        from auth import ensure_default_admin
        ensure_default_admin()
    except Exception:
        pass

    # ── Auth Gate ──
    if not st.session_state.get("current_user"):
        from auth import render_auth_page
        render_auth_page()
        return

    _sidebar(st.session_state.page)

    if st.session_state.page == "chat":
        page_chat()
    elif st.session_state.page == "crm":
        # Admin only
        user = st.session_state.get("current_user", {})
        if user.get("role") == "admin":
            page_crm()
        else:
            st.warning("🔒 هذه الصفحة للأدمن فقط.")
            st.session_state.page = "chat"
            st.rerun()
    elif st.session_state.page == "monitor":
        # Admin only
        user = st.session_state.get("current_user", {})
        if user.get("role") == "admin":
            from monitoring import render_monitoring_page
            render_monitoring_page()
        else:
            st.warning("🔒 لوحة المراقبة للأدمن فقط.")
            st.session_state.page = "chat"
            st.rerun()


if __name__ == "__main__":
    main()