import base64
import streamlit as st


def get_base64_image(image_path: str) -> str:
    """Read an image file and return its base64-encoded string."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def set_background(image_path: str) -> None:
    """
    Set a full-page background image with a dark overlay and
    inject all global UI styles (inputs, buttons, selectboxes, etc.).
    """
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





def get_admin_css() -> str:
    """Returns the Midnight Cinema CSS for the admin dashboard."""

    return """
    <style>

        /* ─────────────────────────────────────────────
           MAIN BACKGROUND
        ───────────────────────────────────────────── */
        .stApp {
            background: linear-gradient(180deg, #020617 0%, #0f172a 100%);
            color: #f8fafc;
        }


        /* ─────────────────────────────────────────────
           HEADINGS + TEXT
        ───────────────────────────────────────────── */
        h1, h2, h3 {
            color: #f8fafc !important;
        }

        p, span, label {
            color: #cbd5e1;
        }

        hr {
            border-color: rgba(148, 163, 184, 0.12) !important;
        }


        /* ─────────────────────────────────────────────
           METRIC CARDS
        ───────────────────────────────────────────── */
        [data-testid="stMetric"] {
            background: rgba(17, 24, 39, 0.95);
            border: 1px solid #334155;
            border-radius: 16px;
            padding: 22px;
            box-shadow: 0 6px 18px rgba(0,0,0,0.25);
        }

        [data-testid="stMetricLabel"] {
            color: #38bdf8 !important;
            font-size: 0.8rem;
            letter-spacing: 1px;
            text-transform: uppercase;
        }

        [data-testid="stMetricValue"] {
            color: #f8fafc !important;
            font-size: 2rem;
            font-weight: 700;
        }


        /* ─────────────────────────────────────────────
           INPUTS
        ───────────────────────────────────────────── */
        [data-testid="stTextInput"] input,
        [data-testid="stSelectbox"] > div > div {
            background: #0f172a !important;
            color: #f8fafc !important;
            border: 1px solid #334155 !important;
            border-radius: 10px !important;
        }


        /* ─────────────────────────────────────────────
           BUTTONS
        ───────────────────────────────────────────── */
        [data-testid="stButton"] > button[kind="primary"] {
            background: linear-gradient(135deg, #0ea5e9, #38bdf8);
            border: none;
            border-radius: 10px;
            color: white;
            font-weight: 600;
            transition: all 0.25s ease;
            box-shadow: 0 4px 14px rgba(14,165,233,0.18);
        }

        [data-testid="stButton"] > button[kind="primary"]:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 18px rgba(56,189,248,0.25);
        }

        [data-testid="stButton"] > button[kind="secondary"] {
            background: #111827;
            border: 1px solid #334155;
            border-radius: 10px;
            color: #cbd5e1;
        }


        /* ─────────────────────────────────────────────
           ALERTS + EXPANDERS
        ───────────────────────────────────────────── */
        [data-testid="stAlert"] {
            background: rgba(30, 41, 59, 0.92) !important;
            border: 1px solid #475569 !important;
            border-radius: 12px !important;
            color: #f8fafc !important;
        }

        [data-testid="stExpander"] {
            background: rgba(17, 24, 39, 0.92) !important;
            border: 1px solid #334155 !important;
            border-radius: 12px !important;
        }


        /* ─────────────────────────────────────────────
           CAPTIONS
        ───────────────────────────────────────────── */
        [data-testid="stCaptionContainer"] {
            color: #94a3b8 !important;
        }


        /* ─────────────────────────────────────────────
           DATAFRAME
        ───────────────────────────────────────────── */
        .stDataFrame {
            border: 1px solid #334155;
            border-radius: 12px;
            overflow: hidden;
        }


        /* ─────────────────────────────────────────────
           SIDEBAR
        ───────────────────────────────────────────── */
        section[data-testid="stSidebar"] {
            background: #020617;
            border-right: 1px solid rgba(148,163,184,0.1);
        }

    </style>
    """


def apply_admin_css() -> None:
    """Injects Midnight Cinema admin CSS into the Streamlit page."""

    import streamlit as st
    st.markdown(get_admin_css(), unsafe_allow_html=True)