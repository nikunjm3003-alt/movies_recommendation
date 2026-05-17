# 🎬 Movie Recommendation System

A mood-based movie recommendation web app built with **Python**, **Streamlit**, and **PostgreSQL** — featuring user authentication, search history logging, and an admin dashboard.

---

## 🔗 Live Demo

| | Link |
|---|---|
| 🎬 **Main App** | [moviesrecommendation-ezv8gs7emymt2nbdkk5lcu.streamlit.app](https://moviesrecommendation-ezv8gs7emymt2nbdkk5lcu.streamlit.app/) |
| 🛠️ **Admin Dashboard** | [moviesrecommendation-rrwg7q4rszzoxdfjdpcyl6.streamlit.app](https://moviesrecommendation-rrwg7q4rszzoxdfjdpcyl6.streamlit.app/) |

---

## 📸 Overview

Users log in, pick a mood and genre, and get personalized movie recommendations ranked by IMDb rating. Every search is saved to a database, and an admin dashboard provides live analytics across all users.

---

## 🚀 Features

### User App
- 🔐 Register & Login with bcrypt-hashed passwords
- 😊 Filter movies by **mood**, **genre**, and **year range**
- ⭐ Results ranked by IMDb rating with platform badges
- 📋 Personal search history per user
- 🎨 Cinematic UI with custom background images

### Admin Dashboard
- 🔒 Password-protected login
- 📊 Live charts: top genres, mood distribution, activity per user (Plotly)
- 👥 Searchable registered users table with avatar initials
- 🔍 Recent searches table with genre & mood badges
- 🗑️ Delete user (removes user + all search history)

---

## 🗂️ Project Structure

```
MOVIE_RECOMMENDATION_SYSTEM/
│
├── .streamlit/
│   └── secrets.toml              # DB URL + admin token (never commit this)
│
├── assets/
│   ├── cinema.jpg                # Background for auth/login page
│   └── galaxy.jpg                # Background for main app
│
├── data/
│   ├── movies.csv                # Raw MovieLens movies dataset
│   ├── ratings.csv               # Raw MovieLens ratings dataset
│   ├── movies_updated.csv        # Intermediate dataset with IMDb ratings & platforms
│   └── movies_final.csv          # Final processed dataset used by the app
│
├── notebook/
│   └── movie_system.ipynb        # EDA, data processing, and mood mapping
│
├── src/
│   ├── __init__.py
│   ├── deployment.py             # Local test runner for recommendation logic
│   ├── preprocess.py             # CSV loader and column validator
│   ├── recommendation.py         # Filtering and ranking logic
│   └── utils.py                  # Background setter + admin CSS injector
│
├── venv/                         # Virtual environment (not committed)
├── .gitignore
├── admin.py                      # Admin dashboard (Plotly charts + styled tables)
├── app.py                        # Main Streamlit app (auth + recommendations)
└── requirements.txt
```

---

## 🧠 How It Works

### Data Pipeline (Notebook)
1. Load `movies.csv` and `ratings.csv` from MovieLens
2. Merge on `movieId`, drop `userId` and `timestamp`
3. Filter to movies from **1980 onwards**, remove entries with no genre
4. Replace `|` genre separator with spaces for TF-IDF vectorization
5. Map genres → moods using a custom `genre_mood` dictionary:

| Genre | Mood |
|---|---|
| Action, Adventure | Excitement |
| Animation, Children | Joy |
| Comedy | Happy |
| Romance | Romantic |
| Horror, Thriller | Thrilled |
| Mystery, Crime | Curious |
| Sci-Fi, Fantasy, IMAX | Wonder |
| Documentary | Inspired |
| War, History | Reflective |
| Musical, Music | Cheerful |
| Western | Adventurous |
| Film-Noir | Melancholic |

6. Export final dataset as `data/movies_final.csv`

### Recommendation Logic (`src/recommendation.py`)
Filters the dataframe by mood, genre (partial match), and year range, then sorts by `imdb_rating` descending and returns the top N results.

### Database (`PostgreSQL`)
Two tables:

**`users`**
| Column | Type |
|---|---|
| user_id | UUID (PK) |
| username | VARCHAR |
| email | VARCHAR |
| password | VARCHAR (bcrypt hash) |

**`movie_searches`**
| Column | Type |
|---|---|
| id | SERIAL (PK) |
| user_id | UUID (FK → users) |
| genre | VARCHAR |
| mood | VARCHAR |
| min_year | INT |
| max_year | INT |
| num_results | INT |
| where_to_watch | TEXT |

---

## ⚙️ Local Setup

### 1. Clone the repo
```bash
git clone https://github.com/nikunjm3003-alt/movie-recommendation-system.git
cd movie-recommendation-system
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure secrets
Create `.streamlit/secrets.toml`:
```toml
ADMIN_TOKEN = "your_secret_admin_password"

[connections.postgresql]
url = "postgresql://user:password@host:port/dbname"
```

> ⚠️ This file is already in `.gitignore` — never remove it from there.

### 5. Set up the database
Run these SQL statements in your PostgreSQL instance:
```sql
CREATE TABLE users (
    user_id  TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email    TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE movie_searches (
    id             SERIAL PRIMARY KEY,
    user_id        TEXT REFERENCES users(user_id),
    genre          TEXT,
    mood           TEXT,
    min_year       INT,
    max_year       INT,
    num_results    INT,
    where_to_watch TEXT
);
```

### 6. Run the app
```bash
streamlit run app.py
```

### 7. Test recommendations locally
```bash
python src/deployment.py
```

---

## 📦 Requirements

```
streamlit
pandas
numpy
scikit-learn
bcrypt
sqlalchemy
plotly
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | Python 3 |
| Database | PostgreSQL (Supabase / Neon) |
| Auth | bcrypt password hashing |
| Charts | Plotly Express |
| ML / Data | pandas, scikit-learn (TF-IDF) |
| Deployment | Streamlit Cloud |

---

## 👤 Author

**Nikunj Mishra**
Specialization: Machine Learning & Data Analysis

- GitHub: [github.com/nikunjm3003-alt](https://github.com/nikunjm3003-alt)
- LinkedIn: [linkedin.com/in/nikunj-mishra-68b7052bb](https://linkedin.com/in/nikunj-mishra-68b7052bb/)

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
