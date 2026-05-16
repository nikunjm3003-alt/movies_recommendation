import streamlit as st
import pandas as pd
from sqlalchemy import text

# ── Page config ───────────────────────────────────────────────
st.set_page_config(page_title="Admin Panel", layout="wide")

# ── Styling ───────────────────────────────────────────────────
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #0d0d1a;
    }
    [data-testid="stHeader"] {
        background: transparent;
    }
    html, body, [class*="css"] {
        color: #e2e8f0;
        font-family: 'Courier New', monospace;
    }
    .admin-title {
        font-size: 1.8rem;
        font-weight: 800;
        color: #6c63ff;
        letter-spacing: 1px;
        margin-bottom: 0;
    }
    .admin-sub {
        font-size: 0.82rem;
        color: #64748b;
        margin-top: 2px;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: rgba(108, 99, 255, 0.08);
        border: 1px solid rgba(108, 99, 255, 0.3);
        border-radius: 10px;
        padding: 1rem 1.2rem;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        color: #a855f7;
    }
    .metric-label {
        font-size: 0.78rem;
        color: #94a3b8;
        margin-top: 2px;
    }
    .section-header {
        font-size: 1rem;
        font-weight: 700;
        color: #c4b5fd;
        border-left: 3px solid #6c63ff;
        padding-left: 10px;
        margin: 1.5rem 0 0.8rem 0;
    }
    .stDataFrame { border: 1px solid #6c63ff33; border-radius: 8px; }
    .stButton > button {
        background: linear-gradient(90deg, #6c63ff, #a855f7);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: bold;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #a855f7, #6c63ff);
        transform: scale(1.02);
    }
    .back-link {
        font-size: 0.82rem;
        color: #6c63ff;
        text-decoration: none;
    }
    .back-link:hover { color: #a855f7; }
    </style>
""", unsafe_allow_html=True)

# ── Admin password guard ──────────────────────────────────────
st.write("Available secret keys:", list(st.secrets.keys()))

if "ADMIN_PASSWORD" not in st.secrets:
    st.error("Admin access is not configured.")
    st.stop()

ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]

if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

if not st.session_state.admin_authenticated:
    st.markdown('<p class="admin-title">⚙️ Admin Panel</p>', unsafe_allow_html=True)
    st.markdown('<p class="admin-sub">Restricted access — enter the admin password to continue.</p>', unsafe_allow_html=True)

    pwd = st.text_input("Admin Password", type="password", placeholder="Enter admin password")

    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Unlock", use_container_width=True):
            if pwd == ADMIN_PASSWORD:
                st.session_state.admin_authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password.")

    st.markdown('<br><a class="back-link" href="/" target="_self">← Back to app</a>', unsafe_allow_html=True)
    st.stop()

# ── Authenticated admin view ──────────────────────────────────
conn = st.connection("postgresql", type="sql")

st.markdown('<p class="admin-title">⚙️ Admin Panel</p>', unsafe_allow_html=True)
st.markdown('<p class="admin-sub">Movie Recommendation System — Admin Dashboard</p>', unsafe_allow_html=True)

col_back, _ = st.columns([1, 6])
with col_back:
    if st.button("🔒 Lock Panel"):
        st.session_state.admin_authenticated = False
        st.rerun()

st.markdown('<a class="back-link" href="/" target="_self">← Back to app</a>', unsafe_allow_html=True)

st.divider()

# ── Metrics ───────────────────────────────────────────────────
try:
    with conn.session as s:
        total_users   = pd.read_sql(text("SELECT COUNT(*) AS n FROM users"), s.connection()).iloc[0]["n"]
        total_searches = pd.read_sql(text("SELECT COUNT(*) AS n FROM movie_searches"), s.connection()).iloc[0]["n"]
        top_genre_row  = pd.read_sql(
            text("SELECT genre, COUNT(*) AS cnt FROM movie_searches GROUP BY genre ORDER BY cnt DESC LIMIT 1"),
            s.connection()
        )
        top_genre = top_genre_row.iloc[0]["genre"] if not top_genre_row.empty else "—"

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{total_users}</div><div class="metric-label">Registered Users</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{total_searches}</div><div class="metric-label">Total Searches</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{top_genre}</div><div class="metric-label">Top Genre</div></div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"Failed to load metrics: {e}")

# ── All Users ─────────────────────────────────────────────────
st.markdown('<p class="section-header">👥 Registered Users</p>', unsafe_allow_html=True)
try:
    with conn.session as s:
        users_df = pd.read_sql(
            text("SELECT user_id, username, email FROM users ORDER BY username"),
            s.connection()
        )
    if users_df.empty:
        st.info("No users registered yet.")
    else:
        st.dataframe(users_df, use_container_width=True)
except Exception as e:
    st.error(f"Failed to load users: {e}")

# ── Recent Searches ───────────────────────────────────────────
st.markdown('<p class="section-header">🔍 Recent Searches (Last 50)</p>', unsafe_allow_html=True)
try:
    with conn.session as s:
        searches_df = pd.read_sql(
            text("""
                SELECT u.username,
                       ms.genre,
                       ms.mood,
                       ms.min_year,
                       ms.max_year,
                       ms.num_results
                FROM movie_searches ms
                JOIN users u ON ms.user_id = u.user_id
                ORDER BY ms.id DESC
                LIMIT 50
            """),
            s.connection()
        )
    if searches_df.empty:
        st.info("No searches recorded yet.")
    else:
        st.dataframe(searches_df, use_container_width=True)
except Exception as e:
    st.error(f"Failed to load searches: {e}")

# ── Genre breakdown ───────────────────────────────────────────
st.markdown('<p class="section-header">🎭 Genre Popularity</p>', unsafe_allow_html=True)
try:
    with conn.session as s:
        genre_df = pd.read_sql(
            text("SELECT genre, COUNT(*) AS searches FROM movie_searches GROUP BY genre ORDER BY searches DESC"),
            s.connection()
        )
    if not genre_df.empty:
        st.bar_chart(genre_df.set_index("genre")["searches"])
except Exception as e:
    st.error(f"Failed to load genre data: {e}")