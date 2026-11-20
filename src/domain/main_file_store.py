import json
from pathlib import Path

from config import MAIN_FILE_STORE_NAME


class MainFileStore:
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.store_path = project_root / MAIN_FILE_STORE_NAME

    def get_main_file(self) -> str | None:
        if not self.store_path.exists():
            return None
        try:
            data = json.loads(self.store_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
        value = data.get("main_file")
        return value if isinstance(value, str) and value else None

    def set_main_file(self, relative_path: str) -> None:
        data = {}
        if self.store_path.exists():
            try:
                data = json.loads(self.store_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                data = {}
        data["main_file"] = relative_path
        self.store_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
