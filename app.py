import streamlit as st
import pandas as pd
import uuid
from sqlalchemy import text
from src.preprocess import load_and_preprocess
from src.recommendation import recommend

# ── Page config ───────────────────────────────────────────────
st.set_page_config(page_title='Movie Recommendation System', layout='centered')

# ── Database connection ───────────────────────────────────────
conn = st.connection('postgresql', type='sql')

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
    st.title("🎬 Movie Recommendation System")
    tab1, tab2 = st.tabs(['Register', 'Login'])

    with tab1:
        new_un   = st.text_input("Username", key='reg_un',   placeholder='geeksformovie')
        new_mail = st.text_input("Email",    key='reg_mail', placeholder='you@gmail.com')
        new_pass = st.text_input("Password", key='reg_pass', type='password', placeholder='something unique')

        if st.button("Register"):
            if not new_un or not new_mail or not new_pass:
                st.warning("Please fill in all fields.")
            else:
                existing = conn.query(
                    "SELECT user_id FROM users WHERE username = :un OR email = :mail",
                    params={"un": new_un, "mail": new_mail},
                    ttl=0
                )
                if not existing.empty:
                    st.error("Username or email already registered.")
                else:
                    user_id = str(uuid.uuid4())
                    with conn.session as s:
                        s.execute(text("""
                            INSERT INTO users (user_id, username, email, password)
                            VALUES (:uid, :un, :mail, :pw)
                        """), {"uid": user_id, "un": new_un, "mail": new_mail, "pw": new_pass})
                        s.commit()
                    st.success("Registered successfully! Please login.")

    with tab2:
        login_un   = st.text_input("Username", key='log_un',   placeholder='geeksformovie')
        login_pass = st.text_input("Password", key='log_pass', type='password', placeholder='your password')

        if st.button("Login"):
            if not login_un or not login_pass:
                st.warning("Please enter both username and password.")
            else:
                result = conn.query(
                    "SELECT user_id, username FROM users WHERE username = :un AND password = :pw",
                    params={"un": login_un, "pw": login_pass},
                    ttl=0
                )
                if result.empty:
                    st.error("Invalid username or password.")
                else:
                    st.session_state.logged_in = True
                    st.session_state.user_id   = result.iloc[0]['user_id']
                    st.session_state.username  = result.iloc[0]['username']
                    st.rerun()


# ── Main app ──────────────────────────────────────────────────
def main_page():
    df = load_data()

    st.title("🎬 Movie Recommendation System")
    st.write(f"Welcome, **{st.session_state.username}**!")

    if st.button("Logout", type="secondary"):
        st.session_state.logged_in = False
        st.session_state.user_id   = None
        st.session_state.username  = None
        st.rerun()

    st.divider()

    # ── Filters ───────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        all_genres = sorted(df['genres'].dropna().unique().tolist())
        all_moods  = sorted(df['mood'].dropna().unique().tolist())
        genre  = st.selectbox("Genre", all_genres)
        mood   = st.selectbox("Mood",  all_moods)

    with col2:
        min_year   = int(df['year'].min())
        max_year   = int(df['year'].max())
        year_range = st.slider("Year Range", min_year, max_year, (1990, 2020))
        number     = st.number_input("Number of Recommendations", min_value=1, max_value=20, value=5)

    # ── Recommend ─────────────────────────────────────────────
    if st.button("Get Recommendations", type="primary"):
        results = recommend(
            df,
            number=int(number),
            genre=genre,
            mood=mood,
            min_year=year_range[0],
            max_year=year_range[1]
        )

        if isinstance(results, str):
            st.warning(results)  # "No movies found..."
        else:
            st.success(f"Top {number} recommendations for you!")
            st.dataframe(results, use_container_width=True)

            # 4. Save search to Database
            try:
                with conn.session as s:
                    s.execute(
                        text("""
                            INSERT INTO movie_searches (
                                user_id, genre, mood, min_year, max_year, num_results
                            )
                            VALUES (:uid, :genre, :mood, :min_year, :max_year, :num_results)
                        """),
                        {
                            "uid":         st.session_state.user_id,
                            "genre":       genre,
                            "mood":        mood,
                            "min_year":    int(year_range[0]),
                            "max_year":    int(year_range[1]),
                            "num_results": int(len(results))
                        }
                    )
                    s.commit()
                st.caption("✅ Search saved to history.")
            except Exception as e:
                st.warning(f"Results displayed, but failed to save to database: {e}")

    st.divider()

    # ── Search History ────────────────────────────────────────
    with st.expander("📋 My Search History"):
        history = conn.query(
            "SELECT genre, mood, min_year, max_year, num_results FROM movie_searches WHERE user_id = :uid ORDER BY id DESC LIMIT 10",
            params={"uid": st.session_state.user_id},
            ttl=0
        )
        if history.empty:
            st.info("No search history yet.")
        else:
            st.dataframe(history, use_container_width=True)


# ── Router ────────────────────────────────────────────────────
if st.session_state.logged_in:
    main_page()
else:
    auth_page()