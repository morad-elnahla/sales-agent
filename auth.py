"""
auth.py — Kayfa Auth Layer
sign-up / login · user & admin roles · passwords hashed with sha256 + salt
"""

import hashlib
import secrets
import streamlit as st

# ── import db helpers lazily to avoid circular issues ──────────────────────

def _create_user(username: str, password_hash: str, salt: str, role: str) -> bool:
    from db import _get_db
    db = _get_db()
    if db["users"].find_one({"username": username}):
        return False
    db["users"].insert_one({
        "username":      username,
        "password_hash": password_hash,
        "salt":          salt,
        "role":          role,
    })
    return True


def _find_user(username: str) -> dict | None:
    from db import _get_db
    return _get_db()["users"].find_one({"username": username})


# ── Core helpers ────────────────────────────────────────────────────────────

def _hash(password: str, salt: str) -> str:
    return hashlib.sha256(f"{salt}{password}".encode("utf-8")).hexdigest()


def signup(username: str, password: str, role: str = "user") -> tuple[bool, str]:
    """
    Returns (ok, message). Validation errors are returned normally;
    any unexpected DB/connection failure is caught here so it never
    surfaces as a raw traceback in the UI.
    """
    username = username.strip().lower()
    if len(username) < 3:
        return False, "اسم المستخدم يجب أن يكون 3 أحرف على الأقل"
    if len(password) < 6:
        return False, "كلمة المرور يجب أن تكون 6 أحرف على الأقل"
    try:
        if _find_user(username):
            return False, "اسم المستخدم موجود بالفعل — جرّب اسماً آخر"
        salt   = secrets.token_hex(16)
        hashed = _hash(password, salt)
        ok = _create_user(username, hashed, salt, role)
        if not ok:
            return False, "اسم المستخدم موجود بالفعل — جرّب اسماً آخر"
        return True, "تم إنشاء الحساب بنجاح ✅"
    except Exception:
        return False, "⚠️ تعذّر إنشاء الحساب الآن، حدث خطأ في الاتصال بالخادم. حاول مرة أخرى بعد قليل."


def login(username: str, password: str) -> tuple[dict | None, str]:
    """
    Returns (user, status).
    status ∈ {"ok", "not_found", "wrong_password", "error"}
    - "not_found": no account exists with this username (clear Arabic message in the UI)
    - "wrong_password": account exists, password is incorrect
    - "error": unexpected/DB connection failure, caught instead of crashing the page
    """
    username = username.strip().lower()
    try:
        user = _find_user(username)
    except Exception:
        return None, "error"

    if not user:
        return None, "not_found"
    if _hash(password, user.get("salt", "")) == user.get("password_hash", ""):
        return user, "ok"
    return None, "wrong_password"


def ensure_default_admin():
    """
    Creates the default admin account on first run if it doesn't exist yet.
    Credentials: admin / morad
    """
    try:
        if not _find_user("admin"):
            signup("admin", "morad", role="admin")
    except Exception:
        pass


# ── Streamlit helpers ───────────────────────────────────────────────────────

def get_current_user() -> dict | None:
    return st.session_state.get("current_user")


def is_admin() -> bool:
    user = get_current_user()
    return bool(user and user.get("role") == "admin")


