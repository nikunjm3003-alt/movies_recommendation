import streamlit as st
import pandas as pd

# ── Page config ───────────────────────────────────────────────
st.set_page_config(page_title="Admin Dashboard", layout="wide")

# ── Auth via secret token ─────────────────────────────────────
token = st.query_params.get("admin_token", "")

if token != st.secrets["ADMIN_TOKEN"]:
    st.error("🚫 Access Denied. Invalid or missing admin token.")
    st.stop()

# ── Database connection ───────────────────────────────────────
conn = st.connection('postgresql', type='sql')

# ── Header ────────────────────────────────────────────────────
st.title("🛠️ Admin Dashboard")
st.caption("Movie Recommendation System — Admin View")
st.divider()

# ── Helper: fetch data ────────────────────────────────────────
def get_stats():
    return conn.query("SELECT COUNT(*) AS total_users FROM users", ttl=30).iloc[0]["total_users"]

def get_search_count():
    return conn.query("SELECT COUNT(*) AS total_searches FROM movie_searches", ttl=30).iloc[0]["total_searches"]

def get_all_users():
    return conn.query(
        "SELECT user_id, username, email FROM users ORDER BY username ASC",
        ttl=30
    )

def get_all_searches():
    return conn.query(
        """
        SELECT u.username, ms.genre, ms.mood, ms.min_year, ms.max_year, ms.num_results
        FROM movie_searches ms
        JOIN users u ON ms.user_id = u.user_id
        ORDER BY ms.id DESC
        LIMIT 100
        """,
        ttl=30
    )

def get_top_genres():
    return conn.query(
        """
        SELECT genre, COUNT(*) AS count
        FROM movie_searches
        GROUP BY genre
        ORDER BY count DESC
        LIMIT 10
        """,
        ttl=30
    )

def get_top_moods():
    return conn.query(
        """
        SELECT mood, COUNT(*) AS count
        FROM movie_searches
        GROUP BY mood
        ORDER BY count DESC
        LIMIT 10
        """,
        ttl=30
    )

# ── Stats Row ─────────────────────────────────────────────────
total_users   = get_stats()
total_searches = get_search_count()

col1, col2, col3 = st.columns(3)
col1.metric("👥 Total Users",    total_users)
col2.metric("🔍 Total Searches", total_searches)
col3.metric("🎬 Searches / User",
            round(total_searches / total_users, 1) if total_users else 0)

st.divider()

# ── All Registered Users ──────────────────────────────────────
st.subheader("👥 Registered Users")

users_df = get_all_users()

if users_df.empty:
    st.info("No users registered yet.")
else:
    st.caption(f"Showing {len(users_df)} users")

    search_user = st.text_input("🔎 Search by username or email", placeholder="type to filter...")
    if search_user:
        users_df = users_df[
            users_df["username"].str.contains(search_user, case=False, na=False) |
            users_df["email"].str.contains(search_user, case=False, na=False)
        ]

    st.dataframe(
        users_df[["username", "email"]].reset_index(drop=True),
        use_container_width=True,
        hide_index=True
    )

    # ── Delete User ───────────────────────────────────────────
    st.markdown("#### 🗑️ Delete a User")
    st.warning("⚠️ This will permanently delete the user and all their search history.")

    usernames = users_df["username"].tolist()
    user_to_delete = st.selectbox("Select user to delete", ["— select —"] + usernames)

    if user_to_delete != "— select —":
        if st.button(f"Delete '{user_to_delete}'", type="primary"):
            try:
                from sqlalchemy import text
                uid_row = conn.query(
                    "SELECT user_id FROM users WHERE username = :un",
                    params={"un": user_to_delete},
                    ttl=0
                )
                if not uid_row.empty:
                    uid = uid_row.iloc[0]["user_id"]
                    with conn.session as s:
                        s.execute(text("DELETE FROM movie_searches WHERE user_id = :uid"), {"uid": uid})
                        s.execute(text("DELETE FROM users WHERE user_id = :uid"), {"uid": uid})
                        s.commit()
                    st.success(f"✅ User '{user_to_delete}' deleted successfully.")
                    st.rerun()
                else:
                    st.error("User not found.")
            except Exception as e:
                st.error(f"Failed to delete user: {e}")

st.divider()

# ── All Movie Searches ────────────────────────────────────────
st.subheader("🔍 All Movie Searches (last 100)")

searches_df = get_all_searches()

if searches_df.empty:
    st.info("No searches yet.")
else:
    st.caption(f"Showing {len(searches_df)} recent searches")

    search_filter = st.text_input("🔎 Filter by username", placeholder="type to filter...", key="search_filter")
    if search_filter:
        searches_df = searches_df[
            searches_df["username"].str.contains(search_filter, case=False, na=False)
        ]

    st.dataframe(
        searches_df.reset_index(drop=True),
        use_container_width=True,
        hide_index=True
    )

st.divider()

# ── Top Genres & Moods ────────────────────────────────────────
st.subheader("📊 Most Popular Genres & Moods")

gcol, mcol = st.columns(2)

with gcol:
    st.markdown("**🎭 Top Genres**")
    genres_df = get_top_genres()
    if genres_df.empty:
        st.info("No data yet.")
    else:
        st.dataframe(genres_df.reset_index(drop=True), use_container_width=True, hide_index=True)

with mcol:
    st.markdown("**😊 Top Moods**")
    moods_df = get_top_moods()
    if moods_df.empty:
        st.info("No data yet.")
    else:
        st.dataframe(moods_df.reset_index(drop=True), use_container_width=True, hide_index=True)