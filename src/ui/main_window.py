from pathlib import Path

from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QPushButton,
    QFileDialog,
    QApplication,
    QMessageBox,
)
from PySide6.QtCore import Qt, QTimer

from domain.apply_plan import apply_plan, format_report
from domain.main_file_store import MainFileStore
from domain.settings_store import Settings, SettingsStore
from services.clipboard_service import copy_prompt, copy_project_content
from services.preview_service import build_preview
from services.run_service import RunService
from ui.settings_dialog import SettingsDialog
from ui.theme import apply_theme
from ui.widgets.project_tree import ProjectTree
from ui.widgets.center_tabs import CenterTabs
from ui.widgets.preview_panel import PreviewPanel
from ui.widgets.console_panel import ConsolePanel


class MainWindow(QMainWindow):
    def __init__(self, store: SettingsStore | None = None) -> None:
        super().__init__()
        self.setWindowTitle("LLM Assistant")
        self.resize(1200, 800)

        self.store = store or SettingsStore()
        self.current_project: Path | None = None
        self.main_file: str | None = None
        self.main_store: MainFileStore | None = None
        self.run_service = RunService(self)
        self.run_service.output_ready.connect(self.console_panel_append)
        self.run_service.finished.connect(self._on_run_finished)
        self.run_service.failed.connect(self._on_run_failed)

        self._build_menu()
        self._build_central()
        self._apply_editor_font(self.store.get())
        self.statusBar().showMessage("Открой проект: Проект → Открыть проект…")
        QTimer.singleShot(0, self._offer_last_project)

    def _build_menu(self) -> None:
        project_menu = self.menuBar().addMenu("Проект")
        open_action = QAction("Открыть проект…", self)
        open_action.triggered.connect(self._open_project)
        project_menu.addAction(open_action)

        llm_menu = self.menuBar().addMenu("Для LLM")
        copy_prompt_action = QAction("Скопировать промпт", self)
        copy_prompt_action.triggered.connect(self._on_copy_prompt)
        llm_menu.addAction(copy_prompt_action)

        copy_project_action = QAction("Скопировать содержание проекта", self)
        copy_project_action.triggered.connect(self._on_copy_project)
        llm_menu.addAction(copy_project_action)

        settings_action = QAction("Настройки…", self)
        settings_action.triggered.connect(self._open_settings)
        self.menuBar().addAction(settings_action)

    def _build_central(self) -> None:
        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(0)

        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)
        top_bar.setSpacing(8)
        self.btn_apply = QPushButton("Выполнить изменения")
        self.btn_apply.setEnabled(False)
        self.btn_apply.clicked.connect(self._on_apply_clicked)
        self.btn_run = QPushButton("Запуск")
        self.btn_run.setEnabled(False)
        self.btn_run.clicked.connect(self._on_run_clicked)
        top_bar.addStretch(1)
        top_bar.addWidget(self.btn_apply)
        top_bar.addWidget(self.btn_run)
        root.addLayout(top_bar)

        main_splitter = QSplitter(Qt.Horizontal)

        self.project_tree = ProjectTree()
        self.project_tree.set_main_requested.connect(self._on_set_main_requested)
        self.project_tree.open_file_requested.connect(self._on_open_file_requested)
        main_splitter.addWidget(self.project_tree)

        right_splitter = QSplitter(Qt.Vertical)
        self.center_tabs = CenterTabs()
        self.center_tabs.code_input.text_changed_debounced.connect(self._on_raw_changed)
        right_splitter.addWidget(self.center_tabs)

        bottom_splitter = QSplitter(Qt.Horizontal)
        self.preview_panel = PreviewPanel()
        self.console_panel = ConsolePanel()
        bottom_splitter.addWidget(self.preview_panel)
        bottom_splitter.addWidget(self.console_panel)
        bottom_splitter.setStretchFactor(0, 1)
        bottom_splitter.setStretchFactor(1, 1)

        right_splitter.addWidget(bottom_splitter)
        right_splitter.setStretchFactor(0, 2)
        right_splitter.setStretchFactor(1, 1)

        main_splitter.addWidget(right_splitter)
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 3)

        root.addWidget(main_splitter, 1)
        self.setCentralWidget(central)

    def _apply_editor_font(self, settings: Settings) -> None:
        family = settings.font_family or "Consolas"
        size = settings.font_size or 12
        self.center_tabs.code_input.editor.setStyleSheet(
            f"font-family: '{family}', monospace; font-size: {size}px;"
        )

    def console_panel_append(self, text: str) -> None:
        self.console_panel.append(text)

    def _offer_last_project(self) -> None:
        settings = self.store.get()
        last = settings.last_project.strip()
        if not last:
            return
        path = Path(last)
        if not path.is_dir():
            return
        answer = QMessageBox.question(
            self,
            "Открыть последний проект?",
            f"Открыть последний проект?\n{path}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )
        if answer == QMessageBox.Yes:
            self._load_project(path)

    def _open_settings(self) -> None:
        dialog = SettingsDialog(self.store.get(), self)
        dialog.set_apply_theme_callback(self._apply_accent_live)
        if dialog.exec():
            new_settings = dialog.result_settings()
            self.store.save(new_settings)
            app = QApplication.instance()
            if app is not None:
                apply_theme(app, self.store.accent_color())
            self._apply_editor_font(new_settings)

    def _apply_accent_live(self, hex_color: str) -> None:
        app = QApplication.instance()
        if app is not None:
            app.setStyleSheet(self._build_stylesheet_with_accent(hex_color))

    def _build_stylesheet_with_accent(self, accent: str) -> str:
        from config import THEME_FILE
        if not THEME_FILE.exists():
            return ""
        template = THEME_FILE.read_text(encoding="utf-8")
        return template.replace("__ACCENT__", accent)

    def _open_project(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Открыть проект")
        if not folder:
            return
        self._load_project(Path(folder))

    def _load_project(self, path: Path) -> None:
        self.current_project = path
        self.main_store = MainFileStore(self.current_project)
        self.main_file = self.main_store.get_main_file()
        self.project_tree.load_project(self.current_project, self.main_file)
        self._update_run_state()
        self._refresh_preview()
        settings = self.store.get()
        settings.last_project = str(self.current_project)
        self.store.save(settings)
        if self.main_file:
            self.statusBar().showMessage(f"Проект: {self.current_project} | main: {self.main_file}")
        else:
            self.statusBar().showMessage(
                f"Проект: {self.current_project} | выбери main-файл (ПКМ по файлу)"
            )

    def _on_set_main_requested(self, rel_path: str) -> None:
        if not self.main_store:
            return
        self.main_store.set_main_file(rel_path)
        self.main_file = rel_path
        self.project_tree.set_main_file(rel_path)
        self._update_run_state()
        self.statusBar().showMessage(f"Main: {rel_path}")

    def _on_open_file_requested(self, rel_path: str) -> None:
        if not self.current_project:
            return
        self.center_tabs.open_file_tab(self.current_project, rel_path)

    def _update_run_state(self) -> None:
        running = self.run_service.is_running()
        self.btn_run.setEnabled(self.main_file is not None and not running)
        if self.main_file:
            self.btn_run.setToolTip(f"poetry run python {self.main_file}")
        else:
            self.btn_run.setToolTip("Сначала выбери main-файл (ПКМ по файлу)")

    def _on_raw_changed(self, text: str) -> None:
        self._refresh_preview(text)

    def _refresh_preview(self, text: str | None = None) -> None:
        if text is None:
            text = self.center_tabs.raw_text()
        preview_text, actionable = build_preview(self.current_project, text)
        self.preview_panel.set_preview(preview_text)
        self.btn_apply.setEnabled(actionable > 0 and self.current_project is not None)

    def _on_apply_clicked(self) -> None:
        if not self.current_project:
            self.statusBar().showMessage("Проект не открыт")
            return
        raw = self.center_tabs.raw_text()
        report = apply_plan(self.current_project, raw)
        self.console_panel.append("=== Применение изменений ===")
        self.console_panel.append(format_report(report).rstrip())

        self.project_tree.load_project(self.current_project, self.main_file)
        self._refresh_preview()
        summary = f"+{len(report.created)} ~{len(report.updated)} -{len(report.deleted)}"
        if report.errors:
            self.statusBar().showMessage(f"Применено с ошибками: {summary}")
        else:
            self.statusBar().showMessage(f"Применено: {summary}")

    def _on_copy_prompt(self) -> None:
        ok, msg = copy_prompt()
        self.statusBar().showMessage(msg)

    def _on_copy_project(self) -> None:
        if not self.current_project:
            self.statusBar().showMessage("Проект не открыт")
            return
        ok, msg = copy_project_content(self.current_project)
        self.statusBar().showMessage(msg)

    def _on_run_clicked(self) -> None:
        if not self.current_project or not self.main_file:
            self.statusBar().showMessage("Нет проекта или main-файла")
            return
        self.console_panel.clear()
        self.console_panel.append(f"=== Запуск: {self.main_file} ===")
        self.btn_run.setEnabled(False)
        self.run_service.start(self.current_project, self.main_file)

    def _on_run_finished(self, code: int) -> None:
        self.console_panel.append(f"=== Процесс завершён (код {code}) ===")
        self.statusBar().showMessage(f"Завершено, код {code}")
        self._update_run_state()

    def _on_run_failed(self, message: str) -> None:
        self.console_panel.append(f"[ОШИБКА] {message}")
        self.statusBar().showMessage(message)
        self._update_run_state()