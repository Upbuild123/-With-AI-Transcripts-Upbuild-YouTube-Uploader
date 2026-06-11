import streamlit as st


def inject_custom_css() -> None:
    """Inject custom CSS to align the app's look with Upbuild's brand."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        html, body, .stApp {
            font-family: 'Inter', sans-serif;
        }

        h1 {
            font-family: 'Inter', sans-serif;
            font-size: 2.25rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            padding-bottom: 0.75rem;
            border-bottom: 2px solid #5E328C;
            margin-bottom: 1.5rem;
        }

        section.main > div.block-container {
            gap: 1.5rem;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 12px;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
            background-color: #FFFFFF;
            padding: 1.5rem;
            margin-bottom: 1.25rem;
        }

        button {
            border-radius: 8px !important;
        }

        button[kind="primary"] {
            background-color: #5E328C !important;
            color: #FFFFFF !important;
            border: none !important;
        }

        button[kind="primary"]:hover {
            background-color: #4D2A75 !important;
        }

        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input,
        div[data-testid="stTextArea"] textarea,
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
            border-radius: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
