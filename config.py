"""
Configuration module for Web Séance.
Centralizes paths, API endpoints, rate limiting, and theme constants.
"""

from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ARCHIVE_PAGES_FILE = DATA_DIR / "archive_pages.json"
LINK_EVIDENCE_FILE = DATA_DIR / "link_evidence.json"
ARCHIVE_RESULTS_FILE = DATA_DIR / "archive_results.json"
GEMMA_TEST_FILE = DATA_DIR / "gemma_test_result.json"

# Ollama / Local AI
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_TAGS_ENDPOINT = f"{OLLAMA_BASE_URL}/api/tags"
OLLAMA_GENERATE_ENDPOINT = f"{OLLAMA_BASE_URL}/api/generate"
DEFAULT_MODEL = "gemma3:4b"
OLLAMA_TIMEOUT_SECONDS = 240

# Internet Archive CDX & Replay
CDX_API_URL = "https://web.archive.org/cdx/search/cdx"
WAYBACK_RAW_PREFIX = "https://web.archive.org/web/"
ARCHIVE_USER_AGENT = "WebSeance/1.0 (Digital Archaeology Tool; Hacktoberfest 2026; Responsible Research)"
CDX_TIMEOUT_SECONDS = 15
CAPTURE_TIMEOUT_SECONDS = 20
POLITE_REQUEST_DELAY = 2.0  # seconds between live IA requests

# App Meta
APP_NAME = "Web Séance"
APP_TAGLINE = "AI-Assisted Digital Archaeology for Forgotten Internet Culture"
APP_VERSION = "1.0.0"

# Design System Colors
THEME_BG = "#0c100e"
THEME_PANEL = "#131a17"
THEME_PANEL_ALT = "#18221e"
THEME_BORDER = "#23342d"
THEME_ACCENT = "#00ff88"
THEME_ACCENT_MUTED = "#34d399"
THEME_AMBER = "#fbbf24"
THEME_RED = "#f87171"
THEME_TEXT = "#e2e8f0"
THEME_TEXT_MUTED = "#94a3b8"
