"""
Theme and custom styling for Web Séance.
Implements the 'Digital Séance' aesthetic: deep charcoal backgrounds, phosphor-green accents,
subtle glow effects, monospace typography for technical artifacts, and clean responsive layout.
"""

import streamlit as st


def apply_theme():
    """Injects custom CSS styling for the digital archaeology séance atmosphere."""
    st.markdown(
        """
        <style>
        /* Import Google Fonts for vintage terminal and scholarly aesthetic */
        @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,600;1,6..72,400&family=Inter:wght@400;500;600;700&display=swap');

        /* Root background and variables */
        :root {
            --bg-color: #0b0f0d;
            --panel-bg: #121815;
            --panel-border: #1e2c24;
            --accent-green: #00ff88;
            --accent-green-dim: #10b981;
            --accent-cyan: #38bdf8;
            --accent-amber: #f59e0b;
            --text-main: #e2e8f0;
            --text-muted: #94a3b8;
            --glow: 0 0 15px rgba(0, 255, 136, 0.15);
        }

        /* Global App Background */
        .stApp {
            background-color: var(--bg-color);
            color: var(--text-main);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Typography */
        h1, h2, h3, h4 {
            color: #f1f5f9 !important;
            font-family: 'Newsreader', Georgia, serif;
            letter-spacing: -0.02em;
        }

        .seance-title {
            font-family: 'Newsreader', serif;
            font-size: 2.8rem;
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 0.2rem;
            text-shadow: 0 0 20px rgba(0, 255, 136, 0.25);
        }

        .seance-tagline {
            font-family: 'Fira Code', monospace;
            font-size: 0.95rem;
            color: var(--accent-green);
            margin-bottom: 1.5rem;
            letter-spacing: 0.05em;
        }

        /* Monospace technical callouts */
        code, .mono-text {
            font-family: 'Fira Code', monospace !important;
            color: var(--accent-green-dim);
            background: #16201b;
            padding: 0.15rem 0.4rem;
            border-radius: 4px;
            font-size: 0.88em;
        }

        /* Evidence Cards */
        .seance-card {
            background: var(--panel-bg);
            border: 1px solid var(--panel-border);
            border-radius: 8px;
            padding: 1.25rem;
            margin-bottom: 1rem;
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }

        .seance-card:hover {
            border-color: #2e4439;
            box-shadow: var(--glow);
        }

        /* Evidence Badge */
        .evidence-badge {
            display: inline-block;
            font-family: 'Fira Code', monospace;
            font-size: 0.75rem;
            font-weight: 600;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .badge-verified {
            background: rgba(0, 255, 136, 0.12);
            color: var(--accent-green);
            border: 1px solid rgba(0, 255, 136, 0.3);
        }

        .badge-external {
            background: rgba(56, 189, 248, 0.12);
            color: var(--accent-cyan);
            border: 1px solid rgba(56, 189, 248, 0.3);
        }

        .badge-samesite {
            background: rgba(16, 185, 129, 0.12);
            color: #6ee7b7;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }

        .badge-ai {
            background: rgba(245, 158, 11, 0.12);
            color: var(--accent-amber);
            border: 1px solid rgba(245, 158, 11, 0.3);
        }

        /* Disclaimer Banner */
        .disclaimer-banner {
            background: #141b18;
            border-left: 3px solid var(--accent-green);
            padding: 0.85rem 1.2rem;
            border-radius: 0 6px 6px 0;
            margin: 1rem 0;
            font-size: 0.88rem;
            color: #cbd5e1;
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #080c0a;
            border-right: 1px solid var(--panel-border);
        }

        /* Streamlit metrics styling */
        div[data-testid="stMetricValue"] {
            color: var(--accent-green) !important;
            font-family: 'Fira Code', monospace !important;
            font-size: 1.8rem !important;
        }
        
        div[data-testid="stMetricLabel"] {
            color: var(--text-muted) !important;
            font-size: 0.82rem !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        /* Streamlit Buttons */
        .stButton > button {
            background: #16221c;
            color: #ffffff;
            border: 1px solid #283d32;
            border-radius: 6px;
            font-family: 'Inter', sans-serif;
            font-weight: 500;
            transition: all 0.2s ease;
        }

        .stButton > button:hover {
            background: #1c2e26;
            border-color: var(--accent-green);
            color: var(--accent-green);
            box-shadow: 0 0 10px rgba(0, 255, 136, 0.2);
        }

        .stButton > button[kind="primary"] {
            background: #00ff88;
            color: #06110a;
            font-weight: 600;
            border: none;
        }

        .stButton > button[kind="primary"]:hover {
            background: #22c55e;
            box-shadow: 0 0 15px rgba(0, 255, 136, 0.4);
        }

        /* Streamlit Tabs */
        .stTabs [data-baseweb="tab-list"] {
            background-color: #0e1411;
            border-radius: 8px;
            padding: 4px;
            gap: 4px;
            border: 1px solid #1a251f;
        }

        .stTabs [data-baseweb="tab"] {
            color: #94a3b8;
            border-radius: 6px;
            padding: 8px 16px;
            font-family: 'Inter', sans-serif;
            font-size: 0.9rem;
        }

        .stTabs [aria-selected="true"] {
            background-color: #17231d !important;
            color: var(--accent-green) !important;
            font-weight: 600;
            box-shadow: 0 0 10px rgba(0, 255, 136, 0.1);
        }

        /* Status Pill */
        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 0.78rem;
            font-family: 'Fira Code', monospace;
            padding: 2px 8px;
            border-radius: 12px;
            margin-bottom: 4px;
        }
        .status-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
        }
        .status-active .status-dot {
            background-color: #00ff88;
            box-shadow: 0 0 6px #00ff88;
        }
        .status-active {
            background: rgba(0, 255, 136, 0.1);
            color: #00ff88;
            border: 1px solid rgba(0, 255, 136, 0.25);
        }
        .status-inactive .status-dot {
            background-color: #f87171;
        }
        .status-inactive {
            background: rgba(248, 113, 113, 0.1);
            color: #f87171;
            border: 1px solid rgba(248, 113, 113, 0.25);
        }
        </style>
        """,
        unsafe_allow_html=True
    )
