from pathlib import Path

from PySide6.QtWidgets import QApplication

from config import THEME_FILE

ACCENT_PLACEHOLDER = "__ACCENT__"


def apply_theme(app: QApplication, accent: str) -> None:
    if not THEME_FILE.exists():
        return
    qss = Path(THEME_FILE).read_text(encoding="utf-8")
    qss = qss.replace(ACCENT_PLACEHOLDER, accent)
    app.setStyleSheet(qss)
