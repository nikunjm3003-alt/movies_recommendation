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
    """Returns the Professional Corporate Slate Blue CSS string for the admin dashboard."""
    return """
    <style>
        /* Main background standard assignment */
        .stApp { background-color: #0b0f19; }
 
        /* ── Metric cards ── */
        [data-testid="stMetric"] {
            background: #1e293b;
            border: 1px solid #334155;
            padding: 16px;
            border-radius: 10px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        [data-testid="stMetricLabel"] {
            color: #94a3b8 !important;
            font-size: 0.85rem;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }
        [data-testid="stMetricValue"] {
            color: #38bdf8 !important;
            font-size: 2rem;
            font-weight: 700;
        }
 
        /* ── Headings ── */
        h1, h2, h3, h4, h5, h6, p, label, .stMarkdown { 
            color: #f1f5f9 !important; 
        }
        hr { 
            border-color: rgba(51, 65, 85, 0.5) !important; 
        }
 
        /* ── Targeted Inputs Fix ── */
        [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
        [data-testid="stTextInput"] div[data-baseweb="input"] {
            color: #f1f5f9 !important;
            background-color: #1e293b !important;
            border-color: #334155 !important;
            border-radius: 6px !important;
        }

        /* Ensure input text remains cleanly readable */
        [data-testid="stTextInput"] input {
            color: #f1f5f9 !important;
        }
 
        /* ── Primary button (Enterprise Sky Blue Gradient) ── */
        [data-testid="stButton"] > button[kind="primary"] {
            background: linear-gradient(135deg, #0284c7, #0369a1) !important;
            border: none !important;
            border-radius: 6px !important;
            color: #ffffff !important;
            font-weight: 600 !important;
            box-shadow: 0 2px 4px rgba(2, 132, 199, 0.2);
        }
 
        /* ── Secondary button (Subtle Cool Gray Frame) ── */
        [data-testid="stButton"] > button[kind="secondary"] {
            background: transparent !important;
            border: 1px solid #475569 !important;
            border-radius: 6px !important;
            color: #cbd5e1 !important;
            font-weight: 500;
        }
        [data-testid="stButton"] > button[kind="secondary"]:hover {
            border-color: #94a3b8 !important;
            color: #ffffff !important;
            background: rgba(255, 255, 255, 0.02) !important;
        }
 
        /* ── Caption ── */
        [data-testid="stCaptionContainer"] { color: #64748b !important; }
 
        /* ── Warning box ── */
        [data-testid="stAlert"] {
            background: rgba(30, 41, 59, 0.7) !important;
            border: 1px solid #334155 !important;
            border-radius: 8px !important;
        }
 
        /* ── Expander ── */
        [data-testid="stExpander"] {
            background: #131c2e !important;
            border: 1px solid #1e293b !important;
            border-radius: 8px !important;
        }
    </style>
    """
 
 
def apply_admin_css() -> None:
    """Injects professional administrative dark theme CSS into the Streamlit page."""
    import streamlit as st
    st.markdown(get_admin_css(), unsafe_allow_html=True)