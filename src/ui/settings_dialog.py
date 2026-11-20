from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QColor, QDesktopServices
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QFileDialog,
    QWidget,
)

from domain.settings_store import ACCENT_PRESETS, Settings
from ui.widgets.accent_picker import AccentPicker
from ui.widgets.easter_egg import EasterEggDialog


class SettingsDialog(QDialog):
    def __init__(self, settings: Settings, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.resize(560, 560)
        self._settings = settings
        self._apply_theme_cb = None

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Акцентный цвет"))
        self.picker = AccentPicker()
        layout.addWidget(self.picker)

        layout.addWidget(QLabel("Шрифт редактора"))
        row = QHBoxLayout()
        self.font_family = QLineEdit(settings.font_family)
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 32)
        self.font_size.setValue(settings.font_size)
        row.addWidget(self.font_family, 1)
        row.addWidget(self.font_size)
        layout.addLayout(row)

        layout.addWidget(QLabel("Путь к промпту"))
        prompt_row = QHBoxLayout()
        self.prompt_path = QLineEdit(settings.prompt_path)
        open_folder = QPushButton("Открыть папку")
        open_folder.clicked.connect(self._open_prompt_folder)
        browse = QPushButton("…")
        browse.clicked.connect(self._browse_prompt)
        prompt_row.addWidget(self.prompt_path, 1)
        prompt_row.addWidget(open_folder)
        prompt_row.addWidget(browse)
        layout.addLayout(prompt_row)

        layout.addWidget(QLabel("Исключения сканера: папки (через запятую)"))
        self.exclude_dirs = QLineEdit(", ".join(settings.scan_exclude_dirs))
        layout.addWidget(self.exclude_dirs)

        layout.addWidget(QLabel("Исключения сканера: файлы (через запятую)"))
        self.exclude_files = QLineEdit(", ".join(settings.scan_exclude_files))
        layout.addWidget(self.exclude_files)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        save = QPushButton("Сохранить")
        save.setObjectName("accentButton")
        save.clicked.connect(self.accept)
        cancel = QPushButton("Отмена")
        cancel.clicked.connect(self.reject)
        buttons.addWidget(cancel)
        buttons.addWidget(save)
        layout.addLayout(buttons)

        self.picker.accent_changed.connect(self._on_accent_changed)
        self.picker.preset_clicked.connect(self._on_preset_clicked)
        self._preset_sequence: list[str] = []
        self._preset_timer = None

    def set_apply_theme_callback(self, cb) -> None:
        self._apply_theme_cb = cb

    def _open_prompt_folder(self) -> None:
        path = self.prompt_path.text().strip()
        if not path:
            return
        folder = Path(path).parent
        if folder.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder)))

    def _browse_prompt(self) -> None:
        file, _ = QFileDialog.getOpenFileName(self, "Выбрать файл промпта")
        if file:
            self.prompt_path.setText(file)

    def _on_accent_changed(self, color: QColor) -> None:
        if self._apply_theme_cb:
            self._apply_theme_cb(color.name())

    def _on_preset_clicked(self, name: str) -> None:
        from PySide6.QtCore import QTimer
        self._preset_sequence.append(name)
        if self._preset_timer is None:
            self._preset_timer = QTimer(self)
            self._preset_timer.setSingleShot(True)
            self._preset_timer.setInterval(3000)
            self._preset_timer.timeout.connect(self._reset_sequence)
        self._preset_timer.start()
        if self._preset_sequence[-3:] == ["white", "blue", "red"]:
            self._preset_sequence.clear()
            EasterEggDialog(self).exec()

    def _reset_sequence(self) -> None:
        self._preset_sequence.clear()

    def result_settings(self) -> Settings:
        s = Settings(
            accent_name=self._settings.accent_name,
            accent_custom=self._settings.accent_custom,
            font_family=self.font_family.text().strip() or "Consolas",
            font_size=self.font_size.value(),
            prompt_path=self.prompt_path.text().strip(),
            scan_exclude_dirs=[x.strip() for x in self.exclude_dirs.text().split(",") if x.strip()],
            scan_exclude_files=[x.strip() for x in self.exclude_files.text().split(",") if x.strip()],
            last_project=self._settings.last_project,
        )
        color = self.picker.current_color()
        for name, hexv in ACCENT_PRESETS.items():
            if hexv.lower() == color.name():
                s.accent_name = name
                return s
        s.accent_name = "custom"
        s.accent_custom = color.name()
        return s