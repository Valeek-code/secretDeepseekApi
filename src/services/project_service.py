from pathlib import Path

from util.paths import is_excluded_dir, is_excluded_file


def list_children(directory: Path) -> list[Path]:
    result: list[Path] = []
    try:
        entries = sorted(directory.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    except OSError:
        return result
    for entry in entries:
        if entry.is_dir():
            if is_excluded_dir(entry):
                continue
        else:
            if is_excluded_file(entry):
                continue
        result.append(entry)
    return result


def build_project_content(project_root: Path) -> str:
    parts: list[str] = []
    _walk(project_root, project_root, parts)
    return "\n".join(parts)


def _walk(root: Path, current: Path, parts: list[str]) -> None:
    for entry in list_children(current):
        if entry.is_dir():
            _walk(root, entry, parts)
            continue
        try:
            text = entry.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        try:
            rel = entry.resolve().relative_to(root.resolve())
        except ValueError:
            rel = entry
        rel_str = str(rel).replace("\\", "/")
        parts.append(f"=== FILE: {rel_str} ===")
        parts.append(text)
        parts.append("=== END ===")
        parts.append("")


def read_text_file(path: Path) -> tuple[bool, str]:
    try:
        return True, path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False, "Файл не в UTF-8 (бинарь или другая кодировка) — просмотр недоступен."
    except OSError as exc:
        return False, f"Не удалось прочитать файл: {exc}"