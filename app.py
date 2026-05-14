import streamlit as st
import pandas as pd
import uuid
import base64
import bcrypt
from sqlalchemy import text
from src.preprocess import load_and_preprocess
from src.recommendation import recommend

# ── Background ────────────────────────────────────────────────
def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def set_background(image_path):
    img_base64 = get_base64_image(image_path)
    st.markdown(f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/jpg;base64,{img_base64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        [data-testid="stHeader"] {{
            background: transparent;
        }}
        [data-testid="stAppViewContainer"]::before {{
            content: "";
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: rgba(0, 0, 0, 0.65);
            z-index: 0;
        }}

        /* Input fields */
        .stTextInput > div > div > input {{
            background-color: rgba(30, 30, 46, 0.85);
            color: white;
            border: 1px solid #6c63ff;
            border-radius: 8px;
        }}

        /* Buttons */
        .stButton > button {{
            background: linear-gradient(90deg, #6c63ff, #a855f7);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1.5rem;
            font-weight: bold;
            transition: 0.3s;
        }}
        .stButton > button:hover {{
            transform: scale(1.03);
            background: linear-gradient(90deg, #a855f7, #6c63ff);
        }}

        /* Wide recommend button */
        div[data-testid="stButton"].recommend-btn > button {{
            width: 100% !important;
            padding: 0.75rem 2rem;
            font-size: 1.1rem;
            letter-spacing: 0.5px;
        }}

        /* Selectbox */
        .stSelectbox > div > div {{
            background-color: rgba(30, 30, 46, 0.85);
            color: white;
            border: 1px solid #6c63ff;
            border-radius: 8px;
        }}

        /* Tabs */
        .stTabs [data-baseweb="tab"] {{
            color: #a855f7;
            font-weight: bold;
        }}
        .stTabs [aria-selected="true"] {{
            border-bottom: 2px solid #6c63ff;
            color: white;
        }}

        /* Dataframe */
        .stDataFrame {{
            border: 1px solid #6c63ff;
            border-radius: 8px;
        }}

        /* Expander */
        .streamlit-expanderHeader {{
            background-color: rgba(30, 30, 46, 0.85);
            color: white;
            border-radius: 8px;
        }}

        /* Divider */
        hr {{
            border-color: #6c63ff;
        }}

        /* General text color */
        html, body, [class*="css"] {{
            color: white;
        }}

        /* Filter label style */
        .filter-label {{
            font-size: 0.85rem;
            font-weight: 600;
            color: #c4b5fd;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }}

        /* Movie quote style */
        .movie-quote {{
            font-style: italic;
            color: #c4b5fd;
            font-size: 0.9rem;
            margin-top: -8px;
            margin-bottom: 8px;
            opacity: 0.85;
        }}
        </style>
    """, unsafe_allow_html=True)

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
    # Cinema background for login page
    set_background("assets/cinema.jpg")

    st.title("🎬 Movie Recommendation System")
    tab1, tab2 = st.tabs(['Register', 'Login'])

    with tab1:
        new_un   = st.text_input("Username", key='reg_un',   placeholder='geeksformovie')
        new_mail = st.text_input("Email",    key='reg_mail', placeholder='you@gmail.com')
        new_pass = st.text_input("Password", key='reg_pass', type='password', placeholder='something unique')

        if st.button("Register", use_container_width=True):
            if not new_un or not new_mail or not new_pass:
                st.warning("Please fill in all fields.")
            else:
                try:
                    with conn.session as s:
                        existing = pd.read_sql(
                            text("""
                                SELECT user_id
                                FROM users
                                WHERE username = :un
                                OR email = :mail
                            """),
                            s.connection(),
                            params={
                                "un": new_un,
                                "mail": new_mail
                            }
                        )

                        if not existing.empty:
                            st.error("Username or email already registered.")
                        else:
                            user_id = str(uuid.uuid4())

                            hashed_pw = bcrypt.hashpw(
                                new_pass.encode(),
                                bcrypt.gensalt()
                            ).decode()

                            s.execute(
                                text("""
                                    INSERT INTO users (
                                        user_id,
                                        username,
                                        email,
                                        password
                                    )
                                    VALUES (
                                        :uid,
                                        :un,
                                        :mail,
                                        :pw
                                    )
                                """),
                                {
                                    "uid": user_id,
                                    "un": new_un,
                                    "mail": new_mail,
                                    "pw": hashed_pw
                                }
                            )

                            s.commit()
                            st.success("Registered successfully! Please login.")

                except Exception as e:
                    st.error(f"Database error: {e}")

    with tab2:
        login_un   = st.text_input("Username", key='log_un',   placeholder='geeksformovie')
        login_pass = st.text_input("Password", key='log_pass', type='password', placeholder='your password')

        if st.button("Login", use_container_width=True):
            if not login_un or not login_pass:
                st.warning("Please enter both username and password.")

            else:
                try:
                    with conn.session as s:
                        result = pd.read_sql(
                            text("""
                                SELECT user_id, username, password
                                FROM users
                                WHERE username = :un
                            """),
                            s.connection(),
                            params={
                                "un": login_un
                            }
                        )

                    if result.empty:
                        st.error("Invalid username or password.")

                    else:
                        stored_hash = result.iloc[0]["password"]

                        if bcrypt.checkpw(
                            login_pass.encode(),
                            stored_hash.encode()
                        ):
                            st.session_state.logged_in = True
                            st.session_state.user_id = result.iloc[0]["user_id"]
                            st.session_state.username = result.iloc[0]["username"]

                            st.success("Login successful!")
                            st.rerun()

                        else:
                            st.error("Invalid username or password.")

                except Exception as e:
                    st.error(f"Database connection error: {e}")


# ── Main app ──────────────────────────────────────────────────
def main_page():
    # Space/galaxy background for main page
    set_background("assets/galaxy.jpg")

    df = load_data()

    st.title("🎬 Movie Recommendation System")
    st.write(f"Welcome, **{st.session_state.username}**! 👋")

    # Static movie quote below username
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
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<p class="filter-label">😊 Mood</p>', unsafe_allow_html=True)
        all_moods = sorted(df['mood'].dropna().unique().tolist())
        mood = st.selectbox("Mood", all_moods, label_visibility="collapsed")

        st.markdown('<p class="filter-label">🎭 Genre</p>', unsafe_allow_html=True)
        valid_genres = sorted(
            df[df['mood'] == mood]['genres']
            .dropna().str.split()
            .explode().unique().tolist()
        )
        genre = st.selectbox("Genre", valid_genres, label_visibility="collapsed")

    with col2:
        st.markdown('<p class="filter-label">📅 Year Range</p>', unsafe_allow_html=True)
        min_year   = int(df['year'].min())
        max_year   = int(df['year'].max())
        year_range = st.slider("Year Range", min_year, max_year, (1990, 2020), label_visibility="collapsed")

        st.markdown('<p class="filter-label">⭐ Number of Recommendations</p>', unsafe_allow_html=True)
        number = st.number_input("Number of Recommendations", min_value=1, max_value=20, value=5, label_visibility="collapsed")

    # ── Wide Recommend Button ─────────────────────────────────
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
            max_year=year_range[1]
        )

        if isinstance(results, str):
            st.warning(results)
        else:
            st.success(f"🎉 Top {number} recommendations for you!")
            st.dataframe(results, use_container_width=True)

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
        try:
            with conn.session as s:
                history = pd.read_sql(
                    text("""
                        SELECT genre,
                               mood,
                               min_year,
                               max_year,
                               num_results
                        FROM movie_searches
                        WHERE user_id = :uid
                        ORDER BY id DESC
                        LIMIT 10
                    """),
                    s.connection(),
                    params={
                        "uid": st.session_state.user_id
                    }
                )

        except Exception as e:
            st.error(f"Failed to load history: {e}")
            history = pd.DataFrame()
        if history.empty:
            st.info("No search history yet.")
        else:
            st.dataframe(history, use_container_width=True)


# ── Router ────────────────────────────────────────────────────
if st.session_state.logged_in:
    main_page()
else:
    auth_page()