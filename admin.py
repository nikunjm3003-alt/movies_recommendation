import streamlit as st
import plotly.express as px
from sqlalchemy import text
from src.utils import apply_admin_css

# ── Page config ───────────────────────────────────────────────
st.set_page_config(page_title="Admin Dashboard", layout="wide")

# ── Inject CSS ────────────────────────────────────────────────
apply_admin_css()

# ── Session state ─────────────────────────────────────────────
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# ── Chart theme ───────────────────────────────────────────────
GRID_COLOR = "rgba(148,163,184,0.12)"
BG_COLOR   = "rgba(2,6,23,0)"

def apply_chart_theme(fig, title=""):
    fig.update_layout(
        title=dict(text=title, font=dict(color="#f8fafc", size=15, family="sans-serif")),
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=BG_COLOR,
        font=dict(color="#cbd5e1", family="sans-serif"),
        margin=dict(l=20, r=20, t=44, b=20),
        xaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR, linecolor=GRID_COLOR),
        yaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR, linecolor=GRID_COLOR),
    )
    return fig

# ── HTML table builders ───────────────────────────────────────
def users_table_html(df):
    rows = ""
    for _, row in df[["username", "email"]].iterrows():
        initials = row["username"][:2].upper()
        rows += f"""
        <tr style="border-bottom:1px solid #f1f5f9;"
            onmouseover="this.style.background='#f8fafc'"
            onmouseout="this.style.background='#ffffff'">
            <td style="padding:12px 16px;">
                <span style="background:linear-gradient(135deg,#0284c7,#0ea5e9);
                    border-radius:50%;width:32px;height:32px;display:inline-flex;
                    align-items:center;justify-content:center;font-size:0.7rem;
                    font-weight:700;color:#fff;margin-right:10px;">{initials}</span>
                <span style="color:#0f172a;font-weight:500;">{row['username']}</span>
            </td>
            <td style="padding:12px 16px;color:#64748b;">{row['email']}</td>
        </tr>"""

    return f"""
    <div style="border-radius:12px;border:1px solid #e2e8f0;overflow:hidden;
        margin-bottom:8px;box-shadow:0 1px 4px rgba(0,0,0,0.05);">
        <table style="width:100%;border-collapse:collapse;background:#ffffff;">
            <thead>
                <tr style="background:linear-gradient(90deg,#f0f9ff,#e0f2fe);
                    border-bottom:1px solid #bae6fd;">
                    <th style="padding:12px 16px;text-align:left;color:#0284c7;
                        font-size:0.75rem;letter-spacing:1px;text-transform:uppercase;">
                        👤 Username</th>
                    <th style="padding:12px 16px;text-align:left;color:#0284c7;
                        font-size:0.75rem;letter-spacing:1px;text-transform:uppercase;">
                        📧 Email</th>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
    </div>"""


