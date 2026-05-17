import streamlit as st
import plotly.express as px
from sqlalchemy import text
from src.utils import apply_admin_css

# ── Page config ───────────────────────────────────────────────
st.set_page_config(page_title="Admin Dashboard", layout="wide")

# ── Inject Modern Professional CSS ────────────────────────────
apply_admin_css()

# ── Session state ─────────────────────────────────────────────
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# ── Chart theme colors (Slate Blue/Steel Theme) ───────────────
GRID_COLOR = "rgba(148, 163, 184, 0.08)"
BG_COLOR   = "rgba(0,0,0,0)"

def apply_chart_theme(fig, title=""):
    fig.update_layout(
        title=dict(text=title, font=dict(color="#f1f5f9", size=15, family="sans-serif")),
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=BG_COLOR,
        font=dict(color="#94a3b8", family="sans-serif"),
        margin=dict(l=20, r=20, t=44, b=20),
        xaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR, linecolor="rgba(51,65,85,0.5)"),
        yaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR, linecolor="rgba(51,65,85,0.5)"),
    )
    return fig

# ── HTML table builders ───────────────────────────────────────
def users_table_html(df):
    rows = ""
    for _, row in df[["username", "email"]].iterrows():
        initials = row["username"][:2].upper()
        rows += f"""
        <tr style="border-bottom:1px solid #1e293b;"
            onmouseover="this.style.background='rgba(56,189,248,0.04)'"
            onmouseout="this.style.background='transparent'">
            <td style="padding:12px 16px; display:flex; align-items:center;">
                <span style="background:linear-gradient(135deg,#0369a1,#0284c7);
                    border-radius:50%;width:32px;height:32px;display:inline-flex;
                    align-items:center;justify-content:center;font-size:0.75rem;
                    font-weight:700;color:#fff;margin-right:12px;">{initials}</span>
                <span style="color:#f1f5f9;font-weight:500;">{row['username']}</span>
            </td>
            <td style="padding:12px 16px;color:#94a3b8;">{row['email']}</td>
        </tr>"""

    return f"""
    <div style="border-radius:8px;border:1px solid #334155;overflow:hidden;
        margin-bottom:8px;box-shadow:0 4px 6px -1px rgba(0,0,0,0.2);">
        <table style="width:100%;border-collapse:collapse;background:#0f172a;">
            <thead>
                <tr style="background:#1e293b; border-bottom:1px solid #334155;">
                    <th style="padding:12px 16px;text-align:left;color:#38bdf8;
                        font-size:0.75rem;letter-spacing:1px;text-transform:uppercase;font-weight:600;">👤 Username</th>
                    <th style="padding:12px 16px;text-align:left;color:#38bdf8;
                        font-size:0.75rem;letter-spacing:1px;text-transform:uppercase;font-weight:600;">📧 Email</th>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
    </div>"""


def searches_table_html(df):
    rows = ""
    for _, row in df.iterrows():
        rows += f"""
        <tr style="border-bottom:1px solid #1e293b;"
            onmouseover="this.style.background='rgba(56,189,248,0.04)'"
            onmouseout="this.style.background='transparent'">
            <td style="padding:12px 14px;color:#f1f5f9;font-weight:500;">{row['username']}</td>
            <td style="padding:12px 14px;">
                <span style="background:rgba(14,165,233,0.1);border:1px solid rgba(14,165,233,0.3);
                    border-radius:4px;padding:3px 8px;font-size:0.75rem;color:#38bdf8;font-weight:500;">
                    {row['genre']}
                </span>
            </td>
            <td style="padding:12px 14px;">
                <span style="background:rgba(99,102,241,0.1);border:1px solid rgba(99,102,241,0.3);
                    border-radius:4px;padding:3px 8px;font-size:0.75rem;color:#818cf8;font-weight:500;">
                    {row['mood']}
                </span>
            </td>
            <td style="padding:12px 14px;color:#cbd5e1;font-size:0.85rem;">
                {int(row['min_year'])} – {int(row['max_year'])}
            </td>
            <td style="padding:12px 14px;color:#38bdf8;font-size:0.85rem;font-weight:500;">
                ⭐ {float(row['min_rating']):.1f} – {float(row['max_rating']):.1f}
            </td>
            <td style="padding:12px 14px;text-align:center;color:#0ea5e9;font-weight:700;">
                {int(row['num_results'])}
            </td>
        </tr>"""

    return f"""
    <div style="border-radius:8px;border:1px solid #334155;
        overflow:hidden;overflow-x:auto;margin-bottom:8px;
        box-shadow:0 4px 6px -1px rgba(0,0,0,0.2);">
        <table style="width:100%;border-collapse:collapse;background:#0f172a;">
            <thead>
                <tr style="background:#1e293b; border-bottom:1px solid #334155;">
                    <th style="padding:12px 14px;text-align:left;color:#38bdf8;
                        font-size:0.72rem;letter-spacing:1px;text-transform:uppercase;font-weight:600;">👤 User</th>
                    <th style="padding:12px 14px;text-align:left;color:#38bdf8;
                        font-size:0.72rem;letter-spacing:1px;text-transform:uppercase;font-weight:600;">🎭 Genre</th>
                    <th style="padding:12px 14px;text-align:left;color:#38bdf8;
                        font-size:0.72rem;letter-spacing:1px;text-transform:uppercase;font-weight:600;">😊 Mood</th>
                    <th style="padding:12px 14px;text-align:left;color:#38bdf8;
                        font-size:0.72rem;letter-spacing:1px;text-transform:uppercase;font-weight:600;">📅 Years</th>
                    <th style="padding:12px 14px;text-align:left;color:#38bdf8;
                        font-size:0.72rem;letter-spacing:1px;text-transform:uppercase;font-weight:600;">⭐ Rating Range</th>
                    <th style="padding:12px 14px;text-align:center;color:#38bdf8;
                        font-size:0.72rem;letter-spacing:1px;text-transform:uppercase;font-weight:600;">🎬 Results</th>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
    </div>"""


