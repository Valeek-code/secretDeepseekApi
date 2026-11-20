from pathlib import Path

from PySide6.QtGui import QGuiApplication

from config import PROMPT_FILE


def copy_prompt() -> tuple[bool, str]:
    if not PROMPT_FILE.exists():
        return False, f"Файл промпта не найден: {PROMPT_FILE}"
    try:
        text = PROMPT_FILE.read_text(encoding="utf-8")
    except OSError as exc:
        return False, f"Не удалось прочитать промпт: {exc}"
    QGuiApplication.clipboard().setText(text)
    return True, f"Промпт скопирован ({len(text)} символов)"


def copy_project_content(project_root: Path) -> tuple[bool, str]:
    from services.project_service import build_project_content

    if not project_root.exists():
        return False, "Проект не открыт"
    content = build_project_content(project_root)
    QGuiApplication.clipboard().setText(content)
    return True, f"Содержание проекта скопировано ({len(content)} символов)"
