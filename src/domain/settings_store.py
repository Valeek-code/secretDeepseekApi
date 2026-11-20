import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from config import SETTINGS_FILE

ACCENT_PRESETS = {
    "white": "#ffffff",
    "blue": "#6cb6ff",
    "red": "#ff5a5a",
}


@dataclass
class Settings:
    accent_name: str = "blue"
    accent_custom: str = "#6cb6ff"
    font_family: str = "Consolas"
    font_size: int = 12
    prompt_path: str = ""
    scan_exclude_dirs: list[str] = field(default_factory=list)
    scan_exclude_files: list[str] = field(default_factory=list)
    last_project: str = ""


class SettingsStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or SETTINGS_FILE
        self._settings = self._load()

    def _load(self) -> Settings:
        if not self.path.exists():
            return Settings()
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return Settings()
        s = Settings()
        for key, value in data.items():
            if hasattr(s, key):
                setattr(s, key, value)
        return s

    def get(self) -> Settings:
        return self._settings

    def save(self, settings: Settings) -> None:
        self._settings = settings
        self.path.write_text(
            json.dumps(asdict(settings), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def accent_color(self) -> str:
        s = self._settings
        if s.accent_name in ACCENT_PRESETS:
            return ACCENT_PRESETS[s.accent_name]
        return s.accent_custom