def searches_table_html(df):
    rows = ""
    for _, row in df.iterrows():
        rows += f"""
        <tr style="border-bottom:1px solid #f1f5f9;"
            onmouseover="this.style.background='#f8fafc'"
            onmouseout="this.style.background='#ffffff'">
            <td style="padding:11px 14px;color:#0f172a;font-weight:500;">{row['username']}</td>
            <td style="padding:11px 14px;">
                <span style="background:#e0f2fe;border:1px solid #bae6fd;
                    border-radius:20px;padding:2px 10px;font-size:0.75rem;color:#0369a1;">
                    {row['genre']}
                </span>
            </td>
            <td style="padding:11px 14px;">
                <span style="background:#f0fdf4;border:1px solid #bbf7d0;
                    border-radius:20px;padding:2px 10px;font-size:0.75rem;color:#15803d;">
                    {row['mood']}
                </span>
            </td>
            <td style="padding:11px 14px;color:#94a3b8;font-size:0.82rem;">
                {int(row['min_year'])} – {int(row['max_year'])}
            </td>
            <td style="padding:11px 14px;text-align:center;color:#0284c7;font-weight:700;">
                {int(row['num_results'])}
            </td>
        </tr>"""

    return f"""
    <div style="border-radius:12px;border:1px solid #e2e8f0;overflow:hidden;
        overflow-x:auto;margin-bottom:8px;box-shadow:0 1px 4px rgba(0,0,0,0.05);">
        <table style="width:100%;border-collapse:collapse;background:#ffffff;">
            <thead>
                <tr style="background:linear-gradient(90deg,#f0f9ff,#e0f2fe);
                    border-bottom:1px solid #bae6fd;">
                    <th style="padding:12px 14px;text-align:left;color:#0284c7;
                        font-size:0.72rem;letter-spacing:1px;text-transform:uppercase;">👤 User</th>
                    <th style="padding:12px 14px;text-align:left;color:#0284c7;
                        font-size:0.72rem;letter-spacing:1px;text-transform:uppercase;">🎭 Genre</th>
                    <th style="padding:12px 14px;text-align:left;color:#0284c7;
                        font-size:0.72rem;letter-spacing:1px;text-transform:uppercase;">😊 Mood</th>
                    <th style="padding:12px 14px;text-align:left;color:#0284c7;
                        font-size:0.72rem;letter-spacing:1px;text-transform:uppercase;">📅 Years</th>
                    <th style="padding:12px 14px;text-align:center;color:#0284c7;
                        font-size:0.72rem;letter-spacing:1px;text-transform:uppercase;">🎬 Results</th>
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
        <div style="text-align:center; padding: 48px 0 32px 0;">
            <div style="font-size:3rem;">🛠️</div>
            <h1 style="color:#f8fafc; font-size:1.8rem; font-weight:800; margin:8px 0 4px 0;">
                Admin Access
            </h1>
            <p style="color:#cbd5e1; font-size:0.85rem; letter-spacing:1px;">
                MOVIE RECOMMENDATION SYSTEM
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background:rgba(17,24,39,0.92); border:1px solid #334155;
            border-radius:16px; padding:32px;
            box-shadow:0 4px 16px rgba(0,0,0,0.08);">
        """, unsafe_allow_html=True)

        password = st.text_input(
            "Admin Password",
            type="password",
            placeholder="Enter admin password...",
        )

        if st.button("Login", use_container_width=True, type="primary"):
            if password == st.secrets["ADMIN_TOKEN"]:
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("❌ Incorrect password.")

        st.markdown("</div>", unsafe_allow_html=True)