# ── Admin Login Page ──────────────────────────────────────────
def admin_login():
    col1, col2, col3 = st.columns([1, 1.6, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center; padding: 64px 0 24px 0;">
            <div style="font-size:2.5rem; margin-bottom:12px;">🛡️</div>
            <h1 style="color:#f1f5f9; font-size:1.6rem; font-weight:700; margin:0 0 4px 0;">
                Enterprise Console
            </h1>
            <p style="color:#64748b; font-size:0.8rem; letter-spacing:1.5px; text-transform:uppercase;">
                System Administration
            </p>
        </div>
        """, unsafe_allow_html=True)

        password = st.text_input(
            "Admin Password",
            type="password",
            placeholder="Enter secure master credential...",
            label_visibility="collapsed"
        )

        st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
        if st.button("Authenticate", use_container_width=True, type="primary"):
            if password == st.secrets["ADMIN_TOKEN"]:
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("❌ Invalid system access credential.")


# ── Admin Dashboard ───────────────────────────────────────────
def admin_dashboard():
    conn = st.connection('postgresql', type='sql', pool_pre_ping=True)

    # Header
    st.markdown("""
    <div style="padding: 12px 0 16px 0; display:flex; justify-content:space-between; align-items:center;">
        <div>
            <h1 style="color:#f1f5f9; margin:0; font-size:1.8rem; font-weight:700; letter-spacing:-0.5px;">
                📈 Movie Recommendation System Dashboard
            </h1>
            <p style="color:#64748b; margin:2px 0 0 0; font-size:0.85rem;">
                Real-time execution performance and demographic tracking metrics.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    columns_btn = st.columns([8, 1.2])
    with columns_btn[1]:
        if st.button("Term Session", type="secondary", use_container_width=True):
            st.session_state.admin_logged_in = False
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Fetch data ────────────────────────────────────────────
    users_df = conn.query(
        "SELECT user_id, username, email FROM users ORDER BY username ASC", ttl=30)

    searches_df = conn.query("""
        SELECT u.username, ms.genre, ms.mood, ms.min_year, ms.max_year, ms.min_rating, ms.max_rating, ms.num_results
        FROM movie_searches ms
        JOIN users u ON ms.user_id = u.user_id
        ORDER BY ms.id DESC LIMIT 100
    """, ttl=30)

    genres_df = conn.query("""
        SELECT genre, COUNT(*) AS count
        FROM movie_searches GROUP BY genre ORDER BY count DESC LIMIT 10
    """, ttl=30)

    moods_df = conn.query("""
        SELECT mood, COUNT(*) AS count
        FROM movie_searches GROUP BY mood ORDER BY count DESC LIMIT 10
    """, ttl=30)

    per_user_df = conn.query("""
        SELECT u.username, COUNT(ms.id) AS searches
        FROM users u
        LEFT JOIN movie_searches ms ON u.user_id = ms.user_id
        GROUP BY u.username ORDER BY searches DESC LIMIT 15
    """, ttl=30)

    total_users    = len(users_df)
    total_searches = len(searches_df)
    avg_per_user   = round(total_searches / total_users, 1) if total_users else 0

    # ── Metrics ───────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    c1.metric("👥 TOTAL ACCOUNTS",     total_users)
    c2.metric("🔍 QUERY REQUESTS",  total_searches)
    c3.metric("📊 AVG SYSTEM UTILITY", f"{avg_per_user} reqs")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts: Genres + Moods ────────────────────────────────
    st.subheader("📊 Analytical Overview")
    col1, col2 = st.columns(2)

    with col1:
        if not genres_df.empty:
            fig = px.bar(
                genres_df, x="count", y="genre", orientation="h",
                color="count",
                color_continuous_scale=[[0, "#1e3a8a"], [1, "#0ea5e9"]],
            )
            fig.update_traces(marker_line_width=0)
            fig = apply_chart_theme(fig, "🎭 High-Demand Movie Genres")
            fig.update_layout(
                coloraxis_showscale=False,
                yaxis=dict(categoryorder="total ascending", gridcolor=GRID_COLOR),
                xaxis_title="", yaxis_title=""
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No query volume analytics found.")

    with col2:
        if not moods_df.empty:
            fig = px.pie(
                moods_df, values="count", names="mood",
                color_discrete_sequence=["#0284c7","#38bdf8","#0f172a",
                                         "#1e3a8a","#334155","#64748b"],
                hole=0.55,
            )
            fig.update_traces(
                textfont_color="#fff",
                marker=dict(line=dict(color="#0b0f19", width=2))
            )
            fig = apply_chart_theme(fig, "😊 Filtered Emotional Mood Targets")
            fig.update_layout(legend=dict(font=dict(color="#94a3b8")))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No context mood matrix parameters available.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Chart: Searches per User ──────────────────────────────
    st.subheader("👥 User Engagement Balance")
    if not per_user_df.empty:
        fig = px.bar(
            per_user_df, x="username", y="searches",
            color="searches",
            color_continuous_scale=[[0, "#1e3a8a"], [1, "#38bdf8"]],
        )
        fig.update_traces(marker_line_width=0)
        fig = apply_chart_theme(fig, "")
        fig.update_layout(
            coloraxis_showscale=False,
            xaxis_title="", yaxis_title="Requests Dispatched",
            xaxis=dict(tickangle=-30, gridcolor=GRID_COLOR),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No diagnostic request logs compiled.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Users table ───────────────────────────────────────────
    st.subheader("👥 Account Database Records")

    search_user = st.text_input("🔎 Search by unique identifier or email", placeholder="Type user criteria to isolate records...")
    filtered_users = users_df.copy()
    if search_user:
        filtered_users = filtered_users[
            filtered_users["username"].str.contains(search_user, case=False, na=False) |
            filtered_users["email"].str.contains(search_user, case=False, na=False)
        ]

    st.caption(f"Isolating {len(filtered_users)} of {total_users} database entries")

    if filtered_users.empty:
        st.info("No profiles match the filter specification.")
    else:
        st.markdown(users_table_html(filtered_users), unsafe_allow_html=True)

    # ── Delete user ───────────────────────────────────────────
    with st.expander("🗑️ System Account Purge"):
        st.warning("⚠️ Critical: Purging an account removes all diagnostic search history metadata permanently.")
        user_to_delete = st.selectbox("Select Target User ID", ["— Select Target —"] + users_df["username"].tolist())

        if user_to_delete != "— Select Target —":
            if st.button(f"Purge Account: {user_to_delete}", type="primary"):
                try:
                    uid_row = conn.query(
                        "SELECT user_id FROM users WHERE username = :un",
                        params={"un": user_to_delete}, ttl=0
                    )
                    if not uid_row.empty:
                        uid = uid_row.iloc[0]["user_id"]
                        with conn.session as s:
                            s.execute(text("DELETE FROM movie_searches WHERE user_id = :uid"), {"uid": uid})
                            s.execute(text("DELETE FROM users WHERE user_id = :uid"), {"uid": uid})
                            s.commit()
                        st.success(f"✅ Master Purge Completed: System data dropped for '{user_to_delete}'.")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("Target identifier missing from catalog.")
                except Exception as e:
                    st.error(f"Execution Error: Purge sequence failed: {e}")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Searches table ────────────────────────────────────────
    st.subheader("🔍 Master Search Activity Logs")

    search_filter     = st.text_input("🔎 Isolate logs by username ID", placeholder="Isolate query tracking data...", key="sf")
    filtered_searches = searches_df.copy()
    if search_filter:
        filtered_searches = filtered_searches[
            filtered_searches["username"].str.contains(search_filter, case=False, na=False)
        ]

    st.caption(f"Compiled {len(filtered_searches)} individual query events")

    if filtered_searches.empty:
        st.info("No active logs register under this entry.")
    else:
        st.markdown(searches_table_html(filtered_searches), unsafe_allow_html=True)


# ── Router ────────────────────────────────────────────────────
if st.session_state.admin_logged_in:
    admin_dashboard()
else:
    admin_login()