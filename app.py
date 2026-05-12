import streamlit as st
import pandas as pd
import uuid
from sqlalchemy import text
from src.preprocess import load_and_preprocess
from src.recommendation import recommend

# 1. Page Config
st.set_page_config(page_title="Movie Recommendation System", layout='centered')

# 2. Database Connection
# This uses st.connection to connect to your PostgreSQL instance
conn = st.connection('postgresql', type='sql')

# 3. Session State Initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None

# --- AUTHENTICATION PAGE ---
def auth_page():
    st.title("🎬 Welcome to MovieRec")
    tab1, tab2 = st.tabs(['Login', 'Register'])

    with tab2:
        st.subheader("Create Account")
        new_un = st.text_input("Username", key="reg_un")
        new_addr = st.text_area("Location/Address", key="reg_addr")
        
        if st.button("Register"):
            if new_un:
                u_id = str(uuid.uuid4())
                try:
                    with conn.session as s:
                        s.execute(
                            text("INSERT INTO movie_users(user_id, username, address) VALUES(:id, :un, :ad)"),
                            {"id": u_id, "un": new_un, "ad": new_addr}
                        )
                        s.commit()
                    st.success("Registered! Please switch to the Login tab.")
                except Exception as e:
                    st.error(f"Registration Error: {e}")
            else:
                st.warning("Please enter a username.")

    with tab1:
        st.subheader("Login")
        un = st.text_input("Enter Username", key='log_un')
        if st.button("Login"):
            res = conn.query("SELECT user_id FROM movie_users WHERE username = :un", 
                             params={"un": un}, ttl=0)
            
            if not res.empty:
                st.session_state.logged_in = True
                st.session_state.user_id = res.iloc[0]['user_id']
                st.session_state.username = un
                st.rerun()
            else:
                st.error("Username Not Found. Please register first.")

# --- MAIN RECOMMENDATION PAGE ---

@st.cache_data
def load_data():
    return load_and_preprocess('data/movies_final.csv')

def main_app():
    with st.sidebar:
        st.write(f"Welcome, **{st.session_state.username}**!")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()
        
        st.divider()
        st.header("Filter Preferences")
        
        # Load Data
        df = load_data()
        
        # Extract unique genres for the selectbox
        all_genres = df['genres'].str.split(' ').explode()
        unique_genres = sorted(all_genres.dropna().unique().tolist())
        if "" in unique_genres: unique_genres.remove("")
        
        mood_options = sorted(df['mood'].unique())
        
        # Inputs
        sel_mood = st.selectbox("How is your mood?", mood_options)
        sel_genre = st.selectbox("Choose a Genre", unique_genres)
        num_rec = st.slider("Number of recommendations", 1, 10, 5)
        year_range = st.slider("Year Range", int(df['year'].min()), int(df['year'].max()), (2000, int(df['year'].max())))

    st.title("MOVIE RECOMMENDATION SYSTEM")

    # The Logic starts here
    results = recommend(
        df, 
        number=num_rec, 
        genre=sel_genre, 
        mood=sel_mood, 
        min_year=year_range[0], 
        max_year=year_range[1]
    )

    if isinstance(results, str):
        st.warning(results)
    else:
        # --- AUTOMATIC SAVE LOGIC ---
        try:
            with conn.session as s:
                s.execute(
                    text("""
                        INSERT INTO movie_search_history (
                            user_id, searched_mood, searched_genre, num_results
                        ) 
                        VALUES (:uid, :mood, :genre, :num)
                    """),
                    {
                        "uid": st.session_state.user_id,
                        "mood": sel_mood,
                        "genre": sel_genre,
                        "num": len(results)
                    }
                )
                s.commit()
            # We use a toast (small popup) so it doesn't clutter the UI
            st.toast("Search history updated!", icon="✅")
        except Exception as e:
            # Silent error in console so user experience isn't interrupted
            print(f"Database Error: {e}")

        # Display Results to User
        st.markdown(f"### Top picks for {st.session_state.username}:")
        for index, row in results.iterrows():
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.subheader(f"{row['title']} ({row['year']})")
                    st.caption(f"Genres: {row['genres']} | Mood: {row['mood']}")
                with col2:
                    st.metric("Rating", f"⭐ {row['imdb_rating']}")
                st.divider()

# --- ROUTING ---
if not st.session_state.logged_in:
    auth_page()
else:
    main_app()