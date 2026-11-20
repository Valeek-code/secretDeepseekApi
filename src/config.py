import sys
from pathlib import Path

APP_NAME = "LLM Assistant"
APP_VERSION = "0.1.0"


def _base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


PROJECT_ROOT = _base_dir()
RESOURCES_DIR = PROJECT_ROOT / "resources"
OUTPUT_DIR = PROJECT_ROOT / "output"
PROMPT_FILE = OUTPUT_DIR / "llm_prompt.txt"
THEME_FILE = RESOURCES_DIR / "theme.qss"
SETTINGS_FILE = PROJECT_ROOT / ".llm_assistant_settings.json"

MAIN_FILE_STORE_NAME = ".llm_assistant.json"

ACCENT_PRESETS = {
    "Белый": "#ffffff",
    "Синий": "#6cb6ff",
    "Красный": "#ff5a5a",
}
DEFAULT_ACCENT = "#6cb6ff"

SCAN_EXCLUDE_DIRS = {".git", "__pycache__", ".venv", "venv", ".idea", ".vscode"}
SCAN_EXCLUDE_FILES = {".llm_assistant.json", "poetry.lock"}
SCAN_EXCLUDE_BINARY_EXT = {
    ".pyc", ".pyo", ".pyd", ".so", ".dll", ".exe", ".bin",
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".webp",
    ".zip", ".tar", ".gz", ".7z", ".rar", ".pdf", ".woff", ".woff2", ".ttf",
}