# ── Admin Dashboard ───────────────────────────────────────────
def admin_dashboard():
    conn = st.connection('postgresql', type='sql')

    # Header
    st.markdown("""
    <div style="padding: 8px 0 24px 0;">
        <h1 style="color:#0f172a; margin:0; font-size:2rem; font-weight:800;">
            🛠️ Admin Dashboard
        </h1>
        <p style="color:#94a3b8; margin:4px 0 0 0; font-size:0.85rem; letter-spacing:1px;">
            MOVIE RECOMMENDATION SYSTEM
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Logout", type="secondary"):
        st.session_state.admin_logged_in = False
        st.rerun()

    st.divider()

    # ── Fetch data ────────────────────────────────────────────
    users_df = conn.query(
        "SELECT user_id, username, email FROM users ORDER BY username ASC", ttl=30)

    searches_df = conn.query("""
        SELECT u.username, ms.genre, ms.mood, ms.min_year, ms.max_year, ms.num_results
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
    c1.metric("👥 Total Users",     total_users)
    c2.metric("🔍 Total Searches",  total_searches)
    c3.metric("📊 Searches / User", avg_per_user)

    st.divider()

    # ── Charts: Genres + Moods ────────────────────────────────
    st.subheader("📊 Search Trends")
    col1, col2 = st.columns(2)

    with col1:
        if not genres_df.empty:
            fig = px.bar(
                genres_df, x="count", y="genre", orientation="h",
                color="count",
                color_continuous_scale=[[0, "#38bdf8"], [1, "#0ea5e9"]],
            )
            fig.update_traces(marker_line_width=0)
            fig = apply_chart_theme(fig, "🎭 Top Genres")
            fig.update_layout(
                coloraxis_showscale=False,
                yaxis=dict(categoryorder="total ascending", gridcolor=GRID_COLOR),
                xaxis_title="", yaxis_title=""
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No genre data yet.")

    with col2:
        if not moods_df.empty:
            fig = px.pie(
                moods_df, values="count", names="mood",
                color_discrete_sequence=[
                    "#38bdf8",
                    "#0ea5e9",
                    "#0284c7",
                    "#0369a1",
                    "#7dd3fc",
                    "#334155"
                ],
                hole=0.45,
            )
            fig.update_traces(
                textfont_color="#0f172a",
                marker=dict(line=dict(color="#f0f4f8", width=2))
            )
            fig = apply_chart_theme(fig, "😊 Mood Distribution")
            fig.update_layout(legend=dict(font=dict(color="#475569")))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No mood data yet.")

    st.divider()

    # ── Chart: Searches per User ──────────────────────────────
    st.subheader("👥 Activity per User")
    if not per_user_df.empty:
        fig = px.bar(
            per_user_df, x="username", y="searches",
            color="searches",
            color_continuous_scale=[[0, "#38bdf8"], [1, "#0ea5e9"]],
        )
        fig.update_traces(marker_line_width=0)
        fig = apply_chart_theme(fig, "")
        fig.update_layout(
            coloraxis_showscale=False,
            xaxis_title="", yaxis_title="Searches",
            xaxis=dict(tickangle=-30, gridcolor=GRID_COLOR),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No user search data yet.")

    st.divider()

    # ── Users table ───────────────────────────────────────────
    st.subheader("👥 Registered Users")

    search_user    = st.text_input("🔎 Filter by username or email", placeholder="type to filter...")
    filtered_users = users_df.copy()
    if search_user:
        filtered_users = filtered_users[
            filtered_users["username"].str.contains(search_user, case=False, na=False) |
            filtered_users["email"].str.contains(search_user, case=False, na=False)
        ]

    st.caption(f"Showing {len(filtered_users)} of {total_users} users")

    if filtered_users.empty:
        st.info("No users match your filter.")
    else:
        st.markdown(users_table_html(filtered_users), unsafe_allow_html=True)

    # ── Delete user ───────────────────────────────────────────
    with st.expander("🗑️ Delete a User"):
        st.warning("⚠️ This will permanently delete the user and all their search history.")
        user_to_delete = st.selectbox("Select user", ["— select —"] + users_df["username"].tolist())

        if user_to_delete != "— select —":
            if st.button(f"Delete '{user_to_delete}'", type="primary"):
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
                        st.success(f"✅ User '{user_to_delete}' deleted successfully.")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("User not found.")
                except Exception as e:
                    st.error(f"Failed to delete user: {e}")

    st.divider()

    # ── Searches table ────────────────────────────────────────
    st.subheader("🔍 Recent Searches")

    search_filter     = st.text_input("🔎 Filter by username", placeholder="type to filter...", key="sf")
    filtered_searches = searches_df.copy()
    if search_filter:
        filtered_searches = filtered_searches[
            filtered_searches["username"].str.contains(search_filter, case=False, na=False)
        ]

    st.caption(f"Showing {len(filtered_searches)} searches")

    if filtered_searches.empty:
        st.info("No searches match your filter.")
    else:
        st.markdown(searches_table_html(filtered_searches), unsafe_allow_html=True)


# ── Router ────────────────────────────────────────────────────
if st.session_state.admin_logged_in:
    admin_dashboard()
else:
    admin_login()