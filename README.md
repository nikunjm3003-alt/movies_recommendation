# 🎬 Movie Recommendation System

**APP**
[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://moviesrecommendation-gkngo4aeu8pbrpcqmobmfk.streamlit.app/)

A modern and interactive **Movie Recommendation Web App** built using **Python, Streamlit, PostgreSQL, and Pandas**.  
The application recommends movies based on:

- 🎭 Genre
- 😊 Mood
- 📅 Release Year Range
- ⭐ IMDb Ratings

It also includes:

- 🔐 User Authentication
- 🗂 Search History
- 🌌 Cinematic UI Design

---

# 🚀 Features

## 🔐 Authentication System
- User Registration
- Secure Login System
- Password hashing using `bcrypt`
- Session management with Streamlit

---

## 🎬 Movie Recommendation Engine

Filter movies based on:
- Mood
- Genre
- Release year
- Number of recommendations

Recommendations are sorted using IMDb ratings.

---

## 🗃 Search History

Every recommendation search is stored in PostgreSQL and displayed inside the user dashboard.

---

## 🎨 Modern UI

- Neon cinema-inspired design
- Glassmorphism effects
- Responsive layout
- Custom CSS styling
- Dynamic background images

---

# 🛠 Tech Stack

| Technology | Usage |
|---|---|
| Python | Backend Logic |
| Streamlit | Web Application |
| Pandas | Data Processing |
| PostgreSQL | Database |
| SQLAlchemy | Database Connection |
| bcrypt | Password Hashing |
| CSS | UI Styling |

---

# 📂 Project Structure

```bash
movie_recommendation_system/
│
├── app.py
├── requirements.txt
├── deployment.py
│
├── data/
│   └── movies_final.csv
│
├── assets/
│   ├── cinema.jpg
│   └── galaxy.jpg
│
├── src/
│   ├── preprocess.py
│   └── recommendation.py
│
└── README.md
```



# 🧠 Recommendation Logic

The recommendation engine filters movies based on:
- mood
- genre
- release year range

Then sorts them by IMDb rating.

---

# 📊 Data Preprocessing

Movie dataset preprocessing is handled in:
- `preprocess.py`
- `movie_system.ipynb`

The preprocessing pipeline:
- loads CSV data
- validates required columns
- prepares recommendation-ready data

---

# 🔐 Security Improvements

This project uses:
- `bcrypt` password hashing
- parameterized SQL queries
- SQLAlchemy session handling

---

# 🌟 Future Improvements

- 🎥 Poster integration using TMDB API
- 🤖 ML-based recommendation engine
- ❤️ Favorite movies feature
- 📈 User analytics dashboard
- 🌙 Light/Dark mode toggle
- 🎭 Multi-genre recommendations

---

# 📦 Requirements

```txt
pandas
numpy
matplotlib
streamlit
sqlalchemy
psycopg2-binary
bcrypt
```

---

# 👨‍💻 Author

Developed by **Nikunj Mishra**

---

# ⭐ If You Like This Project

Give it a ⭐ on GitHub and share your feedback!
