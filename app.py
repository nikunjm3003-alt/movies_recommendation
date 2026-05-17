import streamlit as st
import datetime
import pandas as pd
import uuid
import bcrypt
from sqlalchemy import text
from src.preprocess import load_and_preprocess
from src.recommendation import recommend

from src.utils import set_background

# ── Page config ───────────────────────────────────────────────
st.set_page_config(page_title='Movie Recommendation System', layout='centered')

# ── Database connection ───────────────────────────────────────
conn = st.connection('postgresql', type='sql', pool_pre_ping=True)

# ── Session state ─────────────────────────────────────────────
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id   = None
    st.session_state.username  = None

# ── Cache the dataframe ───────────────────────────────────────
@st.cache_resource
def load_data():
    return load_and_preprocess(data_path='data/movies_final.csv')


# ── Auth page ─────────────────────────────────────────────────
def auth_page():
    set_background("assets/cinema.jpg")

    st.title("🎬 Movie Recommendation System")
    tab1, tab2 = st.tabs(['Register', 'Login'])

    # ── Register ──────────────────────────────────────────────
    with tab1:
        new_un   = st.text_input("Username", key='reg_un',   placeholder='geeksformovie')
        new_mail = st.text_input("Email",    key='reg_mail', placeholder='you@gmail.com')
        new_pass = st.text_input("Password", key='reg_pass', type='password', placeholder='something unique')

        if st.button("Register", use_container_width=True):
            if not new_un or not new_mail or not new_pass:
                st.warning("Please fill in all fields.")
            else:
                try:
                    existing = conn.query(
                        "SELECT user_id FROM users WHERE username = :un OR email = :mail",
                        params={"un": new_un, "mail": new_mail},
                        ttl=0
                    )

                    if not existing.empty:
                        st.error("Username or email already registered.")
                    else:
                        user_id = str(uuid.uuid4())
                        hashed_pw = bcrypt.hashpw(
                            new_pass.encode(),
                            bcrypt.gensalt()
                        ).decode()

                        with conn.session as s:
                            s.execute(
                                text("""
                                    INSERT INTO users (user_id, username, email, password)
                                    VALUES (:uid, :un, :mail, :pw)
                                """),
                                {"uid": user_id, "un": new_un, "mail": new_mail, "pw": hashed_pw}
                            )
                            s.commit()
                        st.success("Registered successfully! Please login.")

                except Exception as e:
                    st.error(f"Database error: {e}")

    # ── Login ─────────────────────────────────────────────────
    with tab2:
        login_un   = st.text_input("Username", key='log_un',   placeholder='geeksformovie')
        login_pass = st.text_input("Password", key='log_pass', type='password', placeholder='your password')

        if st.button("Login", use_container_width=True):
            if not login_un or not login_pass:
                st.warning("Please enter both username and password.")
            else:
                try:
                    result = conn.query(
                        "SELECT user_id, username, password FROM users WHERE username = :un",
                        params={"un": login_un},
                        ttl=0
                    )

                    if result.empty:
                        st.error("Invalid username or password.")
                    else:
                        stored_hash = result.iloc[0]["password"]

                        if bcrypt.checkpw(login_pass.encode(), stored_hash.encode()):
                            st.session_state.logged_in = True
                            st.session_state.user_id   = result.iloc[0]["user_id"]
                            st.session_state.username  = result.iloc[0]["username"]
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error("Invalid username or password.")

                except Exception as e:
                    st.error(f"Database connection error: {e}")