def render_auth_page():
    """
    Renders the sign-up / login form.
    Sets st.session_state.current_user and returns True when authenticated.
    """
    st.markdown("""
    <style>
    .auth-logo-wrap {
        max-width: 420px;
        margin: 4.5rem auto 0;
        text-align: center;
    }
    .auth-title {
        font-size: 40px;
        font-weight: 800;
        color: var(--blue, #3D3DB4);
        margin-bottom: 2px;
        line-height: 1;
    }
    .auth-sub {
        color: var(--muted, #6B6B8A);
        font-size: 15px;
        margin-bottom: 1.75rem;
    }

    /* center & restyle the login/signup tabs */
    div[data-testid="stTabs"] {
        max-width: 420px;
        margin: 0 auto;
    }
    div[data-testid="stTabs"] button[role="tab"] {
        flex: 1;
        justify-content: center;
        font-weight: 600;
        font-size: 15px;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] {
        color: var(--blue, #3D3DB4) !important;
    }
    div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
        background-color: var(--blue, #3D3DB4) !important;
    }

    /* card around the form */
    div[data-testid="stTabs"] + div [data-testid="stVerticalBlockBorderWrapper"],
    div[data-testid="stVerticalBlockBorderWrapper"]:has(input) {
        border-radius: var(--radius, 14px) !important;
        border: 1px solid var(--border, #E8E8F4) !important;
        background: #FFFFFF !important;
        box-shadow: 0 4px 18px rgba(61, 61, 180, 0.06) !important;
        padding: 1.6rem 1.4rem !important;
    }

    /* RTL, rounded inputs */
    div[data-testid="stTabs"] input {
        direction: rtl;
        text-align: right;
        border-radius: 10px !important;
    }
    div[data-testid="stTabs"] label {
        direction: rtl;
        text-align: right;
        width: 100%;
        display: block;
        font-weight: 500;
        color: var(--text, #1A1A3E);
    }

    /* primary buttons */
    div[data-testid="stTabs"] button[kind="primary"],
    div[data-testid="stTabs"] button[kind="secondary"] {
        border-radius: 10px !important;
        font-weight: 700 !important;
    }
    </style>
    <div class="auth-logo-wrap">
        <div class="auth-title">كيف</div>
        <div class="auth-sub">Kayfa AI Sales Agent</div>
    </div>
    """, unsafe_allow_html=True)

    col = st.columns([1, 3, 1])[1]
    with col:
        tab_login, tab_signup = st.tabs(["تسجيل الدخول", "حساب جديد"])

        with tab_login:
            with st.container(border=True):
                uname = st.text_input("اسم المستخدم", key="login_uname",
                                      placeholder="اسم المستخدم")
                pwd   = st.text_input("كلمة المرور", type="password",
                                      key="login_pwd", placeholder="••••••")
                if st.button("دخول →", use_container_width=True, key="login_btn", type="primary"):
                    if not uname or not pwd:
                        st.error("أدخل اسم المستخدم وكلمة المرور")
                    else:
                        user, status = login(uname, pwd)
                        if status == "ok":
                            user.pop("_id", None)
                            st.session_state.current_user = user
                            st.rerun()
                        elif status == "not_found":
                            st.error("❌ هذا الحساب غير مسجل — تأكد من اسم المستخدم أو أنشئ حساباً جديداً من تبويب «حساب جديد»")
                        elif status == "wrong_password":
                            st.error("❌ كلمة المرور غير صحيحة")
                        else:
                            st.error("⚠️ تعذّر الاتصال بالخادم الآن، حاول مرة أخرى بعد قليل")

        with tab_signup:
            with st.container(border=True):
                new_uname = st.text_input("اسم المستخدم", key="su_uname",
                                           placeholder="اختر اسماً فريداً")
                new_pwd   = st.text_input("كلمة المرور", type="password",
                                           key="su_pwd", placeholder="6 أحرف على الأقل")
                new_pwd2  = st.text_input("تأكيد كلمة المرور", type="password",
                                           key="su_pwd2", placeholder="أعد كتابة كلمة المرور")
                if st.button("إنشاء حساب", use_container_width=True, key="signup_btn", type="primary"):
                    if not new_uname or not new_pwd or not new_pwd2:
                        st.error("من فضلك عبّئ كل الحقول")
                    elif new_pwd != new_pwd2:
                        st.error("كلمتا المرور غير متطابقتين")
                    else:
                        ok, msg = signup(new_uname, new_pwd, role="user")
                        if ok:
                            st.success(msg)
                            st.info("سجّل دخولك الآن من تبويب «تسجيل الدخول»")
                        else:
                            st.error(msg)

    return False  # not logged in yet