# ── Main app ──────────────────────────────────────────────────
def main_page():
    set_background("assets/galaxy.jpg")

    df = load_data()

    st.title("🎬 Movie Recommendation System")
    st.write(f"Welcome, **{st.session_state.username}**! 👋")

    st.markdown(
        '<p class="movie-quote">✨ "Cinema is a mirror by which we often see ourselves." — Martin Scorsese</p>',
        unsafe_allow_html=True
    )

    if st.button("Logout", type="secondary"):
        st.session_state.logged_in = False
        st.session_state.user_id   = None
        st.session_state.username  = None
        st.rerun()

    st.divider()

    # ── Filters ───────────────────────────────────────────────
    st.markdown('<p class="filter-label">😊 Mood</p>', unsafe_allow_html=True)
    all_moods = sorted(set(
        m.strip()
        for moods in df['mood'].dropna()
        for m in moods.split(',')
    ))
    mood = st.selectbox("Mood", all_moods, label_visibility="collapsed")

    st.markdown('<p class="filter-label">🎭 Genre</p>', unsafe_allow_html=True)
    valid_genres = sorted(
        df[df['mood'].str.contains(mood, na=False)]['genres']
        .dropna().str.split()
        .explode().unique().tolist()
    )
    genre = st.selectbox("Genre", valid_genres, label_visibility="collapsed")

    st.markdown('<p class="filter-label">⭐ Number of Recommendations</p>', unsafe_allow_html=True)
    number = st.number_input("Number of Recommendations", min_value=1, max_value=20, value=5, label_visibility="collapsed")

    st.markdown('<p class="filter-label">⭐ IMDb Rating Range</p>', unsafe_allow_html=True)
    rating_range = st.slider(
    "IMDb Rating Range",
    min_value=1.0,
    max_value=10.0,
    value=(6.0, 10.0), # Default to a reasonable range
    step=0.1,
    label_visibility="collapsed"
                    )

    # ── Year Range ────────────────────────────────────────────
    st.markdown('<p class="filter-label">📅 Year Range</p>', unsafe_allow_html=True)

    st.markdown("""
        <style>
        div[data-testid="stHorizontalBlock"] button[kind="secondary"] {
            white-space: nowrap !important;
            font-size: 0.78rem !important;
            padding: 0.35rem 0.5rem !important;
        }
        </style>
    """, unsafe_allow_html=True)

    max_year = int(df['year'].max())
    year_options = {
        "Last Year":    1,
        "Last 5 Yrs":  5,
        "Last 10 Yrs": 10,
        "Last 20 Yrs": 20,
        "Last 30 Yrs": 30,
    }
    if 'year_filter' not in st.session_state:
        st.session_state.year_filter = "Last 10 Yrs"

    yr_cols = st.columns(len(year_options))
    for i, (label, val) in enumerate(year_options.items()):
        with yr_cols[i]:
            is_active = st.session_state.year_filter == label
            if st.button(
                f"{'✅ ' if is_active else ''}{label}",
                key=f"yr_{val}",
                use_container_width=True
            ):
                st.session_state.year_filter = label
                st.rerun()

    selected_yrs = year_options[st.session_state.year_filter]
    min_year     = max_year - selected_yrs
    year_range   = (min_year, max_year)
    st.caption(f"📆 {min_year} – {max_year}")

    # ── Recommend Button ──────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    recommend_clicked = st.button("✨ Get Recommendations", type="primary", use_container_width=True)

    # ── Recommend ─────────────────────────────────────────────
    if recommend_clicked:
        results = recommend(
            df,
            number=int(number),
            genre=genre,
            mood=mood,
            min_year=year_range[0],
            max_year=year_range[1],
            min_rating=rating_range[0],
            max_rating=rating_range[1]
        )

        if isinstance(results, str):
            st.warning(results)
        else:
            st.success(f"🎉 Top {number} recommendations for you!")

            display_cols = [c for c in ['title', 'year', 'genres', 'imdb_rating', 'where_to_watch'] if c in results.columns]
            display_df = results[display_cols].reset_index(drop=True)

            row_items = []
            for _, row in display_df.iterrows():
                stars = "⭐" * int(round(float(row["imdb_rating"]) / 2))
                platforms = str(row.get("where_to_watch", "") or "N/A")
                badges = "".join(
                    f'<span style="background:rgba(108,99,255,0.25);border:1px solid #6c63ff;'
                    f'border-radius:12px;padding:2px 9px;margin:2px;font-size:0.73rem;'
                    f'display:inline-block;white-space:nowrap;">{p.strip()}</span>'
                    for p in platforms.split(",") if p.strip()
                )
                row_items.append(
                    f'<tr style="border-bottom:1px solid rgba(108,99,255,0.18);transition:background 0.2s;"'
                    f' onmouseover="this.style.background=\'rgba(108,99,255,0.1)\'"'
                    f' onmouseout="this.style.background=\'transparent\'">'
                    f'<td style="padding:13px 12px;font-weight:600;color:#fff;">{row["title"]}</td>'
                    f'<td style="padding:13px 12px;color:#c4b5fd;text-align:center;">{int(row["year"])}</td>'
                    f'<td style="padding:13px 12px;color:#94a3b8;font-size:0.82rem;">{row["genres"]}</td>'
                    f'<td style="padding:13px 12px;text-align:center;color:#fbbf24;font-weight:700;">'
                    f'{row["imdb_rating"]}<br><span style="font-size:0.68rem;">{stars}</span></td>'
                    f'<td style="padding:13px 12px;">{badges}</td></tr>'
                )

            table_html = (
                '<div style="overflow-x:auto;border-radius:12px;border:1px solid #6c63ff;margin-top:12px;">'
                '<table style="width:100%;border-collapse:collapse;background:rgba(15,15,35,0.88);">'
                '<thead><tr style="background:linear-gradient(90deg,rgba(108,99,255,0.45),rgba(168,85,247,0.45));'
                'border-bottom:2px solid #6c63ff;">'
                '<th style="padding:12px;text-align:left;color:#c4b5fd;font-size:0.78rem;letter-spacing:1px;text-transform:uppercase;">🎬 Title</th>'
                '<th style="padding:12px;text-align:center;color:#c4b5fd;font-size:0.78rem;letter-spacing:1px;text-transform:uppercase;">📅 Year</th>'
                '<th style="padding:12px;text-align:left;color:#c4b5fd;font-size:0.78rem;letter-spacing:1px;text-transform:uppercase;">🎭 Genres</th>'
                '<th style="padding:12px;text-align:center;color:#c4b5fd;font-size:0.78rem;letter-spacing:1px;text-transform:uppercase;">⭐ Rating</th>'
                '<th style="padding:12px;text-align:left;color:#c4b5fd;font-size:0.78rem;letter-spacing:1px;text-transform:uppercase;">📺 Where to Watch</th>'
                '</tr></thead><tbody>'
                + "".join(row_items)
                + '</tbody></table></div>'
            )
            st.markdown(table_html, unsafe_allow_html=True)

            try:
                with conn.session as s:
                    where_to_watch_val = '; '.join(
                        results['where_to_watch'].dropna().astype(str).tolist()
                    ) if 'where_to_watch' in results.columns else ''

                    s.execute(
                        text("""
                            INSERT INTO movie_searches (
                                user_id, genre, mood, min_year, max_year, num_results, where_to_watch
                            )
                            VALUES (:uid, :genre, :mood, :min_year, :max_year, :num_results, :where_to_watch)
                        """),
                        {
                            "uid":            st.session_state.user_id,
                            "genre":          genre,
                            "mood":           mood,
                            "min_year":       int(year_range[0]),
                            "max_year":       int(year_range[1]),
                            "num_results":    int(len(results)),
                            "where_to_watch": where_to_watch_val
                        }
                    )
                    s.commit()
                st.caption("✅ Search saved to history.")
            except Exception as e:
                st.warning(f"Results displayed, but failed to save to database: {e}")

    st.divider()

    # ── Search History ────────────────────────────────────────
    with st.expander("📋 My Search History"):
        try:
            history = conn.query(
                """
                SELECT genre, mood, min_year, max_year, num_results
                FROM movie_searches
                WHERE user_id = :uid
                ORDER BY id DESC
                LIMIT 10
                """,
                params={"uid": st.session_state.user_id},
                ttl=0
            )
        except Exception as e:
            st.error(f"Failed to load history: {e}")
            history = pd.DataFrame()

        if history.empty:
            st.info("No search history yet.")
        else:
            st.dataframe(history.reset_index(drop=True), use_container_width=True, hide_index=True)


# ── Router ────────────────────────────────────────────────────
if st.session_state.logged_in:
    main_page()
else:
    auth_page()